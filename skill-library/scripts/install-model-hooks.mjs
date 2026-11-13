#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { digest } from './model-context-core.mjs';

const args = process.argv.slice(2);
const option = name => { const i = args.indexOf(name); return i < 0 ? null : args[i + 1]; };
for (let i = 0; i < args.length; i++) {
  if (!['--target', '--backup-root'].includes(args[i]) || !args[i + 1] || args[i + 1].startsWith('--')) throw new Error('Usage: install-model-hooks.mjs [--target <codex-home>] --backup-root <data-drive-directory>');
  i++;
}
const target = path.resolve(option('--target') || process.env.CODEX_HOME || path.join(os.homedir(), '.codex'));
const backupRoot = option('--backup-root');
if (!backupRoot) throw new Error('Provide --backup-root on an approved data drive.');
const script = path.join(target, 'skill-library/scripts/model-context-hook.mjs');
for (const file of [script, path.join(target, 'skill-library/scripts/model-context-core.mjs'), path.join(target, 'skills/skill-library-router/references/model-profiles.json')]) {
  if (!fs.statSync(file).isFile()) throw new Error('Install the Skill Library before registering its model hooks.');
}
const file = path.join(target, 'hooks.json');
const original = fs.existsSync(file) ? fs.readFileSync(file) : null;
const current = original ? JSON.parse(original.toString('utf8').replace(/^\uFEFF/, '')) : {};
current.hooks ||= {};
// Only our dedicated entries are updated; preserve existing handlers, order and trust/disabled settings.
const command = `"${process.execPath}" "${script}"`;
for (const event of ['SessionStart', 'UserPromptSubmit']) {
  current.hooks[event] ||= [];
  const entries = current.hooks[event];
  const own = entries.flatMap(entry => entry.hooks || []).filter(item => /(?:^|[\\/])model-context-hook\.mjs["']?(?:\s|$)/.test(item.command || ''));
  if (own.length > 1) throw new Error(`Duplicate model-context hooks in ${event}; inspect before changing.`);
  const handler = { type: 'command', command, timeout: 3, additionalContextLimit: 500 };
  if (own.length) Object.assign(own[0], handler);
  else entries.push({ hooks: [handler] });
}
const content = Buffer.from(JSON.stringify(current, null, 2) + '\n');
if (original?.equals(content)) {
  console.log(JSON.stringify({ changed: false, activation: 'Check hooks/list or Settings > Hooks; installation does not grant trust.' }));
  process.exit(0);
}
const backup = path.resolve(backupRoot, `model-hooks-${new Date().toISOString().replaceAll(':', '-')}`);
fs.mkdirSync(backup, { recursive: true, mode: 0o700 });
if (original) {
  fs.writeFileSync(path.join(backup, 'hooks.json'), original, { mode: 0o600 });
  if (digest(fs.readFileSync(path.join(backup, 'hooks.json'))) !== digest(original)) throw new Error('Backup verification failed');
}
fs.writeFileSync(path.join(backup, 'manifest.json'), JSON.stringify({ target: file, existed: Boolean(original), sha256: original ? digest(original) : null, restore: 'Restore only hooks.json after checking concurrent changes; leave config trust and other files unchanged.' }, null, 2));
// Avoid overwriting a concurrently modified hook file.
if (original && !fs.readFileSync(file).equals(original)) throw new Error('Hook file changed concurrently');
fs.mkdirSync(target, { recursive: true });
fs.writeFileSync(file, content);
console.log(JSON.stringify({ changed: true, backup, activation: 'Review the two exact definitions in Settings > Hooks (CLI: /hooks). Never copy trust hashes between machines.' }));
