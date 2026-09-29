import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';

export function activityDirectory() {
  const codexHome = process.env.CODEX_HOME || path.join(os.homedir(), '.codex');
  return process.env.SKILL_ACTIVITY_DIR || path.join(codexHome, 'skill-activity');
}

export function eventId(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

export function recordActivity(event) {
  const directory = activityDirectory();
  fs.mkdirSync(directory, { recursive: true });
  const file = path.join(directory, 'events.jsonl');
  const line = JSON.stringify({ schemaVersion: 1, at: new Date().toISOString(), ...event }) + '\n';
  fs.appendFileSync(file, line, { encoding: 'utf8', flag: 'a' });
}
