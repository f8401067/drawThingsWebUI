"""
数据库迁移脚本 - 添加 is_nsfw 字段
"""

import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'history.db')

def add_nsfw_column():
    """为 generation_history 表添加 is_nsfw 字段"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # 检查 is_nsfw 列是否已存在
        cursor.execute("PRAGMA table_info(generation_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_nsfw' not in columns:
            print("Adding is_nsfw column to generation_history table...")
            cursor.execute('ALTER TABLE generation_history ADD COLUMN is_nsfw INTEGER DEFAULT 0')
            print("is_nsfw column added successfully!")
        else:
            print("is_nsfw column already exists.")
        
        # 创建索引（如果不存在）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_nsfw 
            ON generation_history(is_nsfw)
        ''')
        print("NSFW index created/verified.")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_nsfw_column()
