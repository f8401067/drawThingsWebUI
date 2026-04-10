# NSFW标记功能说明

## 功能概述

为历史记录页面添加了NSFW（Not Safe For Work）内容标记系统，包括：

1. **NSFW标记**：每张图片可以标记/取消标记为NSFW内容
2. **NSFW筛选**：可以切换显示或隐藏NSFW内容
3. **默认隐藏**：默认情况下不显示带有NSFW标记的图片
4. **视觉标识**：NSFW图片右上角显示红色"🔞 NSFW"徽章

## 使用方法

### 标记NSFW内容

1. 打开历史记录页面（`/history.html`）
2. 在任意图片下方可以看到"标记NSFW"按钮
3. 点击按钮即可将该图片标记为NSFW
4. 再次点击可取消NSFW标记

### 筛选NSFW内容

1. 展开筛选条件面板（点击"🔍 筛选条件"标题）
2. 找到"🔞 NSFW内容"筛选区域
3. 点击"隐藏NSFW"按钮：隐藏所有NSFW图片（默认状态）
4. 点击"显示NSFW"按钮：显示所有图片，包括NSFW内容

### 视觉标识

- 被标记为NSFW的图片右上角会显示红色"🔞 NSFW"徽章
- 该徽章始终可见，即使在不显示NSFW内容的模式下也能看到（如果当前正在查看该图片）

## 技术实现

### 后端改动

1. **数据库结构** (`database.py`)
   - 在 `generation_history` 表中添加 `is_nsfw` 字段（INTEGER，默认0）
   - 添加 `idx_history_nsfw` 索引优化查询性能
   - 新增 `toggle_nsfw()` 函数切换NSFW状态
   - 修改 `get_user_history()`、`get_all_history()`、`get_history_count()` 支持NSFW筛选
   - 默认情况下只返回 `is_nsfw = 0` 的记录

2. **API接口** (`history_routes.py`)
   - 新增 `/api/nsfw` POST 接口处理NSFW标记切换
   - 修改 `/api/history` GET 接口支持 `show_nsfw` 参数

### 前端改动

1. **样式** (`static/history.html`)
   - 添加NSFW徽章样式（`.nsfw-badge`）
   - 添加NSFW切换按钮样式（`.nsfw-toggle-btn`）
   - 添加NSFW筛选按钮样式

2. **功能**
   - `toggleNsfwDisplay()`: 切换NSFW显示/隐藏
   - `toggleNsfw()`: 切换单张图片的NSFW标记
   - 修改 `renderHistory()` 显示NSFW徽章和切换按钮
   - 修改 `loadHistory()` 支持NSFW筛选参数
   - 初始化时默认设置"隐藏NSFW"为激活状态

### 数据迁移

如果数据库中已有历史记录但没有 `is_nsfw` 字段，需要运行迁移脚本：

```bash
python scripts/migrate_add_nsfw.py
```

该脚本会：
1. 检查 `is_nsfw` 字段是否存在
2. 如果不存在则添加该字段（默认值为0）
3. 创建NSFW索引

## NSFW值说明

- `0`: 非NSFW内容（默认值）
- `1`: NSFW内容

## 默认行为

- **星级筛选**：默认不选择任何评级（显示全部）
- **NSFW筛选**：默认隐藏NSFW内容
- 这样设计是为了提供更好的用户体验，避免意外看到不适宜的内容

## 测试

运行测试脚本验证NSFW功能：

```bash
python tests/test_nsfw.py
```

测试内容包括：
1. 创建用户
2. 获取历史记录
3. 标记图片为NSFW
4. 验证默认隐藏NSFW
5. 验证显示NSFW
6. 取消NSFW标记

## 注意事项

⚠️ **重要提示**:
- NSFW标记是全局共享的，一个用户的标记会影响所有用户
- 如果需要每用户独立的NSFW标记，需要重新设计数据库结构
- 当前实现适合公共评审场景

## 后续扩展建议

如果需要支持每用户独立的NSFW标记，可以考虑：

1. **创建NSFW标记表**:
```sql
CREATE TABLE image_nsfw_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    is_nsfw INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(image_id, user_id)
);
```

2. **修改查询逻辑**: 根据当前用户ID查询其个人NSFW标记

3. **更新API**: 返回当前用户的NSFW标记状态

但当前实现已经满足"对所有用户图片标记NSFW"的需求。
