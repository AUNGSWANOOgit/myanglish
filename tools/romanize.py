"""Burmese script -> chat-style Myanglish (the way people type in chat).

Used at build time to give the ~400 pieces from burmese_1m_phrases.txt a Latin spelling.
"""
import re

ONSET = {
 'က':'k','ခ':'kh','ဂ':'g','ဃ':'g','င':'ng','စ':'s','ဆ':'s','ဇ':'z','ဈ':'z','ည':'ny','ဉ':'ny',
 'ဋ':'t','ဌ':'ht','ဍ':'d','ဎ':'d','ဏ':'n','တ':'t','ထ':'ht','ဒ':'d','ဓ':'d','န':'n',
 'ပ':'p','ဖ':'ph','ဗ':'b','ဘ':'b','မ':'m','ယ':'y','ရ':'y','လ':'l','ဝ':'w','သ':'th','ဟ':'h',
 'ဠ':'l','အ':'',
}
# onset + medial ျ/ြ
Y_ONSET = {'က':'ky','ခ':'ch','ဂ':'gy','ပ':'py','ဖ':'phy','ဗ':'by','ဘ':'by','မ':'my','လ':'ly','သ':'sh','ယ':'y','ရ':'y','စ':'s','ဆ':'s'}
H_ONSET = {'ရ':'sh','ယ':'sh','လျ':'sh','သျ':'sh','မ':'hm','န':'hn','လ':'hl','င':'hng','ည':'hny','ဝ':'hw'}
CONS = set(ONSET)
INDEP = {'ဥ':'u','ဦ':'u','ဧ':'ay','ဩ':'aw','ဪ':'aw','ဤ':'i','ဣ':'i','ဿ':'th'}
MEDIALS = '\u103b\u103c\u103d\u103e'
ASAT, VIRAMA, DOT, VIS, ANUS = '\u103a', '\u1039', '\u1037', '\u1038', '\u1036'

# final consonant (with asat) + vowel context -> rhyme
def rhyme(vowels, final, has_w):
    v = vowels.replace('ါ', 'ာ')
    if final is None:
        if ANUS in v:
            return 'one' if 'ု' in v else 'an'
        table = [('ော','aw'),('ို','o'),('ေ','ay'),('ဲ','el'),('ာ','ar'),('ိ','i'),('ီ','i'),('ု','u'),('ူ','u')]
        for k, r in table:
            if k in v: return r
        return 'a'
    # loanword / Pali finals behave like the common ones
    f = {'ဒ':'တ','ဋ':'တ','ဓ':'တ','ဂ':'က','ဘ':'ပ','ဗ':'ပ','ဏ':'န','ဉ':'ဉ'}.get(final, final)
    if f == 'လ':
        return 'o' if 'ို' in v else 'an'
    if f == 'ယ':                        # ယ် = /ɛ/, but ိုယ် = /o/
        return 'o' if 'ို' in v else 'el'
    if f in 'ကင':
        if 'ော' in v: return 'out' if f == 'က' else 'aung'
        if 'ို' in v: return 'ike' if f == 'က' else 'aing'
        return 'et' if f == 'က' else 'in'
    if f in 'စဉ':
        return 'it' if f == 'စ' else 'in'
    if f == 'ည':
        return 'i'
    if f in 'တပ':
        if 'ိ' in v: return 'eik'
        if 'ု' in v: return 'ote'
        return 'ut' if has_w else 'at'
    if f in 'နမ':
        if 'ိ' in v: return 'ein'
        if 'ု' in v: return 'one'
        return 'un' if (has_w and f == 'န') else 'an'
    return 'a'

