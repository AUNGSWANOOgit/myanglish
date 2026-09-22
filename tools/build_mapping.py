#!/usr/bin/env python3
"""Build myanglish_mapping.json v3 (grammar-based; expanded by engine.js at load time).

Usage:  python3 build3.py [blocklist.json]
"""
import json, re, sys

OLD = json.load(open('myanglish_mapping.v1.json'))
WORD = re.compile(r"^[a-z0-9']+$")
def norm(s): return re.sub(r'\s+', ' ', s.lower().strip())
def is_key(k): return bool(k) and all(WORD.match(w) for w in k.split(' '))

# ================================================================ particles
PARTICLES = {
  "TL":   ["tl", "tal", "te", "tae", "del", "tel"],
  "LRR":  ["lrr", "lr", "lar", "la"],
  "ML":   ["ml", "mal", "mel"],
  "LL":   ["ll", "le", "lel"],
  "BU":   ["bu", "woo", "boo", "wu"],
  "NY":   ["ny", "nay"],
  "FIN":  ["p", "pi"],
  "PP":   ["p p", "pyi p", "pee p", "pyi pi"],
  "PYI":  ["pyi", "pee"],
  "CHIN": ["chin", "kyin"],
  "PR":   ["pr", "par", "pa"],
  "TR":   ["tr", "tar", "ta"],
  "NE":   ["ne", "nae", "nh"],
  "THAY": ["thay", "thae"],
  "LO":   ["lo", "loh"],
  "NAI":  ["nai", "naing"],
  "PAY":  ["pay", "pae"],
  "LITE": ["lite", "lait", "lik"],
  "NAW":  ["naw", "nor"],
  "BR":   ["br", "bar", "ba"],
  "BL":   ["bl", "bel"],
  "AYAN": ["a yan", "ayan", "ayyan"],
  "KHAE": ["khae", "khe", "khel", "kae"],
  "TOT":  ["tot", "toh", "taw"],
  "OWN":  ["own", "oo", "ohn", "ounn"],
  "SOT":  ["sot", "sote"],
  "TAT":  ["tat", "tet"],
  "PHOE": ["phoe", "hpo", "pho"],
  "YAE":  ["yae", "yel", "yeh"],
  "SAY":  ["say", "sae", "se"],
  "THWAR":["thwar", "thwa"],
}

# ================================================================ frames
FRAMES = []
def fr(fid, pattern, bur, en): FRAMES.append({"id": fid, "pattern": pattern, "burmese": bur, "english": en})

fr('tl',        ["P","TL"],                "{P}တယ်",        "{v} (statement)")
fr('lrr',       ["P","LRR"],               "{P}လား",        "{v}?")
fr('ml',        ["P","ML"],                "{P}မယ်",        "will {v}")
fr('ma_lrr',    ["P","=ma","LRR"],         "{P}မလား",       "going to {v}?")
fr('ml_lrr',    ["P","ML:2","LRR:2"],      "{P}မလား",       "going to {v}?")
fr('ml_naw',    ["P","ML:2","NAW"],        "{P}မယ်နော်",     "will {v}, okay?")
fr('tl_naw',    ["P","TL:2","NAW"],        "{P}တယ်နော်",     "{v}, you know")
fr('ny_tl',     ["P","NY","TL:2"],         "{P}နေတယ်",      "currently {v}")
fr('ny_lrr',    ["P","NY","LRR:2"],        "{P}နေလား",      "currently {v}?")
fr('ny_p',      ["P","NY","FIN"],            "{P}နေပြီ",       "{v} now")
fr('ny_tr',     ["P","NY","TR:2"],         "{P}နေတာ",       "been {v}")
fr('ny_tr_lrr', ["P","NY:1","TR:2","LRR:2"],"{P}နေတာလား",   "are you {v}?")
fr('p',         ["P","FIN"],                 "{P}ပြီ",         "{v} now / already")
fr('p_lrr',     ["P","=p|pyi|pi","LRR:2"], "{P}ပြီလား",      "{v} already?")
fr('pp',        ["P","PP"],                "{P}ပြီးပြီ",      "finished {v}")
fr('pp_lrr',    ["P","PP:2","LRR:2"],      "{P}ပြီးပြီလား",   "finished {v}?")
fr('pyi_conn',  ["P","PYI"],               "{P}ပြီး",        "after {v}")
fr('chin_tl',   ["P","CHIN","TL:2"],       "{P}ချင်တယ်",     "want to {v}")
fr('chin_lrr',  ["P","CHIN","LRR:2"],      "{P}ချင်လား",     "want to {v}?")
fr('chin_p',    ["P","CHIN","FIN"],          "{P}ချင်ပြီ",      "want to {v} now")
fr('chin_lo',   ["P","CHIN","LO"],         "{P}ချင်လို့",     "because I want to {v}")
fr('chin_yin',  ["P","CHIN","=yin"],       "{P}ချင်ရင်",     "if you want to {v}")
fr('tr',        ["P","TR"],                "{P}တာ",         "{v} (it is that)")
fr('tr_lrr',    ["P","TR:2","LRR:2"],      "{P}တာလား",      "is it that you {v}?")
fr('pr_tl',     ["P","PR:2","TL:2"],       "{P}ပါတယ်",      "{v} (polite)")
fr('ya_lrr',    ["P","=ya","LRR:2"],       "{P}ရလား",       "can/may {v}?")
fr('ya_tl',     ["P","=ya","TL:2"],        "{P}ရတယ်",       "got to {v}")
fr('ya_ml',     ["P","=ya","ML"],          "{P}ရမယ်",       "have to {v}")
fr('lo_ya_lrr', ["P","LO","=ya","LRR:2"],  "{P}လို့ရလား",    "is it okay to {v}?")
fr('lo_ya_tl',  ["P","LO","=ya","TL:2"],   "{P}လို့ရတယ်",    "it is okay to {v}")
fr('nai_tl',    ["P","NAI","TL:2"],        "{P}နိုင်တယ်",     "can {v}")
fr('nai_lrr',   ["P","NAI","LRR:2"],       "{P}နိုင်လား",     "able to {v}?")
fr('tat_tl',    ["P","TAT","TL:2"],        "{P}တတ်တယ်",     "know how to {v}")
fr('tat_lrr',   ["P","TAT","LRR:2"],       "{P}တတ်လား",     "know how to {v}?")
fr('khae_tl',   ["P","KHAE","TL:2"],       "{P}ခဲ့တယ်",      "{v} (past)")
fr('khae_lrr',  ["P","KHAE","LRR:2"],      "{P}ခဲ့လား",      "did you {v}?")
fr('tot_ml',    ["P","TOT","ML:2"],        "{P}တော့မယ်",     "about to {v}")
fr('ma_loh',    ["P","=ma","LO"],          "{P}မလို့",        "was going to {v}")
fr('lo',        ["P","LO"],                "{P}လို့",         "because {v}")
fr('yin',       ["P","=yin"],              "{P}ရင်",         "if/when {v}")
fr('phoe',      ["P","PHOE"],              "{P}ဖို့",         "to {v}")
fr('phoe_lo_tl',["P","PHOE:1","=lo","TL:2"],"{P}ဖို့လိုတယ်",   "need to {v}")
fr('thwar_p',   ["P","THWAR","FIN"],         "{P}သွားပြီ",      "has become {v} / {v} away")
fr('thwar_tl',  ["P","THWAR","TL:2"],      "{P}သွားတယ်",     "became {v}")
fr('lite_tr',   ["P","LITE","TR:2"],       "{P}လိုက်တာ",     "so {v}!")
fr('pr',        ["P","PR"],                "{P}ပါ",          "please {v}")
fr('own',       ["P","OWN"],               "{P}ဦး",          "{v} some more / first")
fr('pr_own',    ["P","PR:2","OWN:2"],      "{P}ပါဦး",        "please {v}")
fr('pay',       ["P","PAY"],               "{P}ပေး",         "{v} for someone")
fr('pay_pr',    ["P","PAY","PR:2"],        "{P}ပေးပါ",       "please {v} (for me)")
fr('pay_ml',    ["P","PAY:2","ML:2"],      "{P}ပေးမယ်",      "will {v} for you")
fr('pay_own',   ["P","PAY:1","OWN:2"],     "{P}ပေးဦး",       "{v} for me, please")
fr('lite',      ["P","LITE"],              "{P}လိုက်",        "{v} (go ahead)")
fr('lite_pr',   ["P","LITE:2","PR:2"],     "{P}လိုက်ပါ",      "go ahead and {v}")
fr('lite_p',    ["P","LITE:2","FIN"],        "{P}လိုက်ပြီ",      "went ahead and {v}")
fr('lite_ml',   ["P","LITE:2","ML:2"],     "{P}လိုက်မယ်",     "will {v}")
fr('kya',       ["P","=kya"],              "{P}ကြ",          "{v} (you all)")
fr('kya_ml',    ["P","=kya","ML:2"],       "{P}ကြမယ်",       "we will {v}")
fr('kya_sot',   ["P","=kya","SOT"],        "{P}ကြစို့",       "let's {v}")
fr('sot',       ["P","SOT"],               "{P}စို့",         "let's {v}")
fr('ayan_tl',   ["AYAN","P","TL:2"],       "အရမ်း{P}တယ်",   "very {v}")
fr('thate_tl',  ["=thate|thait","P","TL:2"],"သိပ်{P}တယ်",    "so {v}")
fr('neg_bu',    ["N","BU"],                "{N}ဘူး",         "not {v}")
fr('neg_pr_bu', ["N","PR:2","BU:2"],       "{N}ပါဘူး",       "really not {v}")
fr('neg_thay_bu',["N","THAY","BU:2"],      "{N}သေးဘူး",      "not {v} yet")
fr('neg_tot_bu',["N","TOT","BU:2"],        "{N}တော့ဘူး",     "not {v} any more")
fr('neg_khae_bu',["N","KHAE:2","BU:2"],    "{N}ခဲ့ဘူး",       "didn't {v}")
fr('neg_chin_bu',["N","CHIN","BU:2"],      "{N}ချင်ဘူး",      "don't want to {v}")
fr('neg_ya_bu', ["N","=ya","BU:2"],        "{N}ရဘူး",        "can't / didn't get to {v}")
fr('lo_neg_ya_bu',["P","LO","=ma","=ya","BU:2"],"{P}လို့မရဘူး", "not allowed to {v}")
fr('neg_nai_bu',["N","NAI","BU:2"],        "{N}နိုင်ဘူး",      "unable to {v}")
fr('neg_tat_bu',["N","TAT","BU:2"],        "{N}တတ်ဘူး",      "don't know how to {v}")
fr('neg_ne',    ["N","NE"],                "{N}နဲ့",          "don't {v}")
fr('neg_pr_ne', ["N","PR:2","NE:2"],       "{N}ပါနဲ့",        "please don't {v}")
fr('neg_ne_naw',["N","NE:2","NAW"],        "{N}နဲ့နော်",       "don't {v}, okay?")
fr('neg_bu_lrr',["N","BU:2","LRR:2"],      "{N}ဘူးလား",      "don't you {v}?")
fr('lar_p',     ["P","=lar","FIN"],        "{P}လာပြီ",       "getting {v} now")
fr('lar_p_lrr', ["P","=lar","=p|pi|pyi","LRR:2"],"{P}လာပြီလား", "getting {v}?")
fr('lar_tl',    ["P","=lar","TL:2"],       "{P}လာတယ်",      "becoming {v}")
fr('yae_lrr',   ["P","YAE","LRR"],         "{P}ရဲ့လား",       "{v}, right? / are you {v}?")
fr('thay_lrr',  ["P","THAY","LRR:2"],      "{P}သေးလား",      "still {v}?")
fr('ny_thay_lrr',["P","NY","THAY","LRR:2"],"{P}နေသေးလား",   "still {v}-ing?")
fr('pr_say',    ["P","PR:2","SAY"],        "{P}ပါစေ",        "may you be {v}")
fr('phoe_plan', ["P","PHOE","=si sin|sisin|si zin","=htar|hta","TL:2"], "{P}ဖို့စီစဉ်ထားတယ်", "planning to {v}")
fr('phoe_try',  ["P","PHOE","=kyo sar|kyoe sar|kyo zar","NY:1","TL:2"], "{P}ဖို့ကြိုးစားနေတယ်", "trying to {v}")
fr('br_ny_ll',  ["BR","P","NY","LL:2"],    "ဘာ{P}နေလဲ",     "what are you {v}-ing?")
fr('br_ny_tr_ll',["BR:2","P","NY:2","TR:2","LL:2"],"ဘာ{P}နေတာလဲ","what are you {v}-ing?")
fr('br_ml',     ["BR","P","ML"],           "ဘာ{P}မလဲ",      "what will you {v}?")
fr('br_ma_ll',  ["BR:2","P","=ma","LL:2"], "ဘာ{P}မလဲ",      "what will you {v}?")
fr('br_chin_ll',["BR","P","CHIN","LL:2"],  "ဘာ{P}ချင်လဲ",    "what do you want to {v}?")
fr('br_tr_ll',  ["BR","P","TR:2","LL:2"],  "ဘာ{P}တာလဲ",     "what did you {v}?")
fr('br_ya_ml',  ["BR:2","P","=ya","ML:2"], "ဘာ{P}ရမလဲ",     "what should I {v}?")
fr('br_khae_ll',["BR:2","P","KHAE:2","LL:2"],"ဘာ{P}ခဲ့လဲ",    "what did you {v}?")
fr('bllo_ml',   ["BL","=lo","P","ML:2"],   "ဘယ်လို{P}မလဲ",  "how will you {v}?")
fr('bllo_ya_ml',["BL:2","=lo","P","=ya","ML:2"],"ဘယ်လို{P}ရမလဲ","how should I {v}?")
fr('bltaw_ml',  ["BL","=taw","P","ML:2"],  "ဘယ်တော့{P}မလဲ", "when will you {v}?")
fr('blmha_ml',  ["BL:2","=mha|hma","P","ML:2"],"ဘယ်မှာ{P}မလဲ","where will you {v}?")
fr('bl_ml',     ["BL","P","ML"],           "ဘယ်{P}မလဲ",     "where will you {v}?")
fr('bl_ny_ll',  ["BL","P","NY","LL:2"],    "ဘယ်{P}နေလဲ",    "where are you {v}-ing?")
fr('bl_khae_ll',["BL:2","P","KHAE:2","LL:2"],"ဘယ်{P}ခဲ့လဲ",   "where did you {v}?")

