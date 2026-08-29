#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

function option(...names) {
  for (const name of names) {
    const index = process.argv.indexOf(name);
    if (index >= 0) return process.argv[index + 1];
  }
  return null;
}

const codexHome = path.resolve(process.env.CODEX_HOME || path.join(os.homedir(), '.codex'));
const catalogPath = option('--catalog') || path.join(codexHome, 'skill-library', 'catalog.json');
const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
const domain = option('--domain', '-Domain');
const discipline = option('--discipline', '-Discipline');
const family = option('--family', '-Family');
const query = String(option('--query', '-Query') || '').toLowerCase();

let skills = catalog.skills.filter((skill) =>
  (!domain || skill.domain === domain) &&
  (!discipline || skill.discipline === discipline) &&
  (!family || skill.family === family) &&
  (!query || `${skill.name} ${skill.trigger || ''}`.toLowerCase().includes(query))
);

if (process.argv.includes('--list-disciplines') || process.argv.includes('-ListDisciplines')) {
  console.log([...new Set(skills.map((skill) => skill.discipline))].sort().join('\n'));
} else if (process.argv.includes('--list-families') || process.argv.includes('-ListFamilies')) {
  console.log([...new Set(skills.map((skill) => skill.family))].sort().join('\n'));
} else {
  skills = skills.sort((a, b) => a.canonicalPath.localeCompare(b.canonicalPath));
  console.log(JSON.stringify(skills, null, 2));
}
