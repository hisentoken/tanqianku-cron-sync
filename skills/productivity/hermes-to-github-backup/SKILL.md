---
name: hermes-to-github-backup
description: 将~/.hermes目录选择性备份到GitHub，包含skills/知识库/cron任务/配置文件，脱敏后可供其他机器人复用
---

# Hermes配置备份到GitHub

## 功能
将`~/.hermes/`目录选择性备份到GitHub，包括skills、知识库、cron任务、配置文件，排除敏感信息和临时文件。

## 核心问题与解决方案

### 中文文件名
GitHub API推送中文文件名时，路径需要URL编码：
```python
from urllib.parse import quote
# 中文路径: "cache/documents/坯布.txt"
# GitHub API路径需要: quote("cache/documents/坯布.txt", safe="/")
```
如果用`git add "cache/documents/坯布.txt"`可以正常推送，不需要手动编码。

### 敏感信息脱敏
`.env`和`auth.json`必须脱敏后才能上传：
```python
# .env 脱敏：长串API密钥用占位符替换
with open(".env") as f:
    lines = f.readlines()
masked = []
for line in lines:
    if '=' in line and not line.strip().startswith('#'):
        val = line.split('=', 1)[1].strip()
        if len(val) > 8 and any(c.isalpha() for c in val) and any(c.isdigit() for c in val):
            key = line.split('=')[0]
            masked.append(f"{key}=YOUR_{key.upper()}_HERE\n")
        else:
            masked.append(line)
    else:
        masked.append(line)

# auth.json 脱敏：替换长token值
masked_auth = re.sub(
    r'"([^"]+)"\s*:\s*"[A-Za-z0-9_+\/=]{30,}"',
    lambda m: f'"{m.group(1)}": "MASKED"',
    content
)
```
上传前用`.env.example`和`auth.json.upload`命名，恢复时反向操作。

### Git staging的坑
`git add`后文件进入staging，但`git commit`不等于`git push`成功。用`git ls-tree -r HEAD --name-only`确认文件真的在仓库里，而不是只看本地commit输出。检查流程：
```bash
git add <file>
git status --short  # 确认是"A"状态
git commit -m "msg"
git ls-tree -r HEAD --name-only | grep <filename>  # 确认在HEAD里
git push origin master
```

### 应该上传的核心文件
```
.env.example              # 脱敏后的环境变量模板
auth.json.upload          # 脱敏后的认证模板
config.yaml               # Hermes主配置
cron/jobs.json            # 定时任务（最核心）
cron/standalone_cron.py   # 守护进程脚本
skills/                   # 所有skill（含textile系列）
cache/documents/          # 知识库文件
docs/                     # 自述文档/运维手册
README.md
.gitignore
```

### 不上传
- `.env`（真实密钥）
- `auth.json`（真实认证）
- `state.db`、日志、sessions、memories、hermes-agent/源码、venv/、bin/、image_cache/、audio_cache/
- `cron/output/`下的临时HTML和图片
- `processes.json`、`gateway_state.json`等运行时状态

### VPN断连时Git push的应对
TLS错误自动重试3次：
```python
for attempt in range(3):
    result = subprocess.run(["git", "push", "origin", "master"], capture_output=True)
    if result.returncode == 0:
        break
    time.sleep(5)
```

## 完整步骤

1. **读取hermes目录，列出所有文件及大小**
   ```python
   for root, dirs, files in os.walk(hermes):
       dirs[:] = [d for d in dirs if d not in skip_dirs]
       for f in files:
           size = os.path.getsize(os.path.join(root, f))
           print(f"  {rel} ({size//1024}KB)")
   ```

2. **脱敏配置文件**
   - 复制`.env`→`.env.example`（长值替换为`YOUR_KEY_HERE`）
   - 复制`auth.json`→`auth.json.upload`（token值替换为`MASKED`）

3. **分批add + commit + push**
   避免单次commit太大，每次10-15个相关文件：
   ```bash
   git add cron/ skills/productivity/textile-article-publishing/ docs/
   git commit -m "描述"
   git push origin master
   ```

4. **验证推送成功**
   ```bash
   git ls-tree -r HEAD --name-only | grep textile
   git log --oneline -3
   ```

5. **其他机器人恢复时**
   ```bash
   cp .env.example .env  # 填入真实API Key
   cp auth.json.upload auth.json  # 填入真实认证
   hermes cron import jobs.json
   ```

## 适用场景
- 换机器时迁移hermes配置
- 多机器人复制同一套workflow
- 系统重装后一键恢复
- 与他人分享hermes配置模板
