#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const args = process.argv.slice(2);
const prepare = args[0] === '--prepare';

if (prepare) {
  const input = args[1];
  const output = args[2];
  if (!input || !output) {
    throw new Error('Usage: materialize-catalog.mjs --prepare <catalog.json> <catalog.portable.json>');
  }
  const catalog = JSON.parse(fs.readFileSync(input, 'utf8'));
  for (const skill of catalog.skills) {
    if (skill.source === 'active') {
      skill.skillPath = `skills/${skill.directory}/SKILL.md`;
    } else {
      const relative = String(skill.relativePath || skill.directory).replaceAll('\\', '/');
      skill.skillPath = `skill-library/leaves/${relative}/SKILL.md`;
    }
  }
  catalog.generatedAt = null;
  fs.writeFileSync(output, `${JSON.stringify(catalog, null, 2)}\n`, 'utf8');
  process.exit(0);
}

const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const codexHome = path.resolve(process.env.CODEX_HOME || path.join(os.homedir(), '.codex'));
const input = args[0] || path.join(repoRoot, 'skill-library', 'catalog.portable.json');
const output = args[1] || path.join(codexHome, 'skill-library', 'catalog.json');
const catalog = JSON.parse(fs.readFileSync(input, 'utf8'));

for (const skill of catalog.skills) {
  const parts = String(skill.skillPath).split('/');
  skill.skillPath = path.join(codexHome, ...parts);
}
catalog.generatedAt = new Date().toISOString();
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, `${JSON.stringify(catalog, null, 2)}\n`, 'utf8');
console.log(`Skill catalog materialized: ${catalog.skills.length}`);