FIDS = {f["id"] for f in FRAMES}

STATE = ['tl','lrr','ml','ma_lrr','tl_naw','ny_tl','ny_lrr','p','p_lrr','tr','tr_lrr','pr_tl','ayan_tl','thate_tl',
         'lite_tr','thwar_p','thwar_tl','lo','yin','khae_tl','neg_bu','neg_pr_bu','neg_thay_bu','neg_tot_bu','neg_bu_lrr',
         'lar_p','lar_p_lrr','lar_tl','yae_lrr','thay_lrr','ny_thay_lrr','pr_say']
EMOTION = STATE + ['chin_tl']
KNOW = ['tl','lrr','ml','ny_tl','p','p_lrr','tr','tr_lrr','pr_tl','chin_tl','chin_lrr','lo','yin','khae_tl','khae_lrr',
        'neg_bu','neg_pr_bu','neg_thay_bu','neg_chin_bu','neg_khae_bu','neg_tot_bu','neg_bu_lrr']
VERB = ['tl','lrr','ml','ma_lrr','ml_lrr','ml_naw','ny_tl','ny_lrr','ny_p','ny_tr','ny_tr_lrr','p','p_lrr','pp','pp_lrr',
        'pyi_conn','chin_tl','chin_lrr','chin_p','chin_lo','chin_yin','tr','tr_lrr','pr_tl','ya_lrr','ya_tl','ya_ml',
        'lo_ya_lrr','lo_ya_tl','nai_tl','nai_lrr','tat_tl','tat_lrr','khae_tl','khae_lrr','tot_ml','ma_loh','lo','yin',
        'phoe','phoe_lo_tl','thwar_p','pr','own','pr_own','pay','pay_pr','pay_ml','pay_own','lite','lite_pr','lite_p',
        'lite_ml','kya','kya_ml','kya_sot','sot','neg_bu','neg_pr_bu','neg_thay_bu','neg_tot_bu','neg_khae_bu',
        'neg_chin_bu','neg_ya_bu','lo_neg_ya_bu','neg_nai_bu','neg_tat_bu','neg_ne','neg_pr_ne','neg_ne_naw','neg_bu_lrr',
        'phoe_plan','phoe_try']
WH = ['br_ny_ll','br_ny_tr_ll','br_ml','br_ma_ll','br_chin_ll','br_tr_ll','br_ya_ml','br_khae_ll','bllo_ml',
      'bllo_ya_ml','bltaw_ml','blmha_ml']
VERB_WH = VERB + WH
MOTION = VERB + ['bl_ml','bl_ny_ll','bl_khae_ll','bltaw_ml']
ACTIVITY = ['ml','ny_tl','phoe_lo_tl','phoe_plan','phoe_try','p','pp','pp_lrr','p_lrr','chin_tl','khae_tl','ya_ml',
            'pr','pay_pr','lrr','tl','tot_ml','ma_loh','lo_ya_lrr','ma_lrr']
FRAME_SETS = {"ACTIVITY": ACTIVITY, "STATE": STATE, "EMOTION": EMOTION, "KNOW": KNOW, "VERB": VERB, "VERB_WH": VERB_WH, "MOTION": MOTION}
for k, v in FRAME_SETS.items():
    assert all(x in FIDS for x in v), (k, [x for x in v if x not in FIDS])

# ================================================================ predicates
# (latin, burmese, english, frames, token, extra)
# frames: set name, or (set name, [exclude], [include])
PRED = []
def pr(latin, bur, en, frames, token=True, **kw):
    PRED.append((latin, bur, en, frames, token, kw))

