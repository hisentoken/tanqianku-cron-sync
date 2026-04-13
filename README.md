# 探钱库内容发布系统 - 完整配置包

一键部署纺织行业B2B内容发布机器人，包含采集、写作、发布全链路。

## 快速开始

1. **克隆本仓库**
2. **复制配置**
   ```bash
   cp .env.example .env
   # 编辑 .env，填入各平台API密钥
   ```
3. **安装Hermes Agent**
   ```bash
   pip install hermes-agent
   # 或: pip install -e hermes-agent/
   ```
4. **初始化cron任务**
   ```bash
   hermes cron import jobs.json
   ```
5. **验证启动**
   ```bash
   hermes cron status
   ```

## 包含内容

### 核心配置文件
| 文件 | 说明 |
|------|------|
| `.env.example` | 环境变量模板（API密钥占位符） |
| `config.yaml` | Hermes Agent主配置 |
| `auth.json` | 认证信息模板 |
| `cron/jobs.json` | 41个定时任务（采集+发布） |
| `cron/standalone_cron.py` | 独立cron调度器（断连自恢复） |

### Skills（技能模块）
| Skill | 用途 |
|-------|------|
| `textile-article-publishing` | 纺织全域内容发布核心skill |
| `textile-trend-collection` | 每日资讯采集skill |

### 知识库
| 文件 | 类目 |
|------|------|
| `doc_735f5261f836_坯布.txt` | 坯布 |
| `doc_9bd48c145906_原料.txt` | 原料 |
| `doc_6e898f7e8e5f_辅料.txt` | 辅料 |
| `doc_c6b4c1a1cb3b_布行.txt` | 布行 |
| `doc_d6412087bfb4_服装.txt` | 服装 |

### 本地图片兜底
路径: `/home/tanqianku/hp/`
当MiniMax额度用尽时，自动从本地相册读取图片。

---

## 系统架构

```
10:00 采集 → textile_trend_YYYYMMDD.md（含6个分析视角）
    ↓
06-23点 每小时发布1-2篇
    ├── 坯布（tanhuo）8篇/天
    ├── 原料（tanjia）8篇/天
    ├── 辅料（tanjia）8篇/天
    ├── 布行（tanhuo）8篇/天
    └── 服装（tanhuo）8篇/天
    ↓
探钱库API → 推送到APP
```

## VPN/代理断连应对规则

### 问题场景
当VPN或代理连接不稳定时，可能导致：
1. MiniMax图片生成失败（API调用超时）
2. GitHub推送失败（TLS连接中断）
3. Hermes cron daemon失活

### 应对方案

#### 1. Cron Daemon自恢复
`standalone_cron.py` 已配置在 cron daemon 崩溃后自动重启：
- 每分钟检查 daemon 进程状态
- 失活时自动拉起
- 无需手动干预

#### 2. 图片生成兜底
当MiniMax API返回以下错误时，自动切换本地图片：
- `quota` / `额度`
- `login fail`
- `invalid signature`

兜底图片目录: `/home/tanqianku/hp/`（需自行维护图片库）

#### 3. GitHub推送重试
TLS错误自动重试3次，间隔5秒：
```python
for attempt in range(3):
    result = subprocess.run(["git", "push", ...])
    if result.returncode == 0:
        break
    time.sleep(5)
```

#### 4. 网络超时配置
所有HTTP请求超时20秒：
```python
urllib.request.urlopen(req, timeout=20)
```

## 每日发布时段表

| 时段 | 坯布 | 原料 | 辅料 | 布行 | 服装 |
|------|------|------|------|------|------|
| 06:xx | 06:37 | 06:52 | 06:15 | 06:25 | 06:33 |
| 07:xx | — | — | — | — | 07:58 |
| 08:xx | 08:22 | 09:27 | 08:08 | 08:42 | 09:13 |
| 09:xx | — | — | — | — | — |
| 10:xx | 10:45(采集) | — | — | 10:58 | — |
| 11:xx | — | 11:33 | 11:07 | — | 11:48 |
| 12:xx | — | — | — | — | — |
| 13:xx | 13:18 | — | 13:47 | 13:35 | — |
| 14:xx | — | 14:08 | — | — | 14:33 |
| 15:xx | 15:43 | — | 16:15 | 15:12 | 16:07 |
| 16:xx | — | 16:52 | — | — | — |
| 17:xx | 17:58 | — | — | 17:28 | — |
| 18:xx | — | 19:15 | 18:43 | — | 18:55 |
| 19:xx | — | — | — | 19:45 | — |
| 20:xx | — | 21:00 | 20:58 | — | 21:37 |
| 21:xx | 21:12 | — | — | 22:18 | — |
| 22:xx | — | 23:58 | 22:33 | — | — |
| 23:xx | 23:26 | — | — | — | — |

## 五类目标签对照

| 类目 | slug | 知识库文件 |
|------|------|---------|
| 坯布 | tanhuo | doc_735f5261f836_坯布.txt |
| 原料 | tanjia | doc_9bd48c145906_原料.txt |
| 辅料 | tanjia | doc_6e898f7e8e5f_辅料.txt |
| 布行 | tanhuo | doc_c6b4c1a1cb3b_布行.txt |
| 服装 | tanhuo | doc_d6412087bfb4_服装.txt |

## 发布API配置

```python
# Endpoint
POST https://gw.tanqianku.com/_data_bus/v1/webhook/openclaw

# Headers
x-openclaw-secret: <your-secret>

# Body (JSON)
{
  "slug": "tanhuo",        # or tanjia
  "title": "文章标题",
  "content": "<html>...",  # HTML格式，含base64图片
  "tags": ["tag1", "tag2"]
}
```

## MiniMax图片生成

```python
POST https://api.minimax.chat/v1/image_generation
Authorization: Bearer <your-minimax-key>

{
  "model": "image-01",    # 必须用 image-01
  "prompt": "英文纯视觉描述",
  "aspect_ratio": "16:9"
}
```

注意：图片URL是阿里云OSS临时链接（2小时有效），必须下载到本地base64后才能发布。

## 写作事实核查红线

- 南通在江苏，海宁在浙江嘉兴，两地无任何隶属关系
- 数字要符合常识（一件衬衫纽扣5-20颗）
- 禁止贬低任何地区或产业带
- 无配图绝对不发布

## 新增类目方法

1. 准备知识库文件，放入 `cache/documents/`
2. 更新 `textile-article-publishing` skill：
   - 添加类目行到时段表
   - 编写类目写作规范（12种文章类型）
   - 添加时段类型分配
3. 更新 `textile-trend-collection` skill：
   - 添加该类目视角分析模块
4. 创建cronjob并写入 `jobs.json`
5. 推送GitHub同步

## 许可证

MIT
