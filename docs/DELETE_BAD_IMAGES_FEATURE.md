# 删除Bad图片功能说明

## 功能概述

替换了原有的"清空历史"功能，新增"删除所有Bad图片"功能。该功能可以：
- 删除数据库中所有标记为 Bad (rating=-1) 的图片记录
- 同时删除对应的原文件
- **必须在选择Bad筛选条件时才能使用**（安全保护机制）

## 使用方法

### 1. 标记图片为Bad
在历史记录页面，点击任意图片下方的"👎 Bad"按钮，将该图片标记为不喜欢。

### 2. 筛选Bad图片
- 点击"🔍 筛选条件"展开筛选面板
- 点击"👎 Bad"按钮，只显示标记为Bad的图片
- 此时页面顶部会显示"🗑️ 删除所有Bad图片"按钮

### 3. 删除Bad图片
- 确保当前处于Bad筛选状态
- 点击"🗑️ 删除所有Bad图片"按钮
- 确认删除操作（会有二次确认提示）
- 系统会同时删除数据库记录和原文件

## 安全机制

### 强制筛选条件
⚠️ **重要**: 只有在选择了Bad筛选条件（rating=-1）时，删除按钮才会显示和启用。

这是为了防止误操作，确保用户明确知道要删除的是哪些图片。

### 二次确认
点击删除按钮后，会弹出确认对话框：
```
确定要删除所有标记为 Bad 的图片吗？
此操作将同时删除数据库记录和原文件，且无法恢复！
```

### 删除范围
- **只看我的**模式：只删除当前用户的Bad图片
- **查看所有用户**模式：删除所有用户的Bad图片

## 技术实现

### 后端API

**接口**: `DELETE /api/history/bad`

**参数**:
- `rating`: 必须为 -1（Bad筛选条件）
- `all_users`: 可选，true表示删除所有用户的，false表示只删除当前用户的

**请求头**:
- `X-User-UID`: 用户唯一标识

**响应**:
```json
{
    "success": true,
    "message": "成功删除 6 张 Bad 图片",
    "deleted_count": 6,
    "files_deleted": 6,
    "files_failed": 0
}
```

**错误响应**:
```json
{
    "success": false,
    "error": "必须先选择 Bad 筛选条件才能删除"
}
```

### 数据库操作

1. **查询Bad图片**: `get_bad_images()`
   - 获取所有rating=-1的记录
   - 返回记录列表包含文件名信息

2. **删除记录**: `delete_bad_images()`
   - 先获取要删除的文件名列表
   - 删除数据库中的记录
   - 返回删除数量和文件名列表

### 文件删除

删除数据库记录后，遍历文件名列表，逐个删除原文件：
```python
file_path = os.path.join(IMAGES_DIR, filename)
if os.path.exists(file_path):
    os.remove(file_path)
```

如果文件不存在或删除失败，会记录警告但不影响其他文件的删除。

### 前端逻辑

1. **按钮显示控制**:
```javascript
function updateDeleteBadButtonVisibility() {
    const deleteBtn = document.getElementById('deleteBadBtn');
    if (currentRatingFilter === -1) {
        deleteBtn.style.display = 'inline-block';
    } else {
        deleteBtn.style.display = 'none';
    }
}
```

2. **删除操作**:
```javascript
async function deleteBadImages() {
    // 二次确认
    if (!confirm('确定要删除...')) return;
    
    // 构建URL，包含rating=-1参数
    let url = `${API_BASE}/api/history/bad?rating=-1`;
    if (showAllUsers) {
        url += '&all_users=true';
    }
    
    // 执行删除
    const response = await fetch(url, { method: 'DELETE', ... });
    
    // 清除筛选并刷新
    currentRatingFilter = null;
    loadHistory();
}
```

## 修改文件清单

### 前端文件
- **static/history.html**
  - 移除"清空历史"按钮
  - 新增"删除所有Bad图片"按钮（默认隐藏）
  - 添加 `updateDeleteBadButtonVisibility()` 函数
  - 添加 `deleteBadImages()` 函数
  - 移除 `clearHistory()` 函数

### 后端文件
- **database.py**
  - 新增 `get_bad_images()` 函数
  - 新增 `delete_bad_images()` 函数

- **app.py**
  - 导入 `delete_bad_images` 函数
  - 新增 `/api/history/bad` DELETE 接口
  - 实现筛选条件校验
  - 实现数据库记录和文件的双重删除

### 测试文件
- **test_delete_bad.py**
  - 完整的删除功能测试脚本
  - 测试标记、筛选、删除、验证全流程

## 测试验证

运行测试脚本验证功能：
```bash
python test_delete_bad.py
```

测试内容包括：
1. ✓ 标记图片为Bad
2. ✓ Bad筛选条件验证
3. ✓ 未选择Bad筛选时的删除保护
4. ✓ 执行删除操作
5. ✓ 验证数据库记录已删除
6. ✓ 验证原文件已删除

## 注意事项

⚠️ **重要提醒**:

1. **不可恢复**: 删除操作是永久性的，无法恢复
2. **双重删除**: 同时删除数据库记录和原文件
3. **筛选保护**: 必须先在Bad筛选状态下才能删除
4. **用户权限**: 
   - 跨用户评分：任何用户可以标记任何图片为Bad
   - 删除权限：根据当前视图模式决定删除范围

## 使用场景

1. **清理低质量图片**: 标记不满意的生成结果为Bad，然后批量删除
2. **节省存储空间**: 定期清理Bad图片释放磁盘空间
3. **优化历史记录**: 保持历史记录中只保留优质图片
4. **协作评审**: 团队成员共同标记并清理不合格的图片

## 与原有功能的对比

| 功能 | 清空历史（已删除） | 删除Bad图片（新增） |
|------|------------------|-------------------|
| 删除范围 | 所有历史记录 | 仅Bad评级的图片 |
| 文件删除 | ❌ 否 | ✅ 是 |
| 筛选要求 | 无 | 必须选择Bad筛选 |
| 安全性 | 低（容易误删） | 高（多重保护） |
| 实用性 | 一般 | 高（精准清理） |

## 未来扩展建议

1. **批量操作**: 支持选择性地删除部分Bad图片
2. **回收站**: 删除前先移到回收站，提供恢复机会
3. **定时清理**: 自动清理超过一定时间的Bad图片
4. **统计报告**: 显示Bad图片的统计信息和趋势
