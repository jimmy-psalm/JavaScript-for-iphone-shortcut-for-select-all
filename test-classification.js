/**
 * Headless checks for 17-type classification + HTML wiring.
 */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const sandbox = { window: {}, console };
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(__dirname, 'psalm-data-17.js'), 'utf8'), sandbox);

const data = sandbox.window.PSALM_APP_DATA;
if (!data) throw new Error('PSALM_APP_DATA missing');
const { FULL_TEXTS, OFFLINE_DB, PSALM_STRUCTURE, PSALMS_JSON_DATA, CLASSIFICATION } = data;

const fails = [];
function ok(cond, msg) { if (!cond) fails.push(msg); }

ok(Object.keys(FULL_TEXTS).length === 150, `FULL_TEXTS ${Object.keys(FULL_TEXTS).length}`);
ok(Object.keys(OFFLINE_DB).length === 150, `OFFLINE_DB ${Object.keys(OFFLINE_DB).length}`);
ok(Object.keys(PSALM_STRUCTURE).length === 150, `PSALM_STRUCTURE ${Object.keys(PSALM_STRUCTURE).length}`);
ok(Object.keys(PSALMS_JSON_DATA).length === 150, `PSALMS_JSON_DATA ${Object.keys(PSALMS_JSON_DATA).length}`);
ok(CLASSIFICATION && CLASSIFICATION.types.length === 17, `types ${CLASSIFICATION && CLASSIFICATION.types.length}`);
ok(CLASSIFICATION.majors.length === 5, `majors ${CLASSIFICATION.majors.length}`);
ok(Object.keys(CLASSIFICATION.psalms).length === 150, `class psalms ${Object.keys(CLASSIFICATION.psalms).length}`);

const typeNames = CLASSIFICATION.types.map(t => t.name);
ok(new Set(typeNames).size === 17, '17 unique type names');

const primaryCounts = {};
const tagCounts = {};
for (let i = 1; i <= 150; i++) {
  const c = CLASSIFICATION.psalms[String(i)];
  const db = OFFLINE_DB[String(i)];
  ok(c, `missing class ${i}`);
  ok(db.major === c.major, `major mismatch ${i} ${db.major} vs ${c.major}`);
  ok(db.primary === c.primary, `primary mismatch ${i}`);
  ok(JSON.stringify(db.tags) === JSON.stringify(c.tags), `tags mismatch ${i}`);
  ok(c.tags.includes(c.primary), `primary not in tags ${i}`);
  ok(FULL_TEXTS[String(i)] && FULL_TEXTS[String(i)].text.length > 20, `short text ${i}`);
  primaryCounts[c.primary] = (primaryCounts[c.primary] || 0) + 1;
  c.tags.forEach(t => { tagCounts[t] = (tagCounts[t] || 0) + 1; });
}

ok(primaryCounts['讚美詩'] === 19, `讚美詩 ${primaryCounts['讚美詩']}`);
ok(primaryCounts['君王詩'] === 11, `君王詩 ${primaryCounts['君王詩']}`);
ok(tagCounts['懺悔詩'] === 7, `懺悔詩 ${tagCounts['懺悔詩']}`);
ok(tagCounts['上行之詩'] === 15, `上行之詩 ${tagCounts['上行之詩']}`);
ok(CLASSIFICATION.psalms['6'].tags.includes('懺悔詩'), 'psalm 6 penitential');
ok(CLASSIFICATION.psalms['120'].tags.includes('上行之詩'), 'psalm 120 ascent');
ok(CLASSIFICATION.psalms['1'].major === '訓誨', 'psalm 1 訓誨');
ok(CLASSIFICATION.psalms['2'].major === '王國', 'psalm 2 王國');
ok(CLASSIFICATION.psalms['8'].major === '讚美', 'psalm 8 讚美');

const html = fs.readFileSync(path.join(__dirname, '0016 Psalm 17 type.html'), 'utf8');
ok(html.includes('psalm-data-17.js'), 'html loads data file');
ok(html.includes('filterMajor'), 'filterMajor present');
ok(html.includes('renderPsalmTagDots'), 'tag dots present');
ok(html.includes('五大類 · 17類搜尋'), 'panel1 title');
ok(html.includes('tag-dot'), 'tag-dot css/markup');
ok(!html.includes("name: '申訴詩'"), 'old 10-type legend removed');

if (fails.length) {
  console.error('FAIL');
  fails.forEach(f => console.error(' -', f));
  process.exit(1);
}
console.log('PASS');
console.log('primary', primaryCounts);
console.log('tags', tagCounts);
console.log('majors', CLASSIFICATION.majors.map(m => m.id).join(', '));
console.log('types', typeNames.join('、'));
