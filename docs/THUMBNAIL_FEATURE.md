# 缩略图功能说明

## 功能概述

为了提升外网访问历史页面时的图片加载速度，系统新增了缩略图功能。历史记录页面现在会加载较小的缩略图（约 300x300 像素），点击后才会加载完整尺寸的原图。

## 技术实现

### 后端改进

1. **缩略图生成**
   - 使用 Python Pillow 库生成缩略图
   - 缩略图格式为 JPEG，质量 85%，优化压缩
   - 保持原图宽高比，最大尺寸 300x300 像素
   - 缩略图保存在 `data/thumbnails/` 目录

2. **数据库扩展**
   - 在 `generation_history` 表中添加了两个字段：
     - `thumbnail_url`: 缩略图 URL
     - `thumbnail_filename`: 缩略图文件名

3. **API 路由**
   - 新增 `/thumbnails/<filename>` 路由提供缩略图服务
   - 修改 `/api/generate` 接口，在生成图片时同时生成缩略图

### 前端改进

- 历史记录页面优先加载缩略图
- 点击缩略图后在新标签页打开原图
- 对于没有缩略图的旧记录，自动回退到加载原图

## 安装依赖

首先需要安装 Pillow 库：

```bash
pip install -r requirements.txt
```

或者单独安装：

```bash
pip install Pillow
```

## 迁移已有数据

如果你已经有生成的图片但没有缩略图，可以运行迁移脚本：

```bash
python scripts/migrate_add_thumbnails.py
```

该脚本会：
- 遍历所有历史记录
- 为每张图片生成缩略图
- 更新数据库记录

## 配置说明

缩略图生成参数可以在 `config.json` 中配置：

```json
{
  "thumbnail": {
    "max_size": [300, 300],
    "quality": 85,
    "format": "JPEG"
  }
}
```

### 配置项说明

- **max_size**: 缩略图最大尺寸 [宽度, 高度]，默认 [300, 300]
  - 建议范围: [150, 150] ~ [600, 600]
  - 越大越清晰，但文件也越大
  
- **quality**: JPEG/WEBP 压缩质量 (1-100)，默认 85
  - 较低值 (60-75): 文件更小，质量稍差
  - 中等值 (80-90): 平衡选择（推荐）
  - 较高值 (90-100): 质量更好，文件更大
  
- **format**: 输出格式，支持 "JPEG", "PNG", "WEBP"
  - **JPEG** (推荐): 体积小，适合照片类图片
  - **PNG**: 无损压缩，体积较大，适合线条图
  - **WEBP**: 现代格式，体积最小，兼容性稍差

### 配置示例

#### 更高质量（适合内网或高速网络）
```json
{
  "thumbnail": {
    "max_size": [400, 400],
    "quality": 90,
    "format": "JPEG"
  }
}
```

#### 更小体积（适合外网或慢速网络）
```json
{
  "thumbnail": {
    "max_size": [200, 200],
    "quality": 75,
    "format": "JPEG"
  }
}
```

#### 使用 WEBP 格式（最佳压缩率）
```json
{
  "thumbnail": {
    "max_size": [300, 300],
    "quality": 80,
    "format": "WEBP"
  }
}
```

**注意**: 修改配置后，新生成的图片会使用新配置。要为已有图片重新生成缩略图，需要删除旧的缩略图并重新运行迁移脚本。

## 性能提升

### 文件大小对比

- **原图**: 通常 1-5 MB（取决于尺寸和质量）
- **缩略图**: 通常 10-50 KB（300x300, JPEG 85% 质量）

### 加载速度提升

在外网环境下（假设带宽 1 Mbps）：
- **原图加载**: 8-40 秒
- **缩略图加载**: 0.1-0.4 秒
- **提升倍数**: 约 80-100 倍

### 流量节省

- 浏览 50 张历史记录：
  - 使用原图: 50-250 MB
  - 使用缩略图: 0.5-2.5 MB
  - 节省流量: 约 98%

## 注意事项

1. **存储空间**: 缩略图会增加一定的存储开销，但相比原图很小（约 1-2%）
2. **首次生成**: 新图片会自动生成缩略图，无需额外操作
3. **旧图片**: 需要运行迁移脚本为旧图片生成缩略图
4. **依赖安装**: 确保已安装 Pillow 库

## 故障排除

### 缩略图未生成

检查以下几点：
1. 确认已安装 Pillow 库：`pip list | findstr Pillow`
2. 检查 `data/thumbnails/` 目录是否存在且有写入权限
3. 查看日志文件 `data/logs/image_generation.log`

### 迁移脚本失败

1. 确认数据库文件路径正确
2. 确认图片目录 `data/generated_images/` 存在
3. 检查是否有足够的磁盘空间

### 常见错误

**ModuleNotFoundError: No module named 'PIL'**
```bash
pip install Pillow
```

**PermissionError: [Errno 13] Permission denied**
- 检查 `data/thumbnails/` 目录的写入权限
- Windows: 右键文件夹 → 属性 → 安全 → 编辑权限

## 配置选项

如需调整缩略图大小或质量，修改 `src/app.py` 中的 `generate_thumbnail` 函数：

```python
# 调整尺寸（默认 300x300）
thumbnail_generated = generate_thumbnail(image_path, thumbnail_path, size=(400, 400))

# 调整质量（默认 85，范围 1-100）
img.save(thumbnail_path, 'JPEG', quality=90, optimize=True)
```

较大的尺寸和更高的质量会带来更好的视觉效果，但会增加文件大小和加载时间。

推荐配置：
- **内网使用**: 400x400, quality=90
- **外网使用**: 300x300, quality=85（当前默认）
- **移动网络**: 200x200, quality=75
