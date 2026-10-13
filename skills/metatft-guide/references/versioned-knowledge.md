# 按版本重新构建知识库

每次补丁或赛季变化，完整获取指定平台榜单，按当期来源评级重新选择全部 S/A。不能沿用上版固定21套。退出集合的阵容留在历史快照，新晋阵容必须获取详情后进入所有索引。相同补丁重新抓取也创建新时间戳，不覆写旧发布。

## 可复用流水线

将 `assets/version-pipeline/scripts/knowledge/` 和 `assets/version-pipeline/templates/` 复制到目标项目相同相对路径。Python 3 标准库负责抓取、归一化、生成；Node 负责逻辑回归检查。

```sh
python3 scripts/knowledge/refresh.py
```

默认只抓取、校验并生成 对应平台版本的 `snapshots/时间戳/pages/` 预览。指定已有快照发布：

```sh
python3 scripts/knowledge/refresh.py --snapshot games/jcc/set18/PATCH/snapshots/TIMESTAMP/data --publish
node scripts/knowledge/test_engine.cjs
```

`--publish` 更新本地主页面及版本目录，不会自动 git push 或部署。仅在用户已授权发布时推送。平台先分开，再按赛季、补丁、时间戳组织页面与数据。历史页面保留，旧链接仅跳转；全新项目应按实际历史资产调整历史链接，不伪造不存在的历史版本。

## 数据分层与验证

- `raw/` 保存完整接口返回，manifest记录请求URL、时间、SHA256、失败项、来源限制。
- `knowledge.json` 统一棋子、装备、职责、星级、条件、分等级棋盘、强化与神器关联；键包括平台、赛季、补丁、阵容ID。
- `games/{platform}/set{N}/{patch}/snapshots/{timestamp}/pages/` 固化页面，同快照的 `data/` 保存证据；`games/{platform}/releases.json` 分别指向各平台当前快照。根目录仅放平台选择与兼容入口。
- 页面、筛选器、反向索引及装备补全从同一个当期知识库生成。不得把TFT统计填进金铲铲空缺。
- 校验S/A集合与完整榜单一致、请求全部成功、原始哈希正确、棋盘不含不可购买单位、索引无越界、三件套多重集合匹配。出错停止发布，不用旧数据补齐。
- 同平台、同赛季前后补丁按稳定ID及棋盘/主C/星级/入场条件比较；定义变化不计算可比差值。低样本明确标记。不同时间窗与段位未知时不能把变化说成补丁的因果效果。
- 物理/法系、运营节奏、装备频率只描述当期选中集合；来源使用统计、来源推荐、S/A评级和自行推定分开显示。

## 金铲铲来源适配器（2026-10-13核验）

非官方来源 `https://www.dataj.cc`，公开API前缀 `/api/web`。每次先确认接口仍有效、补丁和赛季正确；不可将内部catalog的season/version标签直接当平台版本。

- `/gamedata/gameVersion?setId=...`：版本列表；按开始时间选择当前及前一补丁。
- `/comp/rank?setId=...&gameVersion=...&minSample=1`：来源完整返回榜单；筛选S/A。
- `/comp/{id}` 及 `/heroes`、`/equips`、`/hexes`、`/recommended-hexes`、`/battle-builds`：均携带赛季和版本参数。
- `/comp/{id}/hero-equips?setId=...&gameVersion=...&heroId=...`：每名可购买棋子单件及三件套统计。
- `/gamedata?setId=...`：中文词库；不支持历史补丁参数，不能用于历史技能数值比较。

已验证限制：每级棋盘通常仅3组，增加limit未扩大；三件套存在200条上限；推荐强化最多10项。保存全部返回记录并展示限制，不能声称穷尽游戏内组合。来源未公开段位、模式筛选和统计时间窗时留空，不能填默认假值。未知装备ID归档并报告，不能作为推荐选项。

若S/A三件套稀少：保留实际评级，另外提供来源推荐三件套作为明确命名的独立选项，不能把C/D或无评级的推荐出装升级成S/A。装备泛用频率可改用来源推荐出装件数，并说明计数口径。神器只显示有携带关联的记录；使用记录不等于推荐评级。
