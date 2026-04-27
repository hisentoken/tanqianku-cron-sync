---
name: hermes-gateway-troubleshooting
description: Diagnose and fix Hermes gateway service failures, Telegram polling conflicts, and systemd restart loops
category: devops
---

# Hermes Gateway Troubleshooting

## Common Failure Modes

### 1. Telegram Polling Conflict
**Symptom**: `[Telegram] Telegram polling conflict (1/3)` repeated in logs, or `Unauthorized user` despite correct config.

**Cause**: Another instance of the gateway is already running (often from a previous session or manual start).

**Diagnosis**:
```bash
hermes logs --lines 50
journalctl --user -xeu hermes-gateway.service --no-pager -n 100
ps aux | grep hermes
```

**Fix**: Find and kill the stale process:
```bash
# Check for old/stale gateway processes (note the PID and start time)
ps aux | grep gateway | grep -v grep

# Kill the old process by PID directly (more reliable than pkill)
kill <old_pid>
sleep 2

# Verify it's gone
ps aux | grep gateway | grep -v grep

# Then start fresh
hermes gateway start
```

**Key diagnostic**: if `ps aux` shows a gateway process with an old start time (e.g., from yesterday) but `hermes gateway status` says it's stopped or restarting — the old process is zombie/stuck and must be killed by PID.

### 2. Systemd Service in "failed" State (exit-code 75)
**Symptom**: `systemctl --user start hermes-gateway.service` fails with "Start request repeated too quickly" or exit-code 75.

**Cause**: Gateway crashed/restarted too many times in quick succession, and systemd put it in a failed/abort state.

**Fix**:
```bash
systemctl --user reset-failed hermes-gateway.service
systemctl --user start hermes-gateway.service
```

**Note**: `systemctl --user stop` can sometimes timeout (takes 60s for graceful shutdown). If stuck, use `kill <PID>` directly instead.

### 3. Gateway Running but Users Still Unauthorized
**Symptom**: Gateway is `active (running)` but users get `Unauthorized user` warnings.

**Fix**: Set the allowlist explicitly in `.env`:
```bash
# Add to ~/.hermes/.env
echo 'TELEGRAM_ALLOWED_USERS=your_user_id' >> ~/.hermes/.env
hermes gateway restart
```

The config via `hermes config set` may not be picked up correctly — adding directly to `.env` is more reliable.

## Quick Reference

```bash
# Check gateway status
hermes gateway status

# View recent logs
hermes logs --lines 30

# Full journald logs
journalctl --user -xeu hermes-gateway.service --no-pager -n 50

# Restart cleanly
systemctl --user reset-failed hermes-gateway.service
hermes gateway restart

# If all else fails, foreground debug
hermes gateway run
```

### 4. Telegram Connection Fails with `httpx.ConnectError` Behind Proxy
**Symptom**: Logs show `telegram.error.NetworkError: httpx.ConnectError:` and Telegram fails to connect, even though proxy works in terminal.

**Cause**: The systemd service runs in an isolated environment — it does NOT inherit shell env vars. Additionally, `hermes gateway restart` OVERWRITES the systemd unit file, destroying any manually added Environment lines.

**Diagnosis**:
```bash
hermes logs --lines 20
# Look for: httpx.ConnectError

# Check if proxy env vars reached the process
cat /proc/$(systemctl --user show --property MainPID --value hermes-gateway.service)/environ | tr '\0' '\n' | grep proxy
```

**Fix — Use systemd drop-in override (the ONLY reliable method)**:
`hermes gateway restart` rewrites the main unit file, so manual edits to it are not durable. Use a drop-in override instead:

```bash
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d

# Create the drop-in with proxy config AND longer TimeoutStopSec
cat > ~/.config/systemd/user/hermes-gateway.service.d/override.conf << 'EOF'
[Service]
# TimeoutStopSec must be higher than the gateway's drain timeout (60s).
# Without this, systemd kills the process with SIGKILL before graceful shutdown completes.
TimeoutStopSec=300

# Proxy configuration — hermes gateway restart CANNOT override this
EnvironmentFile=/home/user/.hermes/proxy.env
EOF

# Create the proxy env file
cat > ~/.hermes/proxy.env << 'EOF'
http_proxy=http://127.0.0.1:7897
https_proxy=http://127.0.0.1:7897
all_proxy=socks5://127.0.0.1:7897
no_proxy=localhost,127.0.0.1
EOF

systemctl --user daemon-reload
systemctl --user restart hermes-gateway.service
```

**Why drop-in works**: `hermes gateway restart` rewrites only the main unit file. Drop-in files in `.d/` are merged by systemd and cannot be touched by hermes.

