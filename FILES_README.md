# 项目文件说明

## 📦 分发给用户的文件

以下文件/目录需要打包分发给最终用户：

### 必需文件：
- `dist/DrawThings WebUI.app/` - 主应用程序（已包含所有依赖）
- `Launch_DrawThings_WebUI.command` - 启动器（用户双击此文件）
- `README.md` - 用户使用说明
- `LICENSE` - 许可证

### 打包脚本：
运行 `./create_package.sh` 会自动生成 `DrawThings_WebUI_MacOS.zip` 分发包

---

## 🔧 开发者文件（不需要分发）

### 构建脚本：
- `build_standalone.py` - PyInstaller打包脚本
- `create_package.sh` - 创建分发包脚本
- `drawthings_standalone.spec` - PyInstaller配置文件
- `launcher.py` - 应用启动器源码

### 配置文件：
- `config.json` - 当前配置（运行时自动生成）
- `config.example.json` - 配置示例（已包含在应用中）
- `requirements.txt` - Python依赖列表

### 源代码：
- `src/` - Python源代码
- `static/` - 前端静态文件
- `scripts/` - 数据库迁移脚本
- `tests/` - 测试文件
- `docs/` - 文档

### 开发辅助（已移动到dev/目录）：
- `dev/` - 存放旧的启动脚本、测试文件等

### 其他：
- `data/` - 运行时数据（图片、日志、数据库）
- `build/` - 构建临时文件
- `.gitignore` - Git忽略配置
- `.lingma/` - Lingma配置

---

## 🚀 快速开始（开发者）

1. 安装依赖：
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. 重新打包应用：
   ```bash
   python build_standalone.py
   ```

3. 创建分发包：
   ```bash
   ./create_package.sh
   ```

4. 测试启动：
   ```bash
   ./Launch_DrawThings_WebUI.command
   ```
