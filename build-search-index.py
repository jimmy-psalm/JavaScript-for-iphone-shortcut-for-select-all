#!/usr/bin/env python3
"""Build cleaned SEARCH_INDEX and write audit notes."""
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path("/tmp/Psalm-upload")

def load_js_export(path, expr, outfile):
    src = Path(path).read_text(encoding="utf-8")
    Path("/tmp/_dump.js").write_text("var window={};\n" + src + f"\nconst fs=require('fs');\nfs.writeFileSync({json.dumps(outfile)}, JSON.stringify({expr}));\n", encoding="utf-8")
    subprocess.check_call(["node", "/tmp/_dump.js"])
    return json.loads(Path(outfile).read_text(encoding="utf-8"))

complete = load_js_export(ROOT / "psalm_data_complete.js", "PSALM_DATA", "/tmp/complete.json")
app = load_js_export(ROOT / "psalm-data-17.js", "window.PSALM_APP_DATA", "/tmp/app.json")

GENRE = {
    "讚美詩": [8, 19, 29, 33, 100, 103, 104, 111, 113, 114, 117, 135, 136, 145, 146, 147, 148, 149, 150],
    "雅威為王詩": [47, 93, 96, 97, 98, 99],
    "錫安之歌": [46, 48, 76, 84, 87, 122],
    "個人哀歌": [5, 6, 7, 13, 17, 22, 25, 26, 28, 31, 35, 36, 38, 39, 42, 43, 51, 54, 55, 56, 57, 59, 61, 63, 64, 69, 70, 71, 86, 88, 102, 109, 120, 130, 140, 141, 142, 143],
    "群體哀歌": [12, 44, 58, 60, 74, 77, 79, 80, 82, 83, 85, 90, 94, 106, 108, 123, 126, 137],
    "個人信靠詩": [3, 4, 11, 16, 23, 27, 62, 121, 131],
    "群體信靠詩": [115, 125, 129],
    "個人感恩詩": [9, 10, 30, 32, 34, 40, 41, 92, 107, 116, 138],
    "群體感恩詩": [65, 66, 67, 68, 118, 124],
    "君王詩": [2, 18, 20, 21, 45, 72, 89, 101, 110, 132, 144],
    "智慧詩": [1, 37, 49, 73, 91, 112, 119, 127, 128, 133, 139],
    "歷史詩": [78, 105],
    "先知勸告詩": [14, 50, 52, 53, 75, 81, 95],
    "禮儀詩": [15, 24, 134],
    "懺悔詩": [6, 32, 38, 51, 102, 130, 143],
    "詛咒詩": [5, 10, 12, 17, 35, 52, 58, 59, 69, 70, 79, 83, 94, 109, 137, 139, 140],
}
ACROSTIC = [9, 10, 25, 34, 37, 111, 112, 119, 145]
ASCENT = list(range(120, 135))
MIKTAM = [16, 56, 57, 58, 59, 60]
MASSAH_OK = {78, 81, 95, 106}
SOLOMON_OK = {72, 127}
ASAPH = [50] + list(range(73, 84))
KORAH = [42, 44, 45, 46, 47, 48, 49, 84, 85, 87, 88]

PRIMARY_GENRE = {}
for name, nums in GENRE.items():
    if name in ("懺悔詩", "詛咒詩"):
        continue
    for n in nums:
        PRIMARY_GENRE[n] = name

