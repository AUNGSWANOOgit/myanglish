// Bump this together with the ?v= numbers in index.html when you publish an update,
// so browsers never mix a cached old file with a new one.
const APP_VERSION = '4.1';

let transformer = null;

const input = document.getElementById('input');
const output = document.getElementById('output');
const status = document.getElementById('status');
const copyBtn = document.getElementById('copyBtn');
const clearBtn = document.getElementById('clearBtn');
const examples = document.querySelectorAll('[data-example]');
const candTitle = document.getElementById('candTitle');
const candList = document.getElementById('candList');
const candHint = document.getElementById('candHint');
const rulesBody = document.getElementById('rulesBody');
const lookalikeBody = document.getElementById('lookalikeBody');

const WORD_RE = /[A-Za-z0-9']+[:=]?/g;
let segs = [];
let activeWord = null;     // { text, start, end }
let activeCands = [];

// ---------------------------------------------------------------- helpers
function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k === 'lang') node.lang = v;
    else node.setAttribute(k, v);
  }
  for (const c of children.flat()) node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return node;
}

// ---------------------------------------------------------------- conversion
function render() {
  if (!transformer) return;
  segs = transformer.segments(input.value);
  output.value = transformer.constructor.join(segs);
  updateCandidates();
}

// ---------------------------------------------------------------- word choices
function wordAtCaret() {
  const text = input.value;
  const caret = input.selectionStart ?? text.length;
  const words = [...text.matchAll(WORD_RE)].map(m => ({ text: m[0], start: m.index, end: m.index + m[0].length }));
  const idx = words.findIndex(w => w.start <= caret && caret <= w.end);
  if (idx === -1) return null;
  return { ...words[idx], prev: words[idx - 1]?.text ?? null, next: words[idx + 1]?.text ?? null };
}

function updateCandidates() {
  candList.replaceChildren();
  activeCands = [];
  activeWord = transformer ? wordAtCaret() : null;

  if (!activeWord) {
    candTitle.textContent = 'Word choices';
    candHint.hidden = false;
    return;
  }

  const seg = segs.find(s => s.kind !== 'punct' && s.s <= activeWord.start && s.e >= activeWord.end);
  const inPhrase = seg && seg.kind === 'phrase';
  const current = seg && !inPhrase ? seg.output : null;
  activeCands = transformer.candidates(activeWord.text, activeWord.prev, activeWord.next, current);

  candTitle.replaceChildren('Choices for ', el('span', { class: 'cand-word' }, activeWord.text));
  candHint.hidden = activeCands.length > 0;

  if (inPhrase) {
    candList.append(el('li', {}, el('p', { class: 'hint' },
      'Part of the phrase ', el('span', { lang: 'my', class: 'cand-word' }, seg.output),
      '. Picking a choice rewrites just this word.')));
  }

  activeCands.forEach((c, i) => {
    const isCurrent = c.burmese === current;
    const btn = el('button', {
      type: 'button',
      class: 'cand' + (isCurrent ? ' is-current' : ''),
      'aria-label': `${c.burmese}${c.typing ? `, type ${c.typing}` : ''}${c.note ? `, ${c.note}` : ''}`
    },
      el('span', { class: 'cand-num' }, i + 1),
      el('span', { class: 'cand-mm', lang: 'my' }, c.burmese),
      el('span', { class: 'cand-typing' }, c.typing ?? ''),
      el('span', { class: 'cand-note' }, isCurrent ? (c.note ? `Showing now. ${c.note}` : 'Showing now') : c.note)
    );
    if (!c.typing || isCurrent) btn.disabled = true;
    btn.addEventListener('click', () => pick(i));
    candList.append(el('li', {}, btn));
  });
}

