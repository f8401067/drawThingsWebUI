// DrawThings WebUI - Service Worker for Image Caching
const CACHE_NAME = 'drawthings-images-v1';
const IMAGE_CACHE_MAX_SIZE = 50; // 最多缓存50张图片
const CACHE_EXPIRY_TIME = 7 * 24 * 60 * 60 * 1000; // 7天过期时间

// 安装事件
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');
  self.skipWaiting(); // 立即激活新的 SW
});

// 激活事件
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // 删除旧版本的缓存
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim(); // 立即控制所有页面
    })
  );
});

// 拦截请求
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // 只缓存图片请求（png, jpg, jpeg, gif, webp）
  if (url.pathname.match(/\.(png|jpg|jpeg|gif|webp)$/i)) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        try {
          // 先尝试从缓存获取
          const cachedResponse = await cache.match(event.request);
          
          if (cachedResponse) {
            console.log('[SW] Cache hit:', url.pathname.split('/').pop());
            
            // 后台更新缓存（stale-while-revalidate 策略）
            fetch(event.request).then((networkResponse) => {
              if (networkResponse.ok) {
                cache.put(event.request, networkResponse.clone());
                console.log('[SW] Updated cache in background:', url.pathname.split('/').pop());
              }
            }).catch(() => {
              // 静默失败，不影响用户体验
            });
            
            return cachedResponse;
          }
          
          // 缓存未命中，从网络获取
          console.log('[SW] Cache miss, fetching from network:', url.pathname.split('/').pop());
          const networkResponse = await fetch(event.request);
          
          if (networkResponse.ok) {
            // 检查缓存大小，如果超过限制则清理
            await manageCacheSize(cache);
            
            // 缓存新图片
            cache.put(event.request, networkResponse.clone());
            console.log('[SW] Cached new image:', url.pathname.split('/').pop());
          }
          
          return networkResponse;
        } catch (error) {
          console.error('[SW] Fetch failed:', error);
          // 如果网络也失败，返回错误
          throw error;
        }
      })
    );
  }
});

// 管理缓存大小
async function manageCacheSize(cache) {
  try {
    const cacheKeys = await cache.keys();
    
    // 如果超过最大数量，删除最旧的
    if (cacheKeys.length >= IMAGE_CACHE_MAX_SIZE) {
      // 按时间排序，删除最旧的
      const sortedKeys = await Promise.all(
        cacheKeys.map(async (key) => {
          const response = await cache.match(key);
          const date = response.headers.get('date');
          return {
            key: key,
            timestamp: date ? new Date(date).getTime() : Date.now()
          };
        })
      ).then(items => items.sort((a, b) => a.timestamp - b.timestamp));
      
      // 删除最旧的，直到达到限制
      const deleteCount = sortedKeys.length - IMAGE_CACHE_MAX_SIZE + 1;
      for (let i = 0; i < deleteCount && i < sortedKeys.length; i++) {
        await cache.delete(sortedKeys[i].key);
        console.log('[SW] Deleted old cache:', sortedKeys[i].key.url.split('/').pop());
      }
    }
  } catch (error) {
    console.error('[SW] Failed to manage cache size:', error);
  }
}

// 提供缓存统计信息（可通过 postMessage 查询）
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'GET_CACHE_STATS') {
    caches.open(CACHE_NAME).then(async (cache) => {
      const keys = await cache.keys();
      event.ports[0].postMessage({
        type: 'CACHE_STATS',
        count: keys.length,
        maxSize: IMAGE_CACHE_MAX_SIZE,
        urls: keys.map(k => k.url.split('/').pop())
      });
    });
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    caches.delete(CACHE_NAME).then(() => {
      event.ports[0].postMessage({
        type: 'CACHE_CLEARED',
        success: true
      });
    });
  }
});
