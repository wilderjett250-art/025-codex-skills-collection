#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { routeTask } from './route-core.mjs';

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

try {
  const prompt = option('--prompt', '-Prompt');
  if (!prompt) throw new Error('Use --prompt "current user request".');
  const catalogPath = option('--catalog', '-CatalogPath') || path.join(codexHome, 'skill-library', 'catalog.json');
  const profilePath = option('--profile', '-ProfilePath') || path.join(codexHome, 'skill-library', 'routing-profile.json');
  const limit = Number(option('--limit', '-Limit') || 5);
  console.log(JSON.stringify(routeTask(prompt, readJson(catalogPath), readJson(profilePath), limit), null, 2));
} catch (error) {
  console.error(`Skill route failed: ${error.message}`);
  process.exitCode = 1;
}
