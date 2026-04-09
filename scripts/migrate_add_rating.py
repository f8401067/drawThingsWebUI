"""
数据库迁移脚本 - 添加 rating 字段
"""

import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'history.db')

def add_rating_column():
    """为 generation_history 表添加 rating 字段"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # 检查 rating 列是否已存在
        cursor.execute("PRAGMA table_info(generation_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'rating' not in columns:
            print("Adding rating column to generation_history table...")
            cursor.execute('ALTER TABLE generation_history ADD COLUMN rating INTEGER DEFAULT 0')
            print("Rating column added successfully!")
        else:
            print("Rating column already exists.")
        
        # 创建索引（如果不存在）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_rating 
            ON generation_history(rating)
        ''')
        print("Rating index created/verified.")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_rating_column()
