#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { modelContext, defaultStateDirectory } from './model-context-core.mjs';

// Codex supplies the active model in the hook envelope. Never inspect prompt text or transcript_path.
let input = '';
try {
  process.stdin.setEncoding('utf8');
  for await (const chunk of process.stdin) {
    input += chunk;
    if (input.length > 2_000_000) throw new Error('Input budget');
  }
  const event = JSON.parse(input);
  const home = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
  const profiles = JSON.parse(fs.readFileSync(path.join(home, 'skills/skill-library-router/references/model-profiles.json'), 'utf8'));
  const output = modelContext(event, profiles, { stateDirectory: defaultStateDirectory() });
  if (output) console.log(JSON.stringify(output));
} catch {
  // Malformed input, missing resources and cache failures must never block a user turn.
  console.log('Current model routing: use the shared Skill library and existing two-stage router. Disregard earlier model-specific routing notes; do not guess a model or ask the user.');
}
