---
name: textile-article-publishing
description: 纺织全域内容发布系统，支持坯布/原料/辅料三个独立类目，各有专属知识库、独立写作风格、统一采集供联动写作。slug：坯布=tanhuo，原料和辅料=tanjia。
version: 5.0.0
---

# 纺织全域内容发布系统 v5.0

## 核心架构

- **统一采集**：每天 10:00 采集，生成一份 `textile_trend_YYYYMMDD.md`，供三类目联动写作
- **三类目标签**：坯布=tanhuo，原料=辅料=tanjia
- **错峰发布**：07-21点每小时一篇，每天12篇

---

## 采集任务（10:00 统一采集）

### 输出文件
`~/.hermes/cron/output/textile_trend_YYYYMMDD.md`

### 内容结构
```
## 原料动态（纱价/纤维/行情）
## 辅料动态（配件/包装/供需）
## 坯布动态（新品/织造/产能）
## 三品类联动热点
## 今日参考价格（可选）
```

### 采集来源
全球纺织网、慧聪网纺织频道、中国服装辅料网、锦桥纺织网、纺织服装商务网

---

## 三类目标签与发布时段
## 三类目标签与发布时段（41个任务，全部forever，全部非整时）

| 类目 | slug | 知识库 | 发布时段 | 每日篇数 |
|------|------|--------|---------|---------|
| 坯布 | tanhuo | `doc_735f5261f836_坯布.txt` | 06:37/08:22/10:45/13:18/15:43/17:58/21:12/23:26 | 8篇 |
| 原料 | tanjia | `doc_9bd48c145906_原料.txt` | 06:52/09:27/11:33/14:08/16:52/19:15/21:00/23:58 | 8篇 |
| 辅料 | tanjia | `doc_6e898f7e8e5f_辅料.txt` | 06:15/08:08/11:07/13:47/16:15/18:43/20:58/22:33 | 8篇 |
| 布行 | tanhuo | `doc_c6b4c1a1cb3b_布行.txt` | 06:25/08:42/10:58/13:35/15:12/17:28/19:45/22:18 | 8篇 |
| 服装 | tanhuo | `doc_d6412087bfb4_服装.txt` | 06:33/07:58/09:13/11:48/14:33/16:07/18:55/21:37 | 8篇 |
| 采集 | — | — | 10:00 | 1篇 |

注：服装类目8个时段与坯布/布行完全错开（布行在06:25/08:42/...，服装在06:33/07:58/...），同一天内不撞车。

注：采集与坯布10:45之间有45分钟窗口，供采集完成后供坯布下午批次引用。

---

## 写作素材读取规则

每个类目写文章时必须读取：
1. **当日 trend 文件**：`~/.hermes/cron/output/textile_trend_YYYYMMDD.md`（10点采集生成）
2. **对应知识库**：见上表

---

## 坯布类目（独立写作风格）

### 核心定位
工业中间品，技术规格 + 加工可行性 + 采购避坑
读者：面料工程师/染整技术员/坯布采购专员

### 文章类型（6选1）
1. **规格解读型**：术语翻译 + 实际对比，让采购看懂规格书（如"133×72是什么意思"）
2. **选型匹配型**：从终端逆向映射，提供具体规格建议（如"瑜伽服用什么坯布"）
3. **工艺揭秘型**：揭开织造成本差异，理解报价（如"同样40支纱为何差20%"）
4. **疵点识别型**：常见织疵成因 + 鉴别方法，服务验货
5. **认证合规型**：GRS/Oeko-Tex/GOTS实际获取路径
6. **产业带采购型**：产业带横向对比，实用采购参考

### 标题风格
实用导向型，带场景/痛点/具体参数

### HTML结构规范（硬性！）
- 每个文章类型对应一套 `<h2>` 分节结构，写作时必须按以下结构组织：
- 禁止平铺段落，必须分 `<h2>` 章节 + `<p>` 正文
- 列表用 `<ul><li>`，禁止中文顿号或换行堆砌

示例："40支棉缎纹坯布多少钱一米？南通和兰溪的价格差在哪、坯布采购商不敢说的秘密"

