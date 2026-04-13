# 探钱库系统运维手册

## 目录
1. [系统架构](#系统架构)
2. [日常维护](#日常维护)
3. [故障排查](#故障排查)
4. [VPN/代理断连应对](#vpn代理断连应对)
5. [Cron任务管理](#cron任务管理)
6. [图片兜底机制](#图片兜底机制)
7. [GitHub同步](#github同步)

---

## 系统架构

```
Internet
  ├── Telegram Bot ← 用户指令
  ├── Hermes Agent ← 主控大脑
  └── Cron Daemon ← 定时调度（独立进程）

采集链路:
  10:00 → 纺织网站 → trend文件 → 三类目写作

发布链路:
  每小时整点前后 → 写作 → MiniMax配图 → 探钱库API → APP
```

### 关键进程
| 进程 | 说明 | 管理命令 |
|------|------|---------|
| cron daemon | 独立调度，不依赖Telegram | `hermes cron status` |
| hermes-agent | Agent主进程 | `hermes agents` |
| gateway | Telegram连接 | `hermes gateway status` |

---

## 日常维护

### 查看任务状态
```bash
hermes cron list
```

### 查看最近发布
```bash
tail -100 ~/.hermes/cron/output/publish_log.txt
```

### 查看采集结果
```bash
cat ~/.hermes/cron/output/textile_trend_$(date +%Y%m%d).md
```

### 重启cron daemon
```bash
pkill -f standalone_cron && nohup python3 ~/.hermes/cron/standalone_cron.py &
```

---

## 故障排查

### 任务没触发
1. 检查cron daemon是否存活：`ps aux | grep standalone`
2. 查看daemon日志：`tail ~/.hermes/cron/cron_daemon.log`
3. 查看任务下次执行时间：`hermes cron list`

### 发布失败（无图）
**绝对规则：无配图不发布**

图片生成失败时任务直接中止，不发裸文。
图片失败原因及处理：
| 错误 | 处理 |
|------|------|
| MiniMax `quota`/额度 | 自动切本地图片兜底 |
| MiniMax `login fail` | 自动切本地图片兜底 |
| MiniMax `invalid signature` | 自动切本地图片兜底 |
| 网络超时（>20s） | 重试1次，仍失败则切本地图片 |

本地图片目录：`/home/tanqianku/hp/`
格式：jpg/jpeg，16:9推荐

### API推送失败
检查探钱库API是否可达：
```bash
curl -X POST https://gw.tanqianku.com/_data_bus/v1/webhook/openclaw \
  -H "x-openclaw-secret: YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"slug":"tanhuo","title":"test","content":"<p>test</p>"}'
```

---

## VPN/代理断连应对

### 问题识别
VPN断连的表现：
1. MiniMax API返回网络错误
2. GitHub push失败（TLS error）
3. Webhook推送超时
4. Telegram Bot无响应（但gateway进程在）

### 自动恢复机制

#### 1. Cron Daemon自恢复
`standalone_cron.py` 内置守护进程：
- 每分钟检查主进程PID
- 进程消失则自动拉起
- 拉起后从上次中断处继续（所有任务状态存在jobs.json）

```python
# standalone_cron.py 核心逻辑
import psutil, subprocess, time, os, json

DAEMON_PID_FILE = "~/.hermes/cron/.standalone.pid"
CHECK_INTERVAL = 60  # 每分钟检查一次

def is_process_alive(pid):
    try:
        return psutil.Process(pid).is_running()
    except:
        return False

def ensure_daemon():
    # 读取PID文件
    if os.path.exists(DAEMON_PID_FILE):
        with open(DAEMON_PID_FILE) as f:
            pid = int(f.read().strip())
        if is_process_alive(pid):
            return  # 进程存活，无需操作
    
    # 进程已死，拉起
    subprocess.Popen([
        "python3", f"{HERMES}/cron/standalone_cron.py", "--daemon"
    ], detached=True)
```

#### 2. GitHub推送重试（TLS断线）
所有Git操作在推送失败时自动重试3次：
```python
for attempt in range(3):
    result = subprocess.run(
        ["git", "push", "origin", "master"],
        capture_output=True
    )
    if result.returncode == 0:
        break
    time.sleep(5)  # 等待网络恢复
```

常见TLS错误：
- `OpenSSL SSL_connect: Connection was reset`
- `Failed to connect to github.com port 443`
- `SSL_ERROR_SYSCALL`

#### 3. HTTP请求超时
所有HTTP请求统一超时20秒：
```python
import urllib.request
urllib.request.urlopen(req, timeout=20)
```

超时重试逻辑在图片下载和API推送中均已实现。

#### 4. 图片生成兜底
MiniMax不可用时，写作任务自动切换本地图片：
```python
def get_fallback_image():
    local_dir = "/home/tanqianku/hp/"
    images = [f for f in os.listdir(local_dir) if f.endswith(('.jpg', '.jpeg'))]
    if images:
        chosen = random.choice(images)
        # 压缩后base64编码
        return compress_and_encode(os.path.join(local_dir, chosen))
    raise RuntimeError("本地图片库为空，请补充图片")
```

### 手动切换VPN
如果VPN断开超过5分钟：
```bash
# 1. 重启VPN客户端（具体看你的VPN工具）
# 2. 等待网络恢复
# 3. 验证连接
curl -I https://api.minimax.chat

# 4. 检查cron状态
hermes cron list
# 如果任务积压，手动触发：
hermes cron run <job_id>
```

### 预防措施
1. **VPN设置为自动重连**（大多数VPN客户端支持）
2. **保持standalone_cron.py在crontab中**：
   ```bash
   # 系统crontab（独立于VPN）
   * * * * * pgrep -f standalone_cron || (cd ~ && python3 .hermes/cron/standalone_cron.py &)
   ```
3. **本地图片库定期维护**，保证至少50张备选图

---

## Cron任务管理

### 新增任务
1. 编辑 `~/.hermes/cron/jobs.json`
2. 添加任务对象（参考现有格式）
3. 重启cron daemon生效

### 删除任务
1. 从 `jobs.json` 中移除任务对象
2. 或者：`hermes cron remove <job_id>`

### 查看所有任务
```bash
hermes cron list --json
```

### 手动触发单次任务
```bash
hermes cron run <job_id>
```

### 任务执行流程
每分钟轮询 → 检查是否到点 → 创建subagent → 执行prompt → 写作+配图+发布 → 写publish_log

---

## 图片兜底机制

### 图片来源优先级
1. **MiniMax生成**（首选，AI生成，贴合内容）
2. **本地图片库**（兜底，额度用尽时）

### 本地图片库
路径：`/home/tanqianku/hp/`
格式：jpg/jpeg/png，推荐16:9比例

命名规范（可选）：
- `fabric_001.jpg` - 面料
- `yarn_001.jpg` - 纱线
- `warehouse_001.jpg` - 仓储
- `factory_001.jpg` - 工厂

### 图片压缩
大于200KB的图片自动压缩：
```python
from PIL import Image
img = Image.open(src)
img.save(dst, quality=85, optimize=True)
```

### MiniMax API Key轮换（多Key场景）
如需多Key轮换，在 `.env` 中配置：
```
MINIMAX_API_KEY_1=key1
MINIMAX_API_KEY_2=key2
```
代码自动轮询可用Key。

---

## GitHub同步

### 仓库
```
https://github.com/hisentoken/tanqianku-cron-sync
```

### 同步内容
- `cron/jobs.json` - 任务配置
- `skills/textile-article-publishing/` - 发布skill
- `skills/textile-trend-collection/` - 采集skill
- `skills/productivity/` - 其他生产力skill
- `cache/documents/` - 知识库文件
- `docs/` - 本文档

### 手动同步
```bash
cd ~/.hermes
git add .
git commit -m "描述"
git push origin master
```

### 同步触发时机
- 新增类目时
- 修改任务时段时
- 更新知识库时
- 修复重大bug后

### 其他机器人复用
其他机器人克隆后：
1. 复制 `.env.example` → `.env`，填入自己的API Key
2. 复制 `auth.json.upload` → `auth.json`，填入认证信息
3. 根据需要修改 `cron/jobs.json` 中的时段和类目
4. `hermes cron import` 导入任务

---

## 写作事实核查红线

**绝对不能犯的错误：**

1. **地理错误**：南通在江苏，海宁在浙江嘉兴，两地无隶属关系，绝不能混写
2. **数字造假**：一件衬衫纽扣5-20颗，T恤面料用量1.2-1.5米，任何数字要符合常识
3. **贬低地区**：禁止"垃圾/淘汰/落后"等词汇，客观描述即可
4. **无图发布**：图片生成失败必须中止任务，不能发裸文
5. **引用平台**：文章中不能提及任何电商或行业网站

---

## 联系方式

如遇问题，先查本文档，仍有疑问联系维护者。
