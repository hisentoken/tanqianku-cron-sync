---
name: textile-trend-collection
description: 从纺织行业网站采集每日动态，生成结构化trend文件供坯布/原料/辅料三类目联动写作使用。
version: 1.0.0
category: productivity
tags: [纺织, 采集, 内容运营]
---

# 纺织全域每日动态采集

## 核心发现

**可用数据源极有限**：大多数国内纺织行业网站（全球纺织网、慧聪网、锦桥纺织网、中国服装辅料网等）在海外环境均无法访问（DNS失败、连接重置、Cloudflare验证等）。**唯一稳定可用源：texindex.com.cn（纺织网）**。

---

## 采集方案（2026-04验证）

### 唯一稳定可用源
- **纺织网 texindex.com.cn**：主页可访问（140KB+），部分文章页面在登录限制下仍能提取正文（通过侧边栏溢出内容）

### 已知不可用
| 网站 | 问题 |
|------|------|
| textile.net | 无响应 |
| tex.hc360.com | DNS失败 |
| chinafz.com | Cloudflare验证 |
| gainse.com | Cloudflare验证 |
| jqse.com | 连接重置 |
| globaltextile.com | DNS失败 |
| ctnet.com | 连接重置 |
| shanse.com | 超时 |

### 文章提取技巧
texindex文章页在未登录状态下可提取正文（内容从侧边栏区域溢出），使用以下模式按优先级尝试：

```python
patterns = [
    r'<div[^>]*class="[^"]*TRS_Editor[^"]*"[^>]*>(.*?)</div>',
    r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>',
    r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
]
```

### 文章URL规律
texindex文章URL格式：`/Articles/YYYY-M-D/ARTICLEID.html`
例：`https://www.texindex.com.cn/Articles/2026-4-13/649419.html`

---

## 输出文件

路径：`/home/tanqianku/.hermes/cron/output/textile_trend_YYYYMMDD.md`

> ⚠️ 注意：此环境 HOME=/home/tanqianku，不是 /root。写文件时必须用 `/home/tanqianku/.hermes/cron/output/`，不能用 `~/.hermes/cron/output/`

---

## 内容结构（五板块）

```markdown
## 原料动态（纱价 / 纤维 / 行情）
## 辅料动态（配件 / 包装 / 供需）
## 坯布动态（新品 / 织造 / 产能）
## 三品类联动热点
## 今日参考价格（可选）
```

---

## Python采集模板

```python
import urllib.request, re, time

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

def extract_article_body(html):
    if not html or html.startswith("ERROR") or len(html) < 1000:
        return None
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    for pattern in [
        r'<div[^>]*class="[^"]*TRS_Editor[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
    ]:
        m = re.search(pattern, html, re.DOTALL)
        if m:
            text = re.sub(r'<[^>]+>', ' ', m.group(1))
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 100:
                return text
    return None

# 使用示例
html = fetch("https://www.texindex.com.cn/Articles/2026-4-13/649419.html")
body = extract_article_body(html)
```

---

## 已知价格数据文章URL（模板）
texindex当天价格文章URL格式固定：
- PTA: `/Articles/2026-4-13/649415.html`
- 涤纶短纤: `/Articles/2026-4-13/649414.html`
- 粘胶短纤: `/Articles/2026-4-13/649412.html`
- 锦纶DTY/POY/FDY: `/Articles/2026-4-13/649411~649409.html`
- 进口棉: `/Articles/2026-4-13/649417.html`
- 棉花产量: `/Articles/2026-4-13/649418~649419.html`

可通过依次请求这些URL获取当日价格数据。