# --- action verbs with wh-question frames
pr(["lote","loat","lok"], "လုပ်", "do", "VERB_WH")
pr(["sar"], "စား", "eat", ("VERB_WH", ['tl','lrr','ny_tl','ny_lrr','lo','yin'], []))
pr(["thout","thauk","thoke"], "သောက်", "drink", "VERB_WH")
pr(["pyaw"], "ပြော", "say", ("VERB_WH", ['tl','lrr','ny_tl','ny_lrr','lo'], []))
pr(["may","mayy","mae"], "မေး", "ask", "VERB_WH")
pr(["kyi","kyee","kyih"], "ကြည့်", "look/watch", "VERB_WH")
pr(["wel","wal","wae"], "ဝယ်", "buy", "VERB_WH")
pr(["phat","phet"], "ဖတ်", "read", "VERB_WH")
pr(["yay","yae"], "ရေး", "write", ("VERB_WH", ['tl','lrr','tr','tr_lrr','lo','yin'], []), False)
pr(["chet"], "ချက်", "cook", "VERB_WH")
pr(["ga zar","gazar","ka zar","kazar"], "ကစား", "play", "VERB_WH")
pr(["sot","hsot"], "ဆော့", "play around", ("VERB_WH", ['sot','kya_sot'], []))
pr(["shar","sha"], "ရှာ", "look for", "VERB_WH")
pr(["yu"], "ယူ", "take", "VERB_WH")
pr(["pay","pae"], "ပေး", "give", ("VERB_WH", ['pay','pay_pr','pay_ml','pay_own'], []))
pr(["phyay","phye","phyae"], "ဖြေ", "answer", "VERB_WH")
pr(["khaw","khor"], "ခေါ်", "call", "VERB_WH")
pr(["yaung"], "ရောင်း", "sell", "VERB_WH")
pr(["thin"], "သင်", "teach/learn", "VERB_WH", False)
pr(["hmar"], "မှာ", "order", ("VERB", ['tl','lrr','lo','yin','tr','tr_lrr'], ['br_ml','br_ma_ll','br_chin_ll','br_tr_ll']), False)
pr(["tin"], "တင်", "put up/post", ("VERB", ['lo','yin'], []), False)
pr(["sin zar","sinzar","sin sar","sein sar"], "စဉ်းစား", "think about", "VERB_WH")
pr(["shin|pya","shin|pyar"], "ရှင်း|ပြ", "explain", "VERB_WH", False)
# --- motion verbs
pr(["thwar","thwa","twar"], "သွား", "go", ("MOTION", ['thwar_p'], []))
pr(["lar"], "လာ", "come", ("MOTION", ['lo'], []))
pr(["pyan"], "ပြန်", "go back", "MOTION")
pr(["pyan|lar"], "ပြန်|လာ", "come back", "MOTION", False)
pr(["pyan|thwar","pyan|thwa"], "ပြန်|သွား", "go back", ("MOTION", ['thwar_p'], []), False)
pr(["pyan|yout","pyan|yauk"], "ပြန်|ရောက်", "get back", "MOTION", False)
pr(["yout","yauk","yok"], "ရောက်", "arrive", "MOTION")
pr(["htwet","htwat"], "ထွက်", "leave/go out", "MOTION")
pr(["a pyin|thwar","apyin|thwar"], "အပြင်|သွား", "go out", ("MOTION", ['thwar_p'], []), False)
pr(["tet"], "တက်", "go up/attend", "MOTION")
pr(["sin"], "ဆင်း", "get off/go down", "VERB")
pr(["pyay"], "ပြေး", "run", "VERB")
# --- other action verbs
pr(["eik","ake","eit"], "အိပ်", "sleep", "VERB")
pr(["noe"], "နိုး", "wake up", "VERB")
pr(["hta"], "ထ", "get up", "VERB")
pr(["twe","tweh","dwe"], "တွေ့", "meet/see", "VERB")
pr(["saung","saunt"], "စောင့်", "wait", "VERB")
pr(["po","poh"], "ပို့", "send", "VERB")
pr(["phwint","pwint"], "ဖွင့်", "open/turn on", "VERB")
pr(["pate","peik"], "ပိတ်", "close/turn off", "VERB")
pr(["pyin"], "ပြင်", "fix", ("VERB", ['tl','lrr','ny_tl','ny_lrr','neg_bu','neg_pr_bu','neg_thay_bu','lo','yin','tr','tr_lrr'], []), False)
pr(["pyaung"], "ပြောင်း", "change/move", "VERB")
pr(["kaing","kine"], "ကိုင်", "hold", "VERB")
pr(["mhat","hmat"], "မှတ်", "note/remember", "VERB")
pr(["ku"], "ကူ", "help", "VERB")
pr(["ku nyi","kunyi"], "ကူညီ", "help", "VERB")
pr(["pya"], "ပြ", "show", "VERB")
pr(["htaing","htine"], "ထိုင်", "sit", "VERB")
pr(["yat"], "ရပ်", "stop", "VERB")
pr(["maung"], "မောင်း", "drive", "VERB", False)
pr(["shaw"], "လျှော်", "wash", "VERB")
pr(["ngo"], "ငို", "cry", "VERB")
pr(["yel","yal"], "ရယ်", "laugh", "VERB")
pr(["pyone"], "ပြုံး", "smile", "VERB")
pr(["phyat"], "ဖြတ်", "cut", "VERB")
pr(["sone phyat","hsone phyat","sonephyat"], "ဆုံးဖြတ်", "decide", "VERB")
pr(["sa"], "စ", "start", ("VERB", ['tl','lrr','lo','yin','tr','tr_lrr','pr','own','sot','kya'], []), False)
pr(["mway"], "မွေး", "be born", ['tl','khae_tl','p','khae_lrr'])
pr(["yone"], "ယုံ", "believe", "KNOW", False)
pr(["htin"], "ထင်", "think", "KNOW")
pr(["nar"], "နား", "rest", ['ml','ml_naw','lite','lite_pr','pr','own','p','chin_tl','neg_ne','kya_sot','sot'], False)
pr(["kyar","kya"], "ကြာ", "take long", ['tl','lrr','p','p_lrr','ml','tr','neg_bu','neg_thay_bu','ayan_tl','khae_tl'])
pr(["san|kyi","san|kyee"], "စမ်း|ကြည့်", "try", "VERB", False)
pr(["lar|khaw","lar|khor"], "လာ|ခေါ်", "come to pick up", "VERB", False)
pr(["lite|po","lite|poh"], "လိုက်|ပို့", "take someone / see off", "VERB", False)
# --- compound activities
pr(["ein|pyan"], "အိမ်|ပြန်", "go home", "VERB", False)
pr(["ein|yout"], "အိမ်|ရောက်", "reach home", "VERB", False)
pr(["kyaung|thwar","kyaung|twar"], "ကျောင်း|သွား", "go to school", "VERB", False)
pr(["kyaung|tet","kyaung|tat"], "ကျောင်း|တက်", "attend school", "VERB", False)
pr(["a lote|thwar","alote|thwar"], "အလုပ်|သွား", "go to work", "VERB", False)
pr(["a lote|lote","alote|lote"], "အလုပ်|လုပ်", "work", "VERB", False)
pr(["a lote|win","alote|win"], "အလုပ်|ဝင်", "start work", "VERB", False)
pr(["a lote|sin","alote|sin"], "အလုပ်|ဆင်း", "finish work", "VERB", False)
pr(["htamin|sar","hta min|sar","tamin|sar"], "ထမင်း|စား", "have a meal", "VERB", False)
pr(["mont|sar","mone|sar"], "မုန့်|စား", "have a snack", "VERB", False)
pr(["kaw fee|thout","kawfee|thout","coffee|thout"], "ကော်ဖီ|သောက်", "drink coffee", "VERB", False)
pr(["laphet yay|thout","laphetyay|thout","lap phet yay|thout"], "လက်ဖက်ရည်|သောက်", "have tea", "VERB", False)
pr(["hsay|thout","hsay|thauk","say|thout"], "ဆေး|သောက်", "take medicine", "VERB", False)
pr(["yay|cho","yay|chot","ye|cho"], "ရေ|ချိုး", "shower", "VERB", False)
pr(["yay|thout","ye|thout"], "ရေ|သောက်", "drink water", "VERB", False)
pr(["sar|kyat","sar|kyet"], "စာ|ကျက်", "study", "VERB", False)
pr(["sar|phat","sar|phet"], "စာ|ဖတ်", "read/study", "VERB", False)
pr(["sar|po","sar|poh"], "စာ|ပို့", "send a message", "VERB", False)
pr(["phone|set","phone|sat"], "ဖုန်း|ဆက်", "phone someone", "VERB", False)
pr(["phone|khaw"], "ဖုန်း|ခေါ်", "call on the phone", "VERB", False)
pr(["phone|kine","phone|kaing"], "ဖုန်း|ကိုင်", "pick up the phone", "VERB", False)
pr(["phone|pate","phone|peik"], "ဖုန်း|ပိတ်", "turn off the phone", "VERB", False)
pr(["tha ti|thar","thati|thar"], "သတိ|ထား", "be careful", "VERB", False)
# --- knowing / existence
pr(["thi","ti","thee"], "သိ", "know", "KNOW")
pr(["nar|lal","na|lal","nar|lel","narlal","nalal"], "နား|လည်", "understand", "KNOW")
pr(["hok","hout","hote","hoke"], "ဟုတ်", "be so/true", ['tl','lrr','tl_naw','tr','tr_lrr','pr_tl','neg_bu','neg_pr_bu','neg_bu_lrr','yin','lo'])
pr(["shi","shee"], "ရှိ", "have/exist", ("KNOW", [], ['ny_lrr']))
pr(["ya"], "ရ", "get/can", ['tl','lrr','p','p_lrr','pr_tl','tl_naw','khae_tl','lo','yin','neg_bu','neg_pr_bu','neg_thay_bu','neg_khae_bu','neg_bu_lrr'])
pr(["phyit","phit"], "ဖြစ်", "happen/be", ("KNOW", [], ['ny_tl','tot_ml']))
pr(["lo"], "လို", "need", ['tl','lrr','neg_bu','neg_pr_bu','pr_tl','chin_tl','neg_tot_bu'], False)
# --- emotions
pr(["chit"], "ချစ်", "love", "EMOTION")
pr(["kyite","kyike"], "ကြိုက်", "like", "EMOTION")
pr(["lwan"], "လွမ်း", "miss", "EMOTION")
pr(["tha ti|ya","thati|ya","thatiya"], "သတိ|ရ", "remember/miss", "EMOTION")
pr(["mone"], "မုန်း", "hate", "EMOTION")
pr(["pyaw"], "ပျော်", "happy/fun", "STATE", False)
pr(["pyin"], "ပျင်း", "bored/lazy", "STATE", False)
pr(["sar"], "ဆာ", "hungry", ['tl','lrr','ny_tl','ny_lrr','ayan_tl','lo','yin'], False)
pr(["bike|sar","baik|sar"], "ဗိုက်|ဆာ", "hungry", "STATE", False)
pr(["sate|nyit","seit|nyit","sait|nyit"], "စိတ်|ညစ်", "stressed", "STATE", False)
pr(["sate|pu","seit|pu","sait|pu"], "စိတ်|ပူ", "worried", ("STATE", [], ['neg_ne','neg_pr_ne','neg_ne_naw']), False)
pr(["sate|soe","seit|soe","sait|soe"], "စိတ်|ဆိုး", "angry", ("STATE", [], ['neg_ne','neg_pr_ne','neg_ne_naw']), False)
pr(["sate|kg","seit|kg","sate|kaung","seit|kaung"], "စိတ်|ကောင်း", "kind (neg: feel bad/sorry)", "STATE", False)
pr(["sate|shote","seit|shote","sate|shoke"], "စိတ်|ရှုပ်", "confused/annoyed", "STATE", False)
pr(["sate|win zar","seit|win zar","sate|win sar"], "စိတ်|ဝင်စား", "interested", "STATE", False)
pr(["kyout","kyauk"], "ကြောက်", "afraid", ("STATE", [], ['neg_ne']))
pr(["lant"], "လန့်", "startled", "STATE")
pr(["wan thar","wanthar"], "ဝမ်းသာ", "glad", ("STATE", [f for f in STATE if f.startswith('neg')], []))
pr(["wan nee","wannee"], "ဝမ်းနည်း", "sad", ("STATE", [f for f in STATE if f.startswith('neg')], ['neg_ne']))
pr(["shet"], "ရှက်", "shy/embarrassed", ("STATE", [], ['neg_ne']))
pr(["tha nar","thanar"], "သနား", "pity", "STATE")
pr(["kyay nat","kyaynat"], "ကျေနပ်", "satisfied", "STATE")
# --- physical states / adjectives
pr(["ny|kg","nay|kaung","nay|kg","ny|kaung"], "နေ|ကောင်း", "be well", "STATE", False)
pr(["kg","kaung"], "ကောင်း", "good", "STATE")
pr(["sar|kg","sar|kaung"], "စား|ကောင်း", "tasty", "STATE", False)
pr(["a sin|pyay","asin|pyay","a sin|pyae","asin|pyae","a hsin|pyay"], "အဆင်|ပြေ", "okay/convenient", "STATE", False)
pr(["pin pan","pinpan"], "ပင်ပန်း", "tired", "STATE")
pr(["maw"], "မော", "tired/out of breath", "STATE")
pr(["ngite"], "ငိုက်", "sleepy", "STATE")
pr(["nar"], "နာ", "hurt/sore", ['tl','lrr','ny_tl','ayan_tl','thate_tl','neg_bu','neg_thay_bu','neg_tot_bu','khae_tl','thay_lrr','ny_thay_lrr','lar_p','lar_p_lrr'], True, confidence="medium")
pr(["phyar"], "ဖျား", "have a fever", "STATE")
pr(["gaung|kite","khaung|kite"], "ခေါင်း|ကိုက်", "have a headache", "STATE", False)
pr(["chaung|soe","chaung|hsoe"], "ချောင်း|ဆိုး", "have a cough", "STATE", False)
pr(["kyan mar","kyanmar"], "ကျန်းမာ", "healthy", ("STATE", [f for f in STATE if f.startswith('neg')], []))
pr(["pu"], "ပူ", "hot", "STATE")
pr(["chan"], "ချမ်း", "cold (feel)", "STATE")
pr(["aye","ay"], "အေး", "cool/cold", "STATE")
pr(["nwe","nway"], "နွေး", "warm", "STATE")
pr(["hla"], "လှ", "pretty", "STATE")
pr(["chaw"], "ချော", "good-looking", "STATE")
pr(["mike"], "မိုက်", "cool/awesome", "STATE")
pr(["yoo"], "ရူး", "crazy", "STATE")
pr(["soe"], "ဆိုး", "bad/naughty", "STATE")
pr(["khet"], "ခက်", "difficult", "STATE")
pr(["lwe","lwae"], "လွယ်", "easy", "STATE")
pr(["myan"], "မြန်", "fast", "STATE")
pr(["hnay"], "နှေး", "slow", "STATE")
pr(["myar"], "များ", "many/a lot", "STATE")
pr(["nee"], "နည်း", "few/little", "STATE")
pr(["myint"], "မြင့်", "high/tall", "STATE")
pr(["pein"], "ပိန်", "thin", "STATE")
pr(["wa","wah"], "ဝ", "fat", "STATE", False)
pr(["thant"], "သန့်", "clean", "STATE")
pr(["nyit pat","nyitpat"], "ညစ်ပတ်", "dirty", "STATE")
pr(["shote","shoke"], "ရှုပ်", "messy/complicated", "STATE")
pr(["pyet"], "ပျက်", "broken", "STATE")
pr(["pyout","pyauk"], "ပျောက်", "lost/gone", "STATE")
pr(["lan|pyout","lan|pyauk"], "လမ်း|ပျောက်", "lost (way)", "STATE", False)
pr(["hman"], "မှန်", "correct", "STATE")
pr(["mhar"], "မှား", "wrong", "STATE", False)
pr(["cho"], "ချို", "sweet", "STATE")
pr(["khar"], "ခါး", "bitter", "STATE")
pr(["ngan"], "ငန်", "salty", "STATE")
pr(["sat","sut"], "စပ်", "spicy", "STATE", False)
pr(["zay|gyi","zay|kyi"], "ဈေး|ကြီး", "expensive", "STATE", False)
pr(["zay|paw"], "ဈေး|ပေါ", "cheap", "STATE", False)
pr(["a yay|kyi","ayay|kyi","a yay|gyi"], "အရေး|ကြီး", "important", "STATE", False)
pr(["nout|kya","nauk|kya"], "နောက်|ကျ", "late", ("STATE", [], ['neg_ne','neg_ne_naw']), False)
pr(["a lote|myar","alote|myar"], "အလုပ်|များ", "busy", "STATE", False)
pr(["a lote|shote","alote|shote","a lote|shoke"], "အလုပ်|ရှုပ်", "busy", "STATE", False)
pr(["kyaung|pate","kyaung|peik"], "ကျောင်း|ပိတ်", "school is closed", "STATE", False)

# --- wellness / recovery
pr(["thet thar","thetthar","thet tha"], "သက်သာ", "feel better / eased", ("STATE", [f for f in STATE if f.startswith('neg')], []))
pr(["ny lo|kg","nay lo|kaung","ny loh|kg","nay loh|kaung"], "နေလို့|ကောင်း", "feel well", "STATE", False)
pr(["po|kg","po|kaung"], "ပို|ကောင်း", "better", ("STATE", [f for f in STATE if f.startswith('neg')], []), False)
pr(["pyan|kg","pyan|kaung"], "ပြန်|ကောင်း", "recover", "STATE", False)
pr(["a kyan mar","akyanmar"], "အကျန်းမာ", "healthy", ['pr_say'], False)
pr(["chan thar","chanthar"], "ချမ်းသာ", "rich / well-off", ("STATE", [f for f in STATE if f.startswith('neg')], []))
pr(["thar yar","tharyar"], "သာယာ", "pleasant", ("STATE", [f for f in STATE if f.startswith('neg')], []))
pr(["sayarwun|pya","sa yar wun|pya","sayawun|pya","sayarwon|pya"], "ဆရာဝန်|ပြ", "see a doctor", "VERB", False)
pr(["a nar|yu","anar|yu"], "အနား|ယူ", "rest", "VERB", False)
pr(["ga yu|sike","gayu|sike","ga yu|site","ga yu|saik"], "ဂရု|စိုက်", "take care", "VERB", False)
pr(["hmar|htar","hmar|hta"], "မှာ|ထား", "order / instruct (in advance)", "VERB", False)