**Critical: TimeoutStopSec must be 300+**: The gateway uses a 60s drain timeout for graceful shutdown. If `TimeoutStopSec` is shorter (e.g. the default 60s), systemd sends SIGKILL before drain completes. Evidence: `code=killed, status=9/KILL` in `systemctl status`.

### 5. Bot Token 无效导致连接失败（404 Not Found）
**Symptom**: Gateway 日志显示 `httpx.ConnectError: All connection attempts failed`，`hermes gateway status` 报 `telegram startup failed`。直接 curl Telegram API 返回 `{"ok":false,"error_code":404,"description":"Not Found"}`。

**Cause**: `.env` 中的 token 值错误或不完整（如 `819074...tNe0` 被截断显示），或 Bot 在 @BotFather 侧已被删除。

**Diagnosis — 直接验证 token 是否有效**:
```bash
# 查 token 对应的 bot 用户名
curl -s https://api.telegram.org/bot<你的TOKEN>/getMe
# 返回 {"ok":true,"result":{"username":"xxx_bot",...}} = token 有效
# 返回 {"ok":false,"error_code":404,"description":"Not Found"} = token 错误

# 代理环境下
curl -x http://127.0.0.1:7897 -s https://api.telegram.org/bot<TOKEN>/getMe
```

**Fix**: 用正确 token 覆盖：
```bash
hermes config set TELEGRAM_BOT_TOKEN "<完整Token>"
systemctl --user restart hermes-gateway.service
```

**Note**: `hermes config show` 只显示 `Telegram: configured`，不显示 token 值。token 完整值要查 `.env` 文件或用上面 curl 方式验证。

### 6. Token Config Key Format
**Symptom**: `ValueError: Invalid environment variable name: 'TELEGRAM.BOT_TOKEN'`

**Cause**: Wrong format used with `hermes config set`.

**Fix**: Use underscore format, not dot:
```bash
# WRONG:
hermes config set telegram.bot_token TOKEN

# CORRECT:
hermes config set TELEGRAM_BOT_TOKEN TOKEN
```

### 6. Telegram "Zombie" — Gateway Running but Polling Dead (No Reply to Messages)
**Symptom A (classic)**: `hermes gateway status` shows `active (running)`, but Telegram bot does not respond to messages. Logs show repeated `Telegram polling reconnect failed` or `httpx.ConnectError` with no recovery.

**Symptom B (2026-04-20 新发现)**: Gateway 日志显示 `[Telegram] Connected to Telegram (polling mode)`，进程存活，但用户发消息无响应，无任何 `send msg` 或错误日志 — polling 实际已死，但 gateway 主循环（cron ticker）还在跑，给外界造成"连接正常"的假象。

**Cause (Symptom A)**: The gateway's Telegram polling thread crashed/failed but the main process did not exit, leaving the platform in a half-dead state.

**Cause (Symptom B)**: 网络层 mihomo HTTP 代理到 Telegram API 不稳定（~80% 成功率），gateway 的 Telegram polling 连接建立后，send_message 请求撞上那 20% 超时窗口失败，之后 polling 分节继续"存活"但实际上已死。gateway 没有自动重连机制。

**Diagnosis (Symptom B)**:
```bash
# 1. 确认代理到 Telegram 的当前成功率（连续测试5次）
for i in 1 2 3 4 5; do
  curl -x http://127.0.0.1:7897 --connect-timeout 5 -s -w "%{http_code}\n" https://api.telegram.org/botTOKEN/getMe
done
# 返回 401 = 成功，000 或超时 = 失败

# 2. 检查 gateway 是否真的在处理消息（发一条 Telegram，看日志有无反应）
hermes logs --lines 20 | grep -E '(msg|send|telegram)'
# 无输出 = polling 已死
```

**Fix**: 必须重启 gateway — `systemctl --user restart hermes-gateway.service`

**Mitigation for proxy instability**: 在 drop-in 中增加 httpx 超时容忍度：
```bash
# 编辑 drop-in 文件
sudo -u tanqianku systemctl --user edit hermes-gateway.service

# 在 [Service] 下添加（如果还没有的话）：
Environment=HERMES_TELEGRAM_HTTP_CONNECT_TIMEOUT=30
Environment=HERMES_TELEGRAM_HTTP_READ_TIMEOUT=60
Environment=HERMES_TELEGRAM_HTTP_WRITE_TIMEOUT=60
Environment=HERMES_TELEGRAM_HTTP_POOL_TIMEOUT=15
```
默认值分别是 10/20/20/8 秒，提高到 30/60/60/15 可容忍间歇性代理抖动。

**Diagnosis**:
```bash
hermes logs --lines 50 | grep -E '(telegram|polling|connected)'
# Look for: "Telegram polling could not reconnect after 10 network error retries"
# Or: "Gateway failed to connect any configured messaging platform"
```

