---
name: tanqianku-article-publishing
description: 探钱库文章发布经验沉淀——Payload大小限制、图片处理、API格式
---

# 探钱库文章发布经验（TanQianKu Article Publishing）

> 纺织全域内容发布系统文章发布实践沉淀
> 更新：2026-04-13

---

## 核心发现

### 1. 图片Payload大小限制（关键！）

**问题**：POST到 `https://gw.tanqianku.com/_data_bus/v1/webhook/openclaw` 时，当JSON payload总体积超过约450KB，API返回 HTTP 500 "发布失败"。

**原因**：Base64编码会使二进制图片体积膨胀约1.33倍。即使一个217KB的JPG图片，base64后达290KB，加上文章内容后总payload ~454KB，超过限制。

**解决**：
- 图片文件控制在50KB以内（截断使用，而非压缩）
- 经验值：base64前图片≤50KB，base64后≤66KB，对应总payload约70KB，安全
- 未来应寻找服务端图片压缩方案，或分块上传图片

**注意**：API无返回错误细节，单纯返回500，需用 urllib.error.HTTPError 捕获 body 才能看到错误信息。

---

### 2. API重复检测机制

API根据标题做重复检测，相同标题再次发布会返回：
```json
{"code": 200, "message": "文章已存在，跳过重复发布", "data": {"id": 213, "duplicate": true}}
```
每次发布需用**不同标题**。

---

### 3. 测试发布的风险

"无图不发布"是硬性规则，但测试无图版本可能被API接受（返回200）。实际操作中应避免此类测试，或在确认后立即用正确含图版本覆盖。

---

### 4. 标题字数要求

| 类目 | 要求 | 实际验证 |
|------|------|---------|
| 坯布 | 35-60字 | 未验证 |
| 原料 | 40-60字 | 39字标题仍发布成功（差1字但API接受）|
| 辅料 | 40-60字 | 未验证 |

建议严格遵守40字下限。

---

### 5. 探钱库API请求格式

```python
import urllib.request, json, ssl

url = "https://gw.tanqianku.com/_data_bus/v1/webhook/openclaw"
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "x-openclaw-secret": "c9f65f23d9a87f41298a56c7b989a673d74ddc1fc92b196985e2b9fe06240548"
}
payload = {
    "slug": "tanjia",   # 坯布=tanhuo, 原料/辅料=tanjia
    "title": "标题文字",
    "content": "<p>HTML内容（含base64图片）</p>"
}
data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers, method='POST')
ctx = ssl.create_default_context()
with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
    result = json.loads(resp.read())
```

**注意**：
- 用 `x-openclaw-secret` 请求头，不是 `Authorization: Bearer`
- 禁止用 curl（中文引号/特殊符号会导致500）
- 用 `urllib.request + ssl.create_default_context()`

---

### 6. 图片处理

MiniMax生成API已验证可用，image-01模型：
```
POST https://api.minimax.chat/v1/image_generation
Authorization: Bearer sk-cp-OBJYTXCbg4PQS6gO0Col8fT_cEgZY2Ur_6qhB-bWDAqiuFkciSntwIM0U26E-8HrqoqNRbcp8sgdCksRsQTmSoe-PnltkGuNbsE6xxDByKB-Yqr2nNfWNik
```

返回的OSS临时URL必须下载到本地再转base64，不能直接使用。

---

## 发布检查清单

- [ ] 标题字数达标（原料40-60字）
- [ ] 内容引用当日trend文件
- [ ] 探钱库出现≤2次
- [ ] 有base64图片（无图不发布）
- [ ] 图片base64+内容总体积<450KB
- [ ] 标题与已发布文章不重复


---

## 经验记录

### Markdown代码围栏混入正文bug（2026-04-18）

**问题**：LLM生成的HTML内容里出现 ```html 代码围栏标记，导致文章中出现"```html"等markdown语法残留在正文里。

**根因**：LLM在生成HTML内容片段时，会在输出中包含```html围栏标记（常见做法），当这些内容被拼接到article_html变量后，围栏标记就混入了最终HTML。

**修复方案**：在gen_img_and_build_html()调用前，做全局清理 + 断言验证：
```python
article_html = "你的HTML内容（含[插图]占位符）"
        # 清理LLM输出中的markdown代码围栏，防止```html混入正文
# 关键：必须删整个围栏块，不能只删标记不删内容（用[\s\S]*?匹配跨行内容）
        article_html = re.sub(r'```html[\s\S]*?```', '', article_html)
        article_html = re.sub(r'```[\s\S]*?```', '', article_html)
        assert '```' not in article_html, '清理后仍含代码围栏，当前任务中止！'
img_prompt_english = "英文图生prompt（16:9纯视觉场景，无文字）"
img_save_dir = "/home/tanqianku/.hermes/cron/output/images/"
final_html = gen_img_and_build_html(img_prompt_english, article_html, img_save_dir)
```

**关键**：必须用全局 `re.sub(r'```html', ...)` 和 `re.sub(r'```', ...)` 而不是只去头尾。断言确保清理彻底。

**jobs.json重建时**：必须将上方完整片段原样复制进prompt，不得省略或简化。

**JSON嵌入Python的缩进陷阱（2026-04-18血泪）**：prompt里的Python代码是JSON字符串，缩进用0层级（顶格），因为外层有```python markdown围栏包裹，不是真正的函数体内。不要加8空格缩进，否则代码在```python块里会变成函数内嵌而非顶层语句。
