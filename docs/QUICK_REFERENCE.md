# 快速参考指南

## 常用命令

### 启动服务
```bash
# Windows（推荐）
start.bat

# 或手动启动
python src/app.py
```

### 运行测试
```bash
# 运行所有验证
python tests/verify_refactoring.py

# 运行特定测试
python tests/test_database.py
python tests/test_refactored_routes.py
```

### 清理项目
```bash
# 清理缓存和临时文件
python scripts/cleanup.py
```

### 安装依赖
```bash
pip install -r requirements.txt
```

## 目录速查

| 目录 | 用途 | 示例 |
|------|------|------|
| `tests/` | 测试文件 | `python tests/test_api.py` |
| `docs/` | 文档说明 | 查看功能文档 |
| `scripts/` | 工具脚本 | `python scripts/cleanup.py` |
| `static/` | 静态资源 | HTML、CSS、JS |
| `generated_images/` | 生成的图片 | 自动保存 |

## 核心文件

| 文件 | 说明 |
|------|------|
| `app.py` | Flask 主应用 |
| `database.py` | 数据库操作 |
| `history_routes.py` | 历史记录路由 |
| `config.json` | DrawThings 配置 |

## API 端点

### 图片生成
- `POST /api/generate` - 生成图片
- `GET /api/status` - 检查服务状态

### 历史记录
- `GET /api/history` - 获取历史记录
- `DELETE /api/history` - 清空历史
- `POST /api/rating` - 评分
- `DELETE /api/history/bad` - 删除 Bad 图片

### 配置
- `GET /api/config` - 获取配置
- `POST /api/config` - 更新配置

### 状态
- `GET /api/status/generating` - 生成状态

## 常见问题

### Q: 如何修改 DrawThings 服务地址？
A: 访问 `http://localhost:5000`，在页面中配置，或直接编辑 `config.json`

### Q: 历史记录保存在哪里？
A: SQLite 数据库文件 `history.db`

### Q: 如何备份数据？
A: 复制以下文件：
- `history.db` - 数据库
- `generated_images/` - 图片
- `config.json` - 配置

### Q: 如何清理旧图片？
A: 运行清理脚本：
```bash
python scripts/cleanup.py
```

### Q: 测试文件放在哪里？
A: 所有测试文件放在 `tests/` 目录

### Q: 如何添加新功能？
A: 
1. 核心代码 → 根目录或新建模块
2. 测试代码 → `tests/` 目录
3. 文档 → `docs/` 目录
4. 脚本 → `scripts/` 目录

## 开发流程

### 添加新路由
1. 在 `history_routes.py` 或其他路由文件中添加
2. 在 `tests/` 添加对应测试
3. 在 `docs/` 添加文档说明

### 添加数据库功能
1. 在 `database.py` 中添加函数
2. 编写单元测试
3. 更新相关文档

### 修改配置
1. 通过 Web 界面修改（推荐）
2. 或直接编辑 `config.json`
3. 重启服务生效

## 性能优化建议

1. **定期清理**：运行 `scripts/cleanup.py` 清理缓存
2. **图片管理**：定期清理不需要的生成图片
3. **数据库维护**：SQLite 会自动维护，无需额外操作
4. **日志查看**：Flask 会在控制台输出日志

## 调试技巧

### 查看路由列表
```python
python -c "from app import app; [print(f'{rule.rule} [{list(rule.methods)}]') for rule in app.url_map.iter_rules() if rule.endpoint != 'static']"
```

### 检查数据库
```python
python -c "from database import get_history_count; print(f'Records: {get_history_count()}')"
```

### 测试导入
```python
python -c "from app import app; print('OK')"
```

## 版本控制

### 应该提交的文件
- ✅ Python 源代码（`.py`）
- ✅ 文档（`.md`）
- ✅ 配置文件模板
- ✅ 测试文件
- ✅ `requirements.txt`

### 不应提交的文件
- ❌ `generated_images/`
- ❌ `history.db`
- ❌ `config.json`
- ❌ `timing_stats.json`
- ❌ `__pycache__/`
- ❌ IDE 配置

## 扩展阅读

- [目录结构详解](docs/DIRECTORY_STRUCTURE.md)
- [模块化架构](docs/MODULES.md)
- [重构总结](docs/REFACTORING_SUMMARY.md)
- [功能文档](docs/) - 查看所有功能说明

## 获取帮助

1. 查看 `docs/` 目录中的相关文档
2. 查看测试文件了解用法
3. 查看源代码注释
4. 运行 `verify_refactoring.py` 检查系统状态
