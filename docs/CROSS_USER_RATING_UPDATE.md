# 跨用户评分功能更新说明

## 更新内容

移除了评分功能的用户ID校验，现在任何用户都可以对所有用户的图片进行评分。

## 修改文件

### 1. app.py
**修改位置**: `/api/rating` 接口

**改动说明**:
- 移除了 `update_rating()` 调用中的 `uid` 参数
- 更新错误提示信息从"未找到该图片或无权评分"改为"未找到该图片"
- 添加注释说明不校验用户ID

**修改前**:
```python
success = update_rating(image_id, uid, rating)
```

**修改后**:
```python
success = update_rating(image_id, rating)
```

### 2. database.py
**修改位置**: `update_rating()` 函数

**改动说明**:
- 移除函数参数中的 `uid` 参数
- 移除 SQL 查询中的 `AND uid = ?` 条件
- 更新函数文档字符串

**修改前**:
```python
def update_rating(image_id, uid, rating):
    cursor.execute('''
        UPDATE generation_history 
        SET rating = ? 
        WHERE image_id = ? AND uid = ?
    ''', (rating, image_id, uid))
```

**修改后**:
```python
def update_rating(image_id, rating):
    cursor.execute('''
        UPDATE generation_history 
        SET rating = ? 
        WHERE image_id = ?
    ''', (rating, image_id))
```

## 功能说明

### 评分权限
- ✅ **任何用户**都可以对**所有用户**的图片进行评分
- ✅ 不需要验证图片所有者
- ✅ 评分是全局的，所有用户看到的是同一个评分值

### 使用场景
1. **协作评审**: 多个用户可以共同对图片进行评价
2. **公共画廊**: 所有用户上传的图片都可以被其他人评分
3. **社区互动**: 增强用户之间的互动和反馈

## 测试验证

运行测试脚本验证跨用户评分功能：

```bash
python test_cross_user_rating.py
```

测试内容包括：
1. 获取其他用户的图片
2. 使用不同的用户UID进行评分
3. 验证评分已成功保存
4. 确认评分对所有用户可见

## 注意事项

⚠️ **重要提示**:
- 评分是全局共享的，一个用户的评分会影响所有用户看到的评分
- 如果需要对每个用户维护独立的评分，需要重新设计数据库结构
- 当前实现适合公共评审场景，不适合个人私有评分场景

## 数据影响

- 现有的评分数据不受影响
- 所有历史评分仍然有效
- 评分字段（rating）仍然是单值，不支持多用户独立评分

## 后续扩展建议

如果需要支持每用户独立评分，可以考虑：

1. **创建评分表**:
```sql
CREATE TABLE image_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id TEXT NOT NULL,
    user_uid TEXT NOT NULL,
    rating INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(image_id, user_uid)
);
```

2. **修改查询逻辑**: 计算平均评分或显示当前用户的评分

3. **更新API**: 返回当前用户的评分和平均评分

但当前实现已经满足"对所有用户图片评分"的需求。
