#!/usr/bin/env python3
"""Build 17-type classification and merge into psalm-data v2.js."""
import json
import re
from pathlib import Path

# Primary exclusive assignment (房志榮〈聖詠的五大類別〉, 神學論集 1973)
# 14 literary types totalling 150, plus 3 overlay types = 17 search tags.

PRIMARY = {
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
}

OVERLAY = {
    "懺悔詩": [6, 32, 38, 51, 102, 130, 143],
    "詛咒詩": [5, 10, 12, 17, 35, 52, 58, 59, 69, 70, 79, 83, 94, 109, 137, 139, 140],
    "上行之詩": list(range(120, 135)),
}

MAJOR_OF_PRIMARY = {
    "讚美詩": "讚美",
    "雅威為王詩": "讚美",
    "錫安之歌": "讚美",
    "個人哀歌": "哀禱",
    "群體哀歌": "哀禱",
    "個人信靠詩": "哀禱",
    "群體信靠詩": "哀禱",
    "個人感恩詩": "感恩",
    "群體感恩詩": "感恩",
    "君王詩": "王國",
    "智慧詩": "訓誨",
    "歷史詩": "訓誨",
    "先知勸告詩": "訓誨",
    "禮儀詩": "訓誨",
}

# Overlay tags also belong to a major for display grouping
MAJOR_OF_OVERLAY = {
    "懺悔詩": "哀禱",
    "詛咒詩": "哀禱",
    "上行之詩": "訓誨",
}

TYPE_META = [
    {"id": 1, "name": "讚美詩", "major": "讚美", "hex": "#F5D76E", "kind": "primary"},
    {"id": 2, "name": "雅威為王詩", "major": "讚美", "hex": "#F7DC6F", "kind": "primary"},
    {"id": 3, "name": "錫安之歌", "major": "讚美", "hex": "#F8C471", "kind": "primary"},
    {"id": 4, "name": "個人哀歌", "major": "哀禱", "hex": "#85C1E9", "kind": "primary"},
    {"id": 5, "name": "群體哀歌", "major": "哀禱", "hex": "#7FB3D5", "kind": "primary"},
    {"id": 6, "name": "個人信靠詩", "major": "哀禱", "hex": "#AED6F1", "kind": "primary"},
    {"id": 7, "name": "群體信靠詩", "major": "哀禱", "hex": "#D4E6F1", "kind": "primary"},
    {"id": 8, "name": "懺悔詩", "major": "哀禱", "hex": "#F4D03F", "kind": "overlay"},
    {"id": 9, "name": "詛咒詩", "major": "哀禱", "hex": "#E74C3C", "kind": "overlay"},
    {"id": 10, "name": "個人感恩詩", "major": "感恩", "hex": "#82E0AA", "kind": "primary"},
    {"id": 11, "name": "群體感恩詩", "major": "感恩", "hex": "#58D68D", "kind": "primary"},
    {"id": 12, "name": "君王詩", "major": "王國", "hex": "#F1948A", "kind": "primary"},
    {"id": 13, "name": "智慧詩", "major": "訓誨", "hex": "#BB8FCE", "kind": "primary"},
    {"id": 14, "name": "歷史詩", "major": "訓誨", "hex": "#AF7AC5", "kind": "primary"},
    {"id": 15, "name": "先知勸告詩", "major": "訓誨", "hex": "#A569BD", "kind": "primary"},
    {"id": 16, "name": "禮儀詩", "major": "訓誨", "hex": "#D2B4DE", "kind": "primary"},
    {"id": 17, "name": "上行之詩", "major": "訓誨", "hex": "#C39BD3", "kind": "overlay"},
]

MAJORS = [
    {"id": "讚美", "hex": "#F5D76E", "desc": "讚美、雅威為王、錫安"},
    {"id": "哀禱", "hex": "#85C1E9", "desc": "個人／群體哀歌、信靠、懺悔、詛咒"},
    {"id": "感恩", "hex": "#82E0AA", "desc": "個人／群體感恩"},
    {"id": "王國", "hex": "#F1948A", "desc": "君王與彌賽亞詩"},
    {"id": "訓誨", "hex": "#BB8FCE", "desc": "智慧、歷史、先知、禮儀、上行"},
]

NAME_TO_ID = {t["name"]: t["id"] for t in TYPE_META}