### 配图风格（坯布专属）
制造业半成品感，大卷坯布仓储/织机运转/待发场景
prompt示例（英文纯视觉，禁止文字标签）：
- "Large rolls of grey fabric stacked in textile warehouse, factory setting, side lighting, professional photography"
- "Modern rapier loom in operation, close-up of warp and weft交织, Chinese factory interior"
- "Stacked grey fabric rolls ready for shipment, factory loading dock, afternoon light"

可自行进化：加入验布场景/不同织机类型对比/产业带外景/卷标特写

---

## 原料类目（独立写作风格）

### 核心定位
行情分析/成本拆解/B2B采购决策
读者：采购决策者/贸易商

### 文章类型（12选1）
1. B2B采购避坑与供应商筛选
2. 行情趋势与成本拆解
3. 高端料平替与降本
4. 原材料深度对标与极限PK
5. 新品开发与营销卖点提炼
6. 前沿加工工艺与组织适配
7. 行业痛点与技术解决方案
8. 验货标准与物理指标揭秘
9. 大货生产翻车案例复盘
10. 环保认证通关与海外合规
11. 中英外贸黑话与规格参数解析
12. 面料跨界应用与产业用纺织品

### 标题风格
行情分析型，带数字/趋势/对比
示例："纱线CV%值怎么看？四大纺纱工艺的真实差距终于说清楚了"

### 配图风格
工厂内景/面料质感/质量检测场景
prompt示例：
"Modern textile mill interior, worker examining white fabric rolls, Chinese factory setting, clean warehouse, professional photography"

---

## 辅料类目（独立写作风格）

### 核心定位
选型指南/验货标准/成本核算
读者：品质专员/采购专员/工厂技术员

### 文章类型（6选1）
1. 选型指南（拉链/纽扣/衬布怎么选）
2. 验货标准（检测方法、AQL抽检）
3. 成本核算（成本拆解、损耗计算）
4. 问题解决（常见客诉与处理）
5. 产业分析（产业带分布、供应商评估）
6. 行业揭秘（B端采购避坑）

### 标题风格
选型对比型，带参数/疑问/痛点
示例："拉链规格参数怎么选：3号5号8号区别在哪、尼龙金属防水拉链各自优缺点、一文说清楚"

### 配图风格
产品特写（拉链齿型/纽扣质感/色卡对比/标签印刷细节）
prompt示例：
"Close-up macro shot of metal zipper teeth precision detail, silver metallic texture, factory product photography, no text, no labels"

---

## 布行类目（独立写作风格）

### 核心定位
贸易流通视角，帮布行从业者（面料商/贸易商/拿货人）看懂市场、找对货源、避开交易陷阱
读者：面料贸易商、布行采购员、找版拿货的业务员

### 写作立场
**不是生产视角**，不是教你织布，而是：
- 帮读者判断"现在该不该拿货"
- 帮读者判断"哪个产业带拿更划算"
- 帮读者判断"这个价格是高了还是低了"
- 帮读者判断"供应商说的是不是真的"

### 写作视角切换
同一题材，从贸易商角度写：
- 坯布"40支纱支" → 布行视角"问价时对方报C40S还是T40S，差距多大"
- 原料"涤纶短纤涨价" → 布行视角"坯布商会跟进涨价吗，拿货要不要提前锁价"
- 辅料"拉链断货" → 布行视角"哪个替代供应商还来得及供"

### 文章类型（12选1，每天轮转）
1. **拿货时机判断**：根据原料价格走势，判断当前是否适合囤货或观望
2. **产业带横向比价**：同一坯布/面料，不同产业带的到货价+运费+时效对比
3. **供应商筛选与避坑**：常见贸易商套路拆解（虚报规格、拿B布充A布、缸差掩饰）
4. **调样与拿版实战**：如何高效拿到符合需求的小样，避免反复寄样
5. **价格波动传导分析**：从原料到坯布到面料的价格链，传导逻辑与时间差
6. **新品与趋势捕捉**：市场热点切换信号，贸易商如何提前布局
7. **库存与资金策略**：布行库存管理逻辑，什么时候清货什么时候压货
8. **出口与跨境拿货**：FOB/CIF/双清等外贸词解释，及跨境拿货的坑
9. **行业政策影响评估**：环保限产、海运费、汇率对外贸布行的影响
10. **选版与快速响应**：服装品牌/电商的短交期订单，布行如何配合
11. **认证与合规要求**：GRS/Oeko-Tex等认证在外贸单中的实际作用
12. **行业黑话与行话**：布行拿货、炒货、调样时的专业术语与谈判技巧

