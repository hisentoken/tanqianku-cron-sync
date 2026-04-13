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

## 内容结构（七板块）

```markdown
## 原料动态（纱价 / 纤维 / 行情）
## 辅料动态（配件 / 包装 / 供需）
## 坯布动态（新品 / 织造 / 产能）
## 三品类联动热点
## 布行视角：今日市场观察
## 服装视角：下游采购观察
## 今日参考价格（可选）
```

### 布行视角：五大分析角度

"布行视角"模块在统一采集时从texindex文章中筛选+标注贸易流通相关内容，每日输出5个角度的分析素材，供布行类目写作使用。

**角度1：价格波动传导链**
原料涨价/跌价 → 织造成本变化 → 坯布报价调整 → 贸易商拿货策略变化
标注格式：`*[布行-价格传导] 涤纶短纤上调200元，绍兴柯桥坯布商跟涨5%，广州中大贸易商观望*`

**角度2：市场情绪与走货动态**
哪个品种走货快/慢，贸易商库存变化，批发市场热点切换
标注格式：`*[布行-走货] 40支纯棉坯布本周走货加快，盛泽某布行库存清空，即买即发*`

**角度3：产业带价格横向对比**
同一坯布/面料，不同产业带的价格差及原因
标注格式：`*[布行-产业带价差] 全棉府绸盛泽报价比南通高0.3元/米，差价来自运费和中间环节*`

**角度4：采购信号捕捉**
采购商询价热点、新品需求动向、出口订单变化
标注格式：`*[布行-采购信号] 欧美快时尚品牌秋装备货启动，40支棉弹力面料询盘量周增30%*`

**角度5：行业政策与突发事件**
环保限产、原料出口管制、海运费波动、汇率变化对贸易的影响
标注格式：`*[布行-政策] 江苏某印染园区限产30%，贸易商转向绍兴柯桥调货，现货溢价5%*`

### 服装视角：五大分析角度（不同于布行，聚焦下游采购决策）

"服装视角"模块在统一采集时标注服装下游采购相关内容，供服装类目写作使用。**切入角度不同于布行**——布行关注流通，服装关注采购决策。

**角度1：面料成本传导**
原料价格变化→成衣面料成本→品牌/电商调价压力
标注格式：`*[服装-成本] 涤纶短纤涨价0.5元/公斤，T恤品牌承受压力，若持续涨价一个月后或被迫调价*`

**角度2：品类热度轮动**
服装下游哪个品类本周搜索/销量上升，电商平台数据信号
标注格式：`*[服装-品类] 瑜伽服品类周搜索量涨40%，户外防晒衣同步升温，面料备货信号已出现*`

**角度3：退换货透视**
从退货率/售后投诉反推面料问题引发的成衣质量纠纷
标注格式：`*[服装-售后] 运动服电商退货率高企，弹力面料色牢度不达标是主因，采购时需查色牢度报告*`

**角度4：认证合规需求**
跨境电商/外贸出口单的认证要求变化
标注格式：`*[服装-认证] 亚马逊欧盟站要求GRS认证再生涤纶，无证面料商面临订单取消风险*`

**角度5：爆款面料拆解**
已验证爆款的服装面料方案，成本结构和跑量原因
标注格式：`*[服装-爆款] 去年防晒衣爆款采用20D锦纶冰丝+UPF50+，成本19元/米，电商售价79元，倍率4倍*`

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
