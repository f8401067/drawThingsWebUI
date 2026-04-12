# 图片缓存功能 - 快速参考

## 🚀 快速开始

### 1. 启动服务器
```bash
python -m src.app
```

### 2. 打开浏览器
访问: http://127.0.0.1:5000

### 3. 验证 Service Worker
按 F12 打开开发者工具，在 Console 中应该看到：
```
[SW] Registered successfully: http://127.0.0.1:5000/
```

### 4. 默认显示所有图片
- 历史页面**默认不设置日期筛选**，显示所有日期的图片
- 这样可以充分利用浏览器缓存，提升浏览体验
- 如需按日期筛选，可手动选择具体日期

## 📊 使用缓存管理

### 查看缓存状态
1. 访问历史页面: http://127.0.0.1:5000/history.html
2. 展开"筛选条件"面板
3. 点击 **"查看缓存"** 按钮
4. 显示已缓存的图片数量和列表

### 清除缓存
1. 在历史页面的筛选条件面板
2. 点击 **"清除缓存"** 按钮
3. 确认后自动刷新页面

## 🔍 调试技巧

### 控制台命令

```javascript
// 查看缓存统计
caches.open('drawthings-images-v1').then(async cache => {
  const keys = await cache.keys();
  console.log('缓存数量:', keys.length);
});

// 清除所有缓存
caches.delete('drawthings-images-v1');

// 查看 Service Worker 状态
navigator.serviceWorker.getRegistration().then(reg => {
  console.log('SW 状态:', reg ? '已注册' : '未注册');
});
```

### Chrome 专用
- 查看 SW 详情: `chrome://serviceworker-internals/`
- 查看缓存: DevTools → Application → Cache Storage

### Firefox 专用
- 查看 SW 详情: `about:debugging#/runtime/this-firefox`
- 查看缓存: DevTools → Storage → Cache

## ⚙️ 配置选项

### 修改缓存大小限制

编辑 `static/sw.js`:
```javascript
const IMAGE_CACHE_MAX_SIZE = 50; // 改为想要的数量
```

### 修改缓存过期时间

编辑 `static/sw.js`:
```javascript
const CACHE_EXPIRY_TIME = 7 * 24 * 60 * 60 * 1000; // 改为想要的毫秒数
```

### 修改缓存名称（强制刷新所有缓存）

编辑 `static/sw.js`:
```javascript
const CACHE_NAME = 'drawthings-images-v2'; // 递增版本号
```

## 🐛 常见问题

### Q: Service Worker 没有注册？
**A:** 
- 确保使用 localhost 或 HTTPS
- 检查浏览器是否支持 Service Worker
- 清除浏览器数据后重试

### Q: 缓存不生效？
**A:**
- 打开控制台查看 `[SW]` 日志
- 确认图片 URL 以 .png/.jpg 等结尾
- 检查是否禁用了浏览器缓存

### Q: 如何强制更新缓存？
**A:**
```javascript
// 方法1:  unregister 后刷新
navigator.serviceWorker.getRegistrations().then(regs => {
  regs.forEach(reg => reg.unregister());
});
location.reload();

// 方法2: 修改 sw.js 中的 CACHE_NAME
```

### Q: 缓存占用太多空间？
**A:**
- 使用"清除缓存"按钮
- 或减小 `IMAGE_CACHE_MAX_SIZE` 的值

## 📈 性能监控

### 查看缓存命中率

在控制台中运行：
```javascript
let hits = 0, misses = 0;

// 监听 SW 消息（需要先在 sw.js 中添加统计代码）
navigator.serviceWorker.addEventListener('message', (e) => {
  if (e.data.type === 'CACHE_HIT') hits++;
  if (e.data.type === 'CACHE_MISS') misses++;
  console.log(`命中率: ${hits}/${hits+misses} (${(hits/(hits+misses)*100).toFixed(1)}%)`);
});
```

## 🎯 最佳实践

1. **首次访问**: 让用户浏览一些图片以填充缓存
2. **定期清理**: 建议每周清理一次缓存
3. **监控存储**: 注意浏览器存储空间使用情况
4. **版本更新**: 修改 SW 代码时记得递增缓存版本号

## 📝 更新日志

### v1.1 (2026-04-12)
- ✅ 调整日期筛选默认为空，显示所有日期的图片
- ✅ 充分利用浏览器缓存提升浏览体验

### v1.0 (2026-04-12)
- ✅ 实现 Service Worker 图片缓存
- ✅ 添加缓存管理UI
- ✅ 支持最多缓存50张图片
- ✅ 自动清理旧缓存
- ✅ 提供缓存统计功能
