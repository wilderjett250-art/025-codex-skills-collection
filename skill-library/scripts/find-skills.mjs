#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { searchSkills } from './search-skills.mjs';

const args = process.argv.slice(2);
function option(...names) {
  for (const name of names) {
    const index = args.indexOf(name);
    if (index >= 0) return args[index + 1];
  }
  return undefined;
}
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const codexHome = path.resolve(process.env.CODEX_HOME || path.join(os.homedir(), '.codex'));
const catalogPath = option('--catalog', '-CatalogPath') || path.join(codexHome, 'skill-library', 'catalog.json');
const discoveryPath = option('--discovery', '-DiscoveryPath') || path.join(codexHome, 'skill-library', 'discovery-profile.json');

try {
  const catalog = readJson(catalogPath);
  const options = {
    limit: Number(option('--limit', '-Limit') || 3),
    plane: option('--plane', '-Plane'),
    domain: option('--domain', '-Domain'),
    discipline: option('--discipline', '-Discipline'),
    family: option('--family', '-Family'),
  };
  const scoped = catalog.skills.filter(skill => (!options.plane || skill.plane === options.plane)
    && (!options.domain || skill.domain === options.domain)
    && (!options.discipline || skill.discipline === options.discipline)
    && (!options.family || skill.family === options.family));
  if (args.includes('--list-disciplines') || args.includes('-ListDisciplines')) {
    console.log([...new Set(scoped.map(skill => skill.discipline))].sort().join('\n'));
  } else if (args.includes('--list-families') || args.includes('-ListFamilies')) {
    console.log([...new Set(scoped.map(skill => skill.family))].sort().join('\n'));
  } else {
    const query = option('--query', '-Query');
    if (!query) throw new Error('Use --query "task + object + platform" or a listing switch.');
    const discovery = fs.existsSync(discoveryPath) ? readJson(discoveryPath) : {};
    console.log(JSON.stringify(searchSkills(query, catalog, discovery, options), null, 2));
  }
} catch (error) {
  console.error(`Skill lookup failed: ${error.message}`);
  process.exitCode = 1;
}
