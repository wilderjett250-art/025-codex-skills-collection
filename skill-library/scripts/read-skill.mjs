import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { recordActivity } from './activity-core.mjs';

const name = process.argv[2];
if (!name || process.argv.length !== 3) {
  console.error('Usage: node read-skill.mjs <exact-catalog-name>');
  process.exit(2);
}

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'catalog.json'), 'utf8').replace(/^\uFEFF/, ''));
const matches = catalog.skills.filter(skill => skill.name === name);
if (matches.length !== 1) {
  console.error(`Expected one catalog entry for ${JSON.stringify(name)}; found ${matches.length}.`);
  process.exit(2);
}

const skill = matches[0];
const skillPath = path.resolve(skill.skillPath);
const allowedRoots = [path.resolve(root, 'leaves'), path.resolve(root, '..', 'skills')];
if (!allowedRoots.some(base => skillPath.toLowerCase().startsWith((base + path.sep).toLowerCase())) || path.basename(skillPath).toLowerCase() !== 'skill.md') {
  console.error('Catalog entry resolves outside the local Skill roots.');
  process.exit(2);
}

const content = fs.readFileSync(skillPath, 'utf8');
process.stdout.write(content, error => {
  if (error) {
    console.error(`Could not deliver Skill text: ${error.message}`);
    process.exitCode = 1;
    return;
  }
  try {
    recordActivity({ kind: 'skill_load', name: skill.name, eventId: crypto.randomUUID() });
  } catch (activityError) {
    console.error(`Skill text delivered, but local activity recording failed: ${activityError.message}`);
    process.exitCode = 1;
  }
});
