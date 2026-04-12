# DrawThings WebUI - 开发者指南

本文档面向开发者，包含开发环境设置、代码结构、打包部署等技术信息。

---

## 🚀 快速开始

### 开发环境要求

- Python 3.8+
- macOS / Linux / Windows
- DrawThings 服务（运行在 `http://127.0.0.1:7888`）

### 首次设置

```bash
# 1. 克隆项目
cd drawThingsWebUI

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 启动开发服务器

```bash
# 方式1：使用开发者启动脚本（推荐）
./dev_start.sh

# 方式2：手动启动
source venv/bin/activate
python launcher.py
```

访问 `http://localhost:9898` 查看应用。

---

## 📁 项目结构

```
drawThingsWebUI/
├── src/                    # Python 源代码
│   ├── app.py             # Flask 主应用
│   ├── launcher.py        # 应用启动器
│   ├── config_manager.py  # 配置管理
│   ├── database.py        # 数据库操作
│   ├── history_routes.py  # 历史记录路由
│   ├── ai_refine.py       # AI提示词润色
│   └── llm_client.py      # LLM客户端
│
├── static/                # 前端静态文件
│   ├── index.html         # 主页
│   ├── history.html       # 历史记录页
│   ├── sw.js              # Service Worker
│   └── favicon.svg        # 网站图标
│
├── dist/                  # 打包输出
│   └── DrawThings WebUI.app/  # macOS应用包
│
├── build/                 # 构建资源
│   ├── Info.plist         # macOS应用配置
│   ├── app_icon.icns      # 应用图标
│   └── launch_wrapper.sh  # 启动包装器
│
├── data/                  # 运行时数据
│   ├── generated_images/  # 生成的图片
│   ├── thumbnails/        # 缩略图
│   ├── logs/              # 日志文件
│   └── history.db         # SQLite数据库
│
├── scripts/               # 工具脚本
│   ├── migrate_add_*.py   # 数据库迁移脚本
│   └── cleanup.py         # 清理脚本
│
├── tests/                 # 测试文件
│   └── test_*.py          # 单元测试
│
├── docs/                  # 功能文档
│   └── *.md               # 各功能详细说明
│
├── dev_start.sh           # 开发者启动脚本
├── build_standalone.py    # PyInstaller打包脚本
├── create_package.sh      # 分发包创建脚本
├── config.json            # 配置文件
└── requirements.txt       # Python依赖
```

---

## ⚙️ 配置说明

### 配置文件：config.json

```json
{
  "port": 9898,
  "host": "0.0.0.0",
  "debug": false,
  "auto_open_browser": true,
  "drawthings_url": "http://127.0.0.1:7888",
  "llm_api_url": "",
  "llm_model": "",
  "llm_api_key": ""
}
```

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `port` | 服务器端口 | 9898 |
| `host` | 监听地址（0.0.0.0=允许外部访问） | 0.0.0.0 |
| `debug` | 调试模式 | false |
| `auto_open_browser` | 自动打开浏览器 | true |
| `drawthings_url` | DrawThings服务地址 | http://127.0.0.1:7888 |
| `llm_api_url` | LLM API地址 | - |
| `llm_model` | LLM模型名称 | - |
| `llm_api_key` | LLM API密钥 | - |

---

## 📦 打包与分发

### 打包应用（macOS）

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 运行打包脚本
python build_standalone.py
```

打包完成后，应用位于 `dist/DrawThings WebUI.app`

### 创建分发包

```bash
# 创建zip分发包
./create_package.sh
```

生成 `DrawThings_WebUI_MacOS.zip`，包含：
- DrawThings WebUI.app（主应用）
- Launch_DrawThings_WebUI.command（启动器）
- README.md（使用说明）

### 分发给用户

将 `DrawThings_WebUI_MacOS.zip` 发送给用户，用户只需：
1. 解压zip文件
2. 双击 `Launch_DrawThings_WebUI.command`
3. 完成！

**优势：**
- ✅ 无需安装Python
- ✅ 所有依赖已打包
- ✅ 一键启动
- ✅ 显示控制台日志

---

## 🔧 核心模块说明

### src/app.py - Flask主应用

- 定义所有API路由
- 初始化Flask应用
- 配置CORS
- 注册蓝图

### src/launcher.py - 应用启动器

- 统一启动入口
- 加载配置
- 创建数据目录
- 自动打开浏览器

### src/config_manager.py - 配置管理

- 读取config.json
- 提供默认配置
- 验证配置有效性

### src/database.py - 数据库操作

- SQLite数据库初始化
- 历史记录CRUD
- 评分和NSFW标记
- 数据库迁移

### src/history_routes.py - 历史记录路由

- 历史查询API
- 筛选功能
- 批量删除
- 分页支持

### src/ai_refine.py - AI提示词润色

- 调用LLM优化提示词
- 支持多种模型

### src/llm_client.py - LLM客户端

- 统一的LLM调用接口
- NSFW检测
- 超时和错误处理

---

## 🧪 测试

### 运行测试

```bash
# 测试NSFW检测
python tests/test_auto_nsfw.py

# 测试评分功能
python tests/test_rating.py

# 测试多选筛选
python tests/test_multi_rating.py

# 测试删除Bad图片
python tests/test_delete_bad.py

# 测试跨用户评分
python tests/test_cross_user_rating.py

# 测试并发限制
python tests/test_concurrent_limit.py
```

---

## 📝 开发规范

### 代码风格

- 遵循PEP 8规范
- 使用4空格缩进
- 函数和类添加文档字符串
- 变量命名使用snake_case

### 提交规范

```bash
# 功能新增
git commit -m "feat: 添加XXX功能"

# Bug修复
git commit -m "fix: 修复XXX问题"

# 文档更新
git commit -m "docs: 更新XXX文档"

# 重构
git commit -m "refactor: 重构XXX模块"
```

---

## 🐛 常见问题

### 端口被占用

```bash
# 检查端口占用
lsof -i :9898

# 停止占用进程
lsof -ti:9898 | xargs kill -9
```

### 数据库迁移

从旧版本升级时运行迁移脚本：

```bash
# 添加评分字段
python scripts/migrate_add_rating.py

# 添加NSFW字段
python scripts/migrate_add_nsfw.py
```

### 打包失败

确保安装了PyInstaller：

```bash
pip install pyinstaller
```

### Dock图标不显示

确保Info.plist中：
- `LSUIElement` = false
- `LSBackgroundOnly` = false
- `console=True`（在build_standalone.py中）

---

## 📚 相关文档

- [用户使用说明](README.md) - 功能介绍和使用方法
- [目录结构说明](docs/DIRECTORY_STRUCTURE.md)
- [模块化架构](docs/MODULES.md)
- [NSFW检测功能](docs/AUTO_NSFW_DETECTION.md)
- [评分功能](docs/RATING_FEATURE.md)
- [图片缓存功能](docs/IMAGE_CACHE_FEATURE.md)
- [日志记录功能](docs/LOGGING_FEATURE.md)

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
