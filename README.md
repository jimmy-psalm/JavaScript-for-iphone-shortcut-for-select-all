# 詩篇全景 · 搜尋手冊

手機可用的詩篇分析與粵語經文朗讀。這是**全新一組檔案**，不會覆蓋舊的 `0015 Psalm new type.html` 或 `psalm-data v2.js`。

## iPhone 直接開啟

正式站（Psalm 倉 GitHub Pages，待同步）：

**https://jimmy-psalm.github.io/Psalm/psalm-17.html**

若 Pages 尚未更新，可用預覽（先開這個）：

**https://htmlpreview.github.io/?https://github.com/jimmy-psalm/JavaScript-for-iphone-shortcut-for-select-all/blob/main/psalm-17.html**

## 搜尋手冊四個找法

1. **文體**：Gunkel／房志榮（讚美、哀歌、感恩、君王、智慧……一篇可多標）
2. **處境**：現在的心情或處境
3. **傳統**：五卷、上行之詩、埃及頌、哈利路、金詩、字母體、題記作者
4. **綜合導讀**：文學／敬拜／歷史／神學／牧養（每欄可多標）

操作：選找法 → 選標籤 → 圓點亮起 → 點選看經文與朗讀。

標籤矛盾與清理規則見 `TAG-AUDIT.md`。

## 新檔案（不覆蓋舊程式）

| 檔案 | 說明 |
| --- | --- |
| `psalm-17.html` | 主程式：搜尋手冊、全景圓點、分析、經文、朗讀 |
| `psalm-search-index.js` | 清理後的搜尋索引 |
| `psalm-data-17.js` | 經文、結構、舊標籤 |
| `psalm_data_complete.js` | 五向導原文說明 |
| `0015 Psalm new type.html` | 舊版主程式（未改） |
| `psalm-data v2.js` | 舊資料檔（未改） |

```bash
python3 -m http.server 8080
# 開啟 http://localhost:8080/psalm-17.html
node test-search-index.js
```