### 标题风格
贸易决策导向，带数字/对比/行动信号
示例："涤纶短纤三天涨5%，坯布商跟不跟？南通和盛泽拿货价差最新测算"
"广州中大和绍兴柯桥拿全棉府绸，哪个更划算？含运费+时效+损耗对比"

### 配图风格
布行/档口场景：面料市场档口陈列、样卡墙、仓库货架、拿货打包场景
prompt示例：
"Busy fabric market stall with colorful fabric rolls displayed, Chinese wholesale textile market, afternoon light, professional photography"
"Fabric buyer examining fabric samples at wholesale market counter, organized sample cards on wall, warm lighting"

---

## 服装类目（独立写作风格）

### 核心定位
下游采购决策视角，帮服装行业从业者（品牌采购/电商卖家/批发拿货人）判断面料值不值得拿、怎么跟客人解释、备货策略怎么定
读者：服装品牌采购专员、电商卖家、批发档口拿货人

### 写作立场
不是教人设计衣服，而是帮读者解决：
- 这个品类现在值不值得拿货
- 这个价格合不合理
- 这种面料客人会不会买单
- 出问题了怎么跟客人解释

### 写作视角切换
同一题材，从服装采购角度写：
- 原料"涤纶短纤涨价" → 服装采购视角"涨价传导到成衣要多久，我该不该提前备货"
- 坯布"弹力缎纹坯布" → 服装采购视角"这款面料做瑜伽服还是做裙子，成本差多少"
- 辅料"防水拉链缺货" → 服装采购视角"户外服面料供应会不会受影响，有没有替代方案"

### 文章类型（12选1，每天轮转）

1. **面料成本拆解**：某品类服装的面料/辅料/加工费构成，采购报价格值不值
2. **拿货渠道分析**：线上线下各渠道的拿货优劣势，适合什么类型的采购
3. **面料卖点提炼**：从面料参数（克重/纱支/功能）提炼给客人看的产品话术
4. **趋势预判**：从原料行情预判下游服装哪个品类接下来会火或跌价
5. **质量鉴别**：教采购识别以次充好的面料（成分虚标/规格缩水）
6. **场景选品方案**：具体场景（电商/批发/私域）的面料组合推荐
7. **认证合规要求**：出口单/品牌单需要的GRS/Oeko-Tex/BSCI实际作用
8. **供应商筛选**：评估服装面料供应商的维度，怎么避坑
9. **退换货痛点**：面料问题引发的成衣售后纠纷案例分析
10. **爆款复盘**：拆解已跑通的爆款服装的面料方案和成本结构
11. **新品面料机会**：从新原料/新工艺发掘还没被充分竞争的品类
12. **换季交替机会**：季节切换时的面料替代方案，迎接新波段

### 标题风格
采购决策导向，带数字/对比/行动信号
示例："涤纶短纤三天涨5%，T恤品牌要不要提前锁价？成本传导时间线实测"
"瑜伽服面料成本拆解：锦纶氨纶+UPF50+防晒功能，一件成衣面料成本多少"

### 配图风格
电商挂拍/面料特写/服装打包场景/仓储货架
prompt示例：
"Stacked boxes of folded garments in logistics warehouse, professional photography, warm warehouse lighting"
"Fabric texture close-up showing weave pattern, natural light, white background, textile sample photography"

### 与其他类目的核心差异
- vs 坯布：坯布回答"这块布怎么织"，服装回答"这块布做成衣服好不好卖"
- vs 布行：布行关注"去哪拿货"，服装关注"拿了以后怎么跟客人解释、卖不卖得动"

---

## 共同要求（所有类目适用）

### 标题要求（硬性！）
- 坯布：35-60字
- 原料：40-60字
- 辅料：40-60字
- 布行：40-60字
- 服装：40-60字

