#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

function arg(...names) {
  for (const name of names) {
    const index = process.argv.indexOf(name);
    if (index >= 0) return process.argv[index + 1];
  }
  return null;
}

const codexHome = path.resolve(process.env.CODEX_HOME || path.join(os.homedir(), '.codex'));
const prompt = arg('--prompt', '-Prompt');
const limit = Number(arg('--limit', '-Limit') || 8);
const catalogPath = arg('--catalog', '-CatalogPath') || path.join(codexHome, 'skill-library', 'catalog.json');
const profilePath = arg('--profile', '-ProfilePath') || path.join(codexHome, 'skill-library', 'routing-profile.json');
if (!prompt) throw new Error('Usage: route-task.mjs --prompt "<task>" [--limit 8]');

const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
const text = prompt.toLowerCase();
const words = [...new Set(text.split(/[^\p{L}\p{N}_.+-]+/u).filter((word) => word.length >= 2))];
const asArray = (value) => Array.isArray(value) ? value : (value == null ? [] : [value]);
const aliasHits = (items = []) => asArray(items).filter((item) => asArray(item.aliases).some((value) => text.includes(String(value).toLowerCase())));
const projectTypes = aliasHits(profile.projectTypes).map((item) => item.name);
const phases = aliasHits(profile.phases).map((item) => item.name);
const domains = aliasHits(profile.domains).map((item) => item.name);
const disciplines = aliasHits(profile.disciplines).map((item) => item.name);
const families = aliasHits(profile.families).map((item) => item.name);
const matchedRoutes = aliasHits(profile.routes);
const routeNames = matchedRoutes.map((item) => item.name);

const scores = catalog.skills.map((skill) => {
  let score = 0;
  const reasons = [];
  const searchable = `${skill.name} ${skill.trigger || ''} ${asArray(skill.aliases).join(' ')}`.toLowerCase();
  if (text.includes(String(skill.name).toLowerCase())) { score += 100; reasons.push('name'); }
  for (const word of words) {
    if (searchable.includes(word)) { score += 8; reasons.push(`term:${word}`); }
  }
  if (domains.includes(skill.domain)) { score += 18; reasons.push(`domain:${skill.domain}`); }
  if (disciplines.includes(skill.discipline)) { score += 28; reasons.push(`discipline:${skill.discipline}`); }
  if (families.includes(skill.family)) { score += 36; reasons.push(`family:${skill.family}`); }
  if (asArray(skill.projectTypes).some((value) => projectTypes.includes(value))) score += 12;
  if (asArray(skill.phases).some((value) => phases.includes(value))) score += 12;
  let role = 'candidate';
  for (const route of matchedRoutes) {
    if (asArray(route.ownerSkills).includes(skill.name)) { score += 200; role = 'owner'; reasons.push(`route:${route.name}`); }
    const support = asArray(route.supportingSkills).some((item) => (typeof item === 'string' ? item : item.name) === skill.name);
    if (support && role !== 'owner') { score += 80; role = 'support'; reasons.push(`support:${route.name}`); }
  }
  return { score, role, ...skill, matched: [...new Set(reasons)].join('; ') };
}).filter((item) => item.score > 0);

const roleOrder = { owner: 0, support: 1, candidate: 2 };
scores.sort((a, b) => roleOrder[a.role] - roleOrder[b.role] || b.score - a.score || a.name.localeCompare(b.name));
const candidates = scores.slice(0, limit).map((item, index) => ({ ...item, rank: index + 1 }));
const byName = new Map(catalog.skills.map((skill) => [skill.name, skill]));
const resolved = (name) => byName.get(name) || null;
const workUnits = matchedRoutes.filter((route) => route.kind === 'capability').map((route) => ({
  route: route.name,
  plane: route.plane,
  domain: route.domain,
  discipline: route.discipline,
  family: route.family,
  owner: asArray(route.ownerSkills).map(resolved).find(Boolean) || null,
  supportingSkills: asArray(route.supportingSkills).map((item) => resolved(typeof item === 'string' ? item : item.name)).filter(Boolean),
}));
const routeSkills = (kind) => matchedRoutes.filter((route) => route.kind === kind).flatMap((route) => asArray(route.ownerSkills).map(resolved)).filter(Boolean);

console.log(JSON.stringify({
  projectTypes, phases, domains, disciplines, families, routes: routeNames,
  workUnits,
  accessSkills: routeSkills('access'),
  controlSkills: routeSkills('control'),
  candidateCount: scores.length,
  candidates,
}, null, 2));
