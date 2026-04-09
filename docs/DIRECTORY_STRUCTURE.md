# 项目目录结构

## 概述
本项目采用清晰的目录结构，将不同类型的文件分类存放，便于管理和维护。

## 目录说明

### 根目录文件
```
drawThingsWebUI/
├── app.py                    # Flask 主应用入口
├── database.py               # 数据库操作模块
├── history_routes.py         # 历史记录路由模块
├── config.json               # DrawThings 服务配置（自动生成）
├── requirements.txt          # Python 依赖包列表
├── start.bat                 # Windows 启动脚本
├── README.md                 # 项目说明文档
└── .gitignore               # Git 忽略配置
```

### 数据目录

#### `generated_images/`
存储生成的图片文件
- 格式：PNG
- 命名：`generated_YYYYMMDD_HHMMSS.png`
- **注意**: 此目录已被 `.gitignore` 忽略

#### `static/`
静态资源文件
```
static/
├── index.html               # 主页 HTML
└── history.html             # 历史记录页面
```

### 代码目录

#### `tests/` - 测试文件
存放所有测试脚本
```
tests/
├── test_api.py                      # API 接口测试
├── test_database.py                 # 数据库功能测试
├── test_rating.py                   # 评分功能测试
├── test_cross_user_rating.py        # 跨用户评分测试
├── test_multi_rating.py             # 多评级筛选测试
├── test_delete_bad.py               # Bad 图片删除测试
├── test_server.py                   # 服务器测试
├── test_refactored_routes.py        # 重构路由测试
└── verify_refactoring.py            # 重构验证脚本
```

运行测试：
```bash
# 运行单个测试
python tests/test_database.py

# 运行所有测试
python -m pytest tests/
```

#### `scripts/` - 工具脚本
存放辅助工具和迁移脚本
```
scripts/
└── migrate_add_rating.py            # 数据库迁移脚本（添加评分字段）
```

#### `docs/` - 文档目录
存放项目文档和功能说明
```
docs/
├── MODULES.md                       # 模块化架构说明
├── REFACTORING_SUMMARY.md           # 代码重构总结
├── RATING_FEATURE.md                # 评分功能说明
├── MULTI_RATING_FILTER_FEATURE.md   # 多评级筛选功能
├── DELETE_BAD_IMAGES_FEATURE.md     # Bad 图片删除功能
└── CROSS_USER_RATING_UPDATE.md      # 跨用户评分更新说明
```

### 数据文件（自动生成）

以下文件在运行时自动生成，不应手动修改：

- `history.db` - SQLite 数据库文件（存储历史记录）
- `config.json` - DrawThings 服务配置
- `timing_stats.json` - 生成耗时统计数据
- `generation_history.json` - 旧版 JSON 历史文件（已弃用，仅用于迁移）

## 文件分类原则

### 核心代码（根目录）
- 应用入口文件
- 主要业务逻辑模块
- 配置文件模板
- 启动脚本

### 测试代码（tests/）
- 单元测试
- 集成测试
- 功能验证脚本

### 工具脚本（scripts/）
- 数据迁移脚本
- 批量处理工具
- 辅助脚本

### 文档（docs/）
- 功能说明文档
- 技术文档
- API 文档
- 重构记录

### 数据（自动管理）
- 数据库文件
- 生成的图片
- 运行时配置
- 统计数据

## 最佳实践

### 1. 添加新功能
```
1. 核心代码 → 根目录或创建新的模块文件
2. 测试代码 → tests/ 目录
3. 文档说明 → docs/ 目录
4. 工具脚本 → scripts/ 目录
```

### 2. 命名规范
- Python 文件：小写字母 + 下划线（snake_case）
- 测试文件：以 `test_` 开头
- 文档文件：大写字母 + 下划线（UPPER_CASE）
- 脚本文件：描述性名称

### 3. 版本控制
**应该提交到 Git:**
- ✅ 所有 Python 源代码
- ✅ 文档文件
- ✅ 配置文件模板
- ✅ 测试文件

**不应该提交到 Git:**
- ❌ generated_images/ 目录
- ❌ history.db 数据库文件
- ❌ config.json（包含本地配置）
- ❌ timing_stats.json（运行时数据）
- ❌ __pycache__/ 目录
- ❌ IDE 配置文件

## 清理建议

定期清理以下内容：

1. **测试数据**: 清理测试生成的临时文件和数据库记录
2. **旧图片**: 定期清理不需要的生成图片
3. **缓存文件**: 删除 `__pycache__` 目录
4. **日志文件**: 如有日志，定期归档或删除

## 扩展建议

随着项目增长，可以考虑进一步细分：

```
drawThingsWebUI/
├── src/                    # 源代码
│   ├── routes/            # 路由模块
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── tests/                  # 测试
│   ├── unit/              # 单元测试
│   └── integration/       # 集成测试
├── docs/                   # 文档
├── scripts/                # 脚本
├── migrations/             # 数据库迁移
└── config/                 # 配置文件
```

但目前的项目结构已经足够清晰，适合当前规模。
