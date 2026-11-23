# 拾词 · 私人单词书 Android App

用于 vivo 等 Android 8.0 及以上手机。词库只来自用户提供的书和用户自行导入的词表。应用没有广告、账号、云词库、统计 SDK 或联网权限。

## 安装与使用

1. 将 `output/shici-1.0.5.apk` 传到手机。
2. 在手机「文件管理」中打开 APK，按系统提示允许此次安装。
3. 打开「拾词」，点击「开始今日学习」。在「我的」调整每日新词数量。

不用将原 PDF 再复制到手机。书中页面图片和已生成的词卡已经打包在 APK 中。

功能：

- 按原书顺序学习英文词卡，翻面显示完整词条，包括释义、记忆方法、例句及扩展词。跨栏或跨页的续文会拼接在下方，点击词条图片可以放大。
- 「忘记 / 模糊 / 记得」安排复习；忘记的词本轮再次出现。
- 到期复习优先；新词每日默认 20 个，可改为 5–100 个。
- 搜索、收藏、中文提示拼写练习、词条修改、原书阅读和放大。
- 系统英语朗读。需手机已安装英语 TTS 语音；缺少语音包不影响其他学习功能。
- 从自己整理的 JSON、CSV、TSV 导入后续单词书的词表。
- 导出及恢复包含词表、进度、收藏和修改的 JSON 备份。

学习数据保存在应用私有存储中。卸载前请先导出备份。备份恢复会替换当前记录，应用会明确提示并确认。

## 本次词库与准确性

来源：用户提供的 `E:\26英语六级-你还在背单词吗--刘晓燕.pdf`，共 338 个 PDF 页面。它是图片扫描件，不含可直接提取的文字层。

当前版本生成 5,916 张词卡（核心部分 2,219 张、基础部分 3,697 张）；另外 1,372 条索引暂待整理。

识别全部在本机进行，未把书上传到识别服务。正文候选词与书后索引交叉匹配，词卡保留对应扫描截图和 PDF 页码。尚未可靠匹配的条目列在 `output/pending-entries.json`，没有加入日常学习。

这是扫描识别初版，未逐词人工校对；英文拼写和用于搜索、拼写练习的中文文本仍可能有 OCR 错误。日常翻卡优先显示扫描原文，用户可在词库点开单词后选择「修改词条」。修改只保存在本机，可随学习备份导出。

部分图示词、识别不完整的词形或释义被保留在待整理清单中。不要将当前词卡数视为整本书的完整词数。后续 PDF 暂不支持在手机内自动 OCR，需先整理成词表再导入。

原书页面图片裁除了底部的扫描上传者推广条；用户提供的 PDF 文件保持原样。

1.0.1 的完整词卡直接从原 PDF 取图，按编号和章节边界截取；扩展词使用所属核心词条的完整讲解。原书只列出释义的基础词，保留对应的完整释义段落。没有补写原书不存在的例句。

1.0.2 增加原书的 Unit → Lesson → 词以群记分类，覆盖 14 个 Unit、54 个 Lesson。词库可以组合章节、搜索和学习状态筛选，并按所选章节开启学习；每日新词上限仍按整本书累计，进度沿用原单词 ID。

章节标题与目录经过核对。原 PDF 存在缺页和合并书页，因此分类数量是当前已收录词卡数；Unit 5、Unit 9、Unit 10 的部分章节缺页，缺少标题的续页归入“词群待核对”。基础部分 Unit 11–14 按 Lesson 编排，没有另造词群。

## 1.0.6 词库更新（2026-11-20）

