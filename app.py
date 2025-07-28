import streamlit as st
import csv
import os
import datetime

# 保存フォルダ名を変更
DATA_FILE = "customers.csv"
VISIT_FILE = "visits.csv"
PHOTO_DIR = "photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

# --------------------- データ読み込みと保存 ---------------------
def load_customers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_customers(customers):
    with open(DATA_FILE, mode="w", encoding="utf-8", newline="") as f:
        fieldnames = ["名前", "電話番号", "生年月日", "ジェル", "メモ"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(customers)

def load_visits():
    if not os.path.exists(VISIT_FILE):
        return []
    with open(VISIT_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_visits(visits):
    with open(VISIT_FILE, mode="w", encoding="utf-8", newline="") as f:
        fieldnames = ["名前", "来店日", "写真", "メモ", "メニュー"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(visits)

# --------------------- ユーティリティ関数 ---------------------
def calculate_age(birthdate_str):
    try:
        birthdate = datetime.datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    except:
        return "不明"

# --------------------- セッション状態の初期化 ---------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = ""

customers = load_customers()
visits = load_visits()

gel_options = ["RICH GEL", "グレースジェルベース", "NAIL MEIYIZI", "RAINEY", "AKO ALICE NAIL", "para gel"]
menu_options = ["ワンカラー", "フレンチ", "定額コース", "シンプルコース", "ゴージャスコース", "マグネット", "マグネットフレンチ", "チークカラー", "ガラス・ミラーフレンチ"]

# --------------------- UI ---------------------
st.title("💅 ネイルサロン顧客管理アプリ")

if st.session_state.page != "home":
    if st.button("🏠 トップに戻る"):
        st.session_state.page = "home"
        st.session_state.search_keyword = ""
        st.rerun()
    st.markdown("---")

# --------------------- トップページ ---------------------
if st.session_state.page == "home":
    st.subheader("メニューを選択してください")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ 新規登録"):
            st.session_state.page = "register"
    with col2:
        if st.button("🔍 会員検索"):
            st.session_state.page = "search"
    with col3:
        if st.button("📋 顧客一覧"):
            st.session_state.page = "list"
    with col4:
        if st.button("📸 来店履歴"):
            st.session_state.page = "history"

# --------------------- 新規顧客登録 ---------------------
elif st.session_state.page == "register":
    st.header("➕ 新規顧客登録")
    with st.form("register_form"):
        name = st.text_input("名前")
        phone = st.text_input("電話番号")
        birthdate = st.date_input("生年月日", min_value=datetime.date(1900,1,1), max_value=datetime.date.today())
        gels = st.multiselect("使用ジェル", gel_options)
        memo = st.text_area("メモ")
        submitted = st.form_submit_button("登録")
        if submitted:
            if name and phone:
                customers.append({
                    "名前": name,
                    "電話番号": phone,
                    "生年月日": birthdate.strftime("%Y-%m-%d"),
                    "ジェル": ", ".join(gels),
                    "メモ": memo
                })
                save_customers(customers)
                st.success(f"{name} さんを登録しました！")
                st.session_state.page = "search"
                st.session_state.search_keyword = name
                st.rerun()
            else:
                st.error("名前と電話番号は必須です")

# --------------------- 顧客検索 ---------------------
elif st.session_state.page == "search":
    st.header("🔍 顧客検索")
    search = st.text_input("検索キーワード", value=st.session_state.search_keyword)
    st.session_state.search_keyword = search
    filtered = [c for c in customers if search in c["名前"]] if search else []

    for idx, customer in enumerate(filtered):
        st.subheader(f"{customer['名前']}（{customer['電話番号']}）")
        st.write(f"生年月日: {customer['生年月日']}（{calculate_age(customer['生年月日'])}歳）")
        st.write(f"使用ジェル: {customer['ジェル']}")
        st.write(f"メモ: {customer['メモ']}")

        with st.expander("✏️ 顧客情報編集"):
            name = st.text_input("名前", value=customer["名前"], key=f"name_{idx}")
            phone = st.text_input("電話番号", value=customer["電話番号"], key=f"phone_{idx}")
            birthdate = st.date_input("生年月日", value=datetime.datetime.strptime(customer["生年月日"], "%Y-%m-%d").date(), key=f"birth_{idx}")
            gels = st.multiselect("使用ジェル", gel_options, default=[g for g in customer["ジェル"].split(", ") if g], key=f"gel_{idx}")
            memo = st.text_area("メモ", value=customer["メモ"], key=f"memo_{idx}")

            if st.button("保存", key=f"save_{idx}"):
                customer.update({
                    "名前": name,
                    "電話番号": phone,
                    "生年月日": birthdate.strftime("%Y-%m-%d"),
                    "ジェル": ", ".join(gels),
                    "メモ": memo
                })
                save_customers(customers)
                st.success("保存しました")

        if st.button("🗑️ 顧客を削除", key=f"delete_customer_{idx}"):
            customers.remove(customer)
            save_customers(customers)
            visits[:] = [v for v in visits if v["名前"] != customer["名前"]]
            save_visits(visits)
            st.success(f"{customer['名前']} さんのデータを削除しました。トップページに戻ります。")
            st.session_state.page = "home"
            st.rerun()

        st.markdown("##### 📌 来店履歴の登録")
        visit_date = st.date_input("来店日", value=datetime.date.today(), key=f"visit_date_{idx}")
        menu = st.selectbox("メニュー", menu_options, key=f"menu_{idx}")
        visit_memo = st.text_area("来店メモ", key=f"visit_memo_{idx}")
        photo_file = st.file_uploader("写真アップロード（任意）", type=["png", "jpg", "jpeg"], key=f"photo_{idx}")

        photo_path = ""
        if photo_file:
            filename = f"{customer['名前']}_{visit_date.strftime('%Y%m%d')}_{photo_file.name}"
            photo_path = os.path.join(PHOTO_DIR, filename)
            with open(photo_path, "wb") as f:
                f.write(photo_file.read())

        if st.button("📸 来店履歴を保存", key=f"visit_save_{idx}"):
            visits.append({
                "名前": customer["名前"],
                "来店日": visit_date.strftime("%Y-%m-%d"),
                "写真": photo_path,
                "メモ": visit_memo,
                "メニュー": menu
            })
            save_visits(visits)
            st.success("来店履歴を保存しました")

        customer_visits = [v for v in visits if v["名前"] == customer["名前"]]
        for v_idx, visit in enumerate(sorted(customer_visits, key=lambda x: x["来店日"], reverse=True)):
            with st.expander(f"🗓️ {visit['来店日']} - {visit['メニュー']}"):
                new_menu = st.text_input("メニュー", value=visit["メニュー"], key=f"edit_menu_{idx}_{v_idx}")
                new_memo = st.text_area("メモ", value=visit["メモ"], key=f"edit_memo_{idx}_{v_idx}")
                if visit["写真"] and os.path.exists(visit["写真"]):
                    st.image(visit["写真"], width=300)
                if st.button("更新", key=f"update_visit_{idx}_{v_idx}"):
                    visit["メニュー"] = new_menu
                    visit["メモ"] = new_memo
                    save_visits(visits)
                    st.success("来店履歴を更新しました")
                if st.button("❌ 来店履歴を削除", key=f"delete_visit_{idx}_{v_idx}"):
                    visits.remove(visit)
                    save_visits(visits)
                    st.success("来店履歴を削除しました")
                    st.rerun()

# --------------------- 顧客一覧 ---------------------
elif st.session_state.page == "list":
    st.header("📋 顧客一覧")
    for idx, customer in enumerate(customers):
        if st.button(customer["名前"], key=f"goto_{idx}"):
            st.session_state.page = "search"
            st.session_state.search_keyword = customer["名前"]
            st.rerun()
        st.write(f"📞 {customer['電話番号']} / 🎂 {customer['生年月日']} / 💅 {customer['ジェル']}")
        st.markdown("---")

# --------------------- 来店履歴一覧 ---------------------
elif st.session_state.page == "history":
    st.header("📸 来店履歴一覧")
    for idx, visit in enumerate(sorted(visits, key=lambda x: x["来店日"], reverse=True)):
        if st.button(visit["名前"], key=f"hist_{idx}"):
            st.session_state.page = "search"
            st.session_state.search_keyword = visit["名前"]
            st.rerun()
        st.write(f"🗓️ {visit['来店日']} - 💅 {visit['メニュー']}")
        st.write(f"📝 {visit['メモ']}")
        if visit["写真"] and os.path.exists(visit["写真"]):
            st.image(visit["写真"], width=300)
        else:
            st.write("📁 写真なし")
        st.markdown("---")
