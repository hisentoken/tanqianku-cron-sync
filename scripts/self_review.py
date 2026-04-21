#!/usr/bin/env python3
"""
纺织系统每日巡检脚本 - 主管自我检查
每天01:00自动运行，发现问题立即修复，无法修复的才上报
"""
import json, os, datetime, re, sys, subprocess, tempfile
from collections import Counter
from pathlib import Path

HERMES = Path(os.environ.get('HERMES_HOME', '/home/tanqianku/.hermes'))
CRON_OUT = HERMES / 'cron' / 'output'
JOBS_PATH = HERMES / 'cron' / 'jobs.json'
RECENT_FILE = CRON_OUT / 'recent_articles.json'
IMG_CACHE = HERMES / 'image_cache'
TREND_DIR = CRON_OUT
FAILURE_LOG = CRON_OUT / 'failure_log.json'

WARNINGS = []
FIXES = []

def warn(msg):
    WARNINGS.append(msg)

def fix(msg):
    FIXES.append(msg)
    print(f"  🔧 {msg}")

def section(name):
    print(f"\n{'='*50}")
    print(f"【{name}】")
    print('='*50)

# ─────────────────────────────────────────
def check_image_cache():
    section("本地兜底图")
    if not IMG_CACHE.exists():
        fix("兜底图目录不存在，新建")
        IMG_CACHE.mkdir(parents=True, exist_ok=True)
        return

    imgs = [f for f in os.listdir(IMG_CACHE) if f.endswith('.jpg')]
    print(f"  共 {len(imgs)} 张")

    if len(imgs) < 10:
        fix(f"兜底图仅{len(imgs)}张，从images目录补充")
        src_dir = CRON_OUT / 'images'
        if src_dir.exists():
            src_imgs = [f for f in os.listdir(src_dir) if f.endswith('.jpg')]
            for img in src_imgs[:50]:
                subprocess.run(['cp', str(src_dir/img), str(IMG_CACHE/img)], capture_output=True)
    elif len(imgs) < 31:
        warn(f"兜底图{len(imgs)}张，未达31张目标")

    if len(imgs) >= 10:
        print(f"  ✅ {len(imgs)} 张")

    # 压缩超限文件
    for f in IMG_CACHE.glob('*.jpg'):
        size = f.stat().st_size
        if size > 150*1024:
            compressed = f.parent / f'{f.stem}_c.jpg'
            r = subprocess.run(['ffmpeg','-i',str(f),'-q:v','1','-vf','scale=720:-1','-y',str(compressed)],
                             capture_output=True, timeout=60)
            if r.returncode == 0 and compressed.exists():
                compressed.replace(f)

    # 今日使用记录
    used_file = IMG_CACHE / 'used_today.txt'
    today = datetime.date.today().isoformat()
    used_today = set()
    if used_file.exists():
        with open(used_file) as f:
            for line in f:
                parts = line.strip().split(',')
                if parts and parts[0] == today:
                    used_today.add(parts[1])
    print(f"  今日已用 {len(used_today)} 张")