把桌面 `英语\` 下 18 篇「双轨版」讲义 md 的词条并入内置词书，以 md 文本为准：

- 966 条词条（去重 963）：731 条改写释义（原来 OCR 乱码换成讲义的词性、释义、拆字、画面、回锚、派生、例句），232 条为新增词，全书 5916 → 6148 词。
- 新增词没有原书截图（`card: null`），卡片按文字版显示；位置按桌面对应 lesson 的 unit/lesson 插入，学习顺序不乱。
- 合并脚本 `_pdftools/merge_book2.py`，以原始备份 `_pdftools/book-data.orig.js` 为基线重跑；`catalog(ue)`、`hono(u)r` 这类含括号的词按变体匹配，避免重复词条。
- 打包脚本 `_pdftools/build_staged.py`：`aapt2` 不接受含中文的路径，构建时先把 `app/src/main` 复制到 `%TEMP%\shici_build` 再打包。`tools/build_android.py` 在本机这个中文路径下会直接报 `failed to open directory`。
- 本机 `app/`、`build/`、`output/` 三个目录的属主是另一个 Windows 账户，沙箱进程无法写入；改词库、打包需在完全权限（full access）下运行。

## 1.0.7 去掉图片词书（2026-11-20）

- 内置词书只保留讲义里有的 963 条（Unit 1/3/4/6/7/8），`card` 全部置空，卡片按文字版显示。
- 删除了 `assets/cards/`（6235 张词卡截图）和 `assets/book/`（338 张原书页图）；「翻阅原书」入口和 `read` 动作一并移除。这两批图没有备份，只能靠原书 PDF 重新生成。
- APK 从 116.5 MB 降到 0.2 MB；章节保留 Unit → Lesson，「词以群记」（groups）清空后下拉不可用。
- 讲义覆盖不到的 Unit 2、5、9–14 没有词条，书架和筛选里会直接跳过。

## 1.0.9 词条卡改版（2026-11-20）

- 词条从一整段文本拆成结构化字段：phonetic 音标、pos 词性、gloss 核心释义、entry 拆字/画面/回锚/例句/派生条目；meaning 只留「词性 + 释义」，供词库列表和拼写自测用。
- 学习卡片重排：单词和喇叭同排 → 音标+词性小字 → 核心释义加粗放大 → 分块表格（左侧紫色标签、行间细分隔线）。整理备注（（注：…）、时间戳）已从卡片里去掉。
- 词库列表每行显示精简释义，不再被长文本截断；筛选标签改为换行排列，不再被裁掉「基础词」。
- 多词性释义用分号分开，如「专家，内行；adj. 内行的，专家的」。

## 1.0.10 自定义每日新词（2026-11-20）

- 「我的 → 每日新词」从固定下拉改成：可直接输入数字，配 −/＋ 按钮（每次 5 个）和 5/10/20/30/50/100 快捷标签。
- 范围 1–500（原来写死 5–100）。输入 0 或空会被纠正为 1，超过 500 会自动压到 500；设置会写进学习备份。
- 今日页「今日待学新词」= 目标 − 今天已学，复习词不受这个上限限制。

## 1.0.11 跟进讲义改版（2026-11-20）

- 新增 U1 Lesson 4（P5，50 词，emerge/emergency/urgent/haste…），内置书 963 → **1012 词**，Unit 1 现在有 4 个 Lesson。
- P2 改版：embassy、ordinary 从词条降为「记忆锚点」不再单列，所以词表里少这两条；P3 新增 proceed。
- 词条结构、卡片版式沿用 1.0.9；打包走 _pdftools/build_staged.py。

## 1.0.12 记忆锚点并入主词条（2026-11-20）

- 讲义里 > **记忆锚点** … 的引用块（progress、embassy、ordinary、face、pass、translate、success、process、scent、gene、home/homosexual）解析成词条的 锚点 块，跟在宿主词条后面显示，不再单列成卡。
- 锚点文本会去掉 （板面无词头…）、时间戳、反引号等整理痕迹，只留「单词 + 音标 + 词性 + 释义 + 怎么记」。
- 共 11 条锚点：aggressive→progress、ambassador→embassy、coordinate→ordinary、surface→face、surpass→pass、transcend→translate、succeed→success、procession→process、descent→scent、genre→gene、homogeneous→home/homosexual。

## 1.0.13 区分板面与口述（2026-11-20）

- 词条里每个记忆块按来源拆成多段：〔板面〕（PPT 上印的）标紫色「板面」，〔口述〕（她讲的）标橙色「口述」，〔整理〕 标灰色；一个块里两种来源都有时分行并列，不再合并成一句。
- 拆字这类块常见「口述一套 + 板面一套」，现在两套各自成行，能看出哪句是印刷内容、哪句是她的口头解释。
- 回锚、锚点这类没有来源标记的块，左侧留空占位，保证各行文字左对齐。
- 数据里 entry[].parts = [{s:'板面'|'口述'|'整理', v:'...'}]，渲染器 lockBody() 负责拼装。

## 1.0.15 跟进讲义第二轮改版（2026-11-20 19:35）

- 19 篇讲义再次改版：词条 1012 → **999**（新增 24、移除 37、126 条的讲解块改动），现在 999 条全部带音标。
- 新增来源标记 〔词表〕/〔词表·未讲〕 → 卡片上显示灰色「词表」；〔整理〕/〔推论〕/〔原文如此〕 → 「整理」；〔板面例句〕/〔板面·插播〕/〔板面/口述〕 归到「板面」。
- 占位内容（（无）、（无——她没讲）、（无——她没讲；词表 P27 段收有…））不再渲染；只剩占位的 20 个词显示「说明：词表收录，本课未讲」。
- 修掉词性重复：表头写 *v.*、释义行又写 i. 时，取更具体的 i.，不再出现「v. vi. 由…组成」。
- 解析结果与讲义标题数逐课核对一致（19 篇全部相等）。

## 1.0.16 手机端排版修复（2026-11-20）

- **状态栏压字**：Android 15+ 强制 edge-to-edge，旧的 getSystemWindowInsetTop() 在部分机型返回 0，WebView 没留出状态栏/导航栏高度。改成 API 30+ 用 insets.getInsets(WindowInsets.Type.systemBars() | displayCutout()) 再 setPadding，低版本仍走旧接口。
- **窄屏拥挤**：新增 @media (max-width:400px)，弹窗内边距 25→18、来源标签列 42→30、正文 14→13.5、释义 20→18、学习卡片内边距收窄；shici-1.0.16 在 340 CSS px 宽度下也能一行放下 12–14 个字，按钮不再被挤出屏幕。
- **弹窗高度**：max-height:min(86vh, calc(100dvh - 28px)) + overscroll-behavior:contain，避免被导航栏裁掉、滚动时穿透到页面。
- 词条数据未变（999 词）。

## 1.0.17 收紧记忆块留白（2026-11-20）

- .block 上下内边距 10→7px，来源分段之间 7→5px，拆字这类块后面不再拖出一段空白。
- 学习卡片展开后改成顶部对齐（.study-card.revealed{justify-content:flex-start;min-height:auto}）：以前短词条因为 justify-content:center 被竖直居中，上下各留一大片空白；现在卡片高度跟着内容走（如 instance 卡高 313px，底部余量 23px）。
- 词条数据未变（999 词）。

## 1.0.18 来源标签并入标签列（2026-11-20）

- 「口述／板面／词表／整理」不再做成正文里的药丸标签，而是竖排在原来「拆字 / 画面 / 派生」那一列里：块名在上、来源在下，正文统一从标签列右缘起排。
- 正文可用宽度从约 190px 提到 226px（340 CSS px 宽的机器上），拆字样例从 5 行降到 4 行；块之间留白同步收紧。
- 修掉一个 HTML 漏闭合导致的块嵌套 bug（回锚块会把派生块吞进去，派生文字被压成一列）。

## 1.0.19 学习页加「上一个」（2026-11-20）

- 学习卡片上方新增「← 上一个 / 回到当前 →」：往回调看本轮已经评过分的词，最远可回到本轮第一个；本轮还没评过分时按钮置灰。
- 回看是只读的：不写进度、不出现评分按钮，底部提示「回看中 · 不会改动学习进度」；「回到当前」直接跳回正在学的那张卡。
- 实现：session.back 记录已评分的词 id，peekPos 表示往回看了几个；
ate() 里压栈，goBack()/goForward() 负责切换，拼写自测模式不显示该按钮。

## 1.0.20 朗读文本清理（2026-11-20）

- 词条显示保留原书写法（odo(u)r、labo(u)r、catalog(ue)、dialog(ue)），但送进 TTS 前会去掉括号拼成 odour / labour / catalogue / dialogue——之前这 4 个词会被念成「odo u r」。
- 发音仍是系统 TTS：Locale.US、语速 0.82，音质取决于手机装的英文语音包；音标是英式，所以个别词（schedule 等）会有英美差异。

## 1.0.21 词库排序与分页（2026-11-20）

- 词条顺序改成跟讲义一致（order 用讲义里的出现顺序，而不是原书 OCR 位置），U8L3 现在是 rim → grim → trim → mow → clip → …，和 P35 完全对上。
- 选中单元/课程后一次列出该范围的全部词（原来固定每页 60 条，U8L3 的 72 个词只显示 60，看着像少了 12 个）；「再看 N 个单词」改成显示真实剩余数量；列表表头「按原书顺序」改为「按讲义顺序」。

## 1.0.22 彻底去掉扫描书（2026-11-20）

- 数据只认两个来源：六级词汇.pdf（377 页文字版词表）+ 桌面讲义 md（视频课讲解）。扫描件 E:英语六级-你还在背单词吗--刘晓燕.pdf（315 MB）已删除。
- 代码里与扫描书相关的东西全部移除：openReader/
enderReader（原书阅读）、查看原书上下文、放大词条图、w.card/page/printedPage/cardRegions/ullEntry 字段，以及「按原书核对词条」标题；词库列表与词条出处不再出现「PDF 第 X 页」。
- 词条出处只显示 Unit X · Lesson Y；book-data 顶层也去掉了 pageCount / source / cardFormat / pendingCount / indexedCount。

## 1.0.23 全量自查与补课（2026-11-20）

- 补上漏同步的 4 课：U8 Lesson4（P36）、U9 Lesson1/2/3（P37–P39），词条 999 → **1307**，章节新增 Unit 8 Lesson 4 与整个 Unit 9。
- 页脚写死的「拾词 1.0.10」改成「拾词 · 只收录你的词书」；词库副标题改为「每个词都标了 Unit / Lesson」。
- 删掉没有意义的「核心词 / 基础词」筛选（这本书没有基础部分，所有词 section 都是 core）。
- 数据自查：999 → 1307 条 id 唯一、无空释义、无「pos 在释义里重复」、无异常词形、20 条「词表收录未讲」标注正常。
- 讲义文件名有两处与实际标题不符（不影响 App）：U6L2_P25 实际是 U6 Lesson 1-2，U6L2_P26 实际是 U6 Lesson 2-1。

## 1.0.24 同步第三轮讲义（2026-11-20 23:42）

- 新增 U9 Lesson4（P40，81 词）；另外 P2、P4、P5、P16、P25、P26、P35 七篇有改动，127 条讲解块更新、2 条释义变化。
- 词条 1307 → **1388**，Unit 9 现在 4 课共 314 词。

## 1.0.27 App 内更新（2026-11-21）

- 新增「我的 → 检查更新」：拉 https://raw.githubusercontent.com/doropig10/shici/main/version.json（失败自动换 jsDelivr），版本更高时弹「下载并安装」，下载完调系统安装器覆盖安装，学习记录保留。
- APK 主地址走 GitHub Release，失败换 jsDelivr CDN；下载后校验 SHA-256 再安装。新增 INTERNET、REQUEST_INSTALL_PACKAGES 权限（首次装会要求允许「安装未知应用」）。
- 发布脚本 _pdftools/release.py <版本> <versionCode> 说明：打包后把 APK 与 version.json 推到 doropig10/shici（公开仓库），并建 Release。
- 设置页文案同步改成「只有检查更新会联网」。

## 1.0.30 更新源定稿（2026-11-21）

- 检查更新主地址：https://github.com/doropig10/shici/releases/latest/download/version.json（Release 资产，永远是最新、无 CDN 缓存、不占 API 限流）；失败依次回退 raw.githubusercontent 与 jsDelivr。
- APK 主地址走 GitHub Release 资产，失败换 jsDelivr CDN；下载完校验 SHA-256。
- 发布：python _pdftools/release.py <版本> <versionCode> 说明，会自动打包、推仓库、建 Release（含 APK 与 version.json）。

## 1.0.32 发音音色（2026-11-21）

- 「我的 → 发音音色」列出手机语音引擎里所有英文音色，显示「女声/男声 + 本地/需联网」，可切换并记住（SharedPreferences）。
- 默认自动挑质量最高的本地音色（非网络优先），比原来用引擎默认音色更自然；想更像真人可手动切「需联网」音色。
- 和 vivo 翻译机的差别：翻译机用 vivo 自家云端语音，第三方 App 调不到；这里只能用它注册给系统的 TTS 音色。

## 1.0.33 词条标记（2026-11-21）

- 词库点开词条后可以标「重点」或「待核对」，再点一次取消；标记存在 state.marks，随学习备份一起导出/恢复。
- 词库列表里被标记的词显示彩色小标签（重点=紫、待核对=红）；筛选条新增「标记」分类，只看被标记的词。

## 1.0.34 标记写原因 + 导出（2026-11-21）

- 标记后词条弹窗出现「标记原因（可选）」输入框，写「释义存疑 / 例句看不懂 / 重点词」之类，点「保存原因」存进 state.marks[k].n。
- 「我的 → 导出标记」把标记导成 CSV（UTF-8 BOM，Excel 直接打开）：单词、Unit、Lesson、标记、原因、释义；手机上走系统「保存文件」，浏览器预览走下载。
- 数据结构兼容：老版本把 marks 存成字符串，读取时自动当成 {t:...}。

## 1.0.36 同步 39 篇讲义（2026-11-21 23:43）

- 讲义从 24 篇涨到 **39 篇**，新增 Unit 2、3、4、5、8 的多课；词条 1388 → **2451**，Unit 1–9 全覆盖。
- 其中 889 条释义、472 条讲解块有更新，新增 1063 词。
- 修掉两处重复 id（labo(u)r、catalog(ue) 在讲义里出现两次）：构建时按 id 去重，2453 → 2451。

## 1.0.37 同步小改（2026-11-22 10:00）

- 39 篇讲义再次改动：词条数不变（2451），释义变化 2 条（coalition、bold），讲解块变化 44 条（brilliant、embed、alert、reward、swamp、suspicious…）。
- 变更清单见 _pdftools/变更清单.md（脚本 _pdftools/diff_snapshots.py，快照存 _pdftools/snapshots/）。
- 本次发布时 git push 被网络重置，改用 _pdftools/release_api.py（GitHub API 建 Release + 更新仓库文件）；
elease.py 现在会自动检测 git 不可用并回退到 API。

## 1.0.38 词库显示学习记录（2026-11-23）

- 每次评价（记得/模糊/忘记）在 progress 里累计计数 
:{g,h,a}、记录 last，并保存 undo（上一次状态）。
- 词库列表行显示上次评价标签（记得=绿、模糊=黄、忘记=红）；词条弹窗新增「学习记录」：阶段、上次日期、上次评价、三类次数，以及「撤销上一次」「清除该词记录」。
- 清除会删掉该词的 progress 与 history 记录，词条回到「未学」；撤销则恢复上一次评价前的状态。

## 1.0.39 评价筛选并列（2026-11-23）

- 词库筛选条在「全部 / 未学 / 已学 / 收藏 / 标记」后新增 **记得 / 模糊 / 忘记** 三个分类，按 progress.last 过滤；列表行同时显示上次评价的小标签。

## 1.0.40 新增 Gitee 源（2026-11-23）

- 更新源顺序：**Gitee 优先**（https://gitee.com/doro_pig/shici/raw/master/version.json）→ GitHub latest/download → raw.githubusercontent → jsDelivr；四个源都拉、按 versionCode 取最大。
- APK 下载依次尝试：Gitee raw → GitHub Release 资产 → jsDelivr CDN，下载后校验 SHA-256。
- 发布脚本 _pdftools/release_both.py <版本> <code> 说明：同时推 Gitee（git push master）与 GitHub（Release + 仓库文件），version.json 三处一致。

## 导入词表格式

1.0.5 针对真机报告的 READ 错误，原生备用读取改为优先从当前 APK 的 ZIP 条目完整读取图片，再用 decodeByteArray 解码；失败时回退 AssetManager。打包时对图片启用标准 ZIP 压缩，避免只使用未压缩资源的读取路径。构建会逐张核对已签名包中的图片字节与源文件，并检查 ZIP 完整性。错误码进一步区分 APK_READ、IMAGE_DECODE 和 IMAGE_ENCODE。仍需用户 vivo 真机验证，不能把电脑模拟测试视为故障已经解决。

1.0.4 针对 1.0.3 在用户 vivo 上仍出现的破图增加原生图片备用读取：WebView 图片失败后，Android 在后台读取对应打包图片并转换成 PNG 内嵌显示；大图限制解码尺寸，单线程处理、队列有上限，不缓存整本书。失败时显示错误码。强制阻断普通图片请求的回归测试已覆盖 terror 词条、放大、原书页、过期回调、文件缺失和路径检查；原生代码已编译，实际 vivo 效果仍需覆盖安装确认。

1.0.3 修正安卓离线图片加载：从固定的 `file:///android_asset/index.html` 加载打包界面，图片由 WebView 直接读取 APK 内资源，避免虚拟 HTTPS 图片地址受无联网权限限制。仍禁用普通文件访问、跨文件脚本访问和网络访问；学习记录继续使用原 SharedPreferences。已通过文件来源的离线图片、放大和原书阅读测试；vivo 真机显示需安装后确认。

