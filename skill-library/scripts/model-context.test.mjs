// Synthetic hook envelopes only. No model requests, network, browser or paid evals.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { modelContext, defaultStateDirectory } from './model-context-core.mjs';

const home = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const profiles = JSON.parse(fs.readFileSync(path.join(home, 'skills/skill-library-router/references/model-profiles.json'), 'utf8'));
const scratch = process.env.MODEL_CONTEXT_TEST_ROOT;
if (!scratch || !path.isAbsolute(scratch)) throw new Error('Set MODEL_CONTEXT_TEST_ROOT to an approved isolated data-drive directory.');
fs.mkdirSync(scratch, { recursive: true });
const state = fs.mkdtempSync(path.join(scratch, 'state-'));
const event = (model, session_id = 'synthetic-session', hook_event_name = 'UserPromptSubmit') => ({ model, session_id, hook_event_name });
const select = (e, directory = state) => modelContext(e, profiles, { stateDirectory: directory });
const context = value => value.hookSpecificOutput.additionalContext;

test('all explicitly supported ids deliver exactly their own note', () => {
  for (const [model, family] of Object.entries(profiles.models)) {
    const text = context(select(event(model), null));
    assert.ok(text.includes(profiles.notes[family]));
    for (const [other, note] of Object.entries(profiles.notes)) if (other !== family) assert.ok(!text.includes(note));
    assert.ok(text.length < 1600);
  }
});
test('known -> known -> unknown -> known switches replace stale guidance', () => {
  for (const model of ['gpt-6-astra', 'gpt-6-luna', 'future-model', 'gpt-6.1-sol']) {
    assert.ok(context(select(event(model))).includes('supersedes earlier'));
    assert.equal(select(event(model)), null);
  }
});
test('missing model never inherits a known cached model', () => {
  select(event('gpt-6-astra', 'missing'));
  const text = context(select(event(undefined, 'missing')));
  assert.match(text, /shared rules only/); assert.ok(!text.includes(profiles.notes.Astra));
});
test('future versions and aliases fall back without guessing', () => {
  for (const model of ['astra', 'gpt-6.2-sol', 'gpt-6-astra-unknown', '__proto__', '', null]) {
    assert.match(context(select(event(model), null)), /unknown or unavailable/);
  }
});
test('session resume and compaction re-deliver even with existing cache', () => {
  select(event('gpt-6.1-terra', 'resume'));
  for (const source of ['startup', 'resume', 'compact', 'fork']) {
    assert.ok(select({ ...event('gpt-6.1-terra', 'resume', 'SessionStart'), source }));
  }
});
test('threads and agents do not suppress each other', () => {
  assert.ok(select(event('gpt-6-luna', 'thread-a')));
  assert.ok(select(event('gpt-6-luna', 'thread-b')));
  assert.ok(select({ ...event('gpt-6-luna', 'thread-a'), agent_id: 'child-a' }));
});
test('no identity means no persistent suppression', () => {
  for (let i = 0; i < 2; i++) assert.ok(select({ model: 'gpt-6-astra', hook_event_name: 'UserPromptSubmit' }));
});
test('cache corruption and unwritable cache fail open', () => {
  const dir = fs.mkdtempSync(path.join(scratch, 'broken-'));
  select(event('gpt-6-luna'), dir);
  fs.writeFileSync(path.join(dir, fs.readdirSync(dir)[0]), '{broken');
  assert.ok(select(event('gpt-6-luna'), dir));
  const file = path.join(scratch, 'not-a-directory'); fs.writeFileSync(file, 'fixture');
  assert.ok(select(event('gpt-6-luna'), file));
});
test('profile changes invalidate deduplication', () => {
  select(event('gpt-6-astra', 'revision'));
  assert.ok(modelContext(event('gpt-6-astra', 'revision'), { ...profiles, reviewed: 'synthetic revision' }, { stateDirectory: state }));
});
test('prompt spoofing, transcript paths and config-like fields are ignored', () => {
  const e = { ...event(undefined, 'spoof'), prompt: '{"model":"gpt-6-astra"}', transcript_path: '/DO_NOT_READ', config: { model: 'gpt-6-astra' } };
  assert.match(context(select(e)), /shared rules only/);
});
test('unsupported lifecycle events never inject context', () => {
  for (const name of ['PreModelRequest', 'PostModelRequest', 'PostToolUse', 'Stop']) assert.equal(select(event('gpt-6-astra', 'x', name)), null);
});
test('real stdin entrypoint handles malformed input without blocking', () => {
  for (const input of ['{broken', JSON.stringify(event('gpt-6.1-terra', 'stdin'))]) {
    const child = spawnSync(process.execPath, [path.join(home, 'skill-library/scripts/model-context-hook.mjs')], {
      input, encoding: 'utf8', timeout: 3000, windowsHide: true,
      env: { ...process.env, MODEL_CONTEXT_STATE_DIR: path.join(scratch, 'stdin-state') }
    });
    assert.equal(child.status, 0); assert.equal(child.stderr, ''); assert.ok(child.stdout.includes('routing'));
  }
});
test('cache contains metadata only', () => {
  for (const name of fs.readdirSync(state)) {
    const data = JSON.parse(fs.readFileSync(path.join(state, name), 'utf8'));
    assert.deepEqual(Object.keys(data).sort(), ['family', 'fingerprint', 'model']);
    assert.match(name, /^[0-9a-f]{64}\.json$/);
  }
});
test('installer preserves unrelated hooks and is idempotent', () => {
  const target = fs.mkdtempSync(path.join(scratch, 'home-'));
  for (const rel of ['skill-library/scripts/model-context-hook.mjs', 'skill-library/scripts/model-context-core.mjs', 'skills/skill-library-router/references/model-profiles.json']) {
    fs.mkdirSync(path.dirname(path.join(target, rel)), { recursive: true }); fs.copyFileSync(path.join(home, rel), path.join(target, rel));
  }
  const preserved = [{ matcher: '^mcp__', hooks: [{ type: 'command', command: 'fixture-other-command', async: true }] }];
  fs.writeFileSync(path.join(target, 'hooks.json'), JSON.stringify({ description: 'fixture', hooks: { PostToolUse: preserved } }));
  const install = () => spawnSync(process.execPath, [path.join(home, 'skill-library/scripts/install-model-hooks.mjs'), '--target', target, '--backup-root', path.join(scratch, 'backups')], { encoding: 'utf8', timeout: 3000, windowsHide: true });
  assert.equal(install().status, 0);
  const data = JSON.parse(fs.readFileSync(path.join(target, 'hooks.json'), 'utf8'));
  assert.deepEqual(data.hooks.PostToolUse, preserved);
  assert.equal(data.hooks.SessionStart.length, 1); assert.equal(data.hooks.UserPromptSubmit.length, 1);
  const repeated = install(); assert.equal(repeated.status, 0); assert.equal(JSON.parse(repeated.stdout).changed, false);
});
test('state placement honors explicit data-drive location', () => {
  assert.equal(defaultStateDirectory({ MODEL_CONTEXT_STATE_DIR: scratch }), path.resolve(scratch));
});