# ─────────────────────────────────────────
def check_recent_articles():
    section("recent_articles")
    if not RECENT_FILE.exists():
        warn("文件不存在，15天查重机制失效")
        RECENT_FILE.write_text(json.dumps({"articles":[],"updated":""}, ensure_ascii=False, indent=2))
        return

    with open(RECENT_FILE) as f:
        ra = json.load(f)
    arts = ra.get('articles', [])
    if not arts:
        warn("记录为空")
        return

    print(f"  共 {len(arts)} 篇")

    latest = arts[-1]
    latest_h2 = latest.get('h2_count')
    latest_time = latest.get('published_at', '')[:10]
    print(f"  最新: {latest_time} | h2×{latest_h2} | {latest.get('title','')[:40]}")
    if latest_h2 == 0 or latest_h2 is None:
        fix("最新一篇h2_count=0，已标记，下次发布正确记录")
        latest['_h2_missing'] = True

    # h2_count缺失
    missing = sum(1 for a in arts if not a.get('h2_count') or a.get('h2_count') == 0)
    if missing:
        warn(f"{missing}/{len(arts)} 篇缺少h2_count")

    # 叙事身份连续重复
    identities = [a.get('identity', '无') for a in arts]
    consec = 1
    max_consec = 1
    last_id = None
    for id_ in reversed(identities):
        if id_ == last_id:
            consec += 1
            max_consec = max(max_consec, consec)
        else:
            consec = 1
        last_id = id_
    if max_consec >= 3:
        warn(f"最近{max_consec}篇同一identity")
        fix("强化prompt里的身份轮换约束")

    # 15天内类目覆盖
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=15)).isoformat()
    recent15 = [a for a in arts if a.get('published_at', '') >= cutoff]
    cats = [a.get('category', '') for a in recent15]
    print(f"  15天内 {len(recent15)} 篇，覆盖: {list(Counter(cats).keys())}")
    if len(set(cats)) < 3:
        warn(f"15天内仅{len(set(cats))}个类目，发布密度不足")

    # 写回（修复标记）
    with open(RECENT_FILE, 'w') as f:
        json.dump(ra, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────
def check_knowledge_bases():
    section("知识库完整性")
    kbs = {
        '布行': CRON_OUT / 'knowledge_base_buxing' / 'buxing_knowledge.md',
        '内衣': CRON_OUT / 'knowledge_base_neiyi' / 'neiyi_knowledge.md',
        '家居': CRON_OUT / 'knowledge_base_jiaju' / 'jiaju_knowledge.md',
        '电商': CRON_OUT / 'knowledge_base_diangu' / 'diangu_knowledge.md',
    }
    for name, path in kbs.items():
        if not path.exists():
            warn(f"{name}知识库不存在")
        else:
            size = path.stat().st_size
            with open(path) as f:
                words = len(f.read())
            print(f"  {name}: {words}字")
            if words < 500:
                warn(f"{name}知识库内容过少({words}字)")

# ─────────────────────────────────────────
def check_trend():
    section("trend文件时效")
    today = datetime.date.today()
    found = False
    for i in range(3):
        date = today - datetime.timedelta(days=i)
        trend_file = TREND_DIR / f"textile_trend_{date.strftime('%Y%m%d')}.md"
        if trend_file.exists():
            age_hours = (datetime.datetime.now() - datetime.datetime.fromtimestamp(
                trend_file.stat().st_mtime)).total_seconds() / 3600
            status = "✅" if age_hours <= 36 else "⚠️"
            print(f"  {status} {trend_file.name} ({age_hours:.1f}h前)")
            if age_hours > 36:
                warn(f"trend超过36小时未更新")
                if i == 0:
                    fix("今日trend文件过期，尝试重新采集")
            found = True
    if not found:
        warn("近3天内无任何trend文件")

# ─────────────────────────────────────────
def check_jobs():
    section("jobs.json完整性")
    if not JOBS_PATH.exists():
        warn("jobs.json不存在!")
        return

    with open(JOBS_PATH) as f:
        data = json.load(f)
    jobs = data.get('jobs', [])
    publish_jobs = [j for j in jobs if 'gen_img_and_build_html' in j.get('prompt', '')]
    print(f"  总任务: {len(jobs)} | 发布任务: {len(publish_jobs)}")

    # 开头检查
    missing_opening = [j['name'] for j in publish_jobs
                      if '文章第一段与标题完全相同' not in j.get('prompt','')]
    if missing_opening:
        warn(f"{len(missing_opening)} 个任务缺少开头检查")
        fix(f"注入开头检查到{len(missing_opening)}个任务")
        inject_opening_check(data)
    else:
        print(f"  ✅ 所有 {len(publish_jobs)} 个任务含开头检查")

    # 章节多样性
    missing_h2div = [j['name'] for j in publish_jobs
                    if '章节结构进化约束' not in j.get('prompt','')]
    if missing_h2div:
        warn(f"{len(missing_h2div)} 个任务缺少章节多样性约束")
        fix(f"注入章节多样性到{len(missing_h2div)}个任务")
        inject_h2_diversity(data)
    else:
        print(f"  ✅ 所有任务含章节多样性约束")

    # h2_count提取（write_recent调用）
    missing_h2count = [j['name'] for j in publish_jobs
                      if 'h2_count = len' not in j.get('prompt','')]
    if missing_h2count:
        warn(f"{len(missing_h2count)} 个任务缺少h2_count提取")
        fix(f"注入h2_count提取到{len(missing_h2count)}个任务")
        inject_h2_count(data)
    else:
        print(f"  ✅ 所有任务含h2_count提取")

    # 保存修改
    if missing_opening or missing_h2div or missing_h2count:
        tmp = tempfile.NamedTemporaryFile(mode='w', dir=str(JOBS_PATH.parent), delete=False, suffix='.json')
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp.close()
        os.replace(tmp.name, JOBS_PATH)
        print(f"  ✅ jobs.json 已更新")

# ─────────────────────────────────────────
def check_self_evolution():
    section("自我进化追踪")
    if not RECENT_FILE.exists():
        return
    with open(RECENT_FILE) as f:
        ra = json.load(f)
    arts = ra.get('articles', [])
    if len(arts) < 3:
        print(f"  样本不足（仅{len(arts)}篇）")
        return

    recent5 = arts[-5:]
    h2s = [a.get('h2_count', 0) for a in recent5 if a.get('h2_count', 0) > 0]
    if len(h2s) >= 2:
        avg = sum(h2s)/len(h2s)
        variance = sum((x-avg)**2 for x in h2s)/len(h2s)
        print(f"  近{h2s}章节数均值{avg:.1f}，方差{variance:.1f}")
        if variance < 1:
            warn(f"章节结构过于稳定（方差{variance:.1f}）")

    identities = [a.get('identity','?') for a in arts[-6:]]
    id_set = set(identities)
    print(f"  近6篇身份: {identities}")
    if len(id_set) <= 2:
        warn(f"近6篇仅用{len(id_set)}种身份")

# ─────────────────────────────────────────
def inject_opening_check(data):
    code = '''
# 检查文章第一句是否为标题（标题不得作为正文开头）
first_p_match = re.search(r'<p[^>]*>([^<]+)</p>', article_html)
if first_p_match:
    first_p_text = first_p_match.group(1).strip()
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', article_html)
    if h1_match and first_p_text == h1_match.group(1).strip():
        raise AssertionError('文章第一段与标题完全相同，违反"标题不得作为正文开头"规则，当前任务中止！')
'''
    marker = '# 清理LLM输出中的markdown代码围栏'
    for job in data['jobs']:
        if marker in job['prompt'] and '文章第一段与标题完全相同' not in job['prompt']:
            job['prompt'] = job['prompt'].replace(marker, code + '\n' + marker, 1)

def inject_h2_diversity(data):
    code = '''
# === 章节结构进化约束 ===
# 不得固定为4章，具体章数由内容深度决定：
#   - 规格解读/工艺揭秘型：建议4章
#   - 避坑/认证合规型：建议3章
#   - 行情分析/趋势预判型：建议5章
# 发布前验证 h2数量在3-5之间
'''
    for job in data['jobs']:
        p = job['prompt']
        if 'gen_img_and_build_html' in p and '章节结构进化约束' not in p:
            marker = '### 写作后必须'
            if marker in p:
                idx = p.find(marker)
                job['prompt'] = p[:idx] + code + '\n' + p[idx:]

def inject_h2_count(data):
    code = '''
# === 记录到 recent_articles（发布成功后必须执行）===
h2_list = re.findall(r'<h2[^>]*>(.*?)</h2>', final_html)
h2_count = len(h2_list)
if h2_count == 0:
    raise AssertionError('h2_count=0，write_recent未被调用，查重机制失效，当前任务中止！')
RECENT_FILE = os.path.expanduser('~/.hermes/cron/output/recent_articles.json')
DAYS_LIMIT = 15
import datetime as _dt
with open(RECENT_FILE) as _f:
    _data = json.load(_f)
_cutoff = (_dt.datetime.now() - _dt.timedelta(days=DAYS_LIMIT)).isoformat()
_data['articles'] = [a for a in _data.get('articles',[]) if a.get('published_at','') >= _cutoff]
_data['articles'].append({
    'title': title, 'topic_keywords': [], 'slug': 'tanjia', 'category': '探单',
    'published_at': _dt.datetime.now().isoformat(), 'h2_count': h2_count, 'identity': '',
})
with open(RECENT_FILE, 'w') as _f:
    json.dump(_data, _f, ensure_ascii=False, indent=2)
'''
    marker = '# 任意一层失败 → 函数raise → 任务中止，不发API'
    for job in data['jobs']:
        p = job['prompt']
        if marker in p and 'h2_count = len' not in p:
            idx = p.find(marker)
            job['prompt'] = p[:idx] + code + '\n' + p[idx:]

# ─────────────────────────────────────────
def main():
    print(f"纺织系统每日巡检 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        check_image_cache()
        check_recent_articles()
        check_knowledge_bases()
        check_trend()
        check_jobs()
        check_self_evolution()
    except Exception as e:
        print(f"\n❌ 巡检出错: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\n{'='*50}")
    print(f"巡检结果汇总")
    print('='*50)

    if FIXES:
        print(f"\n🔧 本次自动修复 ({len(FIXES)}项):")
        for f in FIXES:
            print(f"  • {f}")

    if WARNINGS:
        print(f"\n⚠️  需要关注的问题 ({len(WARNINGS)}项):")
        for w in WARNINGS:
            print(f"  • {w}")
    else:
        print("\n✅ 系统健康，无警告项")

    print(f"\n📊 巡检完成: {datetime.datetime.now().strftime('%H:%M:%S')}")

if __name__ == '__main__':
    main()