UTF-8 CSV（含逗号的字段要使用 CSV 双引号）：

```csv
word,meaning
eminent,杰出的；有名的
prominent,突出的；重要的
```

JSON：

```json
{"title":"我的单词书","words":[{"word":"eminent","meaning":"杰出的；有名的"}]}
```

每条词目必须提供单词和释义。重复词形在同一导入词表内去重。应用不会自动查询外部词典补全内容。

## 验证范围

- 2026-10-07：已在用户 vivo X100s / Android 16 上覆盖安装 1.0.5，确认原先 READ 报错消失；aggressive、terror 完整词条、点图放大及原书第 10 页均正常显示。学习进度保留。详细证据见 `output/phone-verification-1.0.5.md`。

- 核心测试：复习间隔、遗忘重排、每日新词上限、多书进度隔离、CSV 引号与去重、备份校验、书中英美变体拼写、词卡资源与出处。
- 手机尺寸的界面流程测试：学习、重开进度、搜索、收藏、修改、原书阅读及放大、导入、拼写、备份导出和恢复、小屏布局。
- Android Java 编译、资源打包、APK 对齐、v2/v3 签名验证、Manifest 权限检查。
- 已完成上述真机图片验证；系统英语语音包等未覆盖功能仍以实际手机为准。

## 项目结构

