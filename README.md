# Myanglish → Burmese

A small rule-based browser app that converts common informal **Myanglish** (Romanized Burmese chat spelling) into **Myanmar script**.

Examples:

- `hyg ny kg lrr` → `ဟေ့ရောင် နေကောင်းလား`
- `Br lote ny ll` → `ဘာလုပ်နေလဲ`
- `Ek lo ma hok woo` → `အဲ့လို မဟုတ်ဘူး`

## Put it on GitHub Pages

GitHub does not unzip files. Uploading the zip itself only stores a zip, and the site will not change. Unzip first, then upload what's inside.

1. Unzip the download on your computer.
2. In the repository, choose **Add file → Upload files**, and drag in everything from the unzipped folder: the files and the `tools` and `.github` folders. Files with the same name replace the old ones.
   - `.nojekyll` and `.github` start with a dot, so they may be hidden. On a Mac, press Cmd + Shift + . in Finder to show them. On Windows, turn on **View → Show → Hidden items**. The site still works without them.
3. Click **Commit changes**.
4. Open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, then `main` and `/ (root)`, and click **Save**. You only need to do this once.
5. Wait a minute or two, then open the site. The status line under the title should read **Dictionary v4.1 ready**. If it still shows an older version, refresh once more; GitHub Pages caches files for about 10 minutes.

The **Actions** tab runs the tests after every upload. A green check means all conversions passed; a red cross shows which one failed.

When you publish a future update, bump `APP_VERSION` in `app.js` and the three `?v=` numbers in `index.html`, so browsers never mix old and new files.

## Run locally

Because the app loads the JSON with `fetch()`, open it through a small local web server rather than double-clicking `index.html`.

With Python installed:

```bash
python3 -m http.server 8000
```

Then visit:

```text
http://localhost:8000
```

## How it works

The browser loads `myanglish_mapping.json` and performs:

1. longest phrase matching;
2. token-level lookup;
3. lightweight context disambiguation for forms such as `sar`, `pyaw`, `lar`, `mha/hma`, and `le/lay`;
4. emphasis collapsing (`kg lrrr` is read as `kg lrr`), including inside phrases;
5. joining particles such as `တယ်`, `လား`, `နော်`, and `ကို` onto the Burmese word before them;
6. fallback that preserves unknown tokens, which helps with English/Burmese code-switching.

## Typing rules (precise mode)

Chat spelling is fuzzy: `thar` could mean သာ or သား. When you need to be exact, end a syllable with a mark that looks like the Burmese mark you want:

| You type | You get | Rule |
|---|---|---|
| `tha` | သာ | no mark: plain |
| `tha:` | သား | `:` adds the two dots း |
| `tha'` | သ | `'` gives the short dotted form (ငါ့, နင့်, သူ့) |
| `ne=` | နေ | `=` keeps it plain but skips the dictionary |

Letters stand for script, not sound: `y` = ျ, `r` = ြ, `w` = ွ, and `h` in front = ှ. At the end of a syllable, `ny` = ည် and `iny` = ဉ် (`nany:` = နည်း). For the န family: `nae` = နယ်, `nae'` = နဲ့, `nany:` = နည်း, `ne` = နေ, `ne'` = နေ့. So `pran` = ပြန်, `mran` = မြန်, `hma:` = မှား. Syllables typed this way join into one word: `a' khan: than' shin:` gives အခန်းသန့်ရှင်း. Normal chat spelling keeps working alongside these rules.

The full tables live in `typing_rules` inside the JSON, and the website shows them in the side panel.

## Side panel

Put the cursor on any word to see other ways to write it (for example မှာ, မှား, မှ for `hma`), each with its typing-rule spelling and a short meaning. Click a choice, or press Alt and its number, to rewrite that word. Look-alike word sets come from `confusable_sets` in the JSON.

## How the dictionary is organised

`myanglish_mapping.json` holds two kinds of data:

- **Vocabulary**: `token_map` (single words) and `phrase_map` (fixed phrases).
- **Grammar**: `predicates` (verbs and adjectives) and `frames` (sentence patterns such as VERB + `chin tl` → VERB + ချင်တယ်). `engine.js` combines them when the page loads, producing over 150,000 phrases, including no-space spellings like `kglrr` and `mathibu`, from a file of about 300 KB.

To add a verb, add one entry to `predicates`, for example:

```json
{ "latin": ["nar|lal", "na|lal"], "burmese": "နား|လည်", "english": "understand", "frames": "KNOW" }
```

The `|` marks where the negator goes, so `nar ma lal bu` becomes နားမလည်ဘူး.

## Testing

```bash
npm test
```

This runs the core regression cases plus every entry in `test_cases` inside `myanglish_mapping.json`, so new test cases can be added to the JSON without touching `test.js`.

## Important limitation

Myanglish does not have one standardized spelling system. A short string can therefore have multiple valid Burmese interpretations. The mapping JSON includes ambiguity notes and common chat patterns, but this remains a deterministic rule-based normalizer rather than a full language model.

## Files

- `index.html`, `style.css`, `app.js`: the web page
- `engine.js`: the converter
- `myanglish_mapping.json`: dictionary, grammar, typing rules and look-alike words
- `test.js`, `package.json`: tests (`npm test`)
- `tools/`: rebuilds the dictionary (optional, not needed by the site)
- `.nojekyll`: tells GitHub Pages to serve the files as they are
- `.github/workflows/tests.yml`: runs the tests on GitHub after each upload

## License

Use and modify freely for your own project.

## Rebuilding the dictionary

The `tools/` folder rebuilds `myanglish_mapping.json`:

```bash
cd tools
python3 build_mapping.py join_blocklist.json
```

It reads `phrase_import.json` (the romanized pieces from `burmese_1m_phrases.txt`). To re-import from the full text file, put `burmese_1m_phrases.txt` in `tools/` and run the same command.