# ================================================================ tokens and lexical phrases
tokens, lexical = [], []
def T(variants, burmese, english, typ, conf='high', **extra):
    singles = list(dict.fromkeys(norm(v) for v in variants if WORD.match(norm(v))))
    multis = list(dict.fromkeys(norm(v) for v in variants if ' ' in norm(v) and is_key(norm(v))))
    en = [e for e in (english if isinstance(english, list) else [english]) if e]
    if singles:
        e = {"variants": singles, "burmese": burmese, "english": en, "type": typ, "confidence": conf}
        e.update(extra); tokens.append(e)
    if multis:
        lexical.append((multis, burmese, en[0] if en else ""))

# --- address, family, people
T(["hyg","hyy","heyg","hy yaung","hay yaung","hey yaung"], "ဟေ့ရောင်", ["hey dude","hey bro"], "address")
T(["amay","amae","a may","a mae"], "အမေ", ["mother","mom"], "noun")
T(["aphay","aphe","a phay","a phe"], "အဖေ", ["father","dad"], "noun")
T(["mamae","maymay","maemae","may may","mae mae"], "မေမေ", ["mom"], "noun")
T(["phayphay","phephe","phay phay","phe phe"], "ဖေဖေ", ["dad"], "noun")
T(["aphwar","a phwar","a pwar"], "အဖွား", ["grandmother"], "noun")
T(["aphoe","a phoe"], "အဖိုး", ["grandfather"], "noun")
T(["ulay","u lay","u lae"], "ဦးလေး", ["uncle"], "noun")
T(["adaw","a daw"], "အဒေါ်", ["aunt"], "noun")
T(["thar"], "သား", ["son","I (son to parent)"], "noun/pronoun")
T(["thamee","thamii","tha mee"], "သမီး", ["daughter","I (daughter to parent)"], "noun/pronoun")
T(["ako","a ko","akoe"], "အကို", ["older brother"], "noun")
T(["koko","ko ko"], "ကိုကို", ["big brother (affectionate)"], "noun")
T(["ama"], "အမ", ["older sister"], "noun")
T(["mama"], "မမ", ["big sister"], "noun")
T(["nyi","nyii"], "ညီ", ["younger brother"], "noun")
T(["nyima","nyi ma"], "ညီမ", ["younger sister"], "noun")
T(["nyilay","nyi lay"], "ညီလေး", ["little brother"], "noun")
T(["nyimalay","nyi ma lay"], "ညီမလေး", ["little sister"], "noun")
T(["meinma","mein ma","mane ma"], "မိန်းမ", ["woman","wife"], "noun")
T(["youtkyar","yout kyar","yauk kyar"], "ယောက်ျား", ["man","husband"], "noun")
T(["mitharsu","mi thar su","mi tha su"], "မိသားစု", ["family"], "noun")
T(["thungechin","thu nge chin","thunge chin","tha nge chin"], "သူငယ်ချင်း", ["friend"], "noun")
T(["chitthu","chit thu"], "ချစ်သူ", ["sweetheart"], "noun")
T(["kaunglay","kaung lay","kg lay"], "ကောင်လေး", ["boy","boyfriend"], "noun")
T(["kaungmalay","kaung ma lay","kg ma lay"], "ကောင်မလေး", ["girl","girlfriend"], "noun")
T(["saya","sayar"], "ဆရာ", ["teacher","sir"], "noun")
T(["sayama","sayar ma","sa yar ma"], "ဆရာမ", ["(female) teacher"], "noun")
T(["kyaungthar","kyaung thar"], "ကျောင်းသား", ["student"], "noun")
T(["kyaungthu","kyaung thu"], "ကျောင်းသူ", ["(female) student"], "noun")
T(["lugyi","lu gyi"], "လူကြီး", ["adult","elder","boss"], "noun")
T(["kalay","klay","ka lay"], "ကလေး", ["child"], "noun")
T(["lu"], "လူ", ["person"], "noun")
# --- pronouns
T(["nga"], "ငါ", ["I","me"], "pronoun", register="casual/intimate")
T(["nin"], "နင်", ["you"], "pronoun", register="casual")
T(["min","ming"], "မင်း", ["you"], "pronoun", register="casual")
T(["thu"], "သူ", ["he","she"], "pronoun")
T(["thudo","thu do","thu to"], "သူတို့", ["they"], "pronoun")
T(["shin"], "ရှင်", ["you (female speaker, polite)"], "pronoun")
T(["kyanaw","kya naw","kya nor","kyanote"], "ကျွန်တော်", ["I (male, polite)"], "pronoun")
T(["kyama","kya ma","kya mal"], "ကျွန်မ", ["I (female, polite)"], "pronoun")
T(["khinbya","khin bya"], "ခင်ဗျား", ["you (polite)"], "pronoun")
T(["ngado","nga do","nga to"], "ငါတို့", ["we"], "pronoun")
T(["mindo","min do","ming do"], "မင်းတို့", ["you all"], "pronoun")
T(["nindo","nin do"], "နင်တို့", ["you all"], "pronoun")
T(["doe"], "တို့", ["plural (people)"], "particle")
# --- possessive / object forms (creaky tone ့)
T(["nga ko","ngako"], "ငါ့ကို", ["me (object)"], "pronoun")
T(["thu ko","thuko"], "သူ့ကို", ["him/her (object)"], "pronoun")
T(["nin ko","ninko"], "နင့်ကို", ["you (object)"], "pronoun")
T(["kya naw ko","kyanaw ko"], "ကျွန်တော့်ကို", ["me (object, polite)"], "pronoun")
T(["nga atwat","nga a twat"], "ငါ့အတွက်", ["for me"], "phrase")
T(["thu atwat","thu a twat"], "သူ့အတွက်", ["for him/her"], "phrase")
T(["min atwat","min a twat"], "မင်းအတွက်", ["for you"], "phrase")
# --- particles
T(["ko","koe"], "ကို", ["object marker","to"], "particle", note="engine.js always resolves ko/koe to ကို")
T(["ka","ga"], "က", ["subject/topic marker","from"], "particle")
T(["hmar","mhar","mar"], "မှာ", ["at","in"], "particle", "medium")
T(["mha","hma"], "မှာ", ["at","in"], "particle", "medium", note="engine.js resolves mha/hma itself; phrases give မှ")
T(["ne","nae","nh","net"], "နဲ့", ["with","and"], "particle", "medium")
T(["atwat","a twat"], "အတွက်", ["for"], "particle")
T(["kyount","kyaunt"], "ကြောင့်", ["because of"], "particle", "medium")
T(["phoe","hpo"], "ဖို့", ["in order to"], "particle")
T(["yin","yinn"], "ရင်", ["if","when"], "particle")
T(["si","hsi"], "ဆီ", ["to someone's place"], "particle", "medium")
T(["htel","htae"], "ထဲ", ["inside"], "particle", "medium")
T(["paw"], "ပေါ်", ["on"], "particle", "medium")
T(["tway","dway","tuy"], "တွေ", ["plural marker"], "particle")
T(["lrr","lr","lar","la"], "လား", ["yes/no question particle"], "particle")
T(["ll","le","lel"], "လဲ", ["wh-question particle"], "particle")
T(["tl","tal","te","tae","del","dl"], "တယ်", ["statement ending"], "particle")
T(["bu","boo","woo","wu","buu"], "ဘူး", ["negative ending"], "particle")
T(["ml","mel","mal"], "မယ်", ["will"], "particle")
T(["p","pi"], "ပြီ", ["already","now"], "particle")
T(["pyi","pee"], "ပြီး", ["finish","after","and then"], "verb/connector")
T(["pr","par","pa"], "ပါ", ["polite particle","also"], "particle")
T(["tr","tar","ta"], "တာ", ["nominalizer"], "particle")
T(["naw","nor","nawr"], "နော်", ["okay?","you know"], "particle")
T(["lay"], "လေး", ["little","softener"], "particle")
T(["pal","pel","pe","bal"], "ပဲ", ["only","just"], "particle", "medium")
T(["tot","toh","taw"], "တော့", ["then","as for"], "particle", "medium")
T(["yaw","yor"], "ရော", ["what about","also"], "particle", "medium")
T(["kwar","kwa"], "ကွာ", ["man!","dude"], "particle")
T(["loh","lo"], "လို့", ["because","quotative"], "particle")
T(["chin","kyin","gyin"], "ချင်", ["want to"], "auxiliary")
T(["nai","naing"], "နိုင်", ["can"], "auxiliary")
T(["lite","lait"], "လိုက်", ["go ahead and"], "auxiliary")
T(["khae","khe","khel"], "ခဲ့", ["past marker"], "auxiliary")
T(["own","ohn","ounn"], "ဦး", ["more","first"], "particle")
T(["thay","thae"], "သေး", ["yet","still","small"], "particle", "medium")
T(["ma"], "မ", ["not (prefix)"], "prefix", "medium")
T(["kya"], "ကြ", ["plural (verbs)"], "particle", "low")
# --- determiners / wh
T(["d","di","dii"], "ဒီ", ["this"], "determiner")
T(["ho"], "ဟို", ["that (over there)"], "determiner")
T(["ek","ae","eh"], "အဲ့", ["that"], "determiner")
T(["dr","dar"], "ဒါ", ["this","this thing"], "pronoun")
T(["hrr","har"], "ဟာ", ["thing"], "noun")
T(["aedar","edar","ekdr","ae dar","e dar","ek dr","ek dar"], "အဲ့ဒါ", ["that"], "pronoun")
T(["aelo","elo","eklo","ek lo","ae lo","e lo"], "အဲ့လို", ["like that"], "adverb")
T(["dilo","dlo","d lo","di lo"], "ဒီလို", ["like this"], "adverb")
T(["d hrr","di har","di ha","d har"], "ဒီဟာ", ["this thing"], "pronoun")
T(["ho har","ho hrr"], "ဟိုဟာ", ["that thing"], "pronoun")
T(["dimha","di mha","d mha"], "ဒီမှာ", ["here"], "location")
T(["homha","ho mha"], "ဟိုမှာ", ["there"], "location")
T(["aemha","ae mha","ek mha","ae hma"], "အဲ့မှာ", ["there"], "location")
T(["br","bar","ba"], "ဘာ", ["what"], "wh_word")
T(["bl","bel","bal"], "ဘယ်", ["which","where"], "wh_word")
T(["bllo","bello","bl lo","bel lo"], "ဘယ်လို", ["how"], "wh_word")
T(["blmha","belmha","bl mha","bel mha","bl hmar"], "ဘယ်မှာ", ["where"], "wh_word")
T(["blthu","belthu","bl thu","bel thu"], "ဘယ်သူ", ["who"], "wh_word")
T(["bl ka","bel ka"], "ဘယ်က", ["from where"], "wh_word")
T(["bltaw","beltaw","bl taw","bel taw"], "ဘယ်တော့", ["when"], "wh_word")
T(["bllout","bellout","bllauk","bl lout","bel lout","bl lauk"], "ဘယ်လောက်", ["how much"], "wh_word")
T(["bl nay yar","bel nay yar"], "ဘယ်နေရာ", ["which place"], "wh_word")
T(["br tway","bar tway","br dway"], "ဘာတွေ", ["what (things)"], "wh_word")
T(["br mha","bar mha","br hma","ba mha","bar hma"], "ဘာမှ", ["nothing","anything"], "pronoun")
T(["bl thu mha","bel thu mha","bl thu hma"], "ဘယ်သူမှ", ["nobody"], "pronoun")
T(["br lo","br loh","bar lo","bar loh","ba lo"], "ဘာလို့", ["why"], "wh_word")
T(["br phyit lo","bar phyit lo","ba phyit lo"], "ဘာဖြစ်လို့", ["why"], "wh_word")
# --- time
T(["akhu","khu","a khu"], "အခု", ["now"], "time")
T(["akhu mha","a khu mha"], "အခုမှ", ["only just now"], "time")
T(["khu mha"], "ခုမှ", ["only just now"], "time")
T(["dinay","dnay","d nay","di nay"], "ဒီနေ့", ["today"], "time")
T(["dinya","d nya","di nya"], "ဒီည", ["tonight"], "time")
T(["manayka","ma nay ka"], "မနေ့က", ["yesterday"], "time")
T(["manetphyan","mnetphyan","ma net phyan","manet phyan","mnet phyan"], "မနက်ဖြန်", ["tomorrow"], "time")
T(["manet","ma net"], "မနက်", ["morning"], "time")
T(["nay lel","naylel"], "နေ့လယ်", ["noon"], "time", "medium")
T(["nel","nal"], "နယ်", ["region, area","to knead"], "noun")
T(["nelmye","nel mye","nel myay","nel myae"], "နယ်မြေ", ["territory, area"], "noun")
T(["nelsat","nel sat","nel sut"], "နယ်စပ်", ["border area"], "noun")
T(["nelpal","nel pal","nel pel"], "နယ်ပယ်", ["field, domain"], "noun")
T(["neelan","nee lan","ni lan","nee lam"], "နည်းလမ်း", ["method, way"], "noun")
T(["neenee","nee nee"], "နည်းနည်း", ["a little"], "adverb")
T(["nyanay","nya nay"], "ညနေ", ["evening"], "time")
T(["nya"], "ည", ["night"], "time")
T(["nout nay","nauk nay"], "နောက်နေ့", ["the next day"], "time")
T(["nout mha","nauk mha","nout hma"], "နောက်မှ", ["later"], "time")
T(["khana","kha na"], "ခဏ", ["a moment"], "time")
T(["khanalay","kha na lay","khana lay"], "ခဏလေး", ["just a moment"], "time")
T(["khana khana","kha na kha na"], "ခဏခဏ", ["often"], "time")
T(["ayin","a yin"], "အရင်", ["before","first"], "time")
T(["ayinka","a yin ka"], "အရင်က", ["in the past"], "time")
T(["pyiyin","pyi yin","pee yin"], "ပြီးရင်", ["after that"], "time")
T(["makyakhin","ma kya khin"], "မကြာခင်", ["soon"], "time")
T(["chetchin","chet chin","chat chin"], "ချက်ချင်း", ["immediately"], "time")
T(["achain","a chain"], "အချိန်", ["time"], "noun")
T(["amye","a mye","a myae"], "အမြဲ", ["always"], "time")
T(["naryi","nar yi","nayi"], "နာရီ", ["hour","clock"], "noun")
T(["minit","mi nit"], "မိနစ်", ["minute"], "noun")
T(["yet"], "ရက်", ["day"], "noun", "medium")
T(["tapat","ta pat"], "တစ်ပတ်", ["one week"], "time")
T(["tayet","ta yet"], "တစ်ရက်", ["one day"], "time")
T(["takhar","ta khar"], "တခါ", ["once"], "time")
T(["manetsar","ma net sar"], "မနက်စာ", ["breakfast"], "noun")
T(["naylelsar","nay lel sar"], "နေ့လယ်စာ", ["lunch"], "noun")
T(["nyasar","nya sar"], "ညစာ", ["dinner"], "noun")
T(["mwaynay","mway nay","mwe nay"], "မွေးနေ့", ["birthday"], "noun")
T(["taninganway","ta nin ga nway"], "တနင်္ဂနွေ", ["Sunday"], "time")
T(["taninlar","ta nin lar"], "တနင်္လာ", ["Monday"], "time")
T(["ingar","in gar"], "အင်္ဂါ", ["Tuesday"], "time")
T(["bokdahu","boddahu","boke da hoo","bote da hu"], "ဗုဒ္ဓဟူး", ["Wednesday"], "time")
T(["kyarthapatay","kyar tha pa tay"], "ကြာသပတေး", ["Thursday"], "time")
T(["thoutkyar","thaukkyar","thout kyar"], "သောကြာ", ["Friday"], "time")
T(["sanay","sa nay"], "စနေ", ["Saturday"], "time")
# --- adverbs / connectors
T(["ayan","ayyan","a yan"], "အရမ်း", ["very","too"], "adverb")
T(["thate","thait"], "သိပ်", ["very"], "adverb")
T(["tkai","takel","takal","ta kel","ta kal","ta kai"], "တကယ်", ["really"], "adverb")
T(["nae nae","ne ne","nee nee"], "နည်းနည်း", ["a little"], "adverb")
T(["amyargyi","a myar gyi","amyar gyi","a myar kyi"], "အများကြီး", ["a lot"], "adverb")
T(["myan myan"], "မြန်မြန်", ["quickly"], "adverb")
T(["amyan","a myan"], "အမြန်", ["quickly"], "adverb")
T(["phyay phyay","phye phye"], "ဖြေးဖြေး", ["slowly"], "adverb")
T(["akone","a kone","a koan"], "အကုန်", ["all"], "adverb")
T(["akonelone","a kone lone"], "အကုန်လုံး", ["everything","everyone"], "adverb")
T(["lonewa","lone wa","lone wah"], "လုံးဝ", ["completely","at all"], "adverb")
T(["atutu","a tu tu"], "အတူတူ", ["together"], "adverb")
T(["atu","a tu"], "အတူ", ["together"], "adverb")
T(["pyitot","pyi tot","pyi taw"], "ပြီးတော့", ["and then"], "connector")
T(["dpm","dabaymae","dr pay mae","dar pay mae","da pay mae"], "ဒါပေမဲ့", ["but"], "connector")
T(["darkyount","dr kyount","dar kyount"], "ဒါကြောင့်", ["so","that's why"], "connector")
T(["ae dr kyount","ek dr kyount","ae dar kyount"], "အဲ့ဒါကြောင့်", ["that's why"], "connector")
T(["ma hote yin","ma hok yin"], "မဟုတ်ရင်", ["otherwise"], "connector")
T(["tayout","ta yout"], "တစ်ယောက်", ["one person"], "noun")
T(["hnityout","hnit yout"], "နှစ်ယောက်", ["two people"], "noun")
T(["takhu","ta khu"], "တစ်ခု", ["one thing"], "noun")
# --- interjections / greetings / politeness
T(["inn","ing"], "အင်း", ["yeah","mm"], "interjection")
T(["aw","aww"], "အော်", ["oh","I see"], "interjection", "medium")
T(["amaelay","a mae lay","a may lay"], "အမလေး", ["oh my god"], "interjection")
T(["mingalarpar","mingalarbar","mingalaba","mingalar par","mingalar pr","mingalar bar","min ga lar par"], "မင်္ဂလာပါ", ["hello"], "greeting")
T(["kyayzu","kyayzuu","kyay zu","kyay zuu","kyae zu"], "ကျေးဇူး", ["thanks"], "noun")
T(["taungpan","taung pan"], "တောင်းပန်", ["apologise"], "verb")
T(["hokkae","hok kae","hote kae","hoke kae","hok ke","hote ke"], "ဟုတ်ကဲ့", ["yes (polite)"], "interjection")
T(["ok","okay","oke","okeh"], "အိုကေ", ["okay"], "loanword")
T(["bro"], "ဘရို", ["bro"], "loanword/address")
T(["ty","thx","tq"], "ကျေးဇူးတင်ပါတယ်", ["thank you"], "chat_abbreviation")
T(["sry","sori"], "ဆောရီး", ["sorry"], "chat_abbreviation")
# --- places
T(["ein"], "အိမ်", ["home"], "noun")
T(["kyaung"], "ကျောင်း", ["school"], "noun")
T(["yone","yon"], "ရုံး", ["office"], "noun", "medium")
T(["zay"], "ဈေး", ["market","price"], "noun")
T(["sine","saing"], "ဆိုင်", ["shop"], "noun")
T(["sarthoutsine","sar thout sine"], "စားသောက်ဆိုင်", ["restaurant"], "noun")
T(["laphetyaysine","laphetyay sine","lap phet yay sine"], "လက်ဖက်ရည်ဆိုင်", ["tea shop"], "noun")
T(["phaya","hpaya","pha yar","hpa yar"], "ဘုရား", ["pagoda","Buddha"], "noun")
T(["tekkatho","tet kat tho","tet ka tho"], "တက္ကသိုလ်", ["university"], "noun")
T(["hsayyon","hsay yon","say yone","hsay yone"], "ဆေးရုံ", ["hospital"], "noun")
T(["layseik","lay sate","lay seik"], "လေဆိပ်", ["airport"], "noun")
T(["butar","bu tar"], "ဘူတာ", ["station"], "noun")
T(["einthar","ein thar"], "အိမ်သာ", ["toilet"], "noun")
T(["apyin","a pyin"], "အပြင်", ["outside"], "noun")
T(["ahtel","a htel"], "အထဲ", ["inside"], "noun")
T(["akhan","a khan"], "အခန်း", ["room"], "noun")
T(["lan"], "လမ်း", ["road","street"], "noun")
T(["myo"], "မြို့", ["town","city"], "noun")
T(["ywar"], "ရွာ", ["village"], "noun")
T(["kar"], "ကား", ["car"], "noun")
T(["layyin","lay yin"], "လေယာဉ်", ["plane"], "noun")
T(["yangon","ygn","yan gon","rangoon"], "ရန်ကုန်", ["Yangon"], "place")
T(["mandalay","mdy","man da lay"], "မန္တလေး", ["Mandalay"], "place")
T(["naypyitaw","npt","nay pyi taw"], "နေပြည်တော်", ["Naypyitaw"], "place")
T(["myanmar","myan mar"], "မြန်မာ", ["Myanmar"], "place")
T(["singapore","sing ga pu"], "စင်ကာပူ", ["Singapore"], "place")
# --- food
T(["htamin","tamin","hta min"], "ထမင်း", ["rice","meal"], "noun")
T(["hin"], "ဟင်း", ["curry","dish"], "noun")
T(["hincho","hin cho"], "ဟင်းချို", ["clear soup"], "noun")
T(["mohinga","mohingar","mote hin gar","mont hin gar"], "မုန့်ဟင်းခါး", ["mohinga"], "noun")
T(["laphet","lahpet","lap phet"], "လက်ဖက်", ["tea leaf salad"], "noun")
T(["laphetyay","lahpetyay","lap phet yay","laphet yay"], "လက်ဖက်ရည်", ["milk tea"], "noun")
T(["kawfee","kofi","kaw fee"], "ကော်ဖီ", ["coffee"], "noun")
T(["nwarno","nwar no","nwar noh"], "နွားနို့", ["milk"], "noun")
T(["kyetthar","kyet thar","kyat thar"], "ကြက်သား", ["chicken"], "noun")
T(["wetthar","wet thar"], "ဝက်သား", ["pork"], "noun")
T(["amaethar","a mae thar"], "အမဲသား", ["beef"], "noun")
T(["ngar"], "ငါး", ["fish","five"], "noun", "medium")
T(["khaukswe","khout swel","khout swe"], "ခေါက်ဆွဲ", ["noodles"], "noun")
T(["thitthee","thit thee","thit thi"], "သစ်သီး", ["fruit"], "noun")
T(["yaygel","yay khel","yay gel"], "ရေခဲ", ["ice"], "noun")
T(["kyet u","kyat u"], "ကြက်ဥ", ["egg"], "noun")
T(["mont","mone"], "မုန့်", ["snack","cake"], "noun", "low")
T(["yay","ye"], "ရေ", ["water"], "noun", "medium")
# --- other nouns
T(["alote","a lote"], "အလုပ်", ["work","job"], "noun")
T(["paiksan","pikesan","paik san","pike san"], "ပိုက်ဆံ", ["money"], "noun")
T(["kyat"], "ကျပ်", ["kyat (currency)"], "noun", "medium")
T(["narmae","nar mae","nar me"], "နာမည်", ["name"], "noun")
T(["athet","a thet"], "အသက်", ["age","life"], "noun")
T(["pyatthanar","pyatthana","pyat tha nar"], "ပြဿနာ", ["problem"], "noun")
T(["sagar","zagar","sa kar"], "စကား", ["words","speech"], "noun")
T(["aphyay","a phyay"], "အဖြေ", ["answer"], "noun")
T(["akyaung","a kyaung"], "အကြောင်း", ["about","reason"], "noun")
T(["ayar","a yar"], "အရာ", ["thing"], "noun")
T(["nayyar","nay yar"], "နေရာ", ["place"], "noun")
T(["athit","a thit"], "အသစ်", ["new (one)"], "noun")
T(["ahaung","a haung"], "အဟောင်း", ["old (one)"], "noun")
T(["theechin","thee chin","tha chin"], "သီချင်း", ["song"], "noun")
T(["yokeshin","yoke shin","yote shin"], "ရုပ်ရှင်", ["movie"], "noun")
T(["bawlone","baw lone"], "ဘောလုံး", ["football"], "noun")
T(["sate","seit"], "စိတ်", ["mind","mood"], "noun")
T(["achit","a chit"], "အချစ်", ["love (noun)"], "noun")
T(["gaung","khaung"], "ခေါင်း", ["head"], "noun")
T(["lat"], "လက်", ["hand"], "noun", "medium")
T(["chay","chae"], "ခြေ", ["foot"], "noun")
T(["myetlone","myet lone"], "မျက်လုံး", ["eye"], "noun")
T(["myethnar","myet hnar","myet nhar"], "မျက်နှာ", ["face"], "noun")
T(["hsay"], "ဆေး", ["medicine"], "noun")
T(["asinpyay"], "အဆင်ပြေ", ["okay"], "adjective")
# --- numbers
T(["tit"], "တစ်", ["one"], "number")
T(["hnit"], "နှစ်", ["two","year"], "number")
T(["thone"], "သုံး", ["three","use"], "number", "medium")
T(["chout","chauk"], "ခြောက်", ["six"], "number")
T(["khunit","khu nit"], "ခုနစ်", ["seven"], "number")
T(["sal"], "ဆယ်", ["ten"], "number", "medium")
T(["yar"], "ရာ", ["hundred"], "number", "medium")
T(["htaung"], "ထောင်", ["thousand"], "number")
T(["thaung"], "သောင်း", ["ten thousand"], "number")
T(["thein"], "သိန်း", ["hundred thousand"], "number")

