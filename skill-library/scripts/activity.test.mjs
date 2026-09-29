import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { searchSkills } from './search-skills.mjs';

const scripts = path.dirname(fileURLToPath(import.meta.url));
const parent = process.env.SKILL_ACTIVITY_TEST_ROOT || os.tmpdir();
fs.mkdirSync(parent, { recursive: true });
const directory = fs.mkdtempSync(path.join(parent, 'skill-activity-test-'));
const env = { ...process.env, SKILL_ACTIVITY_DIR: directory };
const run = (script, args = [], input = '') => spawnSync(process.execPath, [path.join(scripts, script), ...args], {
  env, input, encoding: 'utf8', windowsHide: true,
});

test('MCP hook records only call metadata and deduplicates report rows', () => {
  const event = {
    hook_event_name: 'PostToolUse',
    tool_name: 'mcp__example_server__lookup',
    tool_use_id: 'test-call-1',
    tool_input: { password: 'must-not-save' },
    tool_response: { isError: false, content: [{ text: 'private-response' }] },
  };
  const first = run('activity-hook.mjs', [], JSON.stringify(event));
  const duplicate = run('activity-hook.mjs', [], JSON.stringify(event));
  assert.equal(first.status, 0, first.stderr);
  assert.equal(duplicate.status, 0, duplicate.stderr);
  const log = fs.readFileSync(path.join(directory, 'events.jsonl'), 'utf8');
  assert.ok(!log.includes('must-not-save'));
  assert.ok(!log.includes('private-response'));
  assert.ok(!log.includes('test-call-1'));
  const report = run('activity-report.mjs', ['--days', '7']);
  assert.equal(report.status, 0, report.stderr);
  assert.equal(JSON.parse(report.stdout).mcpCalls, 1);
  assert.equal(JSON.parse(report.stdout).mcpServers.example_server, 1);
});

test('on-demand Skill reader emits the full entry and records one load', () => {
  const loaded = run('read-skill.mjs', ['skill-library-router']);
  assert.equal(loaded.status, 0, loaded.stderr);
  assert.match(loaded.stdout, /name: skill-library-router/);
  const report = JSON.parse(run('activity-report.mjs').stdout);
  assert.equal(report.skillInstructionLoads, 1);
  assert.equal(report.skills['skill-library-router'], 1);
});

test('unknown Skill name is rejected without a load event', () => {
  const loaded = run('read-skill.mjs', ['not-a-skill-' + crypto.randomUUID()]);
  assert.equal(loaded.status, 2);
  const report = JSON.parse(run('activity-report.mjs').stdout);
  assert.equal(report.skillInstructionLoads, 1);
});

test('task metadata search loads the selected on-demand library leaf and records one load', () => {
  const root = path.resolve(scripts, '..');
  const readJson = (name) => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8').replace(/^\uFEFF/, ''));
  const result = searchSkills('给 DaVinci Resolve 视频调色', readJson('catalog.json'), readJson('discovery-profile.json'));
  assert.equal(result.candidates[0]?.name, 'davinci-resolve-color');
  const loaded = run('read-skill.mjs', [result.candidates[0].name]);
  assert.equal(loaded.status, 0, loaded.stderr);
  assert.match(loaded.stdout, /name: davinci-resolve-color/);
  assert.match(loaded.stdout, /# Davinci Resolve Color/);
  const report = JSON.parse(run('activity-report.mjs').stdout);
  assert.equal(report.skillInstructionLoads, 2);
  assert.equal(report.skills['davinci-resolve-color'], 1);
});

process.on('exit', () => {
  const actualParent = fs.realpathSync(parent).toLowerCase();
  const actualDirectory = fs.realpathSync(directory).toLowerCase();
  if (actualDirectory.startsWith(actualParent + path.sep) && path.basename(directory).startsWith('skill-activity-test-')) {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});
