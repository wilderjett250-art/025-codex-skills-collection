import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const chars = text => Array.from(text).length;
const within = (file, root) => {
  const relative = path.relative(root, file);
  return relative !== '' && !relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative);
};

export function auditContextCost(home, limit = 10) {
  if (!Number.isInteger(limit) || limit < 1 || limit > 50) throw new Error('limit must be 1..50');
  home = fs.realpathSync(home);
  const roots = ['skills', 'skill-library/leaves'].map(dir => path.join(home, dir));
  const catalog = JSON.parse(fs.readFileSync(path.join(home, 'skill-library/catalog.json'), 'utf8').replace(/^\uFEFF/, ''));
  const seen = new Set();
  const rows = catalog.skills.map(skill => {
    if (seen.has(skill.name)) throw new Error('Duplicate Skill name in catalog');
    seen.add(skill.name);
    const entry = path.resolve(skill.skillPath);
    if (path.basename(entry).toLowerCase() !== 'skill.md' || !roots.some(root => within(entry, root))) throw new Error('Entry outside allowed Skill roots');
    // Existing catalog-linked Skills are part of the library; retain them, mark the link,
    // and never include the target path or file contents in the report.
    const actual = fs.realpathSync(entry);
    if (path.basename(actual).toLowerCase() !== 'skill.md') throw new Error('Linked entry is not a Skill file');
    const raw = fs.readFileSync(entry, 'utf8').replace(/^\uFEFF/, '');
    const text = raw.replace(/\r\n/g, '\n');
    const refs = [...text.matchAll(/\]\((references\/[^)\s#]+)(?:#[^)]*)?\)/g)].map(match => match[1]);
    const missingReferences = refs.filter(ref => {
      const target = path.resolve(path.dirname(entry), ref);
      return !within(target, path.dirname(entry)) || !fs.existsSync(target);
    });
    return { name: skill.name, source: skill.source, chars: chars(text), bytes: Buffer.byteLength(raw),
      lines: text.split(/\r?\n/).length, descriptionChars: chars(skill.trigger || ''),
      linkedReferences: new Set(refs).size, missingReferences,
      externalLink: !roots.some(root => within(actual, fs.realpathSync(root))) };
  });
  const values = rows.map(row => row.chars).sort((a, b) => a - b);
  const median = values.length ? (values[Math.floor((values.length-1)/2)] + values[Math.floor(values.length/2)]) / 2 : 0;
  const rules = fs.readFileSync(path.join(home, 'AGENTS.md'), 'utf8').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
  return { basis: 'Structural entrypoint sizes, not token billing, effective information or task-quality scores.',
    total: rows.length, active: rows.filter(row => row.source === 'active').length,
    onDemand: rows.filter(row => row.source !== 'active').length,
    global: { chars: chars(rules), bytes: Buffer.byteLength(rules) },
    descriptions: { activeChars: rows.filter(row => row.source === 'active').reduce((sum, row) => sum + row.descriptionChars, 0),
      allChars: rows.reduce((sum, row) => sum + row.descriptionChars, 0) },
    entrypoints: { medianChars: median, p95Chars: values[Math.floor((values.length-1)*.95)] || 0,
      over8000Chars: rows.filter(row => row.chars > 8000).length,
      over16000Chars: rows.filter(row => row.chars > 16000).length },
    largest: [...rows].sort((a, b) => b.chars - a.chars).slice(0, limit), rows };
}

function main(args) {
  let home = process.env.CODEX_HOME || path.join(os.homedir(), '.codex');
  let limit = 10, includeRows = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--home' && args[i+1]) home = args[++i];
    else if (args[i] === '--limit' && args[i+1]) limit = Number(args[++i]);
    else if (args[i] === '--rows') includeRows = true;
    else throw new Error('Usage: audit-context-cost.mjs [--home <codex-home>] [--limit 1..50] [--rows]');
  }
  const report = auditContextCost(home, limit);
  if (!includeRows) delete report.rows;
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(process.argv.slice(2)); }
  catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
