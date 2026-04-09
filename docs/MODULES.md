# 模块化架构说明

## 项目结构

本项目采用模块化架构设计，将不同功能分离到独立的模块中，以提高代码的可维护性和可扩展性。

## 核心模块

### 1. `app.py` - 主应用模块
**职责**: 
- Flask应用初始化
- 核心图片生成功能
- 配置管理
- 状态查询
- 路由注册协调

**主要功能**:
- `/api/generate` - 图片生成
- `/api/status` - DrawThings服务状态检查
- `/api/config` - 配置管理
- `/api/status/generating` - 生成状态查询
- 静态文件服务

### 2. `history_routes.py` - 历史记录路由模块
**职责**:
- 所有历史记录相关的API端点
- 用户评分功能
- Bad图片管理

**主要功能**:
- `/api/history` (GET) - 获取历史记录
- `/api/history` (DELETE) - 清空历史
- `/api/rating` (POST) - 图片评分
- `/api/history/bad` (DELETE) - 删除Bad图片

**使用方式**:
```python
from history_routes import register_history_routes

# 在app.py中注册
register_history_routes(app)
```

### 3. `database.py` - 数据库操作模块
**职责**:
- SQLite数据库初始化
- 数据访问层（DAL）
- 数据迁移功能

**主要函数**:
- `init_database()` - 初始化数据库
- `add_history_record()` - 添加记录
- `get_user_history()` - 获取用户历史
- `get_all_history()` - 获取所有历史
- `update_rating()` - 更新评分
- `delete_bad_images()` - 删除Bad图片
- 等等...

## 模块依赖关系

```
app.py
  ├── history_routes.py
  │     └── database.py
  └── database.py
```

## 添加新功能

### 添加新的路由模块

1. 创建新的路由文件，例如 `config_routes.py`:
```python
from flask import request, jsonify

def register_config_routes(app):
    @app.route('/api/custom', methods=['GET'])
    def custom_handler():
        return jsonify({"message": "Custom endpoint"})
```

2. 在 `app.py` 中导入并注册:
```python
from config_routes import register_config_routes

# 在其他路由注册后添加
register_config_routes(app)
```

### 添加新的数据库操作

在 `database.py` 中添加新函数:
```python
def new_database_function(params):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # 执行数据库操作
        return result
```

## 测试

每个模块都应该有对应的测试文件：
- `test_refactored_routes.py` - 测试历史记录路由
- `test_database.py` - 测试数据库操作
- `test_api.py` - 测试API端点

运行测试：
```bash
python test_refactored_routes.py
```

## 最佳实践

1. **单一职责**: 每个模块只负责一个功能领域
2. **清晰命名**: 模块名和函数名要清晰表达其用途
3. **文档完善**: 为每个模块编写清晰的文档字符串
4. **错误处理**: 适当的异常处理和日志记录
5. **向后兼容**: 修改时保持API兼容性

## 未来扩展

可以考虑进一步拆分的模块：
- `generation_routes.py` - 图片生成相关路由
- `status_routes.py` - 状态查询相关路由
- `utils.py` - 通用工具函数
- `validators.py` - 数据验证函数
- `middleware.py` - 中间件函数

## 注意事项

1. 修改任何模块后都要运行测试确保功能正常
2. 保持模块间的低耦合
3. 避免循环导入
4. 及时更新文档