# --- words around သာ/သား and မှာ/မှား, and health
T(["athar","a thar"], "အသား", ["meat","skin"], "noun")
T(["thar thamee","thar tha mee","tharthamee"], "သားသမီး", ["children"], "noun")
T(["amhar","a mhar","a hmar"], "အမှား", ["mistake"], "noun")
T(["amhan","a mhan","a hman"], "အမှန်", ["the truth","correct"], "noun")
T(["sayarwun","sa yar wun","sayawun","sayarwon"], "ဆရာဝန်", ["doctor"], "noun")
T(["kyanmaryay","kyan mar yay"], "ကျန်းမာရေး", ["health"], "noun")
T(["lunar","lu nar"], "လူနာ", ["patient"], "noun")
T(["thetthar","thet thar"], "သက်သာ", ["relieved","feeling better"], "adjective/state")
T(["a khu yaw","akhu yaw"], "အခုရော", ["and now?"], "phrase")

# predicate single-word fallbacks
for latin, bur, en, frames, tok, kw in PRED:
    if not tok: continue
    singles = [v for v in latin if '|' not in v and ' ' not in v]
    fs = frames if isinstance(frames, (str, list)) else frames[0]
    typ = 'verb' if fs in ('VERB', 'VERB_WH', 'MOTION') else 'adjective/state' if fs in ('STATE', 'EMOTION') else 'verb'
    conf = kw.get('confidence', 'medium' if latin[0] in ('sar', 'pyaw', 'lar', 'yone') else 'high')
    T(singles, bur.replace('|', ''), en, typ, conf)
