import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os

# ================= 1. 字体与页面设置 =================
font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
font_path = "NotoSansCJKsc-Regular.otf"
if not os.path.exists(font_path):
    urllib.request.urlretrieve(font_url, font_path)
fm.fontManager.addfont(font_path)
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC'] 
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="员工管理系统", page_icon="📊", layout="wide")

# ================= 2. 登录验证 =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 系统登录")
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        if st.form_submit_button("登录"):
            if username == "admin" and password == "123456":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("用户名或密码错误！")
    st.stop()

st.sidebar.success("✅ 已登录: admin")
if st.sidebar.button("退出登录"):
    st.session_state.logged_in = False
    st.rerun()

st.title("📊 员工管理系统 & 薪资看板")
db_path = 'practice.db'

# ================= 3. 数据库：自动建两张表并关联 =================
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS salaries (id INTEGER PRIMARY KEY, user_id INTEGER, amount INTEGER, month TEXT)")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, role) VALUES ('张三', 'CTO')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('王五', '财务')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('李四', '销售')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('赵六', '销售')")
        cursor.execute("INSERT INTO salaries (user_id, amount, month) VALUES (1, 50000, '2026-11')")
        cursor.execute("INSERT INTO salaries (user_id, amount, month) VALUES (2, 15000, '2026-11')")
        cursor.execute("INSERT INTO salaries (user_id, amount, month) VALUES (3, 8000, '2026-11')")
        conn.commit()
    conn.close()

init_db()

def get_joined_data(search_term=""):
    conn = sqlite3.connect(db_path)
    query = """
        SELECT u.id, u.name, u.role, COALESCE(s.amount, 0) as 工资, s.month as 月份
        FROM users u
        LEFT JOIN salaries s ON u.id = s.user_id
    """
    if search_term:
        query += f" WHERE u.name LIKE '%{search_term}%' OR u.role LIKE '%{search_term}%'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

# ================= 4. 侧边栏：完整数据操作 =================
with st.sidebar:
    st.header("🛠️ 数据操作")
    
    # 新增
    st.subheader("➕ 新增员工")
    new_name = st.text_input("姓名", key="add_name")
    new_role = st.text_input("角色", key="add_role")
    if st.button("添加"):
        if new_name and new_role:
            execute_query("INSERT INTO users (name, role) VALUES (?, ?)", (new_name, new_role))
            st.success("添加成功！")
            st.rerun()
        else:
            st.warning("请填写完整")

    st.divider()

    # 修改
    st.subheader("✏️ 修改角色")
    modify_name = st.text_input("要修改谁的名字？", key="mod_name")
    modify_role = st.text_input("改成什么角色？", key="mod_role")
    if st.button("更新"):
        if modify_name and modify_role:
            execute_query("UPDATE users SET role = ? WHERE name = ?", (modify_role, modify_name))
            st.success(f"已更新 {modify_name}！")
            st.rerun()
        else:
            st.warning("请填写完整")

    st.divider()

    # 删除
    st.subheader("🗑️ 删除员工")
    delete_name = st.text_input("要开除谁？(输入名字)", key="del_name")
    if st.button("删除", type="primary"):
        if delete_name:
            execute_query("DELETE FROM users WHERE name = ?", (delete_name,))
            st.success(f"已删除 {delete_name}！")
            st.rerun()
        else:
            st.warning("请输入名字")

# ================= 5. 主界面：搜索与多表展示 =================
st.subheader("🔍 员工综合查询（输入名字或角色进行实时搜索）")
search_query = st.text_input("搜索框：", "")

data = get_joined_data(search_query)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("👥 员工与薪资详情")
    st.dataframe(data, width='stretch')

with col2:
    st.subheader("📈 团队角色分布")
    if not data.empty:
        role_counts = data['role'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(role_counts, labels=role_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal') 
        st.pyplot(fig)
    else:
        st.info("没有找到匹配的数据。")
