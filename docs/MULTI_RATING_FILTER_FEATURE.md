# 星级筛选多选功能说明

## 功能概述

星级筛选现在支持**多选**，可以同时选择多个评级进行筛选。例如，可以同时查看5星和4星的高质量图片，或者同时查看1星、2星和Bad的低质量图片。

## 使用方法

### 基本操作

1. **单选**: 点击任意星级按钮（如★★★★★），只显示该评级的图片
2. **多选**: 继续点击其他星级按钮（如★★★★），会同时显示5星和4星的图片
3. **取消选择**: 再次点击已选中的星级按钮，取消该评级的筛选
4. **清空所有**: 点击"全部"按钮，清除所有星级筛选

### UI反馈

- **选中的按钮**: 背景变为紫色 (#667eea)，文字变为白色
- **未选中的按钮**: 保持白色背景，灰色边框
- **"全部"按钮**: 只有在没有任何选择时才高亮显示

### 组合筛选

星级筛选可以与其他筛选条件组合使用：
- ✅ 星级 + 日期筛选
- ✅ 星级 + 用户视图（只看我的/所有用户）
- ✅ 多星级 + 日期 + 用户视图

## 技术实现

### 前端实现

#### 数据结构
```javascript
// 使用Set存储选中的评级，天然支持去重和快速查找
let currentRatingFilters = new Set();
```

#### 选择逻辑
```javascript
function selectRatingFilter(rating) {
    const ratingValue = rating === '' ? null : parseInt(rating);
    
    if (ratingValue === null) {
        // 点击"全部"，清空所有选择
        currentRatingFilters.clear();
    } else {
        // 切换该评级的选中状态
        if (currentRatingFilters.has(ratingValue)) {
            currentRatingFilters.delete(ratingValue);  // 取消选择
        } else {
            currentRatingFilters.add(ratingValue);     // 添加选择
        }
    }
    
    // 更新UI显示
    updateUI();
    
    // 重新加载历史记录
    loadHistory();
}
```

#### URL参数格式
```javascript
// 单个评级: rating=5
// 多个评级: rating=5,4,3
// 包含Bad: rating=5,-1
// 所有评级: rating=1,2,3,4,5,-1

if (currentRatingFilters.size > 0) {
    const ratings = Array.from(currentRatingFilters).join(',');
    params.push(`rating=${ratings}`);
}
```

### 后端实现

#### 参数解析 (app.py)
```python
# 获取评分筛选参数（支持多选，用逗号分隔）
rating_filter = request.args.get('rating', None)
if rating_filter is not None:
    if ',' in rating_filter:
        # 多个评级，转换为列表
        rating_list = [int(r.strip()) for r in rating_filter.split(',')]
        # 验证所有值都有效
        rating_filter = [r for r in rating_list if r in [-1, 1, 2, 3, 4, 5]]
    else:
        # 单个评级
        rating_filter = int(rating_filter)
```

#### 数据库查询 (database.py)
```python
# 支持多个评级筛选
if rating_filter is not None:
    if isinstance(rating_filter, list):
        if len(rating_filter) > 0:
            # 使用 SQL IN 子句
            placeholders = ','.join(['?' for _ in rating_filter])
            conditions.append(f'rating IN ({placeholders})')
            params.extend(rating_filter)
    else:
        # 单个评级
        conditions.append('rating = ?')
        params.append(rating_filter)
```

生成的SQL示例：
```sql
-- 单个评级
SELECT * FROM generation_history WHERE rating = 5

-- 多个评级
SELECT * FROM generation_history WHERE rating IN (5, 4, 3)

-- 包含Bad
SELECT * FROM generation_history WHERE rating IN (5, -1)
```

## 修改文件清单

### 前端文件
- **static/history.html**
  - 修改 `currentRatingFilter` → `currentRatingFilters` (Set类型)
  - 重写 `selectRatingFilter()` 函数支持多选
  - 更新 `updateDeleteBadButtonVisibility()` 逻辑
  - 修改 `loadHistory()` 生成逗号分隔的rating参数
  - 更新 `deleteBadImages()` 清除逻辑

### 后端文件
- **database.py**
  - 修改 `get_user_history()`: 支持rating_filter为列表
  - 修改 `get_all_history()`: 支持rating_filter为列表
  - 修改 `get_history_count()`: 支持rating_filter为列表
  - 使用 SQL IN 子句处理多值查询

- **app.py**
  - 修改 `/api/history` GET接口: 解析逗号分隔的rating参数
  - 验证所有评级值的有效性
  - 过滤无效值

### 测试文件
- **test_multi_rating.py**
  - 完整的多选功能测试脚本
  - 测试单选、多选、组合筛选等场景

## 测试验证

运行测试脚本：
```bash
python test_multi_rating.py
```

测试内容包括：
1. ✓ 标记不同评级的图片
2. ✓ 单个评级筛选
3. ✓ 多评级筛选 (5星+4星)
4. ✓ 多评级筛选 (3星+2星+1星)
5. ✓ 包含Bad的多选 (5星+Bad)
6. ✓ 所有有评级的图片
7. ✓ 无效参数处理

**测试结果**: ✅ 全部通过！

## 使用场景

### 1. 高质量图片筛选
选择 5星 + 4星，快速找到优质作品：
```
URL: /api/history?rating=5,4
```

### 2. 低质量图片清理
选择 1星 + 2星 + Bad，批量清理不满意的图片：
```
URL: /api/history?rating=1,2,-1
```

### 3. 中等质量审查
选择 3星，查看一般质量的图片：
```
URL: /api/history?rating=3
```

### 4. 优秀作品集
选择 5星 + 4星 + 3星，展示中上等作品：
```
URL: /api/history?rating=5,4,3
```

### 5. 对比分析
分别选择不同星级组合，分析生成质量分布：
```
高分组: rating=5,4
中分组: rating=3
低分组: rating=2,1,-1
```

## 注意事项

⚠️ **重要提示**:

1. **删除Bad图片的限制**: 
   - 只有当**仅选择Bad(-1)**且没有其他选择时，才显示删除按钮
   - 如果同时选择了Bad和其他星级，删除按钮隐藏
   - 这是为了防止误删其他评级的图片

2. **性能考虑**:
   - 多选会使用 SQL IN 子句，性能仍然很好
   - 建议不要同时选择过多评级（虽然技术上支持）

3. **URL长度**:
   - 浏览器对URL长度有限制（通常2000+字符）
   - 当前实现最多6个评级值，远未达到限制

4. **兼容性**:
   - 向后兼容单个评级筛选
   - 旧的URL格式 `rating=5` 仍然有效

## 与单选的对比

| 特性 | 单选（旧） | 多选（新） |
|------|----------|----------|
| 选择方式 | 只能选一个 | 可以选多个 |
| 切换逻辑 | 互斥 | 独立开关 |
| URL格式 | `rating=5` | `rating=5,4,3` |
| SQL查询 | `WHERE rating = 5` | `WHERE rating IN (5,4,3)` |
| 灵活性 | 低 | 高 |
| 实用性 | 一般 | 很高 |

## 未来扩展建议

1. **保存筛选预设**: 允许用户保存常用的筛选组合
2. **筛选历史**: 记录最近使用的筛选条件
3. **快捷组合**: 提供预设的组合按钮（如"高质量"、"待清理"）
4. **统计图表**: 显示各星级图片的数量分布
5. **批量操作**: 对筛选结果进行批量评分或删除

## 示例截图说明

### 界面布局
```
⭐ 星级筛选:
[全部] [★★★★★] [★★★★] [★★★] [★★] [★] [👎 Bad]
```

### 选中状态示例
```
选择5星和4星:
[全部] [★★★★★✓] [★★★★✓] [★★★] [★★] [★] [👎 Bad]
       ^紫色     ^紫色
```

### URL示例
```
http://localhost:5000/history.html?rating=5,4&date=2026-04-09
```