MOOD_RULES = [
    ("恐懼／受敵", ["敵人", "受敵", "攻擊", "追殺", "恐懼", "害怕", "仇敵", "圍困", "爭戰"]),
    ("被背叛／被誣", ["背叛", "誣", "冤枉", "毀謗", "讒", "誣告", "朋友"]),
    ("夜間／失眠", ["夜", "睡", "失眠", "躺"]),
    ("清晨", ["清晨", "早晨"]),
    ("悔罪／病痛", ["罪", "悔", "病", "痛苦", "懺悔", "疾病"]),
    ("感恩／稱謝", ["感恩", "稱謝", "得救", "拯救後", "經歷了神"]),
    ("讚美／敬拜", ["讚美", "敬拜", "頌讚", "哈利路"]),
    ("憂悶／傷心", ["憂悶", "傷心", "憂鬱", "眼淚", "哀傷", "絕望"]),
    ("等候／信靠", ["等候", "信靠", "投靠", "倚靠", "安穩"]),
    ("年老", ["年老", "老年", "髮白"]),
    ("被擄／異鄉", ["被擄", "異鄉", "流亡", "遠離"]),
    ("不公／惡人亨通", ["惡人亨通", "不公", "困惑", "義人受苦"]),
    ("朝聖／聖殿", ["聖殿", "朝聖", "錫安", "帳幕", "聖所"]),
    ("平安／休息", ["平安", "休息", "安歇", "安然"]),
    ("方向／抉擇", ["方向", "道路", "選擇", "人生"]),
]

def moods_for(text):
    text = text or ""
    hits = [name for name, keys in MOOD_RULES if any(k in text for k in keys)]
    return hits or ["等候／信靠"]

# --- build cleaned guide labels ---
raw_psalms = {}
for p in complete["psalms"]:
    n = int("".join(c for c in str(p["id"]) if c.isdigit()))
    slots = defaultdict(list)
    for guide, items in (p.get("categories") or {}).items():
        for item in items or []:
            cat, tag = item.get("category"), item.get("tag")
            if not cat or not tag:
                continue
            # unify names
            if tag in ("字母詩結構", "不完全字母"):
                tag = "字母詩"
                cat = "結構特徵"
            if tag == "字母詩" and cat == "詩歌類型":
                cat = "結構特徵"
            if tag == "被擄歸回後":
                tag = "歸回後"
            if tag == "咒詰詩":
                tag = "咒詛詩"
            if tag == "瑪撒" and n not in MASSAH_OK:
                continue
            if cat == "作者/群體" and tag == "所羅門" and n not in SOLOMON_OK:
                continue
            slots[(guide, cat)].append(tag)
    # force acrostic on structure
    if n in ACROSTIC:
        struct = slots[("文學", "結構特徵")]
        if "字母詩" not in struct:
            struct.append("字母詩")
    # genre slot: never 字母詩; fix 金詩
    types = slots[("文學", "詩歌類型")]
    types[:] = [t for t in types if t not in (
        "字母詩", "字母詩結構", "上行之詩", "金詩", "哈利路亞詩", "埃及頌讚"
    )]
    if not types and PRIMARY_GENRE.get(n):
        types.append(PRIMARY_GENRE[n])
    if n in GENRE["懺悔詩"] and "懺悔詩" not in types:
        types.append("懺悔詩")
    if n in MASSAH_OK:
        events = slots[("歷史", "歷史事件")]
        if "瑪撒" not in events:
            events.append("瑪撒")
    # unique preserve order
    for k in list(slots):
        seen = []
        for t in slots[k]:
            if t not in seen:
                seen.append(t)
        slots[k] = seen
    raw_psalms[n] = {f"{g}|{c}": tags for (g, c), tags in slots.items()}

# taxonomy cleaned
tax = json.loads(json.dumps(complete["taxonomy"]))
for drop_type in ("字母詩", "金詩", "上行之詩", "哈利路亞詩", "埃及頌讚"):
    if drop_type in tax["文學"]["詩歌類型"]:
        tax["文學"]["詩歌類型"].remove(drop_type)
if "咒詰詩" in tax["文學"]["詩歌類型"]:
    tax["文學"]["詩歌類型"].remove("咒詰詩")
    if "咒詛詩" not in tax["文學"]["詩歌類型"]:
        tax["文學"]["詩歌類型"].append("咒詛詩")
if "懺悔詩" not in tax["文學"]["詩歌類型"]:
    tax["文學"]["詩歌類型"].append("懺悔詩")
for drop in ("字母詩結構", "不完全字母"):
    if drop in tax["文學"]["結構特徵"]:
        tax["文學"]["結構特徵"].remove(drop)
if "字母詩" not in tax["文學"]["結構特徵"]:
    tax["文學"]["結構特徵"].insert(0, "字母詩")
