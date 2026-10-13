# 项目数据契约与脚本

`build_indexes.py SOURCE_DIR OUTPUT_DIR [--html REPORT]` 使用 Python 标准库。输出反向推荐、名单差异和校验摘要；不更改原稿或源文件。

沿用当前项目的文件名以便直接调用：
- `selected.json`: 数组，至少 `{id,name,units}`；可包含 tier,econ,builds,special。
- `海克斯推荐与依据.json`: 数组 `{id,name,recommendations:[{apiName,name,rarity,rounds,guide,reason,condition,...}]}`。rarity 为 Silver/Gold/Prismatic；无法确认阶位时使用 Unknown，不猜测。同名但不同apiName的变体不可合并。
- `前期过渡路线与证据.json`: `{routes:[{title,opener,targets:[{id,name,level4_sample_count}],...}]}`。
- 可选 `核心棋子与人口换人对照.json`: 数组 `{id,variants:[{level,units,samples}]}`；按level排序后计算相邻差异和交集。

原始数据仍需另存。脚本检查结构与关系一致性，不验证来源正确、阵容版本或游戏机制。HTML校验仅检查静态ID/锚点；不替代交互测试。

例：
```sh
python3 scripts/build_indexes.py /path/to/source /tmp/metatft-derived --html /path/to/guide.html
```

技能资产示例的来源快照未打包；不要以缺少来源链接为由发明原始统计。

## 神器索引

`build_artifact_index.py SOURCE_DIR OUTPUT_DIR` 读取 selected.json、zh.json 和各阵容ID.json。输出按神器、棋子组织的索引及完整记录。筛选参数与证据解释见 [artifacts.md](artifacts.md)。

全量模式输出：`海克斯全池逐阵容审计.json`、`海克斯攻略全部出现记录.json`、`全量过渡路线与证据.json`、`神器未返回携带者.json`、`全部转职阵容记录.json`、`完整性审计.json`。同名海克斯按 apiName 建主键，展示名加变体标记。
