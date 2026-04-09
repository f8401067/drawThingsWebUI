"""
数据库管理模块 - 使用 SQLite 存储生成历史
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

# 数据库文件路径
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'history.db')


@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器
    
    自动处理连接的打开和关闭，确保资源正确释放。
    
    Yields:
        sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """初始化数据库
    
    创建历史记录表，如果表已存在则跳过。
    包含必要的索引以优化查询性能。
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 检查是否需要重建表（从旧版本升级）
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generation_history'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # 检查表结构是否包含 user_id 字段
            cursor.execute("PRAGMA table_info(generation_history)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'user_id' not in columns and 'uid' in columns:
                # 旧表结构，需要重建
                print("检测到旧表结构，正在重建...")
                cursor.execute('DROP TABLE IF EXISTS generation_history')
                cursor.execute('DROP TABLE IF EXISTS users')
                table_exists = None
        
        if not table_exists:
            # 创建历史记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    image_id TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    image_filename TEXT NOT NULL,
                    prompt TEXT,
                    negative_prompt TEXT,
                    width INTEGER DEFAULT 512,
                    height INTEGER DEFAULT 512,
                    steps INTEGER DEFAULT 8,
                    seed INTEGER DEFAULT -1,
                    elapsed_time REAL,
                    rating INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # 创建用户表（使用自增ID）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            print("数据库表创建完成")
        
        # 创建索引以优化查询
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_user_id 
            ON generation_history(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_created_at 
            ON generation_history(created_at)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_user_id_created 
            ON generation_history(user_id, created_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_rating 
            ON generation_history(rating)
        ''')
        
        print("数据库初始化完成")


def get_or_create_user(is_new=False):
    """获取或创建用户记录
    
    Args:
        is_new (bool): 如果为 True，则总是创建新用户；如果为 False，则返回最后一个用户
    
    Returns:
        int: 用户 ID
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if is_new:
            # 强制创建新用户
            cursor.execute('INSERT INTO users (first_seen, last_seen) VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)')
            new_id = cursor.lastrowid
            print(f"创建新用户 ID: {new_id}")
            return new_id
        else:
            # 获取最后一个用户（用于向后兼容）
            cursor.execute('SELECT id FROM users ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            
            if row:
                # 更新最后访问时间
                user_id = row['id']
                cursor.execute('UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
                return user_id
            else:
                # 没有用户，创建第一个
                cursor.execute('INSERT INTO users (first_seen, last_seen) VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)')
                new_id = cursor.lastrowid
                print(f"创建第一个用户 ID: {new_id}")
                return new_id


def add_history_record(record):
    """添加一条生成历史记录
    
    Args:
        record (dict): 包含图片信息的记录字典
            - user_id: 用户 ID（整数）
            - image_id: 图片 ID（时间戳）
            - image_url: 图片 URL
            - image_filename: 图片文件名
            - prompt: 提示词
            - negative_prompt: 负面提示词
            - width: 图片宽度
            - height: 图片高度
            - steps: 生成步数
            - seed: 随机种子
            - elapsed_time: 耗时（秒）
            - rating: 评分（-1为bad，0为未评分，1-5为星级）
    
    Returns:
        int: 新记录的 ID
    """
    user_id = record.get('user_id')
    if not user_id:
        raise ValueError("Record must contain 'user_id'")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO generation_history (
                user_id, image_id, image_url, image_filename,
                prompt, negative_prompt, width, height, steps, seed,
                elapsed_time, rating, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            record.get('id'),
            record.get('image_url'),
            record.get('image_filename'),
            record.get('prompt', ''),
            record.get('negative_prompt', ''),
            record.get('width', 512),
            record.get('height', 512),
            record.get('steps', 8),
            record.get('seed', -1),
            record.get('elapsed_time', 0),
            record.get('rating', 0),
            record.get('created_at', datetime.now().isoformat())
        ))
        
        return cursor.lastrowid


def get_user_history(user_id, limit=50, offset=0, date_filter=None, rating_filter=None):
    """获取指定用户的历史记录
    
    Args:
        user_id (int): 用户 ID
        limit (int): 返回记录数量限制
        offset (int): 偏移量（用于分页）
        date_filter (str, optional): 日期筛选，格式 YYYY-MM-DD
        rating_filter (int or list, optional): 评分筛选（-1为bad，1-5为星级），支持单个值或列表
    
    Returns:
        list: 历史记录列表（字典形式）
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = ['user_id = ?']
        params = [user_id]
        
        if date_filter:
            conditions.append('DATE(created_at) = ?')
            params.append(date_filter)
        
        if rating_filter is not None:
            # 支持多个评级筛选
            if isinstance(rating_filter, list):
                if len(rating_filter) > 0:
                    placeholders = ','.join(['?' for _ in rating_filter])
                    conditions.append(f'rating IN ({placeholders})')
                    params.extend(rating_filter)
            else:
                conditions.append('rating = ?')
                params.append(rating_filter)
        
        where_clause = ' AND '.join(conditions)
        
        query = f'''
            SELECT * FROM generation_history 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_all_history(limit=100, offset=0, date_filter=None, rating_filter=None):
    """获取所有用户的历史记录
    
    Args:
        limit (int): 返回记录数量限制
        offset (int): 偏移量（用于分页）
        date_filter (str, optional): 日期筛选，格式 YYYY-MM-DD
        rating_filter (int or list, optional): 评分筛选（-1为bad，1-5为星级），支持单个值或列表
    
    Returns:
        list: 历史记录列表（字典形式）
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if date_filter:
            conditions.append('DATE(created_at) = ?')
            params.append(date_filter)
        
        if rating_filter is not None:
            # 支持多个评级筛选
            if isinstance(rating_filter, list):
                if len(rating_filter) > 0:
                    placeholders = ','.join(['?' for _ in rating_filter])
                    conditions.append(f'rating IN ({placeholders})')
                    params.extend(rating_filter)
            else:
                conditions.append('rating = ?')
                params.append(rating_filter)
        
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        
        query = f'''
            SELECT * FROM generation_history 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_available_dates(user_id=None):
    """获取有记录的日期列表
    
    Args:
        user_id (int, optional): 用户 ID，如果为 None 则返回所有用户的日期
    
    Returns:
        list: 日期列表（格式 YYYY-MM-DD），按降序排列
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if user_id:
            query = '''
                SELECT DISTINCT DATE(created_at) as date 
                FROM generation_history 
                WHERE user_id = ?
                ORDER BY date DESC
            '''
            cursor.execute(query, (user_id,))
        else:
            query = '''
                SELECT DISTINCT DATE(created_at) as date 
                FROM generation_history 
                ORDER BY date DESC
            '''
            cursor.execute(query)
        
        rows = cursor.fetchall()
        return [row['date'] for row in rows]


def clear_user_history(user_id):
    """清空指定用户的历史记录
    
    Args:
        user_id (int): 用户 ID
    
    Returns:
        int: 删除的记录数量
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM generation_history WHERE user_id = ?', (user_id,))
        return cursor.rowcount


def get_history_count(user_id=None, date_filter=None, rating_filter=None):
    """获取历史记录数量
    
    Args:
        user_id (int, optional): 用户 ID，如果为 None 则统计所有用户
        date_filter (str, optional): 日期筛选，格式 YYYY-MM-DD
        rating_filter (int or list, optional): 评分筛选（-1为bad，1-5为星级），支持单个值或列表
    
    Returns:
        int: 记录数量
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if user_id:
            conditions.append('user_id = ?')
            params.append(user_id)
        
        if date_filter:
            conditions.append('DATE(created_at) = ?')
            params.append(date_filter)
        
        if rating_filter is not None:
            # 支持多个评级筛选
            if isinstance(rating_filter, list):
                if len(rating_filter) > 0:
                    placeholders = ','.join(['?' for _ in rating_filter])
                    conditions.append(f'rating IN ({placeholders})')
                    params.extend(rating_filter)
            else:
                conditions.append('rating = ?')
                params.append(rating_filter)
        
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        
        query = f'SELECT COUNT(*) as count FROM generation_history WHERE {where_clause}'
        cursor.execute(query, params)
        
        result = cursor.fetchone()
        return result['count'] if result else 0


def update_rating(image_id, rating):
    """更新图片评分
    
    Args:
        image_id (str): 图片 ID
        rating (int): 评分值（-1为bad，0为清除评分，1-5为星级）
    
    Returns:
        bool: 更新是否成功
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE generation_history 
            SET rating = ? 
            WHERE image_id = ?
        ''', (rating, image_id))
        return cursor.rowcount > 0


def get_bad_images(all_users=False, user_id=None):
    """获取所有标记为 Bad 的图片
    
    Args:
        all_users (bool): 是否获取所有用户的 Bad 图片
        user_id (int, optional): 用户 ID
    
    Returns:
        list: Bad 图片记录列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if all_users:
            query = '''
                SELECT * FROM generation_history 
                WHERE rating = -1
                ORDER BY created_at DESC
            '''
            cursor.execute(query)
        else:
            query = '''
                SELECT * FROM generation_history 
                WHERE rating = -1 AND user_id = ?
                ORDER BY created_at DESC
            '''
            cursor.execute(query, (user_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_bad_images(all_users=False, user_id=None):
    """删除所有标记为 Bad 的图片记录
    
    Args:
        all_users (bool): 是否删除所有用户的 Bad 图片
        user_id (int, optional): 用户 ID
    
    Returns:
        tuple: (删除的记录数, 删除的图片文件名列表)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 先获取要删除的图片文件名
        if all_users:
            query = 'SELECT image_filename FROM generation_history WHERE rating = -1'
            cursor.execute(query)
        else:
            query = 'SELECT image_filename FROM generation_history WHERE rating = -1 AND user_id = ?'
            cursor.execute(query, (user_id,))
        
        rows = cursor.fetchall()
        filenames = [row['image_filename'] for row in rows]
        
        # 删除记录
        if all_users:
            delete_query = 'DELETE FROM generation_history WHERE rating = -1'
            cursor.execute(delete_query)
        else:
            delete_query = 'DELETE FROM generation_history WHERE rating = -1 AND user_id = ?'
            cursor.execute(delete_query, (user_id,))
        
        deleted_count = cursor.rowcount
        return deleted_count, filenames


def migrate_from_json(json_file=None):
    """从 JSON 文件迁移数据到数据库（已弃用，仅保留接口）
    
    Args:
        json_file (str, optional): JSON 文件路径
    
    Returns:
        dict: 迁移统计信息
    """
    return {"success": False, "error": "Migration from JSON is no longer supported"}


# 初始化数据库（模块导入时自动执行）
init_database()