if "歸回後" not in tax["歷史"]["歷史時期"]:
    tax["歷史"]["歷史時期"].append("歸回後")
if "被擄歸回後" in tax["歷史"]["歷史時期"]:
    tax["歷史"]["歷史時期"].remove("被擄歸回後")

# collect used tags
used = defaultdict(set)
for n, slots in raw_psalms.items():
    for key, tags in slots.items():
        g, c = key.split("|", 1)
        for t in tags:
            used[(g, c)].add(t)

guide_categories = {}
for g, cats in tax.items():
    for c, tags in cats.items():
        keep = [t for t in tags if t in used[(g, c)]]
        extra = sorted(used[(g, c)] - set(keep))
        guide_categories[c] = {"group": g, "tags": keep + extra}

guide_psalms = {}
for n in range(1, 151):
    labels = defaultdict(list)
    for key, tags in raw_psalms.get(n, {}).items():
        _, c = key.split("|", 1)
        for t in tags:
            if t not in labels[c]:
                labels[c].append(t)
    guide_psalms[str(n)] = dict(labels)

def invert(mapping):
    out = defaultdict(list)
    for name, nums in mapping.items():
        for n in nums:
            out[name].append(n)
    return {k: sorted(set(v)) for k, v in out.items()}

genre_psalms = invert(GENRE)
# add 字母詩 as structure-only in genre facet? No - 文體 facet is Gunkel; 字母詩 is in 綜合 結構 and also add to 傳統? 
# User wanted 字母詩 under 結構 in 綜合導讀. Also add 字母詩 to 傳統 as 字母體? I'll put 字母詩 in 傳統 as well as a collection feature.

tradition = {
    "卷一（1–41）": list(range(1, 42)),
    "卷二（42–72）": list(range(42, 73)),
    "卷三（73–89）": list(range(73, 90)),
    "卷四（90–106）": list(range(90, 107)),
    "卷五（107–150）": list(range(107, 151)),
    "上行之詩": ASCENT,
    "埃及頌（113–118）": list(range(113, 119)),
    "結尾哈利路（146–150）": list(range(146, 151)),
    "金詩（標題 miktam）": MIKTAM,
    "字母體": ACROSTIC,
    "亞薩詩": ASAPH,
    "可拉詩": KORAH,
    "所羅門詩（題記）": list(SOLOMON_OK),
    "摩西詩（題記）": [90],
}
# 大衛 from JSON
david = []
json_data = app.get("PSALMS_JSON_DATA") or {}
for i in range(1, 151):
    rec = json_data.get(str(i)) or {}
    author = rec.get("作者") or ""
    if "大衛" in author:
        david.append(i)
tradition["大衛詩（題記／傳統）"] = david

mood_psalms = defaultdict(list)
for i in range(1, 151):
    rec = json_data.get(str(i)) or {}
    text = (rec.get("適合的處境／情緒") or "") + " " + (rec.get("作者情緒") or "")
    for m in moods_for(text):
        mood_psalms[m].append(i)

index = {
    "facets": [
        {"id": "genre", "name": "文體", "hint": "Gunkel／文體：讚美、哀歌、感恩、君王、智慧……"},
        {"id": "mood", "name": "處境", "hint": "現在的心情或處境"},
        {"id": "tradition", "name": "傳統", "hint": "五卷、上行之詩、哈利路、題記作者、金詩、字母體"},
        {"id": "guide", "name": "綜合導讀", "hint": "文學／敬拜／歷史／神學／牧養（可多標）"},
    ],
    "genre": {"tags": list(GENRE.keys()), "psalms": genre_psalms},
    "mood": {"tags": [k for k, _ in MOOD_RULES], "psalms": {k: sorted(v) for k, v in mood_psalms.items()}},
    "tradition": {"tags": list(tradition.keys()), "psalms": tradition},
    "guide": {
        "groups": [{"id": g, "categories": list(cats.keys())} for g, cats in tax.items()],
        "categories": guide_categories,
        "psalms": guide_psalms,
    },
    "audit": {
        "acrostic": ACROSTIC,
        "removed_massah_except": sorted(MASSAH_OK),
        "solomon_kept": sorted(SOLOMON_OK),
        "miktam": MIKTAM,
        "notes": [
            "字母詩只留在結構特徵；詩歌類型改回文體。",
            "金詩只保留標題 miktam：16、56–60。",
            "瑪撒只保留確實相關的 78、81、95、106。",
            "所羅門作者只保留題記 72、127。",
            "被擄歸回後與歸回後合併。",
            "每欄改為標籤陣列，一篇可同時是智慧詩與字母詩。",
        ],
    },
}

