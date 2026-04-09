# 用户ID系统升级说明

## 概述

本次更新将用户标识系统从 UUID 字符串改为数字自增 ID，简化了用户管理并提高了数据库查询效率。

## 主要变更

### 1. 数据库结构变更

#### users 表
- **之前**: `uid TEXT PRIMARY KEY` - 使用 UUID 字符串作为主键
- **现在**: `id INTEGER PRIMARY KEY AUTOINCREMENT` - 使用自增整数作为主键

#### generation_history 表
- **之前**: `uid TEXT NOT NULL` - 外键引用 users.uid
- **现在**: `user_id INTEGER NOT NULL` - 外键引用 users.id

### 2. API 变更

#### 请求头变更
- **之前**: `X-User-UID: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- **现在**: `X-User-ID: 1` (整数)

#### 响应字段变更
所有 API 响应中的用户标识字段已更新：
- **之前**: `"uid": "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"`
- **现在**: `"user_id": 1`

### 3. 前端变更

#### index.html 和 history.html
- 移除了 UUID 生成逻辑
- 用户 ID 从 localStorage 加载（键名从 `user_uid` 改为 `user_id`）
- 如果 localStorage 中没有用户 ID，首次请求时服务器会自动创建

### 4. 后端变更

#### database.py
- `add_user(uid)` → `get_or_create_user()` - 返回整数用户 ID
- 所有函数的 `uid` 参数改为 `user_id` (int 类型)
- 更新了所有 SQL 查询以使用新的字段名

#### history_routes.py
- `get_user_uid()` → `get_user_id()` - 自动获取或创建用户 ID
- 移除了 UID 验证逻辑（不再需要检查是否存在）
- 所有路由处理函数更新为使用 `user_id`

#### app.py
- 添加了 `get_user_id()` 函数
- 更新了图片生成流程以使用数字用户 ID
- 弃用了 JSON 数据迁移功能

## 数据迁移

### 自动迁移
系统启动时会自动检测旧表结构：
1. 如果发现旧的 `uid` 字段，会自动删除旧表
2. 重新创建符合新结构的表
3. **注意**: 旧的历史记录数据不会被保留（根据需求，历史用户不需要兼容）

### 手动清理
以下文件已被删除：
- `history.db` - 旧数据库文件（已重建）
- `generation_history.json` - 旧的 JSON 历史文件

## 测试验证

运行测试脚本验证功能：
```bash
python test_numeric_user_id.py
```

测试包括：
1. ✓ 用户 ID 自动创建
2. ✓ 使用用户 ID 获取历史记录
3. ✓ 获取所有用户的历史记录
4. ✓ 日期查询功能

## 兼容性说明

### 不兼容的变更
- **历史数据**: 旧的用户数据不会迁移到新系统
- **API 客户端**: 使用旧 API 的客户端需要更新请求头和响应解析
- **浏览器缓存**: 建议用户清除浏览器缓存和 localStorage

### 向后兼容
- 如果客户端未提供 `X-User-ID` 头，服务器会自动创建新用户
- 前端页面会自动处理这种情况

## 优势

1. **性能提升**: 整数索引比字符串索引更高效
2. **存储优化**: 整数占用空间更小
3. **简化逻辑**: 无需生成和管理 UUID
4. **易于理解**: 数字 ID 更直观，便于调试和日志分析

## 注意事项

1. 用户 ID 是全局自增的，第一个访问系统的用户获得 ID=1
2. 用户 ID 一旦分配就不会改变
3. 不同浏览器/设备会有不同的用户 ID（除非手动同步 localStorage）
4. 评分功能仍然可以对所有用户的图片进行评分（不校验用户所有权）

## 回滚方案

如果需要回滚到旧系统：
1. 恢复 Git 版本到更新前
2. 删除新的 `history.db`
3. 如果有备份，恢复旧的 `history.db` 和 `generation_history.json`

**警告**: 回滚会导致新产生的数据丢失。
