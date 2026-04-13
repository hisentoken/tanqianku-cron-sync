---
name: tanqianku-api-publish-format
description: 探钱库 API 正确 payload 格式 —— 通过对比成功案例确定的字段结构
version: 1.0.0
---

# 探钱库 API 发布格式

> 经验沉淀：2026-04-13，通过对比 `publish_accessory_20260413.json` 成功案例与失败 payload 确定正确格式。

## 正确 API payload 格式

```python
payload = {
    "title": "文章标题（HTML外单独放）",
    "content": "<h1>...</h1><p>...</p>",  # HTML内容，图片用 <img src="https://..." /> 外链
    "slug": "tanjia",       # 或 "tanhuo"
    "article_type": "行情趋势与成本拆解",  # 文章类型中文名
    "image_url": "https://hailuo-image-...oss-cn-...jpeg"  # MiniMax返回的OSS临时URL
}
```

**注意**：
- `title` 必须作为独立字段，不是 HTML 内的 `<title>`
- `article_type` 必填，中文类型名
- `image_url` 用 MiniMax 返回的外部 OSS URL，**不需要**本地 base64（base64 嵌入 HTML 的 img src 不会显示）
- HTML 内的 `<img src="data:image/jpeg;base64,..." />` 用于平台内嵌图片，但发布 API 用 `image_url` 字段

## 失败 payload（400 错误）

```python
# 错误1：少了 title 和 article_type
{"content": html, "slug": "tanjia", "type": "article"}  # → 400

# 错误2：用 HTML title 标签代替独立 title 字段
{"content": "<html><head><title>标题</title>...", "slug": "tanjia"}  # → 400
```

## 发布成功后响应

```json
{"code": 200, "message": "发布成功", "data": {"id": 228}}
```

## API Endpoint

```
POST https://gw.tanqianku.com/_data_bus/v1/webhook/openclaw
Header: x-openclaw-secret: c9f65f23d9a87f41298a56c7b989a673d74ddc1fc92b196985e2b9fe06240548
```

## 调试方法

参考 `~/.hermes/cron/output/publish_accessory_20260413.json` —— 这是已验证成功的发布记录，含完整 payload 字段，可直接对照。
