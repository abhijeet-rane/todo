import streamlit as st
import mysql.connector
import pandas as pd
import os

def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",   
        password="root",  
        database="todo_list",
        auth_plugin="mysql_native_password"
    )

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            description VARCHAR(255) NOT NULL,
            due_date DATE NOT NULL,
            status ENUM('Pending', 'Completed') DEFAULT 'Pending'
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def execute_query(query, params=None, fetch=False):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params) if params else cursor.execute(query)
        result = cursor.fetchall() if fetch else None
        conn.commit()
    except mysql.connector.Error as e:
        st.error(f"Database Error: {e}")
        result = None
    finally:
        cursor.close()
        conn.close()
    return result

# Initialize the database
create_table()

# Streamlit UI
st.title("📌 To-Do List Manager")

menu = st.sidebar.radio("Menu", ["➕ Add Task", "📋 View Tasks", "✏ Edit Task", "❌ Delete Task", "✔ Complete Task"])

if menu == "➕ Add Task":
    st.header("Add a New Task")
    task = st.text_input("Task Description")
    due_date = st.date_input("Due Date")
    if st.button("Save Task"):
        if task.strip():
            execute_query("INSERT INTO tasks (description, due_date) VALUES (%s, %s)", (task, due_date))
            st.success("🎉 Task Added Successfully!")
        else:
            st.warning("⚠ Task description cannot be empty.")

elif menu == "📋 View Tasks":
    st.header("Your To-Do List")
    filter_option = st.radio("Filter Tasks", ["All", "Pending", "Completed"])
    if filter_option == "Pending":
        tasks = execute_query("SELECT * FROM tasks WHERE status='Pending'", fetch=True)
    elif filter_option == "Completed":
        tasks = execute_query("SELECT * FROM tasks WHERE status='Completed'", fetch=True)
    else:
        tasks = execute_query("SELECT * FROM tasks", fetch=True)

    if tasks:
        df = pd.DataFrame(tasks)
        st.dataframe(df)
    else:
        st.info("🚀 No tasks available.")

elif menu == "✏ Edit Task":
    st.header("Edit Task Details")
    tasks = execute_query("SELECT * FROM tasks", fetch=True)
    if tasks:
        df = pd.DataFrame(tasks)
        st.dataframe(df)
        task_id = st.number_input("Enter Task ID to Edit", min_value=1, step=1)
        new_desc = st.text_input("New Task Description")
        new_date = st.date_input("New Due Date")
        if st.button("Update Task"):
            if new_desc.strip():
                execute_query("UPDATE tasks SET description=%s, due_date=%s WHERE id=%s",
                              (new_desc, new_date, task_id))
                st.success("✅ Task Updated!")
            else:
                st.warning("⚠ Task description cannot be empty.")
    else:
        st.info("No tasks found to edit.")

elif menu == "❌ Delete Task":
    st.header("Remove Task")
    tasks = execute_query("SELECT * FROM tasks", fetch=True)
    if tasks:
        df = pd.DataFrame(tasks)
        st.dataframe(df)
        task_id = st.number_input("Enter Task ID to Remove", min_value=1, step=1)
        if st.button("Delete Task"):
            execute_query("DELETE FROM tasks WHERE id=%s", (task_id,))
            st.success("🚮 Task Removed!")
        if st.button("Clear All Tasks"):
            if st.checkbox("Confirm Delete All Tasks"):
                execute_query("DELETE FROM tasks")
                st.success("🗑 All Tasks Cleared!")
    else:
        st.info("No tasks to delete.")

elif menu == "✔ Complete Task":
    st.header("Mark Task as Completed")
    tasks = execute_query("SELECT * FROM tasks WHERE status='Pending'", fetch=True)
    if tasks:
        df = pd.DataFrame(tasks)
        st.dataframe(df)
        task_id = st.number_input("Enter Task ID to Mark as Completed", min_value=1, step=1)
        if st.button("Complete Task"):
            execute_query("UPDATE tasks SET status='Completed' WHERE id=%s", (task_id,))
            st.success("🎯 Task Marked as Completed!")
    else:
        st.info("All tasks are already completed! 🎉")
