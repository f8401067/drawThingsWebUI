# 历史记录加载动画功能

## 功能概述

在历史记录页面中，对于尚未生成完成的图片项显示一个加载动画，而不是空白或无图状态。

## 实现原理

### 1. 判断生成状态

通过检查 `elapsed_time` 字段来判断图片是否还在生成中：
- `elapsed_time === 0` 或 `!elapsed_time`：表示图片正在生成中
- `elapsed_time > 0`：表示图片已生成完成

### 2. 前端渲染逻辑

在 `renderHistory()` 函数中：
```javascript
// Check if the image is still generating (elapsed_time is 0 or very small)
const isGenerating = !item.elapsed_time || item.elapsed_time === 0;

let imageContent;
if (isGenerating) {
    // Show loading animation for incomplete images
    imageContent = `
        <div class="history-item-loading">
            <div class="loading-spinner"></div>
            <div class="loading-text">生成中...</div>
        </div>
    `;
} else {
    // Show actual image for completed generations
    imageContent = `<img src="${item.image_url}" alt="Generated Image" loading="lazy" onclick="openImage('${item.image_url}')">`;
}
```

### 3. 加载动画样式

CSS 动画包括：
- **Shimmer 效果**：背景渐变从左到右流动
- **旋转 Spinner**：经典的圆形加载指示器
- **"生成中..." 文本**：清晰的状态提示

```css
.history-item-loading {
    width: 100%;
    aspect-ratio: 1;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading-shimmer 1.5s infinite;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(102, 126, 234, 0.3);
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
```

### 4. 自动刷新机制

当检测到有正在生成的项目时，启动自动刷新：
- **刷新间隔**：每 3 秒刷新一次历史记录
- **智能停止**：当所有项目都生成完成后，自动停止刷新
- **资源清理**：页面卸载时清除定时器，避免内存泄漏

```javascript
function setupAutoRefresh() {
    clearAutoRefresh();
    autoRefreshTimer = setInterval(() => {
        loadHistory();
    }, 3000);
}

function clearAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
        autoRefreshTimer = null;
    }
}
```

## 用户体验改进

### 之前的问题
- 用户发起图片生成后，立即在历史记录中看到空白项
- 无法区分是加载中还是图片缺失
- 需要手动刷新页面才能看到生成进度

### 现在的体验
- ✅ 清晰的加载动画，明确表示"正在生成中"
- ✅ 自动刷新，无需手动操作
- ✅ 生成完成后自动显示实际图片
- ✅ 流畅的视觉反馈，提升用户体验

## 技术细节

### 数据库层面
- 图片生成开始时创建初始记录，`elapsed_time = 0`
- 图片生成完成后更新记录，设置实际的 `elapsed_time`
- 通过 `update_history_record()` 更新耗时和 seed 信息

### 前端层面
- 检测 `elapsed_time` 判断状态
- 条件渲染：加载动画 vs 实际图片
- 定时轮询：3秒间隔自动刷新
- 事件清理：页面卸载时清除定时器

## 相关文件

- `static/history.html` - 历史记录页面（主要修改）
- `src/app.py` - 后端API（创建和更新历史记录）
- `src/database.py` - 数据库操作

## 测试方法

1. 启动服务器：`python -m src.app`
2. 访问历史记录页面：`http://127.0.0.1:5000/history.html`
3. 在主页面发起一个新的图片生成任务
4. 立即切换到历史记录页面
5. 应该看到新创建的记录显示加载动画
6. 等待几秒后，加载动画会自动替换为实际图片

## 注意事项

- 自动刷新会增加服务器负载，但3秒间隔是合理的平衡点
- 如果同时有多个用户生成图片，每个用户的历史记录页面都会独立刷新
- 加载动画只在 `elapsed_time = 0` 时显示，确保准确性