### 输出格式（硬性！所有类目必须遵守）
**必须直接生成HTML内容字符串，不是Markdown，不是纯文本！**
- 用 `<h2>` 表示章节标题，如 `<h2>一、棉花系：成本支撑转强，拿货窗口在收窄</h2>`
- 用 `<p>` 包段落，如 `<p>正文内容</p>`
- 用 `<table><tr><td>...</td></tr></table>` 表示表格，禁止用Markdown表格格式
- 用 `<ul><li>` 表示列表，禁止用中文顿号或纯换行
- 图片用 `[插图]` 占位符标记插入位置
- **绝对禁止输出Markdown格式**（不能用 `#`、`##`、`|` 表格等Markdown语法）
## 写作事实核查底线（硬性！写完必查，错了永不原谅）

### 地理位置（绝对不能混）
- 南通在江苏，家纺/坯布产区
- 海宁在浙江嘉兴，经编氨纶重镇，两地无任何隶属关系，绝不能混写
- 长乐在广东佛山，经编产业集群
- 盛泽在江苏苏州吴江，化纤重镇
- 张槎在广东佛山，针织坯布基地

### 绝对禁止的写作态度
- 禁止丑化、贬低、嘲讽任何地区
- 写产业带对比要客观陈述差异，不能用"垃圾""淘汰""落后"等贬义词汇
- 质量差异要技术性描述（如"品质稳定性需实地验证"），不要地域黑

### 数据合理性
- 数字要符合常识（一件成人衬衫纽扣5-20颗，不是几百颗）
- 规格参数引用前先过一遍逻辑
- 价格要有区间感，明显离谱的数字不要写

### 发布绝对要求
- **无图片绝对不发布**：图片生成失败或下载失败，当前任务必须中止
- **图片必须独立成段，禁止内嵌段落中**：`[插图]` 标记必须在段落开头独立成行或独占一行，前后必须有空行隔断。绝对禁止在句子中间插入图片，否则必须拆分段落或移动图片到段首后再发布
- 探钱库APP插入≤2次，场景触发，不硬广
- 禁止引用其他平台
- 末尾评论引导从读者视角出发

### HTML排版规范（硬性！必须严格遵守）
**文章必须使用以下HTML标签结构，禁止平铺文字：**
- `<h2>` — 每个分析维度/章节用二级标题，长度10-20字，如 `<h2>一、棉花系成本支撑转强</h2>`
- `<p>` — 每段正文必须包在 `<p>` 中，禁止裸文字串联
- `<ul><li>` — 列表项用标准ul/li，禁止用中文顿号或换行冒充列表
- `<table>` — 表格必须用 `<table><tr><th>...</th></tr><tr><td>...</td></tr></table>`，禁止Markdown表格
- `<p>` 段落之间必须有换行分隔（HTML里是 `</p>\n<p>`）
- 禁止：大段文字（超过200字无小标题分割）、连续多行无 `<p>` 包裹的文字、所有内容堆在一个 `<div>` 里

**验证方法**：发布前用以下代码检查结构：
```python
import re
html = html_content  # 待发布HTML
# 0. 禁止Markdown格式（Markdown字符出现即中止）
md_chars = re.findall(r'#{1,6}\s|[*\-_]{3,}|^\|[^\n]+\|$', html, re.MULTILINE)
assert not md_chars, f"发现Markdown语法（{md_chars}），HTML拼接代码未生效，当前任务中止，禁止发布！"
# 1. 必须有<h2>标签
h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html)
assert len(h2s) >= 2, f"文章仅有{len(h2s)}个<h2>，少于2个，结构混乱，当前任务中止！"
# 2. <h2>之间必须有内容，不能连续<h2>无内容
# 3. 不能有大段裸文字（超过200字无<h2>分割）
segments = re.split(r'<h2[^>]*>.*?</h2>', html)
for seg in segments:
    seg_text = re.sub(r'<[^>]+>', '', seg)
    if len(seg_text.strip()) > 250:
        print(f"警告：发现{len(seg_text.strip())}字无小标题段落，建议拆分：{seg_text[:80]}...")
# 4. 图片已正确独立成段
assert 'data:image/jpeg;base64,' in html, "HTML中没有找到base64图片，当前任务必须中止，禁止发布！
```

### 图片压缩流程（硬性步骤，必须执行）
图片生成并下载后，**必须压缩再base64**，严禁直接使用原图（320KB原图base64后约430KB，嵌入HTML超500KB会导致API 500错误，LLM会因此删图硬发，绝对禁止！）。