// Replace the word under the caret with the typing-rule spelling of a choice.
function pick(i) {
  const c = activeCands[i];
  if (!c || !c.typing || !activeWord) return;
  let spelling = c.typing;
  const plain = !/[:'=]$/.test(spelling);
  if (plain && (transformer.tokenMap.has(spelling) || transformer.phraseMap.has(spelling) ||
                transformer.typing.keepEnglish.has(spelling))) {
    spelling += '=';     // force the typing rules over the dictionary
  }
  const { start, end } = activeWord;
  input.value = input.value.slice(0, start) + spelling + input.value.slice(end);
  const caret = start + spelling.length;
  input.focus();
  input.setSelectionRange(caret, caret);
  render();
}

// ---------------------------------------------------------------- cheat-sheet
function buildRules(rules) {
  const t = transformer.typing;
  const syl = (stem, mark = '') => t.syllable(stem, mark) ?? '';

  const intro = el('ul', { class: 'rule-list' },
    [['tha', ''], ['tha', ':'], ['tha', "'"], ['ne', '=']].map(([stem, mark]) =>
      el('li', {}, el('span', { class: 'typed' }, stem + mark), el('span', { class: 'mm', lang: 'my' }, syl(stem, mark)))));

  const notes = [
    el('p', { class: 'rule-note' }, 'No mark gives the plain form. ', el('kbd', {}, ':'), ' adds the two dots း. ',
      el('kbd', {}, "'"), ' gives the short dotted form. ', el('kbd', {}, '='), ' keeps it plain but skips the dictionary.'),
    el('p', { class: 'rule-note' }, 'Letters stand for script, not sound: y = ျ, r = ြ, w = ွ, and h in front = ှ.'),
    el('p', { class: 'rule-note' }, 'At the end of a syllable, ny = ည် and iny = ဉ်.'),
  ];

  const examples = el('ul', { class: 'rule-list' },
    (rules.examples ?? []).filter(([lat]) => !/^tha/.test(lat)).map(([lat, mm]) =>
      el('li', {}, el('span', { class: 'typed' }, lat), el('span', { class: 'mm', lang: 'my' }, mm))));

  const joinNote = el('p', { class: 'rule-note' },
    'Syllables typed this way join into one word: ', el('span', { class: 'typed' }, "a' khan: than' shin:"),
    ' gives ', el('span', { lang: 'my' }, syl('a', "'") + syl('khan', ':') + syl('than', "'") + syl('shin', ':')), '.');

  // full tables, folded away
  const openRows = Object.keys(rules.open_rhymes ?? {}).map(rh =>
    el('tr', {}, el('td', { class: 'typed' }, 'k' + rh),
      ...['', ':', "'"].map(m => el('td', { class: 'mm', lang: 'my' }, syl('k' + rh, m)))));
  const openTable = el('table', { class: 'rule-table' },
    el('thead', {}, el('tr', {}, el('th', {}, 'Type'), el('th', {}, 'plain'), el('th', {}, ':'), el('th', {}, "'"))),
    el('tbody', {}, openRows));

  const closed = [...Object.keys(rules.nasal_rhymes ?? {}), ...Object.keys(rules.checked_rhymes ?? {})];
  const closedRows = [];
  for (let i = 0; i < closed.length; i += 2) {
    closedRows.push(el('tr', {}, closed.slice(i, i + 2).flatMap(rh =>
      [el('td', { class: 'typed' }, 'k' + rh), el('td', { class: 'mm', lang: 'my' }, syl('k' + rh))])));
  }
  const closedTable = el('table', { class: 'rule-table' },
    el('thead', {}, el('tr', {}, el('th', {}, 'Type'), el('th', {}, ''), el('th', {}, 'Type'), el('th', {}, ''))),
    el('tbody', {}, closedRows));

  const initials = (rules.canonical_initials ?? []).filter(Boolean);
  const iniRows = [];
  for (let i = 0; i < initials.length; i += 3) {
    iniRows.push(el('tr', {}, initials.slice(i, i + 3).flatMap(k =>
      [el('td', { class: 'typed' }, k), el('td', { class: 'mm', lang: 'my' }, rules.initials[k])])));
  }
  const iniTable = el('table', { class: 'rule-table' }, el('tbody', {}, iniRows));

  const more = el('details', {},
    el('summary', {}, 'All letters and endings'),
    el('p', { class: 'rule-note' }, 'Vowel endings take a mark. Shown with k:'), openTable,
    el('p', { class: 'rule-note' }, 'Closed endings. : and \' work on the nasal ones (kan: = ကန်း, kan\' = ကန့်):'), closedTable,
    el('p', { class: 'rule-note' }, 'First letters. A syllable with no first letter starts with အ:'), iniTable);

  rulesBody.replaceChildren(intro, ...notes, examples, joinNote, more);
}

function buildLookalikes(sets) {
  const t = transformer.typing;
  lookalikeBody.replaceChildren(...sets.map(set =>
    el('div', { class: 'lookalike' }, (set.items ?? []).map(it =>
      el('div', { class: 'lookalike-row' },
        el('span', { class: 'mm', lang: 'my' }, it.burmese),
        el('span', { class: 'typed' }, t.spell(it.burmese) ?? ''),
        el('span', { class: 'note' }, it.note ?? ''))))));
}

// ---------------------------------------------------------------- boot
async function boot() {
  try {
    // 'no-cache' revalidates with the server (ETag) instead of re-downloading every visit
    const response = await fetch(`./myanglish_mapping.json?v=${APP_VERSION}`, { cache: 'no-cache' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    transformer = new MyanglishTransformer(data);

    const words = transformer.tokenMap.size.toLocaleString();
    const phrases = transformer.phraseMap.size.toLocaleString();
    status.textContent = `Dictionary v${data.schema_version ?? APP_VERSION} ready: ${words} spellings and ${phrases} phrases`;
    status.classList.add('ready');

    buildRules(data.typing_rules ?? {});
    buildLookalikes(data.confusable_sets ?? []);
    for (const button of examples) button.title = transformer.transform(button.dataset.example);
    render();
  } catch (err) {
    status.textContent = "Couldn't load myanglish_mapping.json. Open this page through GitHub Pages or a local server (python3 -m http.server).";
    status.classList.add('error');
    console.error(err);
  }
}

input.addEventListener('input', render);
for (const ev of ['click', 'keyup', 'focus']) input.addEventListener(ev, e => {
  if (e.type === 'keyup' && !/^(Arrow|Home|End|Page)/.test(e.key)) return;
  updateCandidates();
});
input.addEventListener('keydown', e => {
  if (e.altKey && /^Digit[1-9]$/.test(e.code)) {
    const i = Number(e.code.slice(5)) - 1;
    if (activeCands[i]) { e.preventDefault(); pick(i); }
  }
});

copyBtn.addEventListener('click', async () => {
  if (!output.value) return;
  try {
    await navigator.clipboard.writeText(output.value);
  } catch {
    output.select();
    document.execCommand('copy');
  }
  copyBtn.textContent = 'Copied';
  copyBtn.classList.add('done');
  setTimeout(() => {
    copyBtn.textContent = 'Copy';
    copyBtn.classList.remove('done');
  }, 1200);
});

clearBtn.addEventListener('click', () => {
  input.value = '';
  render();
  input.focus();
});

for (const button of examples) {
  button.addEventListener('click', () => {
    input.value = button.dataset.example;
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
    render();
  });
}

boot();