def verify_primary():
    assigned = {}
    dupes = []
    for name, nums in PRIMARY.items():
        for n in nums:
            if n in assigned:
                dupes.append((n, assigned[n], name))
            assigned[n] = name
    missing = [i for i in range(1, 151) if i not in assigned]
    extra = [n for n in assigned if n < 1 or n > 150]
    print("primary count", len(assigned))
    print("missing", missing)
    print("dupes", dupes)
    print("extra", extra)
    for name, nums in PRIMARY.items():
        print(f"  {name}: {len(nums)}")
    assert not missing, missing
    assert not dupes, dupes
    assert not extra, extra
    assert len(assigned) == 150
    return assigned


def build_psalm_index(assigned):
    psalms = {}
    for n in range(1, 151):
        primary = assigned[n]
        tags = [primary]
        for overlay_name, nums in OVERLAY.items():
            if n in nums and overlay_name not in tags:
                tags.append(overlay_name)
        psalms[str(n)] = {
            "major": MAJOR_OF_PRIMARY[primary],
            "primary": primary,
            "primaryId": NAME_TO_ID[primary],
            "tags": tags,
            "tagIds": [NAME_TO_ID[t] for t in tags],
        }
    return psalms


def js_literal(obj):
    # compact but readable JSON that is valid JS
    return json.dumps(obj, ensure_ascii=False, indent=2)


def main():
    assigned = verify_primary()
    psalms = build_psalm_index(assigned)

    classification = {
        "majors": MAJORS,
        "types": TYPE_META,
        "psalms": psalms,
        "source": "房志榮〈聖詠的五大類別〉（神學論集 1973）為 14 種主分類；另加懺悔詩、詛咒詩、上行之詩為可重疊搜尋標籤，合共 17 類。",
    }

    path = Path("/workspace/psalm-data v2.js")
    text = path.read_text(encoding="utf-8")

    # Inject tags/major/primary into each OFFLINE_DB entry
    def inject_offline(match):
        key = match.group(1)
        body = match.group(2)
        info = psalms[key]
        # avoid double-inject
        if '"major":' in body or '"tags":' in body:
            body = re.sub(r'\n "major": .*?(?=\n "theme")', '', body, flags=re.S)
            body = re.sub(r'\n "primary": .*?(?=\n "theme")', '', body, flags=re.S)
            body = re.sub(r'\n "tags": .*?(?=\n "theme")', '', body, flags=re.S)
            body = re.sub(r'\n "tagIds": .*?(?=\n "theme")', '', body, flags=re.S)
        inject = (
            f'\n "major": {json.dumps(info["major"], ensure_ascii=False)},'
            f'\n "primary": {json.dumps(info["primary"], ensure_ascii=False)},'
            f'\n "tags": {json.dumps(info["tags"], ensure_ascii=False)},'
            f'\n "tagIds": {json.dumps(info["tagIds"])},'
        )
        # insert after type line
        if re.search(r'\n "type": "[^"]*",', body):
            body = re.sub(r'(\n "type": "[^"]*",)', r'\1' + inject, body, count=1)
        else:
            body = inject + body
        return f' "{key}": {{{body}}}'

    pattern = re.compile(r' "(\d+)": \{([^}]+)\}', re.S)
    offline_start = text.index("const OFFLINE_DB = {")
    offline_end = text.index("  // ==================== 3) PSALM_STRUCTURE")
    offline_block = text[offline_start:offline_end]
    new_offline, nsub = pattern.subn(inject_offline, offline_block)
    print("offline entries patched", nsub)
    if nsub != 150:
        raise SystemExit(f"expected 150 OFFLINE_DB patches, got {nsub}")
    text = text[:offline_start] + new_offline + text[offline_end:]

    class_js = f"""  // ==================== 5) CLASSIFICATION（五大類 × 17 類標籤） ====================
  const CLASSIFICATION = {js_literal(classification)};

"""
    export_old = """  window.PSALM_APP_DATA = {
    FULL_TEXTS,
    OFFLINE_DB,
    PSALM_STRUCTURE,
    PSALMS_JSON_DATA
  };"""
    export_new = """  window.PSALM_APP_DATA = {
    FULL_TEXTS,
    OFFLINE_DB,
    PSALM_STRUCTURE,
    PSALMS_JSON_DATA,
    CLASSIFICATION
  };"""
    if "CLASSIFICATION" not in text.split("window.PSALM_APP_DATA")[0]:
        text = text.replace("  // 對外匯出\n", class_js + "  // 對外匯出\n")
    text = text.replace(export_old, export_new)
    path.write_text(text, encoding="utf-8")
    print("wrote", path, "size", path.stat().st_size)

    # sanity: overlay counts
    for name, nums in OVERLAY.items():
        print(f"overlay {name}: {len(nums)}")


if __name__ == "__main__":
    main()