**Fix**: Force-kill the stale process and restart:
```bash
# Find the actual running PID
ps aux | grep 'hermes_cli.main gateway' | grep -v grep

# Kill it directly (do NOT use systemctl stop — it times out)
kill -9 <PID>

# Wait for systemd to auto-restart, or trigger manually
systemctl --user reset-failed hermes-gateway.service
systemctl --user start hermes-gateway.service

# Verify
sleep 8 && hermes logs --lines 10 | grep Telegram
# Should see: "[Telegram] Connected to Telegram (polling mode)"
```

**Prevention**: Ensure `Restart=on-failure` is set and `TimeoutStopSec=300` in the drop-in so systemd can properly manage restarts.

### 7. All Platforms Permanently Failed — Gateway Alive but Disconnected
**Symptom**: Gateway is `active (running)`, no crash, but Telegram never reconnects after a failure. `hermes logs` shows all reconnect retries exhausted, then silence.

**Root cause**: In `gateway/run.py`, `_platform_reconnect_watcher`'s inner for loop runs forever. When all adapters have permanently failed (gave up after max retries), `_failed_platforms` gets exhausted (empty after give-up), but the gateway continues running with no adapters and no reconnect queue. Systemd doesn't know to restart because the process hasn't exited. This creates a zombie state: process alive, Telegram permanently dead.

**Fix — Patch `run.py` to exit with code 75 when all platforms permanently fail**:
```python
# File: ~/.hermes/hermes-agent/gateway/run.py
# Location: end of `_platform_reconnect_watcher` inner for loop, after line ~1947
# (after the `else: break` that exits when _failed_platforms is empty)

# ADD THIS after the inner for loop completes (all platforms gave up their cycle):
if not self.adapters and not self._failed_platforms:
    # All platforms have permanently failed. Exit so systemd can restart.
    self._exit_code = 75
    self._request_clean_exit("All messaging platforms failed")
    return
```

**Why exit code 75**: `EX_TEMPFAIL` (BSD style) = temporary failure, suitable for retry. systemd `Restart=on-failure` treats exit 75 as a restartable failure and will re-attempt after `RestartSec=30`.

**Why `_request_clean_exit()` instead of bare `return`**: The original `return` left `_shutdown_event` unset, potentially hanging the event loop. `_request_clean_exit()` properly triggers the shutdown path including `self._shutdown_event.set()`, clean platform disconnects, and `self._running = False`.

**Verification**:
```bash
# Trigger a reconnect cycle that will fail (e.g., stop proxy temporarily)
# Then check systemd journal:
journalctl --user -xeu hermes-gateway.service --no-pager -n 20 | grep -E '(exit|code=)'
# Should show: code=exited, status=75

# Confirm systemd auto-restarts:
systemctl --user status hermes-gateway.service
# Should show: `Active: active (running)` with a new PID
```
## Key Lessons

1. **Always check for stale processes first** — the most common cause of polling conflicts
2. **Systemd can enter a "failed" state** that blocks further restarts; must `reset-failed` before starting again
3. **Direct `.env` editing is more reliable than `hermes config set`** for environment variables like `TELEGRAM_ALLOWED_USERS`
4. **Exit code 75** from the gateway is an auto-restart abort, not a config error — and it must be explicitly triggered by patching `run.py` when all platforms permanently fail (the gateway does not do this by default)
5. **Behind a proxy, systemd services don't inherit shell env vars** — proxy must be explicitly set via `EnvironmentFile=` in a systemd drop-in override
6. **Token config uses underscore format** (`TELEGRAM_BOT_TOKEN`), not dot format (`telegram.bot_token`)
7. **`hermes gateway restart` regenerates the main unit file** — any `Environment=` lines added manually are lost; use drop-in overrides (`*.service.d/override.conf`) instead, which are not touched by `hermes gateway restart`
8. **`TimeoutStopSec=60` is dangerously short** — gateway drain takes ~60s; systemd sends SIGKILL at 60s and kills the process mid-drain. Always set `TimeoutStopSec=300` in the drop-in override.
9. **The gateway can enter a "zombie disconnected" state** where it stays alive but Telegram is permanently dead — the reconnect watcher loops forever but nothing recovers. The fix is patching `run.py` to exit code 75 when `not self.adapters and not self._failed_platforms`.
10. **mihomo HTTP 代理到 Telegram API 不稳定时（~80% 成功率），gateway 可能出现"假连接"状态** — polling 看起来建立了，但 send_message 因代理超时失败，之后 polling 进入 zombie 状态。增加 httpx 超时容忍度 + 发现无响应立即重启 gateway。
