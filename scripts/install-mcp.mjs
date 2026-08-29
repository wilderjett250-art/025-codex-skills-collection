#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..');
const codexHome = path.resolve(process.env.CODEX_HOME || path.join(os.homedir(), '.codex'));

function option(name, fallback = null) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

const profileName = option('--profile', 'full');
const filesystemRoot = option('--filesystem-root');
const force = process.argv.includes('--force');
const skipPlugins = process.argv.includes('--skip-plugins');
const catalog = JSON.parse(fs.readFileSync(path.join(repoRoot, 'mcp', 'catalog.json'), 'utf8'));
const profiles = JSON.parse(fs.readFileSync(path.join(repoRoot, 'mcp', 'profiles.json'), 'utf8'));
const selected = profiles[profileName];
if (!selected) throw new Error(`Unknown MCP profile: ${profileName}`);

function codex(args, quiet = false) {
  return spawnSync('codex', args, {
    encoding: 'utf8',
    env: process.env,
    stdio: quiet ? 'ignore' : 'inherit',
  });
}

if (spawnSync('codex', ['--version'], { stdio: 'ignore' }).status !== 0) {
  throw new Error('codex command is required for MCP registration.');
}

const results = { installed: 0, existing: 0, local: 0 };
for (const name of selected) {
  const entry = catalog.find((item) => item.name === name);
  if (!entry) throw new Error(`Missing MCP catalog entry: ${name}`);
  const exists = codex(['mcp', 'get', name, '--json'], true).status === 0;
  if (exists && !force) {
    console.log(`  Existing MCP kept: ${name}`);
    results.existing += 1;
    continue;
  }
  if (exists && force && codex(['mcp', 'remove', name], true).status !== 0) {
    throw new Error(`Unable to remove existing MCP: ${name}`);
  }
  if (entry.installMode === 'manual') {
    console.log(`  Requires local setup: ${name}`);
    results.local += 1;
    continue;
  }
  if (entry.installMode === 'parameter' && !filesystemRoot) {
    console.log(`  Requires --filesystem-root: ${name}`);
    results.local += 1;
    continue;
  }

  let commandArgs;
  if (entry.installMode === 'parameter') {
    const resolvedRoot = path.resolve(filesystemRoot);
    if (!fs.statSync(resolvedRoot).isDirectory()) throw new Error(`Not a directory: ${resolvedRoot}`);
    commandArgs = ['mcp', 'add', name, '--', entry.command, ...entry.args, resolvedRoot];
  } else if (entry.type === 'http') {
    commandArgs = ['mcp', 'add', name, '--url', entry.url];
    if (entry.bearerTokenEnvVar) {
      commandArgs.push('--bearer-token-env-var', entry.bearerTokenEnvVar);
    }
  } else {
    commandArgs = ['mcp', 'add', name, '--', entry.command, ...entry.args];
  }
  if (codex(commandArgs, true).status !== 0) throw new Error(`MCP registration failed: ${name}`);
  console.log(`  MCP registered: ${name}`);
  results.installed += 1;
}

if (!skipPlugins) {
  const configPath = path.join(codexHome, 'config.toml');
  const plugins = JSON.parse(fs.readFileSync(path.join(repoRoot, 'presets', 'plugins.json'), 'utf8'));
  let config = fs.existsSync(configPath) ? fs.readFileSync(configPath, 'utf8') : '';
  for (const plugin of plugins) {
    const section = `[plugins."${plugin.id}"]`;
    if (!config.split(/\r?\n/).some((line) => line.trim() === section)) {
      config += `\n${section}\nenabled = ${plugin.enabled ? 'true' : 'false'}\n`;
    }
  }
  fs.mkdirSync(path.dirname(configPath), { recursive: true });
  fs.writeFileSync(configPath, config, 'utf8');
  console.log(`Plugin presets applied: ${plugins.length}`);
}

console.log(`MCP result: installed ${results.installed}, kept ${results.existing}, local setup ${results.local}`);