使用ffmpeg压缩（JPEG质量1，宽1280，长边按比例）：
```python
import subprocess, os, base64

img_path = "/path/to/downloaded.jpg"  # 下载后的原图路径
compressed_path = img_path.replace(".jpg", "_compressed.jpg")

# 压缩：-q:v 1 (JPEG quality 1, 最低质量, 通常100-115KB)
# 注意：-q:v 2 在某些图片上仍超150KB，必须用 -q:v 1
result = subprocess.run(
    ["ffmpeg", "-i", img_path, "-q:v", "1", "-vf", "scale=1280:-1",
     "-y", compressed_path],
    capture_output=True, text=True, timeout=60
)
assert result.returncode == 0, f"图片压缩失败: {result.stderr}"

size = os.path.getsize(compressed_path)
assert size < 150 * 1024, f"压缩后仍{size//1024}KB，超过150KB，当前任务中止！"

# base64用压缩后的文件
b64 = base64.b64encode(open(compressed_path, "rb").read()).decode()
```
**验证**：压缩后文件必须 < 150KB，base64后约110KB，HTML总大小约300KB，安全。

**经验坑（2026-04-13验证）**：`-q:v 2` 在实际测试中 Produces ~160KB 仍超限，必须用 `-q:v 1` 才能稳定在108KB左右。

### 图片校验流程（硬性步骤，必须逐条执行）
1. MiniMax图片生成完成后，立即用 `urllib.request.urlopen()` 下载到本地 `~/.hermes/cron/output/images/`
2. **立即压缩**（质量85，宽1280）到150KB以下，验证通过才继续
3. 用压缩后的图片做 `base64.b64encode(open(compressed_path,'rb').read()).decode()`
4. **拼接HTML（图片必须独立成段，禁止内嵌段落中）**：
   - 替换方式：`content = content.replace('[插图]', f'<p style="text-align:center;margin:16px 0;"><img src="data:image/jpeg;base64,{b64}" style="max-width:100%;border-radius:8px;" /></p>')`
   - **关键约束**：`[插图]` 标记必须出现在**段落开头独立成行**，或独占一行。LLM写作时必须在 `[插图]` 前后保留空行，确保图片前后都有段落分隔。绝对禁止把 `[插图]` 放在句子中间或段落内部。
   - 如果 LLM 把 `[插图]` 放在了段落中间（如 `xxx[插图]xxx`），发布前必须将其拆分为 `xxx</p><p>...[插图]...</p><p>xxx` 或整体前移图片到段首
5. **发布前自检**（两项都必须通过）：
   ```python
   # 检查1：HTML中确实含有base64图片
   assert 'data:image/jpeg;base64,' in html_content, "HTML中没有找到base64图片，当前任务必须中止，禁止发布！"
   # 检查2：图片前后必须是段落分隔（不能内嵌在句子中间）
   import re
   # 匹配 <p>...</p> 中间有 <img 的情况（段落内嵌图 = 错误）
   bad嵌入式 = re.findall(r'<p[^>]*>[^<]*<img[^>]*>[^<]*</p>', html_content)
   assert not bad嵌入式, f"发现图片内嵌段落中的错误HTML（破坏段落完整性）：{bad嵌入式}，当前任务必须中止，禁止发布！"
   ```
6. 只有两项校验都通过才发API；任何一项失败立即中止，不发布

### 类目时段与文章类型强制分配表
同一类目相邻时段不得选同一类型，原料类12种类型必须逐日轮转。

