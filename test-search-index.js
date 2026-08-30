/** 搜尋手冊索引與五向導清理規則測試 */
const fs = require('fs');
const vm = require('vm');

const ctx = { window: {}, console };
vm.runInNewContext(fs.readFileSync('psalm-search-index.js', 'utf8'), ctx);
const I = ctx.window.SEARCH_INDEX;

function assert(cond, msg) {
    if (!cond) throw new Error(msg);
}

assert(I.facets.map(f => f.id).join(',') === 'genre,mood,tradition,guide', '四個找法');
assert(!I.genre.tags.includes('字母詩'), '字母詩不是文體');
assert(I.genre.psalms['智慧詩'].includes(119), '119 是智慧詩');
assert(I.tradition.psalms['字母體'].slice().sort((a,b)=>a-b).join(',') === '9,10,25,34,37,111,112,119,145', '字母體九篇');
assert(I.tradition.psalms['金詩（標題 miktam）'].join(',') === '16,56,57,58,59,60', '金詩 miktam');
assert(I.tradition.psalms['所羅門詩（題記）'].join(',') === '72,127', '所羅門題記');
assert(I.guide.psalms['119'].結構特徵.includes('字母詩'), '119 結構有字母詩');
assert(I.guide.psalms['119'].結構特徵.includes('最長'), '119 可同時最長');
assert(I.guide.psalms['119'].詩歌類型.includes('智慧詩'), '119 詩歌類型智慧詩');
assert(!(I.guide.psalms['119'].詩歌類型 || []).includes('字母詩'), '119 詩歌類型不再是字母詩');
assert(!(I.guide.psalms['119'].歷史事件 || []).includes('瑪撒'), '119 不再誤標瑪撒');

let acrostic = 0;
const massah = [];
const solomon = [];
const goldType = [];
for (let n = 1; n <= 150; n++) {
    const p = I.guide.psalms[String(n)] || {};
    if ((p.結構特徵 || []).includes('字母詩')) acrostic++;
    if ((p.歷史事件 || []).includes('瑪撒')) massah.push(n);
    if ((p['作者/群體'] || []).includes('所羅門')) solomon.push(n);
    if ((p.詩歌類型 || []).includes('金詩')) goldType.push(n);
}
assert(acrostic === 9, '字母詩結構共 9 篇，得 ' + acrostic);
assert(massah.join(',') === '78,81,95,106', '瑪撒白名單，得 ' + massah);
assert(solomon.join(',') === '72,127', '所羅門作者，得 ' + solomon);
assert(goldType.length === 0, '詩歌類型不再有金詩');

const slots = Object.values(I.guide.psalms).flatMap(p => Object.values(p));
assert(slots.some(v => Array.isArray(v) && v.length > 1), '至少一個欄位是多標');

console.log('test-search-index: ok');
