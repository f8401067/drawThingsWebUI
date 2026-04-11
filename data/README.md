# Data Directory

此目录包含应用程序运行时生成的数据文件。

## 目录结构

```
data/
├── history.db              # SQLite数据库，存储图片生成历史记录
├── timing_stats.json       # 图片生成耗时统计数据
├── generated_images/       # 生成的图片文件
│   ├── generated_*.png     # 按时间戳命名的图片文件
│   └── ...
└── logs/                   # 日志文件
    ├── image_generation.log  # 图片生成日志
    └── llm_calls.log         # LLM调用日志
```

## 文件说明

### history.db
- **类型**: SQLite数据库
- **用途**: 存储所有图片生成的历史记录，包括提示词、参数、评分等信息
- **注意**: 不要手动修改此文件

### timing_stats.json
- **类型**: JSON文件
- **用途**: 记录最近100次图片生成的耗时数据，用于预估生成时间
- **格式**: 包含`times`数组和`average_time`平均值

### generated_images/
- **类型**: 图片目录
- **用途**: 存储所有通过应用生成的图片
- **命名规则**: `generated_YYYYMMDD_HHMMSS.png`
- **注意**: 删除Bad图片时会同时删除此目录中的对应文件

### logs/
- **类型**: 日志目录
- **用途**: 存储应用运行日志
- **image_generation.log**: 记录图片生成的详细信息（开始、成功、失败、清理等）
- **llm_calls.log**: 记录LLM调用的详细信息（提示词润色、NSFW检测等）

## 备份建议

建议定期备份以下文件：
- `history.db` - 重要的历史记录数据
- `generated_images/` - 用户生成的图片
- `timing_stats.json` - 可选，可以重新生成

## 清理建议

可以安全清理的文件：
- `logs/` 目录下的日志文件（应用会自动创建新的）
- `timing_stats.json`（应用会重新生成）