| 类目 | 时段 | 指定文章类型编号 | 类型名称 |
|------|------|----------------|---------|
| 坯布 | 06:37 | 类型1 | 规格解读型 |
| 坯布 | 08:22 | 类型2 | 选型匹配型 |
| 坯布 | 10:45 | 类型3 | 工艺揭秘型 |
| 坯布 | 13:18 | 类型4 | 疵点识别型 |
| 坯布 | 15:43 | 类型5 | 认证合规型 |
| 坯布 | 17:58 | 类型6 | 产业带采购型 |
| 坯布 | 21:12 | 类型1 | 规格解读型 |
| 坯布 | 23:26 | 类型2 | 选型匹配型 |
| 原料 | 06:52 | 类型1 | B2B采购避坑与供应商筛选 |
| 原料 | 09:27 | 类型2 | 行情趋势与成本拆解 |
| 原料 | 11:33 | 类型3 | 高端料平替与降本 |
| 原料 | 14:08 | 类型4 | 原材料深度对标与极限PK |
| 原料 | 16:52 | 类型5 | 新品开发与营销卖点提炼 |
| 原料 | 19:15 | 类型6 | 前沿加工工艺与组织适配 |
| 原料 | 21:00 | 类型7 | 行业痛点与技术解决方案 |
| 原料 | 23:58 | 类型8 | 验货标准与物理指标揭秘 |
| 辅料 | 06:15 | 类型1 | 选型指南 |
| 辅料 | 08:08 | 类型2 | 验货标准 |
| 辅料 | 11:07 | 类型3 | 成本核算 |
| 辅料 | 13:47 | 类型4 | 问题解决 |
| 辅料 | 16:15 | 类型5 | 产业分析 |
| 辅料 | 18:43 | 类型6 | 行业揭秘 |
| 辅料 | 20:58 | 类型1 | 选型指南 |
| 辅料 | 22:33 | 类型2 | 验货标准 |
| 布行 | 06:25 | 类型1 | 拿货时机判断 |
| 布行 | 08:42 | 类型2 | 产业带横向比价 |
| 布行 | 10:58 | 类型3 | 供应商筛选与避坑 |
| 布行 | 13:35 | 类型4 | 调样与拿版实战 |
| 布行 | 15:12 | 类型5 | 价格波动传导分析 |
| 布行 | 17:28 | 类型6 | 新品与趋势捕捉 |
| 布行 | 19:45 | 类型7 | 库存与资金策略 |
| 布行 | 22:18 | 类型8 | 出口与跨境拿货 |
| 服装 | 06:33 | 类型1 | 面料成本拆解 |
| 服装 | 07:58 | 类型2 | 拿货渠道分析 |
| 服装 | 09:13 | 类型3 | 面料卖点提炼 |
| 服装 | 11:48 | 类型4 | 趋势预判 |
| 服装 | 14:33 | 类型5 | 质量鉴别 |
| 服装 | 16:07 | 类型6 | 场景选品方案 |
| 服装 | 18:55 | 类型7 | 认证合规要求 |
| 服装 | 21:37 | 类型8 | 供应商筛选 |

服装第9-12类型在第二天继续轮转（类型9→退换货痛点，类型10→爆款复盘，类型11→新品面料机会，类型12→换季交替机会），循环往复。

### 配图规范（通用）
- 16:9比例
- prompt用英文，纯视觉场景
- 禁止任何文字/标签/符号
- 插入位置：与内容高度相关处（非头尾）
- 必须下载到本地 `~/.hermes/cron/output/images/`，用base64发布

---

### MiniMax配图生成

```
POST https://api.minimax.chat/v1/image_generation
Authorization: Bearer sk-cp-OBJYTXCbg4PQS6gO0Col8fT_cEgZY2Ur_6qhB-bWDAqiuFkciSntwIM0U26E-8HrqoqNRbcp8sgdCksRsQTmSoe-PnltkGuNbsE6xxDByKB-Yqr2nNfWNik
```

```json
{
  "model": "image-01",
  "prompt": "英文描述，纯视觉，无文字无标签",
  "aspect_ratio": "16:9"
}
```

**注意**：`model` 必须用 `image-01`，`Pixart-Mega` 会返回 `status_code: 2013 unsupported model`。
超时120秒，图片下载到本地，必须保存到磁盘后用base64发布。

**图片URL是阿里云OSS临时链接**，外部平台无法直接显示。必须：
1. `urllib.request.urlopen(img_url)` 下载到本地
2. `base64.b64encode(read()).decode()` 转base64
3. 发布时 `<img src="data:image/jpeg;base64,{b64}" />` 嵌入HTML

### 本地图片兜底机制

当MiniMax API返回额度用尽错误（status_code=1004 "login fail" 或 quota相关错误）时，自动切换本地图片：

**本地图片目录**：`/home/tanqianku/hp/`
**已使用记录文件**：`/home/tanqianku/.hermes/cron/output/used_local_images.txt`