# lower-priority alternative readings
T(["sar"], "ဆာ", ["hungry"], "adjective/state", "medium", ambiguous_with=["စား","စာ"])
T(["sar"], "စာ", ["text","lesson"], "noun", "low", ambiguous_with=["စား","ဆာ"])
T(["pyaw"], "ပျော်", ["happy"], "adjective/state", "medium", ambiguous_with=["ပြော"])
T(["pyin"], "ပျင်း", ["bored"], "adjective/state", "medium", ambiguous_with=["ပြင်"])
T(["lo"], "လို", ["need","like/as"], "verb/particle", "medium", ambiguous_with=["လို့"])
T(["may"], "မေ့", ["forget"], "verb", "low", ambiguous_with=["မေး"])

# ================================================================ curated phrases
phrases, owner = [], {}
def C(variants, burmese, english, confidence='high', **extra):
    kept = []
    for v in variants:
        k = norm(v)
        if is_key(k) and k not in owner:
            owner[k] = True; kept.append(k)
    if kept:
        it = {"myanglish": kept, "burmese": burmese, "english": english, "confidence": confidence}
        it.update(extra); phrases.append(it)

FIX = {"ကျေးဇူးနော် / ကျေးဇူးတင်ပါတယ်": "ကျေးဇူးနော်", "ဆောရီးနော် / တောင်းပန်ပါတယ်": "ဆောရီးနော်"}
for it in OLD['phrase_map']:
    C(it['myanglish'], FIX.get(it['burmese'], it['burmese']), it['english'], it.get('confidence', 'high'),
      **{k: it[k] for k in it if k == 'note'})

C(["kyay zu tin pr tl","kyay zu tin par tal","kyayzu tin pr tl","kyay zuu tin pr tl","kyay zu tin pr tal"], "ကျေးဇူးတင်ပါတယ်", "Thank you.")
C(["kyay zu tin tl","kyayzu tin tl","kyay zu tin tal"], "ကျေးဇူးတင်တယ်", "Thanks.")
C(["kyay zu pl","kyay zu pal","kyayzu pl","kyay zu pe","kyayzu pal"], "ကျေးဇူးပဲ", "Thanks!")
C(["kyay zu naw","kyayzu naw","ty naw","thx naw","tq naw"], "ကျေးဇူးနော်", "Thanks, okay?")
C(["kyay zu a myar gyi tin pr tl","kyayzu amyargyi tin pr tl"], "ကျေးဇူးအများကြီးတင်ပါတယ်", "Thank you very much.")
C(["taung pan pr tl","taung pan par tal","taungpan pr tl"], "တောင်းပန်ပါတယ်", "I apologise.")
C(["sry naw","sorry naw","sori naw"], "ဆောရီးနော်", "Sorry.")
C(["ya pr tl","ya par tal","ya pa tl"], "ရပါတယ်", "It's fine / no problem.")
C(["ok lrr","ok lar","okay lrr"], "အိုကေလား", "Okay?")
C(["ok tl","ok tal"], "အိုကေတယ်", "It's okay.")
C(["ny kg pr tl","nay kaung par tal","ny kg par tal"], "နေကောင်းပါတယ်", "I'm well.")
C(["ma pu pr ne","sate ma pu pr ne","seit ma pu par nae"], "စိတ်မပူပါနဲ့", "Please don't worry.")
C(["kg kg ny naw","kaung kaung nay naw"], "ကောင်းကောင်းနေနော်", "Take care.")
C(["a sin pyay pr tl","asin pyay pr tl"], "အဆင်ပြေပါတယ်", "It's fine.")
C(["br phyit ll","bar phyit le","br phit ll"], "ဘာဖြစ်လဲ", "What's up? / What's wrong?")
C(["br phyit ny tr ll","bar phyit nay tar le"], "ဘာဖြစ်နေတာလဲ", "What's going on?")
C(["br lo ll","br loh ll","bar lo le","ba lo le","bar loh le"], "ဘာလို့လဲ", "Why?")
C(["br tway lote ny ll","bar tway lote nay le","br dway lote ny ll"], "ဘာတွေလုပ်နေလဲ", "What are you up to?")
C(["br mha ma hok bu","br mha ma hok woo","bar mha ma hote bu"], "ဘာမှမဟုတ်ဘူး", "It's nothing.")
C(["br mha ma shi bu","br mha ma shi woo","bar mha ma shi bu"], "ဘာမှမရှိဘူး", "There's nothing.")
C(["br mha ma thi bu","bar mha ma thi bu"], "ဘာမှမသိဘူး", "I don't know anything.")
C(["br mha ma lote bu","bar mha ma lote bu"], "ဘာမှမလုပ်ဘူး", "I'm not doing anything.")
C(["br mha ma lote ny bu","bar mha ma lote nay bu"], "ဘာမှမလုပ်နေဘူး", "Not doing anything.")
C(["bl mha ny ll","bel mha nay le"], "ဘယ်မှာနေလဲ", "Where do you live / where are you?")
C(["bl lout kya p ll","bel lout kyar pyi le"], "ဘယ်လောက်ကြာပြီလဲ", "How long has it been?")
C(["bl lout lel","bl lauk ll","bel lauk le"], "ဘယ်လောက်လဲ", "How much?")
C(["bl lo ny ll","bel lo nay le"], "ဘယ်လိုနေလဲ", "How are things?")
C(["bl lo lote ya ml ll","bel lo lote ya mal le","bl lo lote ya ml"], "ဘယ်လိုလုပ်ရမလဲ", "What should I do?")
C(["br lote ya ml ll","bar lote ya mal le"], "ဘာလုပ်ရမလဲ", "What should I do?")
C(["bl thu ka ll","bel thu ka le"], "ဘယ်သူကလဲ", "Who (is it)?")
C(["bl hnit yout ll","bel hnit yout le"], "ဘယ်နှစ်ယောက်လဲ", "How many people?")
C(["bl hnit nar yi ll","bl hnit naryi ll"], "ဘယ်နှစ်နာရီလဲ", "What time is it?")
C(["athet bl lout shi p ll","a thet bl lout shi p ll"], "အသက်ဘယ်လောက်ရှိပြီလဲ", "How old are you?")
C(["nar mae br ll","narmae br ll","nar mae bar le"], "နာမည်ဘာလဲ", "What's your name?")
C(["ya ml","ya mal"], "ရမယ်", "must / have to")
C(["hok lrr naw","hote lar naw"], "ဟုတ်လားနော်", "Really, huh?")
C(["hok p","hote pyi","hok pi"], "ဟုတ်ပြီ", "Right, got it.")
C(["tkai lrr","ta kel lar","ta kal lar","takel lrr","tkel lrr"], "တကယ်လား", "Really?")
C(["a yan kg tl","ayan kg tl","a yan kaung tal"], "အရမ်းကောင်းတယ်", "It's really good.")
C(["min ko chit tl","ming ko chit tl","min ko chit tal"], "မင်းကိုချစ်တယ်", "I love you.")
C(["nin ko chit tl","nin ko chit tal"], "နင့်ကိုချစ်တယ်", "I love you.")
C(["min ko lwan tl","ming ko lwan tl","min ko lwan tal"], "မင်းကိုလွမ်းတယ်", "I miss you.")
C(["min ko tha ti ya tl","min ko thati ya tl"], "မင်းကိုသတိရတယ်", "I miss you.")
C(["may thwar p","may thwar pyi","mayy thwar p"], "မေ့သွားပြီ", "I forgot.")
C(["may thwar tl","may thwar tal"], "မေ့သွားတယ်", "I forgot.")
C(["ma may ne naw","ma may nae naw"], "မမေ့နဲ့နော်", "Don't forget, okay?")
C(["ma may ne","ma may nae"], "မမေ့နဲ့", "Don't forget.")
C(["ein pyan p","ein pyan pyi"], "အိမ်ပြန်ပြီ", "Going home now.")
C(["tot p","toh p","taw p"], "တော့ပြီ", "(now) then")
C(["kha na saung pr","khana saung pr","kha na saung par"], "ခဏစောင့်ပါ", "Please wait a moment.")
C(["kha na lay saung","khana lay saung"], "ခဏလေးစောင့်", "Wait a sec.")
C(["bike sar tl","baik sar tl","bike sar tal"], "ဗိုက်ဆာတယ်", "I'm hungry.")
C(["yay thout ml","ye thout ml"], "ရေသောက်မယ်", "I'll drink water.")
C(["mway nay mingalar par","mwaynay mingalarpar"], "မွေးနေ့မင်္ဂလာပါ", "Happy birthday.")
C(["thwar sot","thwar kya sot"], "သွားကြစို့", "Let's go.")
C(["sar kya sot","sar sot"], "စားကြစို့", "Let's eat.")
C(["nout ka nay","nauk ka nay"], "နောက်ကနေ", "from behind / afterwards")
C(["a pyin mha","apyin mha"], "အပြင်မှာ", "outside")
C(["ein mha","ein hma"], "အိမ်မှာ", "at home")
C(["kyaung mha","kyaung hma"], "ကျောင်းမှာ", "at school")
C(["yone mha","yon mha"], "ရုံးမှာ", "at the office")
C(["phone ma ya bu","phone ma ya woo"], "ဖုန်းမရဘူး", "Can't get through by phone.")
C(["bl thwar ml ll","bel thwar mal le"], "ဘယ်သွားမလဲ", "Where are you going?")
C(["thwar p naw","thwar pi naw"], "သွားပြီနော်", "I'm off, okay?")
C(["pyan lar khae","pyan lar khae naw"], "ပြန်လာခဲ့", "Come back.")
C(["lar khae","lar khae naw"], "လာခဲ့", "Come over.")
C(["lar khae pr","lar khae par"], "လာခဲ့ပါ", "Please come.")
# asking after someone's health
C(["ny kg yae lrr","nay kaung yae lar","ny kg yel lrr","nay kaung yeh lar"], "နေကောင်းရဲ့လား", "Are you keeping well?")
C(["ny kg lar p lrr","nay kaung lar pi lar","ny kg lar p lr"], "နေကောင်းလာပြီလား", "Are you getting better?")
C(["ny kg p lrr","nay kaung pi lar"], "နေကောင်းပြီလား", "Are you well now?")
C(["thet thar lar p lrr","thetthar lar p lrr","thet thar lar pi lar"], "သက်သာလာပြီလား", "Are you feeling better?")
C(["thet thar yae lrr","thet thar yel lrr"], "သက်သာရဲ့လား", "Feeling any better?")
C(["po kg lar p lrr","po kaung lar pi lar"], "ပိုကောင်းလာပြီလား", "Is it getting better?")
C(["pyan kg lar p","pyan kaung lar pi"], "ပြန်ကောင်းလာပြီ", "I've recovered.")
C(["ny ma kg phyit ny tl","nay ma kaung phyit nay tal"], "နေမကောင်းဖြစ်နေတယ်", "I'm not feeling well.")
C(["ny ma kg bu","nay ma kaung bu"], "နေမကောင်းဘူး", "I'm unwell.")
C(["myan myan ny kg pr say","myan myan nay kaung par say","myanmyan ny kg pr say"], "မြန်မြန်နေကောင်းပါစေ", "Get well soon.")
C(["ny kg pr say","nay kaung par say"], "နေကောင်းပါစေ", "Wishing you good health.")
C(["kyan mar pr say","kyanmar pr say","kyan mar par say"], "ကျန်းမာပါစေ", "Stay healthy.")
C(["ga yu sike naw","gayu sike naw","ga yu site naw"], "ဂရုစိုက်နော်", "Take care.")
C(["kyan mar yay ga yu sike naw","kyanmaryay gayu sike naw"], "ကျန်းမာရေးဂရုစိုက်နော်", "Look after your health.")
C(["a nar yu naw","anar yu naw"], "အနားယူနော်", "Get some rest.")
C(["a khu yaw bl lo ny ll","akhu yaw bl lo ny ll","a khu yaw bel lo nay le"], "အခုရော ဘယ်လိုနေလဲ", "And how are you now?")
C(["phyar ny thay lrr","phyar nay thay lar"], "ဖျားနေသေးလား", "Do you still have a fever?")
C(["nar thay lrr","nar thay lar"], "နာသေးလား", "Does it still hurt?")
C(["hsay thout p p lrr","say thout p p lrr"], "ဆေးသောက်ပြီးပြီလား", "Have you taken your medicine?")
C(["sayarwun pya p p lrr","sayarwun pya pyi p lar"], "ဆရာဝန်ပြပြီးပြီလား", "Have you seen a doctor?")
C(["mhar thwar p","mhar thwar pi"], "မှားသွားပြီ", "I made a mistake.")
C(["hmar htar tl","hmar htar tal"], "မှာထားတယ်", "I've ordered it / told them.")
C(["thu ma kyar kha na","thu ma kya kha na"], "သူ မကြာခဏ", "He/she often ...")

