import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="员工管理系统", page_icon="📊", layout="wide")
st.title("📊 员工管理系统 & 数据看板")

# 必须用相对路径
db_path = 'practice.db'

def get_data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 自动建表并填入数据（解决云端空库问题）
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
        cursor.execute("INSERT INTO users (name, role) VALUES ('张三', 'CTO')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('王五', '财务')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('李四', '销售')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('赵六', '销售')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('孙七', '技术')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('周八', '技术')")
        cursor.execute("INSERT INTO users (name, role) VALUES ('吴九', '技术')")
        conn.commit()
    
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

with st.sidebar:
    st.header("🛠️ 数据操作")
    
    st.subheader("➕ 新增员工")
    new_name = st.text_input("姓名", key="add_name")
    new_role = st.text_input("角色", key="add_role")
    if st.button("添加"):
        if new_name and new_role:
            execute_query("INSERT INTO users (name, role) VALUES (?, ?)", (new_name, new_role))
            st.success("添加成功！")
        else:
            st.warning("请填写完整")
            
    st.divider()
    
    st.subheader("✏️ 修改角色")
    modify_name = st.text_input("要修改谁的名字？", key="mod_name")
    modify_role = st.text_input("改成什么角色？", key="mod_role")
    if st.button("更新"):
        if modify_name and modify_role:
            execute_query("UPDATE users SET role = ? WHERE name = ?", (modify_role, modify_name))
            st.success(f"已更新 {modify_name} 的角色！")
        else:
            st.warning("请填写完整")

    st.divider()

    st.subheader("🗑️ 删除员工")
    delete_name = st.text_input("要开除谁？(输入名字)", key="del_name")
    if st.button("删除", type="primary"):
        if delete_name:
            execute_query("DELETE FROM users WHERE name = ?", (delete_name,))
            st.success(f"已删除 {delete_name}！")
        else:
            st.warning("请输入要删除的名字")

col1, col2 = st.columns([1, 1])
data = get_data()

with col1:
    st.subheader("👥 当前员工列表")
    st.dataframe(data, use_container_width=True)

with col2:
    st.subheader("📈 团队角色分布")
    if not data.empty:
        role_counts = data['role'].value_counts()
        chart_type = st.radio("选择图表类型：", ["柱状图", "饼图"], horizontal=True)
        
        if chart_type == "柱状图":
            st.bar_chart(role_counts)
        else:
            fig, ax = plt.subplots()
            ax.pie(role_counts, labels=role_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal') 
            st.pyplot(fig)
    else:
        st.info("没有数据，请先添加员工。")
