# TFT 中文对局手册

基于 MetaTFT **18.4b** 快照整理的中文交互攻略，覆盖既定 **21套强势阵容**。阵容数据快照为2026-10-12，装备核对为2026-10-13。它是版本手册，不会自动更新实时榜单，也不将TFT数据直接等同于金铲铲国服。

## 使用页面

下载仓库（Code → Download ZIP）并解压，用Chrome、Edge或Safari打开 **[index.html](index.html)**。保留整个目录，即可使用来源链接；筛选和装备补全在本地浏览器中运行，不需要账户或安装依赖。GitHub文件预览不会运行网页交互。

- [对局助手](assistant.html)：固定等级栏、棋子/转职/海克斯标签、当前过渡/升级补牌双视图，浏览器本地保存选择。
- [正式手册](index.html)：第一章版本与装备泛用性；第二章选阵与过渡筛选；第三章21套阵容详细攻略。
- [装备速查](equipment.html)：按阵容、棋子查看S/A单件装备、三件套和已有装备补全。
- 正文可折叠区域默认收起，左侧章节和阵容索引常驻。

页面与数据也可原样放到支持静态文件的Web服务。仓库首页为`index.html`；本次仅上传仓库，未配置GitHub Pages发布。

## 功能与口径

- 装备分物理与法系，保留主C、主坦、目标星级、运营节奏、换人与核心棋子。
- 当前等级的过渡组合与未来潜在终局分开展示；更换等级保留已有棋子选择。
- 海克斯只列指定阵容推荐条目；神器与转职单列适用条件。
- S/A为棋子层面的装备评级，不冒充特定阵容独立统计。单件与三件套评级分开，S为橙色、A为青色，表格同级按均名升序。
- 装备频次按不同推荐组合统计，不按对局样本加权。泛用性比较覆盖阵容、携带棋子和去重组合数。
- 配装优先主C和主坦，再分副C、副坦。核心候选的频次阈值是整理规则；带转职分支独立核对，无评级记录时不补造。
- 已有装备选择器只列S/A完整组合中出现的装备，支持重复件数，展示缺件和完整组合。

## Skill

Skill源码：[skills/metatft-guide/SKILL.md](skills/metatft-guide/SKILL.md)。

安装包：[downloads/metatft-guide-skill.zip](downloads/metatft-guide-skill.zip)。解压后将`metatft-guide`目录放入你的Codex用户技能目录（通常为`~/.codex/skills/`），新开会话后使用。若已安装同名Skill，请先备份旧版本。

Skill内附历史页面设计样例和数据验证脚本。样例不是实时数据，也不附带本仓库外的原始来源；历史补丁脚本不作为重新生成页面的入口。

## 文件结构

```text
index.html                  正式手册
assistant.html             独立对局助手
equipment.html             装备速查
data/comps/                阵容原始响应与整理记录
data/equipment/            装备原始响应、评级与分析记录
skills/metatft-guide/      可维护的Skill源码
downloads/                 Skill安装包
scripts/validate_release.py 发布文件检查
```

原开发目录中的试用文件、旧布局、临时脚本、历史备份不进入仓库。来源数据保留以便核查；其中原始统计记录不代表所有条目都被推荐。

## 检查

```bash
python3 scripts/validate_release.py
```

数据来源：[MetaTFT](https://www.metatft.com/comps)。网页中的分析、职责划分及运营建议与网站原始统计分别标明；第三方名称、素材及数据权利归其各自权利人。