# ================================================================ burmese_1m_phrases.txt import
# Each line = SUBJECT TIME CONDITION ACTIVITY+ENDING. ~400 unique pieces, romanized to chat spelling.
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from romanize import chat as romanize_chat
PHRASE_FILE = os.environ.get('PHRASE_FILE', 'burmese_1m_phrases.txt')
ENDINGS = [("ဖို့စီစဉ်ထားတယ်။", "phoe si sin htar tl"), ("ဖို့ကြိုးစားနေတယ်။", "phoe kyo sar ny tl"),
           ("ဖို့လိုတယ်။", "phoe lo tl"), ("နေတယ်။", "ny tl"), ("မယ်။", "ml")]
IMPORT = {"subjects": {}, "times": {}, "conditions": {}, "activities": {}}
SAMPLE_LINES = []
if os.path.exists(PHRASE_FILE):
    cols = [set(), set(), set(), set()]
    import random
    rng = random.Random(7)
    with open(PHRASE_FILE, encoding='utf-8') as fh:
        for n, line in enumerate(fh):
            parts = line.rstrip('\n').split(' ')
            if len(parts) != 4: continue
            for i, x in enumerate(parts): cols[i].add(x)
            if len(SAMPLE_LINES) < 150: SAMPLE_LINES.append(line.rstrip('\n'))
            elif rng.random() < 150 / (n + 1): SAMPLE_LINES[rng.randrange(150)] = line.rstrip('\n')
    for subj in sorted(cols[0]):
        noun = subj[:-1] if subj.endswith('က') and len(subj) > 1 else subj
        IMPORT["subjects"][subj] = (noun, romanize_chat(noun), subj != noun)
    for x in sorted(cols[1]): IMPORT["times"][x] = romanize_chat(x)
    for x in sorted(cols[2]): IMPORT["conditions"][x] = romanize_chat(x)
    for x in sorted(cols[3]):
        for end, _ in ENDINGS:
            if x.endswith(end):
                stem = x[:-len(end)]
                IMPORT["activities"][stem] = romanize_chat(stem); break
    json.dump(IMPORT, open('phrase_import.json', 'w'), ensure_ascii=False, indent=1)
elif os.path.exists('phrase_import.json'):
    IMPORT = json.load(open('phrase_import.json'))
    SAMPLE_LINES = json.load(open('sample_lines.json')) if os.path.exists('sample_lines.json') else []
    SAMPLE_LINES = [x[1] for x in SAMPLE_LINES]

for subj, (noun, lat, _) in IMPORT["subjects"].items():
    T([lat], noun, [""], "noun", "medium", source="phrase_list")
for bur, lat in list(IMPORT["times"].items()) + list(IMPORT["conditions"].items()):
    T([lat], bur, [""], "phrase", "medium", source="phrase_list")
for stem, lat in IMPORT["activities"].items():
    pr([lat], stem, "", "ACTIVITY", False, source="phrase_list")

# lexical multi-word vocabulary (after curated so curated wins)
for vs, bur, en in lexical:
    C(vs, bur, en, source='lexical')

# ================================================================ typing rules (precise mode)
INITIALS = {
  "k":"က","kh":"ခ","g":"ဂ","ng":"င","s":"စ","hs":"ဆ","z":"ဇ","ny":"ည","t":"တ","ht":"ထ","d":"ဒ","n":"န",
  "p":"ပ","ph":"ဖ","b":"ဘ","v":"ဗ","m":"မ","y":"ယ","r":"ရ","l":"လ","w":"ဝ","th":"သ","h":"ဟ","":"အ",
  "ch":"ချ","sh":"ရှ","hm":"မှ","hn":"နှ","hl":"လှ","hng":"ငှ","hny":"ညှ","hw":"ဝှ",
  "mh":"မှ","nh":"နှ","lh":"လှ",
}
KEEP = json.load(open('english_keep.json')) if os.path.exists('english_keep.json') else []
TYPING_RULES = {
  "summary": [
    "Type one syllable per word. End it with a mark to pick the tone mark you see in the script.",
    "No mark = plain (သာ).  :  adds the two dots း (သား).  '  gives the short dotted form ့ (သ, ငါ့).  =  means plain, read by these rules instead of the dictionary.",
    "Letters stand for script, not sound: y = ျ, r = ြ, w = ွ, h in front = ှ. So pran = ပြန်, mran = မြန်, hma = မှာ.",
    "At the end of a syllable, ny = ည် and iny = ဉ်: nany: = နည်း, kiny = ကဉ်. In the middle, nae = နယ်, nae: = နဲ, nae' = နဲ့.",
    "Syllables typed with marks join together: a' khan: than' shin: gives အခန်းသန့်ရှင်း."
  ],
  "marks": {":": "း (high)", "'": "့ (short / creaky)", "=": "plain, use the typing rules"},
  "initials": INITIALS,
  "canonical_initials": [k for k in INITIALS if k not in ("mh","nh","lh")],
  "medials": {"y": "ျ", "r": "ြ", "w": "ွ"},
  "medial_combinations": ["y", "r", "w", "yw", "rw"],
  "tall_aa_consonants": "ခဂငဒပဝ",
  "open_rhymes": {
    "a": ["ာ","ား",""], "i": ["ီ","ီး","ိ"], "u": ["ူ","ူး","ု"], "e": ["ေ","ေး","ေ့"],
    "ae": ["ယ်","ဲ","ဲ့"], "aw": ["ော်","ော","ော့"], "o": ["ို","ိုး","ို့"]
  },
  "nasal_rhymes": {"an":"န်","am":"မ်","in":"င်","ein":"ိန်","eim":"ိမ်","on":"ုန်","om":"ုမ်","aung":"ောင်","aing":"ိုင်","any":"ည်","iny":"ဉ်"},
  "checked_rhymes": {"at":"တ်","ap":"ပ်","et":"က်","it":"စ်","eit":"ိတ်","eip":"ိပ်","ot":"ုတ်","op":"ုပ်","aik":"ိုက်","auk":"ောက်"},
  "creaky_exceptions": {"nga":"ငါ့","thu":"သူ့","da":"ဒါ့"},
  "examples": [["tha","သာ"],["tha:","သား"],["tha'","သ"],["hma","မှာ"],["hma:","မှား"],["hma'","မှ"],["nga'","ငါ့"],
               ["thwa:","သွား"],["pran","ပြန်"],["nae","နယ်"],["nae'","နဲ့"],["nany:","နည်း"],["kyaung:","ကျောင်း"],["nin'","နင့်"],["paw","ပေါ်"]],
  "english_keep": KEEP
}