**兜底流程**：
```python
import os, random, subprocess, base64

LOCAL_IMG_DIR = "/home/tanqianku/hp"
USED_FILE = "/home/tanqianku/.hermes/cron/output/used_local_images.txt"

def get_local_fallback_image():
    """从本地相册随机选一张未使用过的图片，压缩后返回base64"""
    all_imgs = [f for f in os.listdir(LOCAL_IMG_DIR)
                if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    if not all_imgs:
        raise Exception("本地图片目录为空，当前任务中止")

    # 读取已使用记录，避免重复
    used = set()
    if os.path.exists(USED_FILE):
        with open(USED_FILE) as f:
            used = set(line.strip() for line in f if line.strip())

    # 找出未使用的图片
    unused = [f for f in all_imgs if f not in used]
    if not unused:
        # 全部用完后重置，重新开始轮循
        used.clear()
        unused = all_imgs

    chosen = random.choice(unused)

    # 记录本次使用
    with open(USED_FILE, "a") as f:
        f.write(chosen + "\n")

    src = os.path.join(LOCAL_IMG_DIR, chosen)
    compressed = src.rsplit('.', 1)[0] + '_compressed.jpg'

    # 压缩：宽1280，质量1（~100KB）
    result = subprocess.run(
        ["ffmpeg", "-i", src, "-q:v", "1", "-vf", "scale=1280:-1", "-y", compressed],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"本地图片压缩失败: {result.stderr}"

    size = os.path.getsize(compressed)
    assert size < 150 * 1024, f"兜底图片仍{size//1024}KB，超过150KB"

    return base64.b64encode(open(compressed, "rb").read()).decode()
```

**触发条件**：MiniMax API调用失败且错误信息包含以下任一关键词时触发兜底：
- `quota`
- `额度`
- `login fail`
- `invalid signature`（疑似额度问题）

**规则**：每天发布任务全用完后才重置used记录，保证同一张图片当天不重复。全部用完则从头轮循。

**禁止**：不可将兜底图片用于非紧急情况，必须先尝试MiniMax生成。

---

## 探钱库API发布（已验证可用）

### Endpoint
```
POST https://gw.tanqianku.com/_data_bus/v1/webhook/openclaw
```

### Auth
```
x-openclaw-secret: c9f65f23d9a87f41298a56c7b989a673d74ddc1fc92b196985e2b9fe06240548
```
**注意**：用 `x-openclaw-secret` 请求头，不是 `Authorization: Bearer`。用Python urllib发布，禁止curl（中文引号/特殊符号会导致500）。
2. base64编码本地图片文件
3. 拼`<img src="data:image/jpeg;base64,{b64}" />`插入HTML
4. POST用`urllib.request + ssl.create_default_context()`，禁止curl

### 已知坑
- 401错误 "密钥验证失败"：用的是Authorization头而非x-openclaw-secret请求头
- 直接用OSS临时URL发布图片不显示，必须下载到本地base64
- HTML含特殊字符（≥、℃、±、中文引号）时禁止curl，用Python urllib

---

## MiniMax配图补充说明（经验验证）

**API基础信息（2026-04-13验证）**
- Base URL: `https://api.minimax.chat/v1/image_generation`
- 可用模型: `image-01`（Pixart-Mega / MiniMax-Image-01 / image-00 均不支持）
- 鉴权: `Authorization: Bearer sk-cp-OBJYTXCbg4PQS6gO0Col8fT_cEgZY2Ur_6qhB-bWDAqiuFkciSntwIM0U26E-8HrqoqNRbcp8sgdCksRsQTmSoe-PnltkGuNbsE6xxDByKB-Yqr2nNfWNik`
- 超时: 建议90-120秒，简单prompt约15秒返回

**返回格式示例（成功）**
```json
{
  "id": "062b9f2983864b11b480983369e187fd",
  "data": {"image_urls": ["https://hailuo-image-...oss-cn-...jpeg?Expires=..."]},
  "base_resp": {"status_code": 0}
}
```

**返回格式示例（失败）**
```json
{"base_resp": {"status_code": 2013, "status_msg": "invalid params, unsupported model: Pixart-Mega"}}
{"base_resp": {"status_code": 1004, "status_msg": "login fail: Please carry the API secret key"}}
```

**关键坑：图片URL是阿里云OSS临时链接，有效期约2小时，必须下载到本地用base64嵌入HTML发布**

---

## 已知坑（经验沉淀）

