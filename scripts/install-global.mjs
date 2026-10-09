#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const targetIndex = args.indexOf('--target');
const target = path.resolve(targetIndex >= 0 ? args[targetIndex + 1] : process.env.CODEX_HOME || path.join(os.homedir(), '.codex'));
const rules = args.includes('--rules');
const hook = args.includes('--hook');
if (!rules && !hook) throw new Error('Select --rules and/or --hook; config defaults are a manual merge reference.');
const known = new Set(['--target', '--rules', '--hook']);
for (let index = 0; index < args.length; index++) {
  if (!known.has(args[index])) throw new Error(`Unknown option: ${args[index]}`);
  if (args[index] === '--target') { if (!args[index + 1]) throw new Error('--target requires a path'); index++; }
}
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const preset = path.join(repo, 'presets', 'global');
const plan = [];
if (rules) {
  const content = fs.readFileSync(path.join(preset, 'AGENTS.md'), 'utf8').replaceAll('<codex-home>', target.replaceAll('\\', '/'));
  plan.push({ file: path.join(target, 'AGENTS.md'), content });
}
if (hook) {
  const file = path.join(target, 'hooks.json');
  const current = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '')) : {};
  const additions = JSON.parse(fs.readFileSync(path.join(preset, 'hooks.template.json'), 'utf8'));
  const command = `"${process.execPath}" "${path.join(target, 'skill-library', 'scripts', 'activity-hook.mjs')}"`;
  if (!fs.existsSync(path.join(target, 'skill-library', 'scripts', 'activity-hook.mjs'))) throw new Error('Install the Skill Library before installing the hook.');
  current.hooks ||= {};
  current.hooks.PostToolUse ||= [];
  const exists = current.hooks.PostToolUse.some(entry => (entry.hooks || []).some(item => item.command?.includes('activity-hook.mjs')));
  if (!exists) {
    const entry = additions.hooks.PostToolUse[0];
    entry.hooks[0].command = command;
    current.hooks.PostToolUse.push(entry);
  }
  plan.push({ file, content: JSON.stringify(current, null, 2) + '\n' });
}
const writes = plan.filter(item => !fs.existsSync(item.file) || fs.readFileSync(item.file, 'utf8') !== item.content);
const backup = path.join(target, 'backups', 'global-settings', new Date().toISOString().replaceAll(':', '-'));
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const manifest = [];
for (const item of writes) {
  const existed = fs.existsSync(item.file);
  const name = path.basename(item.file);
  if (existed) {
    fs.mkdirSync(backup, { recursive: true });
    const original = fs.readFileSync(item.file);
    fs.writeFileSync(path.join(backup, name), original);
    if (hash(fs.readFileSync(path.join(backup, name))) !== hash(original)) throw new Error('Backup hash verification failed');
    manifest.push({ name, existed, sha256: hash(original) });
  } else manifest.push({ name, existed });
}
if (writes.length) {
  fs.mkdirSync(backup, { recursive: true });
  fs.writeFileSync(path.join(backup, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  fs.mkdirSync(target, { recursive: true });
  for (const item of writes) fs.writeFileSync(item.file, item.content);
}
console.log(JSON.stringify({ installed: writes.map(item => path.basename(item.file)), backup: writes.length ? backup : null, configDefaults: 'presets/global/config.defaults.toml (manual merge)' }));
