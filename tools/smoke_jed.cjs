#!/usr/bin/env node
/*
 * Load built messages.json language packs with Jed (jed@1.1.1, the version
 * Superset 6.1.0 ships), the way superset-core's Translator does
 * (`new Jed(languagePack)`), and check that:
 *   - the pack loads and its lang matches the directory name;
 *   - every non-empty entry translates to its first msgstr;
 *   - every 3-form plural entry picks the form given by the Serbian/Croatian/
 *     Bosnian rule for n = 1, 2, 5, 11, 21, 22, 25, 101 (this also proves Jed
 *     parses the Plural-Forms header).
 *
 * Usage: node tools/smoke_jed.cjs <path/to/jed> <messages.json> [...]
 *   where <path/to/jed> is the installed jed package, e.g. build/node-tools/node_modules/jed
 */
const fs = require('fs');
const path = require('path');

const [jedPath, ...files] = process.argv.slice(2);
if (!jedPath || files.length === 0) {
  console.error('usage: node tools/smoke_jed.cjs <path/to/jed> <messages.json> [...]');
  process.exit(2);
}
const Jed = require(path.resolve(jedPath));
const NS = [1, 2, 5, 11, 21, 22, 25, 101];
const slavic = n =>
  n % 10 === 1 && n % 100 !== 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? 1 : 2;

let failures = 0;
for (const file of files) {
  const lang = path.basename(path.dirname(path.dirname(file)));
  const pack = JSON.parse(fs.readFileSync(file, 'utf8'));
  const problems = [];
  let i18n;
  try {
    i18n = new Jed(pack);
  } catch (err) {
    problems.push(`Jed failed to load: ${err.message}`);
  }
  if (i18n) {
    const data = i18n.options.locale_data.superset;
    if (data[''].lang !== lang) problems.push(`lang is ${data[''].lang}, expected ${lang}`);
    let singular = 0;
    let plural = 0;
    for (const [key, value] of Object.entries(data)) {
      if (key === '' || !Array.isArray(value) || !value[0]) continue;
      if (value.length === 3 && value.every(Boolean)) {
        plural += 1;
        for (const n of NS) {
          // fetch() without arguments returns the selected form without sprintf.
          const got = i18n.translate(key).ifPlural(n, `${key} (plural)`).fetch();
          if (got !== value[slavic(n)]) {
            problems.push(`plural ${JSON.stringify(key.slice(0, 40))} n=${n}: got ${JSON.stringify(got.slice(0, 40))}`);
            break;
          }
        }
      } else {
        singular += 1;
        const got = i18n.gettext(key);
        if (got !== value[0]) problems.push(`gettext ${JSON.stringify(key.slice(0, 40))} differs`);
      }
      if (problems.length > 10) break;
    }
    console.log(`${lang}: Jed loaded ${singular} singular and ${plural} plural entries` +
      (problems.length ? ` -> ${problems.length} problems` : ' -> OK'));
  }
  for (const p of problems) console.error(`  ERROR ${lang}: ${p}`);
  failures += problems.length;
}
process.exit(failures ? 1 : 0);