out_js = ROOT / "psalm-search-index.js"
out_js.write_text(
    "/** 搜尋手冊索引：文體／處境／傳統／綜合導讀（已去除互斥矛盾） */\nwindow.SEARCH_INDEX = "
    + json.dumps(index, ensure_ascii=False, indent=2)
    + ";\n",
    encoding="utf-8",
)

# --- raw counts for audit ---
raw_counts = defaultdict(list)
for p in complete["psalms"]:
    n = int("".join(c for c in str(p["id"]) if c.isdigit()))
    for guide, items in (p.get("categories") or {}).items():
        for item in items or []:
            cat, tag = item.get("category"), item.get("tag")
            if cat and tag:
                raw_counts[(guide, cat, tag)].append(n)

clean_counts = defaultdict(list)
for n, labels in guide_psalms.items():
    for cat, tags in labels.items():
        group = (guide_categories.get(cat) or {}).get("group", "?")
        for t in tags:
            clean_counts[(group, cat, t)].append(int(n))

audit = ROOT / "TAG-AUDIT.md"
lines = [
    "# 五向導標籤盤點與清理",
    "",
    "資料來源：`psalm_data_complete.js`（五向導，原設計「每類別每詩篇 1 個」）＋ `psalm-data-17.js`（處境原文、題記作者）。",
    "",
    "## 發現的矛盾（清理前）",
    "",
    "1. **字母詩（詩歌類型 2 篇：34、119）vs 字母詩結構（7 篇：9、10、25、34、37、111、112）vs 不完全字母（145）**：同一結構特徵被拆開；119 因「最長」佔格而沒有字母詩結構。字母詩是結構，不是 Gunkel 文體。",
    "2. **金詩**：標題 *miktam* 應為 16、56–60，原庫卻含 32、38、51、63、67、90、93、95、97、99、108、117 等。",
    "3. **瑪撒**：原庫標了約 80 篇，與曠野試探（出 17）無關；只保留確實提到試探的 78、81、95、106。",
    "4. **所羅門**：原庫約 25 篇標作者／群體為所羅門；希伯來題記僅 72、127。",
    "5. **每欄只能 1 標**：0 個欄位原本是多標，導致 119 不能同時是智慧詩＋字母詩＋最長。",
    "6. **同名標籤跨欄**：禮儀詩（文學／敬拜）、教導／教導詩（敬拜兩欄）、讚美（敬拜功能／神學主題）、歸回後（歷史時期／敬拜場合／舊名被擄歸回後）。舊搜尋用類別名當唯一 key，數字會打架。",
    "7. **集合名混進文體**：上行之詩、哈利路亞詩、埃及頌讚、金詩、字母詩與 Gunkel 文體並列；一篇只能選一個，就把哀歌／讚美擠掉。",
    "8. **寬標籤獨占欄位**：惡人 84 篇、流亡者 28 篇；作為唯一牧養對象時幾乎沒有分辨力。",
    "",
    "## 清理後規則",
    "",
    "- 字母詩只在「結構特徵」，完整名單：" + "、".join(str(x) for x in ACROSTIC) + "。",
    "- 上行之詩、金詩、哈利路亞詩、埃及頌讚從「詩歌類型」移出，改由傳統面承載（上行／金詩／結尾哈利路／埃及頌）。",
    "- 文體面向採用 Gunkel／房志榮五大類細分，一篇可多標（懺悔＋個人哀歌、詛咒＋群體哀歌）。",
    "- 傳統面：五卷、上行、埃及頌、結尾哈利路、金詩標題、字母體、亞薩、可拉、大衛題記、所羅門題記、摩西題記。",
    "- 處境面：由舊資料「適合的處境／情緒」＋「作者情緒」歸成 15 個心情標籤（可複選，OR）。",
    "- 綜合導讀仍是五向導，但每欄改為標籤陣列；同名標籤依欄位分開計算。",
    "- 被擄歸回後與歸回後合併；咒詰詩統一為咒詛詩。",
    "- 瑪撒、所羅門依白名單；誤標直接刪除，不再改成「不詳」。",
    "",
    "## 搜尋手冊四個找法（互不混用）",
    "",
    "| 找法 | 來源 | 選法 |",
    "| --- | --- | --- |",
    "| 文體 | Gunkel／房志榮 | 多標 OR |",
    "| 處境 | 心情歸類 | 多標 OR |",
    "| 傳統 | 五卷／組詩／題記 | 多標 OR |",
    "| 綜合導讀 | 清理後五向導 | 不同欄 AND，同欄多標 OR |",
    "",
    "結構（字母詩）只出現在：綜合導讀 → 文學 → 結構特徵，以及傳統 → 字母體。",
    "",
]