- `app/src/main/java/`：Android 容器、离线资源加载、私有存储、系统文件选择、英语朗读。
- `app/src/main/assets/`：手机界面、复习逻辑、词库与书页截图。
- `tools/prepare_book.py`、`tools/ocr.ps1`、`tools/extract_words.py`：本机扫描书处理流程。
- `tools/group_words.py`、`tools/book-structure.json`：按核对后的目录和词群标题补充章节元数据，重新提取词库后运行。
- `tools/expand_cards.py`：从原 PDF 按完整词条边界重新截取，拼接跨栏和跨页的续文。重新运行 `extract_words.py` 后应运行此脚本。
- `tools/setup_android.py`：从 Google 官方下载并校验构建工具。
- `tools/build_android.py`：不用 Gradle 的可重复 APK 构建。
- `tests/`：核心与界面测试。
- `output/`：安装包、SHA-256、待整理清单和界面截图。

签名密钥位于 `.tooling/shici-release.jks`，配置位于 `.tooling/signing.json`。后续更新请保留这两份文件并提高 Manifest 的版本号，使用同一签名才能覆盖安装并保留学习数据。

构建使用当前电脑已有的 JDK（PyCharm JBR），以及项目内下载的 Android 35 工具。更换电脑时需修改 `tools/build_android.py` 中的 JDK 路径。

## 开发命令

```powershell
node --test tests/core.test.cjs tests/full-entry.test.cjs tests/chapters.test.cjs
# 先在本机 8765 端口启动 assets 目录的 HTTP 服务，再运行：
node tests/ui.test.cjs
node tests/chapters-ui.test.cjs
# 使用含 pypdf、Pillow 的 Python：
python tools/build_android.py
```