1. **三类目独立写作**：坯布/原料/辅料风格必须完全不同，不共用模板
2. **写作必须读取当日trend**：10点采集完成后，所有文章写作时强制引用当日trend文件
3. **标题字数必须验证**：每个标题生成后数字数确认达标再发布
4. **探钱库APP插入≤2次**：场景触发，不硬广
5. **探钱库401错误**：确认用的是`x-openclaw-secret`请求头，而非`Authorization`头
6. **图片不显示**：OSS临时URL直接用不显示，必须本地下载base64后发布
7. **HTML特殊字符**：≥、℃、±、中文引号等会导致curl 500错误，用Python urllib
8. **Hermes路径**：实际路径是`/home/tanqianku/.hermes`，不是`~/.hermes`或`/root/.hermes`；cron输出在`/home/tanqianku/.hermes/cron/output/`，知识库在`/home/tanqianku/.hermes/cache/documents/`

9. **execute_code sandbox不保留变量**：不同execute_code调用之间，变量不保留。生成图片→下载→压缩→base64→构建HTML→发布API，必须全部在**同一个execute_code调用**中完成，切勿分多次调用（分次调用会导致后续调用找不到前面产生的变量，publish失败）。所有步骤从读取knowledge库到最终API发布，整条链路串成一个大脚本。

## Cronjobs 技术坑（经验总结）

### repeat 字段只能用 JSON 直接编辑修改
`cronjob action=update` 不支持更新 `repeat` 字段，会被忽略。
正确做法：用 Python 直接读写 `~/.hermes/cron/jobs.json`。
永久任务设置 `repeat: {"times": null, "completed": 0}`（即 forever）。

### deliver=local 会截断 prompt
用 `cronjob action=create` 创建任务时，如果 `deliver=local`，数据库会截断 prompt。
正确做法：创建任务后，用 Python 直接编辑 `jobs.json` 中的 `prompt` 字段，写入完整内容。

### 手动编辑 jobs.json 后要重建 schedule 字段
当直接写入 `schedule.expr` 字符串（如 `"0 10 * * *"`）时，`next_run_at` 仍为 null，任务不会触发。
必须在 Python 中调用以下两个函数重建：
```python
from cron.jobs import compute_next_run, parse_schedule
parsed = parse_schedule('0 10 * * *')
job['schedule'] = parsed
job['next_run_at'] = compute_next_run(parsed)
```

### repeat=0 等于任务跳过（不执行）
jobs.json 中 `repeat.times=0` 会导致调度器判定 `completed >= times` 为 true，直接跳过。
forever 任务必须 `repeat.times=null`。

### jobs.json 内部格式参考
```json
{
  "jobs": [{
    "id": "唯一ID",
    "name": "任务名",
    "schedule": {"kind": "cron", "expr": "0 10 * * *", "display": "0 10 * * *"},
    "next_run_at": "2026-04-14T10:00:00+08:00",
    "repeat": {"times": null, "completed": 0},
    "prompt": "完整prompt内容",
    "deliver": "local",
    "skills": []
  }]
}
```

### Hermes Gateway Telegram 断连后崩溃
根因：Telegram platform adapter 的 `handle_disconnect` 返回 `True`，导致 gateway 主循环退出。
修复：改为 `return False`，让后台 watcher 处理重连。

### GitHub 备份与跨机同步（经验沉淀）
**PAT 属于 hisentoken，不是 xiezuo**：创建仓库时必须用 PAT 对应的实际账户，否则 403 无权限。
当前已验证可用的备份仓库：`https://github.com/hisentoken/tanqianku-cron-sync`

**同步步骤**：
1. `git init` 初始化 `/home/tanqianku/.hermes`
2. 创建 `.gitignore`（排除 `__pycache__/`、`*.pyc`、`.env`、`cron/.tick.lock`）
3. `git add` 关键文件：`cron/jobs.json`、`skills/textile-*`、`cache/documents/`、`config.yaml`
4. `git commit`
5. **先通过 GitHub API 创建仓库**（`POST https://api.github.com/user/repos`），再用 PAT push
6. 如果 Org 无权限创建（403），说明 PAT 属于个人账户，不是 Org 成员

**已同步文件清单**：
- `cron/jobs.json` — 25个cron job
- `skills/textile-article-publishing/` — 写作skill
- `skills/textile-trend-collection/` — 采集skill
- `cache/documents/` — 三个知识库
- `config.yaml`
