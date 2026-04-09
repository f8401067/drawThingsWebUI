# DrawThings WebUI

一个基于 Python Flask 和静态 HTML 的 DrawThings Web 界面。

## 功能特性

- 服务器状态检查：自动检测 DrawThings 服务状态并显示当前提示词和模型
- 图片生成：支持自定义提示词、尺寸、seed、步数等参数
- 本地存储：自动保存用户输入，下次打开页面时自动填充
- 图片查看：支持放大、缩小、重置和保存生成的图片
- 耗时统计：记录每次生成的耗时并计算平均耗时

## 前置要求

1. Python 3.8 或更高版本
2. DrawThings 服务运行在 `127.0.0.1:8777`

## 安装步骤

1. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 确保 DrawThings 服务正在运行于 `127.0.0.1:8777`

## 运行服务

### Windows 用户（推荐）

双击运行 `start.bat` 脚本，它会自动检查依赖并启动服务。

### 手动启动

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## 使用说明

1. 打开浏览器访问 `http://localhost:5000`
2. 页面会自动检查 DrawThings 服务器状态
3. 如果连接成功，填写生成参数：
   - **提示词**：描述你想要生成的图片内容
   - **图片尺寸**：从预设的尺寸中选择
   - **Seed**：随机种子（-1 表示随机）
   - **负面提示词**：不希望在图片中出现的内容（默认折叠）
   - **步数**：生成步数，越多质量越好但速度越慢
4. 点击"生成图片"按钮
5. 等待生成完成（可能需要几分钟）
6. 查看生成结果，可以放大、缩小、保存图片
7. 点击"返回重新生成"可以再次生成

## 项目结构

```
drawThingsWebUI/
├── app.py                  # Flask 主应用入口
├── database.py             # 数据库操作模块
├── history_routes.py       # 历史记录路由模块
├── requirements.txt        # Python 依赖
├── start.bat              # Windows 启动脚本
├── README.md              # 项目说明文档
├── .gitignore             # Git 忽略配置
│
├── static/                # 静态资源
│   ├── index.html         # 主页
│   └── history.html       # 历史记录页面
│
├── generated_images/      # 生成的图片（自动创建，已忽略）
├── tests/                 # 测试文件
│   ├── test_*.py          # 各种功能测试
│   └── verify_refactoring.py  # 重构验证
│
├── docs/                  # 文档目录
│   ├── DIRECTORY_STRUCTURE.md  # 目录结构说明
│   ├── MODULES.md              # 模块化架构
│   └── *.md                    # 功能说明文档
│
├── scripts/               # 工具脚本
│   ├── migrate_add_rating.py   # 数据迁移脚本
│   └── cleanup.py              # 清理脚本
│
└── 数据文件（自动生成）
    ├── history.db              # SQLite 数据库
    ├── config.json             # DrawThings 配置
    ├── timing_stats.json       # 耗时统计
    └── generation_history.json # 旧版 JSON（仅迁移用）
```

详细的目录结构说明请查看 [docs/DIRECTORY_STRUCTURE.md](docs/DIRECTORY_STRUCTURE.md)

## API 接口

### GET /api/status
检查 DrawThings 服务器状态

**响应示例：**
```json
{
  "success": true,
  "prompt": "当前提示词",
  "model": "当前模型",
  "raw_data": {...}
}
```

### POST /api/generate
生成图片

**请求体：**
```json
{
  "prompt": "提示词",
  "negative_prompt": "负面提示词",
  "width": 768,
  "height": 768,
  "seed": -1,
  "steps": 20
}
```

**响应示例：**
```json
{
  "success": true,
  "image_url": "/generated_images/generated_20260409_120000.png",
  "image_filename": "generated_20260409_120000.png",
  "elapsed_time": 120.5,
  "average_time": 115.3,
  "seed": 1234567890
}
```

## 注意事项

- 首次运行前请确保 DrawThings 服务已启动
- 图片生成可能需要较长时间（约 5 分钟）
- 生成的图片会保存在 `generated_images` 目录
- 用户的输入会自动保存到浏览器本地存储