# cleaned tag tables
for g, cats in tax.items():
    lines.append(f"## 綜合導讀 · {g}（清理後）")
    lines.append("")
    for c in cats:
        tags = (guide_categories.get(c) or {}).get("tags") or []
        if not tags:
            continue
        lines.append(f"### {c}")
        lines.append("")
        for t in tags:
            nums = sorted(clean_counts.get((g, c, t), []))
            if not nums:
                continue
            shown = "、".join(str(x) for x in nums[:20])
            extra = f"…共 {len(nums)} 篇" if len(nums) > 20 else f"（{len(nums)}）"
            lines.append(f"- **{t}** {shown} {extra}")
        lines.append("")

lines += [
    "## 文體找法（Gunkel／房志榮）",
    "",
]
for name, nums in GENRE.items():
    lines.append(f"- **{name}**（{len(nums)}）：" + "、".join(str(x) for x in nums))
lines += [
    "",
    "## 傳統找法",
    "",
]
for name, nums in tradition.items():
    lines.append(f"- **{name}**（{len(nums)}）：" + "、".join(str(x) for x in nums[:24]) + (" …" if len(nums) > 24 else ""))
lines += [
    "",
    "## 處境找法",
    "",
]
for name, _ in MOOD_RULES:
    nums = sorted(mood_psalms.get(name, []))
    lines.append(f"- **{name}**（{len(nums)}）")
lines += [
    "",
    "## 仍保留、但不要當成互斥文體的同名／近義標籤",
    "",
    "- 文學「禮儀詩」與敬拜「禮儀詩」：前者偏文體，後者偏敬拜場合；分欄搜尋。",
    "- 敬拜類型「教導詩」與敬拜功能「教導」：一篇可同時有。",
    "- 敬拜功能「讚美」與神學主題「讚美」：分向導。",
    "- 敬拜場合「歸回後」與歷史時期「歸回後」：分欄；舊「被擄歸回後」已併入歷史時期。",
    "- 文學「哀歌／讚美詩／智慧詩」比文體找法粗；文體找法用個人／群體細分。",
    "- 「惡人」「流亡者」仍在神學／牧養，但不再獨占欄位。",
    "",
]
audit.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out_js, out_js.stat().st_size)
print("acrostic in guide 119", guide_psalms["119"].get("結構特徵"), guide_psalms["119"].get("詩歌類型"))
print("acrostic count", sum(1 for n in range(1,151) if "字母詩" in guide_psalms[str(n)].get("結構特徵", [])))
print("ascent in 詩歌類型", [n for n in range(1,151) if "上行之詩" in guide_psalms[str(n)].get("詩歌類型", [])])
print("miktam in 詩歌類型", [n for n in range(1,151) if "金詩" in guide_psalms[str(n)].get("詩歌類型", [])])
print("solomon author", [n for n in range(1,151) if "所羅門" in guide_psalms[str(n)].get("作者/群體", [])])
print("massah", [n for n in range(1,151) if "瑪撒" in guide_psalms[str(n)].get("歷史事件", [])])
