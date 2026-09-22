const fs = require('fs');
const { MyanglishTransformer } = require('./engine.js');
const data = JSON.parse(fs.readFileSync('./myanglish_mapping.json', 'utf8'));
const transformer = new MyanglishTransformer(data);

// Core regression tests (kept from the original test.js)
const tests = [
  ['hyg ny kg lrr', 'ဟေ့ရောင် နေကောင်းလား'],
  ['Br lote ny ll', 'ဘာလုပ်နေလဲ'],
  ['Ek lo ma hok woo', 'အဲ့လို မဟုတ်ဘူး'],
  ['D Hrr ka', 'ဒီဟာက'],
  ['A May ko thar mayy ma loh', 'အမေကို သားမေးမလို့'],
  ['ma thi bu', 'မသိဘူး'],
  ['yout p lrr', 'ရောက်ပြီလား']
];

// Plus every test case stored in the mapping JSON
for (const c of data.test_cases ?? []) {
  if (c.input && c.expected_burmese) tests.push([c.input, c.expected_burmese]);
}

let failed = 0;
for (const [input, expected] of tests) {
  const actual = transformer.transform(input);
  const ok = actual === expected;
  console.log(`${ok ? 'PASS' : 'FAIL'} | ${input} -> ${actual}`);
  if (!ok) {
    console.log(`       expected: ${expected}`);
    failed += 1;
  }
}

console.log(`\n${tests.length - failed}/${tests.length} passed`);
process.exitCode = failed ? 1 : 0;
