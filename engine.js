'use strict';

/*
 * Myanglish → Burmese engine (v3)
 *
 * 1. Phrases:   longest match against phrase_map + grammar (predicates × frames).
 * 2. Words:     token_map lookup with light context rules.
 * 3. Typing rules (precise mode): a word ending in  :  '  or  =  is spelled by
 *    the typing rules in typing_rules (tha = သာ, tha: = သား, tha' = သ).
 *    Unknown words that fit the rules are read the same way.
 */

// A word may end in one typing mark:  :  (း)   '  (့)   =  (plain, read by rules)
const TOKEN_RE = /[A-Za-z0-9']+[:=]?|[^\w\s]/gu;
const MARK_RE = /^(.*?)([:'=])$/;

// Burmese particles that attach to the word before them (no space).
const ATTACH_PARTICLES = new Set([
  'တယ်', 'လား', 'လဲ', 'ဘူး', 'မယ်', 'ပြီ', 'ပါ', 'နော်', 'တာ', 'ကွာ', 'ရော', 'ပဲ',
  'တော့', 'လို့', 'နဲ့', 'ကို', 'က', 'မှာ', 'မှ', 'တွေ', 'လေး', 'ရင်', 'ဖို့',
  'ကြောင့်', 'အတွက်', 'ဆီ', 'ထဲ', 'ပေါ်', 'တို့', 'ချင်', 'နိုင်', 'လိုက်', 'ပြီး', 'သေး', 'ခဲ့', 'ဦး'
]);

function normText(s) {
  return String(s ?? '').toLowerCase().trim().replace(/\s+/g, ' ');
}

function collapseEmphasis(token) {
  return token.replace(/(.)\1{2,}/g, '$1$1');
}

function endsWithMyanmar(s) {
  return /[\u1000-\u109F]$/.test(s);
}

function startsWithMyanmar(s) {
  return /^[\u1000-\u109F]/.test(s);
}

function isWord(token) {
  return /^[A-Za-z0-9']+[:=]?$/.test(token);
}

// ---------------------------------------------------------------- grammar expansion
// predicates × frames → phrases. "|" in a predicate marks where the negator မ goes.
// Pattern slots: P = predicate, N = negated predicate, GROUP = particle spellings,
// GROUP:2 = first two spellings, =a|b = literal spellings.

function predicateForms(pred) {
  const fullL = [];
  const negL = [];
  for (const v of pred.latin ?? []) {
    const full = normText(v.replace('|', ' '));
    fullL.push(full);
    negL.push(normText('ma ' + full));
    if (v.includes('|')) {
      const [h, t] = v.split('|');
      negL.push(normText(`${h} ma ${t}`));
    }
  }
  const bur = pred.burmese ?? '';
  const fullB = bur.replace('|', '');
  let negB;
  if (bur.includes('|')) {
    const [h, t] = bur.split('|');
    negB = h + 'မ' + t;
  } else {
    negB = 'မ' + bur;
  }
  return { fullL: [...new Set(fullL)], negL: [...new Set(negL)], fullB, negB };
}

function slotPool(slot, forms, particles) {
  if (slot === 'P') return forms.fullL;
  if (slot === 'N') return forms.negL;
  if (slot.startsWith('=')) return slot.slice(1).split('|');
  const [name, limit] = slot.split(':');
  const list = particles[name] ?? [];
  return limit ? list.slice(0, Number(limit)) : list;
}

function* cartesian(pools, idx = 0, acc = []) {
  if (idx === pools.length) { yield acc.join(' '); return; }
  for (const item of pools[idx]) {
    acc.push(item);
    yield* cartesian(pools, idx + 1, acc);
    acc.pop();
  }
}

// ---------------------------------------------------------------- typing rules
const MEDIAL_ORDER = '\u103B\u103C\u103D\u103E';   // ျ ြ ွ ှ
const TONE_INDEX = { '': 0, '=': 0, ':': 1, "'": 2 };

class TypingRules {
  constructor(rules = {}) {
    this.rules = rules;
    this.initials = Object.entries(rules.initials ?? {}).sort((a, b) => b[0].length - a[0].length);
    this.medials = rules.medials ?? {};
    this.open = rules.open_rhymes ?? {};
    this.nasal = rules.nasal_rhymes ?? {};
    this.checked = rules.checked_rhymes ?? {};
    this.tall = new Set([...(rules.tall_aa_consonants ?? '')]);
    this.exceptions = rules.creaky_exceptions ?? {};
    this.keepEnglish = new Set(rules.english_keep ?? []);
    this.medialOptions = ['', ...(rules.medial_combinations ?? ['y', 'r', 'w', 'yw', 'rw'])];
    this._reverse = null;
  }

  // Build one syllable from a Latin stem and a mark. Returns null if the stem doesn't fit the rules.
  syllable(stem, mark = '') {
    stem = normText(stem);
    if (!stem) return null;
    if (mark === "'" && this.exceptions[stem]) return this.exceptions[stem];
    for (const [lat, bur] of this.initials) {
      if (!stem.startsWith(lat)) continue;
      const afterInitial = stem.slice(lat.length);
      for (const med of this.medialOptions) {
        if (!afterInitial.startsWith(med)) continue;
        const rest = afterInitial.slice(med.length);
        const built = this.build(bur, med, rest, mark);
        if (built) return built;
      }
    }
    return null;
  }

  build(initialBur, med, rhymeLatin, mark) {
    const consonant = initialBur[0];
    let medials = initialBur.slice(1);
    for (const ch of med) medials += this.medials[ch] ?? '';
    medials = [...medials].sort((a, b) => MEDIAL_ORDER.indexOf(a) - MEDIAL_ORDER.indexOf(b)).join('');
    const tall = medials === '' && this.tall.has(consonant);
    const fixTall = s => (tall ? s.replace('ာ', 'ါ') : s);
    const head = consonant + medials;

    if (this.open[rhymeLatin]) {
      const forms = this.open[rhymeLatin];
      return head + fixTall(forms[TONE_INDEX[mark] ?? 0]);
    }
    if (this.nasal[rhymeLatin]) {
      const base = fixTall(this.nasal[rhymeLatin]);
      if (mark === ':') return head + base + 'း';
      if (mark === "'") return head + base.replace(/်$/, '့်');
      return head + base;
    }
    if (this.checked[rhymeLatin]) {
      return head + fixTall(this.checked[rhymeLatin]);
    }
    return null;
  }

  // Should an unknown, unmarked word be read by the typing rules?
  canFallback(word) {
    return !this.keepEnglish.has(word) && this.syllable(word, '') !== null;
  }

  // Burmese syllable → the Latin spelling that types it (e.g. သား → "tha:")
  spell(burmese) {
    if (!this._reverse) this._reverse = this.buildReverse();
    return this._reverse.get(burmese) ?? null;
  }

  buildReverse() {
    const map = new Map();
    const canonical = this.rules.canonical_initials ?? Object.keys(this.rules.initials ?? {});
    const rhymes = [...Object.keys(this.open), ...Object.keys(this.nasal), ...Object.keys(this.checked)];
    for (const mark of ['', ':', "'"]) {
      for (const ini of canonical) {
        for (const med of this.medialOptions) {
          for (const rh of rhymes) {
            if (mark && this.checked[rh]) continue;
            const stem = ini + med + rh;
            const bur = this.syllable(stem, mark);
            if (bur && !map.has(bur)) map.set(bur, stem + mark);
          }
        }
      }
    }
    for (const [stem, bur] of Object.entries(this.exceptions)) if (!map.has(bur)) map.set(bur, stem + "'");
    return map;
  }
}

// ---------------------------------------------------------------- transformer
class MyanglishTransformer {
  constructor(data) {
    this.data = data;
    this.phraseMap = new Map();
    this.tokenMap = new Map();
    this.typing = new TypingRules(data.typing_rules);

    for (const item of data.phrase_map ?? []) {
      for (const variant of item.myanglish ?? []) {
        this.phraseMap.set(normText(variant), {
          burmese: item.burmese ?? '',
          english: item.english ?? '',
          confidence: item.confidence ?? 'medium'
        });
      }
    }

    for (const item of data.token_map ?? []) {
      for (const variant of item.variants ?? []) {
        const key = normText(variant);
        if (!this.tokenMap.has(key)) this.tokenMap.set(key, []);
        this.tokenMap.get(key).push(item);
      }
    }

    this.generatedCount = this.expandGrammar(data);

    let maxWords = 1;
    for (const k of this.phraseMap.keys()) {
      let n = 1;
      for (let c = 0; c < k.length; c++) if (k.charCodeAt(c) === 32) n++;
      if (n > maxWords) maxWords = n;
    }
    this.maxPhraseWords = maxWords;

    // Notes for the candidate panel: Burmese → short meaning
    this.notes = new Map();
    for (const set of data.confusable_sets ?? []) {
      for (const it of set.items ?? []) if (it.note) this.notes.set(it.burmese, it.note);
    }
    for (const item of data.token_map ?? []) {
      if (!this.notes.has(item.burmese) && item.english?.length) {
        this.notes.set(item.burmese, [].concat(item.english).join(', '));
      }
    }
  }

  expandGrammar(data) {
    const particles = data.particles ?? {};
    const frames = new Map((data.frames ?? []).map(f => [f.id, f]));
    const sets = data.frame_sets ?? {};
    const gen = data.generation ?? {};
    const joinMax = gen.join_max_words ?? 0;
    const joinMin = gen.join_min_length ?? 5;
    const blocked = new Set(gen.join_blocklist ?? []);
    const joined = [];
    let added = 0;

    const add = (key, entry) => {
      if (this.phraseMap.has(key)) return;
      this.phraseMap.set(key, entry);
      added++;
    };

    for (const pred of data.predicates ?? []) {
      const forms = predicateForms(pred);
      let ids = typeof pred.frames === 'string' ? (sets[pred.frames] ?? []) : (pred.frames ?? []);
      if (pred.exclude?.length) ids = ids.filter(id => !pred.exclude.includes(id));
      if (pred.include?.length) ids = ids.concat(pred.include);

      for (const id of ids) {
        const frame = frames.get(id);
        if (!frame) continue;
        const pools = frame.pattern.map(slot => slotPool(slot, forms, particles));
        const entry = {
          burmese: frame.burmese.replace('{P}', forms.fullB).replace('{N}', forms.negB),
          english: (frame.english ?? '').replace('{v}', pred.english ?? ''),
          confidence: pred.confidence ?? 'high'
        };
        for (const key of cartesian(pools)) {
          add(key, entry);
          if (joinMax && key.split(' ').length <= joinMax) joined.push([key.replace(/ /g, ''), entry]);
        }
      }
      const bare = { burmese: forms.fullB, english: pred.english ?? '', confidence: pred.confidence ?? 'high' };
      for (const v of forms.fullL) if (v.includes(' ')) add(v, bare);
    }

    for (const [key, entry] of joined) {
      if (key.length < joinMin || blocked.has(key) || this.tokenMap.has(key)) continue;
      add(key, entry);
    }
    return added;
  }

  resolveAmbiguous(token, prevTok, nextTok) {
    const t = normText(token);
    const prev = normText(prevTok ?? '');
    const next = normText(nextTok ?? '');

    const statementParticles = new Set(['tl', 'tal', 'te', 'del']);
    const futureParticles = new Set(['ml', 'mel', 'mal']);
    const negativeImperative = new Set(['ne', 'nae']);

    if (t === 'sar') {
      if (['chin', 'kyin', 'pyi', 'pee', 'p', ...futureParticles].includes(next)) return 'စား';
      if (statementParticles.has(next)) return 'ဆာ';
      if (['phat'].includes(next)) return 'စာ';
    }

    if (t === 'pyaw') {
      if (futureParticles.has(next) || ['tr', 'tar'].includes(next) || negativeImperative.has(next)) return 'ပြော';
      if (statementParticles.has(next)) return 'ပျော်';
    }

    if (['lar', 'la'].includes(t)) {
      if (!next || !/^[a-z0-9']+$/.test(next)) return 'လား';
      if (futureParticles.has(next) || ['tl', 'tal', 'te', 'del', 'pyi', 'pee', 'p'].includes(next)) return 'လာ';
    }

    if (['mha', 'hma'].includes(t)) {
      if (['bl', 'bel'].includes(prev)) return 'မှာ';
      if (['nout', 'nauk'].includes(prev)) return 'မှ';
      return 'မှာ';
    }

    if (['le', 'lel'].includes(t)) return 'လဲ';
    if (t === 'lay') return 'လေး';
    if (['ko', 'koe'].includes(t)) return 'ကို';
    if (t === 'kyaung') return 'ကျောင်း';

    return null;
  }

  lookupToken(token, prevTok, nextTok) {
    let key = normText(token);
    if (!key) return token;

    const resolved = this.resolveAmbiguous(key, prevTok, nextTok);
    if (resolved) return resolved;

    let candidates = this.tokenMap.get(key);
    if (!candidates) {
      key = collapseEmphasis(key);
      candidates = this.tokenMap.get(key);
    }
    if (!candidates?.length) return token;

    const unique = [...new Set(candidates.map(x => x.burmese).filter(Boolean))];
    if (unique.length === 1) return unique[0];

    const rank = { high: 3, medium: 2, low: 1 };
    const best = [...candidates].sort(
      (a, b) => (rank[b.confidence] ?? 0) - (rank[a.confidence] ?? 0)
    )[0];
    return best?.burmese || token;
  }

  // One word → { text, kind }. kind: 'precise' (typing rules), 'word' (dictionary), 'unknown'
  resolveWord(tok, prevTok, nextTok) {
    const key = normText(tok);
    const m = key.match(MARK_RE);
    if (m && m[1] && /[a-z]/.test(m[1])) {
      const [, stem, mark] = m;
      const built = this.typing.syllable(stem, mark);
      if (built) return { text: built, kind: 'precise' };
      // not a typing-rule syllable: treat the mark as ordinary punctuation
      const word = this.lookupToken(stem, prevTok, nextTok);
      return { text: word + (mark === '=' ? '' : mark), kind: word === stem ? 'unknown' : 'word' };
    }
    const word = this.lookupToken(tok, prevTok, nextTok);
    if (word !== tok) return { text: word, kind: 'word' };
    if (this.typing.canFallback(key)) return { text: this.typing.syllable(key, ''), kind: 'precise' };
    return { text: tok, kind: 'unknown' };
  }

  // Detailed conversion: which input range produced which output.
  segments(text) {
    const raw = String(text ?? '');
    const toks = [...raw.matchAll(TOKEN_RE)].map(m => ({ t: m[0], s: m.index, e: m.index + m[0].length }));
    const segs = [];
    let i = 0;

    const push = (seg) => {
      const prev = segs[segs.length - 1];
      const prevOut = prev ? prev.output : '';
      let attach = false;
      if (prev) {
        if (seg.kind === 'punct' && endsWithMyanmar(prevOut) && (seg.output === '.' || seg.output === ',')) {
          seg.output = seg.output === '.' ? '။' : '၊';
          attach = true;
        } else if (seg.kind !== 'punct') {
          if (ATTACH_PARTICLES.has(seg.output) && endsWithMyanmar(prevOut)) attach = true;
          else if (prevOut === 'မ' && startsWithMyanmar(seg.output)) attach = true;
          else if (seg.kind === 'precise' && prev.kind === 'precise') attach = true;
        }
      }
      seg.attach = attach;
      segs.push(seg);
    };

    while (i < toks.length) {
      const tok = toks[i].t;

      if (!isWord(tok)) {
        push({ s: toks[i].s, e: toks[i].e, input: tok, output: tok, kind: 'punct' });
        i += 1;
        continue;
      }

      // longest phrase match over consecutive words
      const wordIdx = [];
      let j = i;
      while (j < toks.length && wordIdx.length < this.maxPhraseWords && isWord(toks[j].t)) {
        wordIdx.push(j);
        j += 1;
      }

      let match = null;
      let len = 0;
      for (let n = wordIdx.length; n >= 1; n--) {
        const phraseKey = normText(toks.slice(i, i + n).map(x => x.t).join(' '));
        let m = this.phraseMap.get(phraseKey);
        if (!m) {
          const collapsedKey = phraseKey.split(' ').map(collapseEmphasis).join(' ');
          if (collapsedKey !== phraseKey) m = this.phraseMap.get(collapsedKey);
        }
        if (m) { match = m; len = n; break; }
      }

      if (match) {
        const last = toks[i + len - 1];
        push({
          s: toks[i].s, e: last.e, input: raw.slice(toks[i].s, last.e),
          output: match.burmese, kind: len > 1 ? 'phrase' : 'word', english: match.english
        });
        i += len;
        continue;
      }

      const prevTok = i > 0 && isWord(toks[i - 1].t) ? toks[i - 1].t : null;
      const nextTok = i + 1 < toks.length && isWord(toks[i + 1].t) ? toks[i + 1].t : null;
      const res = this.resolveWord(tok, prevTok, nextTok);
      push({ s: toks[i].s, e: toks[i].e, input: tok, output: res.text, kind: res.kind });
      i += 1;
    }
    return segs;
  }

  static join(segs) {
    const noSpaceBefore = new Set(['.', ',', '!', '?', ':', ';', ')', ']', '}', '။', '၊']);
    const noSpaceAfter = new Set(['(', '[', '{']);
    let result = '';
    segs.forEach((seg, idx) => {
      if (idx === 0) { result = seg.output; return; }
      const prev = segs[idx - 1].output;
      if (seg.attach || noSpaceBefore.has(seg.output) || noSpaceAfter.has(prev)) result += seg.output;
      else result += ' ' + seg.output;
    });
    return result;
  }

  transform(text) {
    return MyanglishTransformer.join(this.segments(text));
  }

  // Alternatives for one input word (for the candidate panel).
  candidates(word, prevTok = null, nextTok = null, current = null) {
    const key = normText(word);
    const m = key.match(MARK_RE);
    const stem = m && m[1] ? m[1] : key;
    const list = [];
    const seen = new Set();
    const add = (burmese, source) => {
      if (!burmese || seen.has(burmese) || !startsWithMyanmar(burmese)) return;
      seen.add(burmese);
      list.push({ burmese, source, typing: this.typing.spell(burmese), note: this.notes.get(burmese) ?? '' });
    };

    if (current) add(current, 'current');
    for (const mark of ['', ':', "'"]) add(this.typing.syllable(stem, mark), 'typing');
    for (const item of this.tokenMap.get(stem) ?? []) add(item.burmese, 'dictionary');
    const resolved = this.resolveAmbiguous(stem, prevTok, nextTok);
    if (resolved) add(resolved, 'dictionary');

    // pull in look-alike words for anything already listed
    for (const set of this.data.confusable_sets ?? []) {
      const members = (set.items ?? []).map(x => x.burmese);
      if (members.some(b => seen.has(b))) for (const b of members) add(b, 'look-alike');
    }
    // current first, then real words (they have a meaning), then rule-only forms
    const rankOf = c => (c.source === 'current' ? 0 : c.note ? 1 : 2);
    list.sort((a, b) => rankOf(a) - rankOf(b));
    return list.slice(0, 9);
  }
}


if (typeof window !== 'undefined') {
  window.MyanglishTransformer = MyanglishTransformer;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MyanglishTransformer, TypingRules, normText, collapseEmphasis, predicateForms };
}