def syllables(text):
    """Split a Burmese string into (onset, medials, vowels, final) tuples."""
    out, i, n = [], 0, len(text)
    cur = None
    while i < n:
        c = text[i]
        nxt = text[i+1] if i + 1 < n else ''
        if c in CONS:
            # kinzi / stacked: C + (့) + ် / ္  -> final of current syllable
            j = i + 1
            while j < n and text[j] == DOT: j += 1
            if j < n and text[j] in (ASAT, VIRAMA) and cur is not None:
                if cur['final'] is None:
                    cur['final'] = c
                cur['vowels'] += text[i+1:j]          # keep the dot below with the syllable
                i = j
                while i < n and text[i] in (ASAT, VIRAMA): i += 1
                while i < n and text[i] in (DOT, VIS):
                    cur['vowels'] += text[i]; i += 1
                continue
            if nxt == ASAT or nxt == VIRAMA:
                if cur is not None and cur['final'] is None:
                    cur['final'] = c
                i += 1
                while i < n and text[i] in (ASAT, VIRAMA): i += 1
                # dot below / visarga after final stay with syllable
                while i < n and text[i] in (DOT, VIS):
                    cur['vowels'] += text[i]; i += 1
                continue
            cur = {'onset': c, 'med': '', 'vowels': '', 'final': None}
            out.append(cur); i += 1
            continue
        if c in INDEP:
            cur = {'onset': c, 'med': '', 'vowels': '', 'final': None, 'indep': True}
            out.append(cur); i += 1
            continue
        if c in MEDIALS:
            cur['med'] += c; i += 1; continue
        if '\u102b' <= c <= '\u1038' or c == ANUS:
            if cur is None:
                cur = {'onset': 'အ', 'med': '', 'vowels': '', 'final': None}; out.append(cur)
            if cur['final'] is not None and c in 'ုိ':
                # ကျွန်ုပ် style: vowel after a closed syllable starts a new one on the final
                cur = {'onset': cur['final'], 'med': '', 'vowels': c, 'final': None}; out.append(cur)
            else:
                cur['vowels'] += c
            i += 1
            continue
        i += 1   # punctuation etc.
    return out

def syl_to_latin(s):
    if s.get('indep'):
        base = INDEP[s['onset']]
        return base
    o, m = s['onset'], s['med']
    has_y = '\u103b' in m or '\u103c' in m
    has_w = '\u103d' in m
    has_h = '\u103e' in m
    if has_h and o in H_ONSET:
        on = H_ONSET[o] if not has_y else 'sh'
    elif has_y and o in Y_ONSET:
        on = Y_ONSET[o]
    else:
        on = ONSET.get(o, '')
        if has_y: on += 'y'
        if has_h: on = 'h' + on
    r = rhyme(s['vowels'], s['final'], has_w)
    if has_w and not r.startswith(('ut', 'un')):
        on += 'w'
    if on == '' and r == 'a':
        return 'a'
    return on + r

def romanize(text):
    text = re.sub(r'[။၊\s]', '', text)
    return ' '.join(syl_to_latin(s) for s in syllables(text))

OVERRIDES = {
    'ကျွန်ုပ်တို့': 'kyun oke to',
    'ကျွန်ုပ်': 'kyun oke',
    'ကျွန်တော်': 'kya naw',
    'ကျွန်မ': 'kya ma',
}

def chat(text):
    for k, v in OVERRIDES.items():
        if text == k: return v
    out = romanize(text)
    return out

if __name__ == '__main__':
    for w in ['မင်္ဂလာပါ','ကုမ္ပဏီက','ကျွန်ုပ်တို့','အခန်းသန့်ရှင်း','စီမံခန့်ခွဲမှုအဖွဲ့','ကြိုးစားနေတယ်','သုံးသပ်','အဓိပ္ပာယ်မလွဲအောင်ပြန်ဖတ်',
              'ကျန်းမာရေးအခြေအနေမှတ်တမ်းတင်','လုံခြုံရေး','ကျွမ်းကျင်မှု','ခန္ဓာကိုယ်','စိတ်ဖိစီးမှုလျှော့','ညစာစား','ရောင်းချသူ','ချိန်းဆိုမှုယူ']:
        print(w, '->', romanize(w))