CONFUSABLE_SETS = [
  {"label": "thar", "items": [{"burmese":"သာ","note":"more, better; only (in compounds: သက်သာ, ချမ်းသာ)"},
                               {"burmese":"သား","note":"son; meat (ကြက်သား)"}]},
  {"label": "hmar", "items": [{"burmese":"မှာ","note":"at, in; will (-မှာ); to order"},
                               {"burmese":"မှား","note":"wrong, mistaken"},
                               {"burmese":"မှ","note":"only then; from; not even (ဘာမှ)"}]},
  {"label": "nga",  "items": [{"burmese":"ငါ","note":"I, me"},{"burmese":"ငါး","note":"fish; five"},
                               {"burmese":"ငါ့","note":"my; me (before ကို)"}]},
  {"label": "thu",  "items": [{"burmese":"သူ","note":"he, she"},{"burmese":"သူ့","note":"his, her; him (before ကို)"}]},
  {"label": "lar",  "items": [{"burmese":"လာ","note":"come"},{"burmese":"လား","note":"yes/no question ending"}]},
  {"label": "nae",  "items": [{"burmese":"နဲ့","note":"with, and; don't (after မ-: မသွားနဲ့)"},
                               {"burmese":"နယ်","note":"region, area (နယ်မြေ, နယ်စပ်); to knead"},
                               {"burmese":"နည်း","note":"few, little; method (နည်းလမ်း)"},
                               {"burmese":"နေ","note":"stay, live; -ing"},{"burmese":"နေ့","note":"day"}]},
  {"label": "lay",  "items": [{"burmese":"လေ","note":"wind; air; emphatic ending"},{"burmese":"လေး","note":"little; four; heavy"},
                               {"burmese":"လဲ","note":"wh-question ending; fall over"}]},
  {"label": "par",  "items": [{"burmese":"ပါ","note":"polite particle; also, included"},{"burmese":"ပါး","note":"cheek; thin"}]},
  {"label": "sar",  "items": [{"burmese":"စား","note":"eat"},{"burmese":"စာ","note":"letter, text, lessons"},{"burmese":"ဆာ","note":"hungry"}]},
  {"label": "pyaw", "items": [{"burmese":"ပြော","note":"say, speak"},{"burmese":"ပျော်","note":"happy, have fun"}]},
  {"label": "ko",   "items": [{"burmese":"ကို","note":"object marker; title for men"},{"burmese":"ကိုး","note":"nine"},
                               {"burmese":"ကိုယ်","note":"self; body"}]},
  {"label": "yay",  "items": [{"burmese":"ရေ","note":"water"},{"burmese":"ရေး","note":"write; affairs (-ရေး)"}]},
  {"label": "may",  "items": [{"burmese":"မေး","note":"ask"},{"burmese":"မေ့","note":"forget"},{"burmese":"မေ","note":"mum (မေမေ)"}]},
  {"label": "thay", "items": [{"burmese":"သေ","note":"die"},{"burmese":"သေး","note":"small; still, yet"}]},
  {"label": "pyi",  "items": [{"burmese":"ပြီ","note":"already, now (sentence end)"},{"burmese":"ပြီး","note":"finish; after, and then"}]},
]

# ================================================================ assemble
blocklist = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else []

def pred_json(p):
    latin, bur, en, frames, tok, kw = p
    d = {"latin": latin, "burmese": bur, "english": en}
    if isinstance(frames, tuple):
        d["frames"], ex, inc = frames
        if ex: d["exclude"] = ex
        if inc: d["include"] = inc
    else:
        d["frames"] = frames
    if 'confidence' in kw: d["confidence"] = kw['confidence']
    return d

out = {
  "schema_version": "4.1",
  "name": "Myanglish → Burmese Normalization Lexicon",
  "description": "Informal Burmese written in Latin letters, mapped to Myanmar script. Vocabulary lives in token_map and phrase_map; grammar lives in predicates × frames, which engine.js expands into phrases when it loads.",
  "language": OLD["language"],
  "engine_compatibility": {
    "requires": "engine.js v3 (expandGrammar + typing rules). Older engines still load token_map and phrase_map but skip grammar and typing rules.",
    "notes": [
      "token_map variants are single [a-z0-9'] words; multi-word forms live in phrase_map.",
      "Explicit phrase_map entries always win over generated ones; among generated ones, earlier predicates win.",
      "In predicate latin/burmese, '|' marks where the negator goes: nar|lal + ma -> nar ma lal -> နားမလည်.",
      "Frame pattern slots: P = predicate, N = negated predicate, GROUP = particle spellings, GROUP:2 = first two spellings, =a|b = literal spellings.",
      "Joined spellings (kglrr, mathibu) are generated for frames up to generation.join_max_words words; join_blocklist holds English words they must never shadow.",
      "engine.js hard-codes sar, pyaw, lar/la, mha/hma, le/lel, lay, ko/koe and kyaung at token level; phrases override that."
    ]
  },
  "important_notes": OLD["important_notes"],
  "normalization_rules": OLD["normalization_rules"] + [
    {"rule": "completed_particle", "forms": ["p","pi"], "burmese": "ပြီ", "meaning": "sentence-final 'already/now'", "example": "yout p -> ရောက်ပြီ"},
    {"rule": "connector", "forms": ["pyi","pee"], "burmese": "ပြီး", "meaning": "after / and then", "example": "sar pyi thwar ml -> စားပြီး သွားမယ်"},
    {"rule": "polite_particle", "forms": ["pr","par","pa"], "burmese": "ပါ", "meaning": "politeness", "example": "kg pr tl -> ကောင်းပါတယ်"},
    {"rule": "past", "forms": ["khae","khe","kae"], "burmese": "ခဲ့", "meaning": "past / completed", "example": "thwar khae tl -> သွားခဲ့တယ်"},
    {"rule": "compound_negation", "pattern": "NOUN + ma + VERB", "burmese_pattern": "NOUN + မ + VERB", "examples": ["nar ma lal bu -> နားမလည်ဘူး", "sate ma pu ne -> စိတ်မပူနဲ့"]},
    {"rule": "possessive_creaky_tone", "examples": ["nga ko -> ငါ့ကို", "thu atwat -> သူ့အတွက်"], "meaning": "ငါ/သူ/နင် take creaky tone ့ before ကို and possessed nouns"}
  ],
  "particles": PARTICLES,
  "frames": FRAMES,
  "frame_sets": FRAME_SETS,
  "predicates": [pred_json(p) for p in PRED],
  "generation": {"join_max_words": 3, "join_min_length": 5, "join_blocklist": blocklist},
  "typing_rules": TYPING_RULES,
  "confusable_sets": CONFUSABLE_SETS,
  "token_map": tokens,
  "phrase_map": phrases,
  "ambiguity_rules": OLD["ambiguity_rules"] + [
    {"latin": "pyin", "possible": [{"burmese": "ပျင်း", "meaning": "bored", "signals": ["tl, a yan before it"]}, {"burmese": "ပြင်", "meaning": "fix", "signals": ["pay pr, ml, lite"]}]},
    {"latin": "may", "possible": [{"burmese": "မေး", "meaning": "ask", "signals": ["ml, chin"]}, {"burmese": "မေ့", "meaning": "forget", "signals": ["thwar p/tl, ma may ne"]}]},
    {"latin": "nar", "possible": [{"burmese": "နာ", "meaning": "hurt", "signals": ["tl"]}, {"burmese": "နား", "meaning": "rest", "signals": ["ml, lite pr"]}]},
    {"latin": "yay", "possible": [{"burmese": "ရေ", "meaning": "water", "signals": ["noun position"]}, {"burmese": "ရေး", "meaning": "write", "signals": ["ml, pay pr"]}]},
    {"latin": "yone", "possible": [{"burmese": "ရုံး", "meaning": "office", "signals": ["noun position"]}, {"burmese": "ယုံ", "meaning": "believe", "signals": ["tl, ma..bu"]}]},
    {"latin": "pyi", "possible": [{"burmese": "ပြီး", "meaning": "after / finished", "signals": ["another verb follows"]}, {"burmese": "ပြီ", "meaning": "already (final)", "signals": ["end of sentence; usually typed p"]}]}
  ],
  "composition_patterns": OLD["composition_patterns"] + [
    {"pattern": "VERB + lo + ya + lrr", "meaning": "Is it okay to VERB?", "example": {"myanglish": "thwar lo ya lrr", "burmese": "သွားလို့ရလား"}},
    {"pattern": "VERB + khae + tl", "meaning": "past", "example": {"myanglish": "thwar khae tl", "burmese": "သွားခဲ့တယ်"}},
    {"pattern": "VERB + kya + sot", "meaning": "let's VERB", "example": {"myanglish": "sar kya sot", "burmese": "စားကြစို့"}},
    {"pattern": "STATE + lite + tr", "meaning": "so STATE!", "example": {"myanglish": "hla lite tr", "burmese": "လှလိုက်တာ"}},
    {"pattern": "ma + VERB + tot + bu", "meaning": "not any more", "example": {"myanglish": "ma thwar tot bu", "burmese": "မသွားတော့ဘူး"}}
  ],
  "model_guidance": OLD["model_guidance"],
  "test_cases": [],
  "changelog": [
    "v4.1: typing rules gain ny = ည် and iny = ဉ် (nany: = နည်း); look-alike set နဲ့ / နယ် / နည်း / နေ / နေ့; nel now means နယ် (noon is nay lel).",
    "v4: typing rules (precise mode): tha = သာ, tha: = သား, tha' = သ; y/r/w/h letters for ျ ြ ွ ှ; = forces the rules. See typing_rules.",
    "v4: confusable_sets with short meanings (သာ/သား, မှာ/မှား/မှ, ငါ/ငါး/ငါ့ ...) for the side panel.",
    "v4: asking after health: ရဲ့လား, လာပြီလား (getting better), သေးလား (still?), ပါစေ (wishes), plus doctor/medicine/rest verbs.",
    "v4: imported burmese_1m_phrases.txt: 80 subjects, 10 time words, 7 conditions, 296 activities with 5 endings; 5000/5000 sample lines convert exactly.",
    "v3: grammar moved into predicates × frames, expanded by engine.js; file size stays small while coverage grows.",
    "v3: about 190 predicates and 95 frames (past ခဲ့, must ရမယ်, let's ကြစို့, about-to တော့မယ်, no-longer တော့ဘူး, know-how တတ်, so-X လိုက်တာ, more wh-questions).",
    "v3: joined no-space spellings generated (kglrr, mathibu, thwarml), filtered against an English word list.",
    "v3: vocabulary expanded: family, places, food, days, time words, connectors, numbers, body, creaky-tone possessives (ငါ့ကို, သူ့အတွက်).",
    "v3: pyi now means ပြီး (connector); p/pi mean ပြီ, so 'sar pyi thwar ml' -> စားပြီး သွားမယ်.",
    "v2: moved unreachable multi-word token variants into phrase_map; removed slash outputs."
  ]
}

TESTS = json.load(open('tests.json'))
END_LAT = dict(ENDINGS)
def line_to_input(line):
    subj, tm, cond, act = line.split(' ')
    noun, lat, has_ka = IMPORT["subjects"][subj]
    parts = [lat + (' ka' if has_ka else ''), IMPORT["times"][tm], IMPORT["conditions"][cond]]
    for end, elat in ENDINGS:
        if act.endswith(end):
            parts.append(IMPORT["activities"][act[:-len(end)]] + ' ' + elat + '.')
            break
    return ' '.join(parts)
if SAMPLE_LINES and os.path.exists(PHRASE_FILE):
    json.dump([[line_to_input(l), l] for l in SAMPLE_LINES], open('sample_lines.json', 'w'), ensure_ascii=False)
TESTS = TESTS + [[line_to_input(l), l, "from burmese_1m_phrases.txt"] for l in SAMPLE_LINES[:60]]
out["test_cases"] = [{"input": i, "expected_burmese": b, "expected_english": e} for i, b, e in TESTS]
json.dump(out, open('myanglish_mapping.json', 'w'), ensure_ascii=False, indent=1)
print(f"predicates {len(PRED)}  frames {len(FRAMES)}  tokens {len(tokens)}  phrases {len(phrases)}  tests {len(TESTS)}")
