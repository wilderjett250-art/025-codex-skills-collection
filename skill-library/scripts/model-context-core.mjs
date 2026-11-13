// Local metadata routing only. This module never reads prompts, transcripts or config defaults.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import os from 'node:os';

export const digest = value => crypto.createHash('sha256').update(value).digest('hex');
export function defaultStateDirectory(env = process.env, platform = process.platform) {
  if (env.MODEL_CONTEXT_STATE_DIR) return path.resolve(env.MODEL_CONTEXT_STATE_DIR);
  if (platform === 'win32') {
    for (const drive of ['I:/', 'G:/']) if (fs.existsSync(drive)) return path.join(drive, 'codex-artifacts', 'skill-model-state');
    return null; // No new state on the system drive; repeated short context is safe.
  }
  return path.join(env.XDG_STATE_HOME || path.join(os.homedir(), '.local', 'state'), 'codex-skill-model');
}
export function modelContext(event, profiles, { stateDirectory = null } = {}) {
  const eventName = event?.hook_event_name;
  if (!['SessionStart', 'UserPromptSubmit'].includes(eventName)) return null;
  const raw = typeof event.model === 'string' && event.model.length < 128 ? event.model : '';
  // Deliberate exact allowlist. Future models and arbitrary aliases fall back to shared rules.
  const family = Object.hasOwn(profiles.models, raw) ? profiles.models[raw] : null;
  const fingerprint = digest(JSON.stringify(profiles));
  const identity = typeof event.session_id === 'string' && event.session_id.length <= 256 ? event.session_id : null;
  const agent = typeof event.agent_id === 'string' ? event.agent_id.slice(0, 256) : '';
  const key = identity ? digest(`${identity}\0${agent}`) : null;
  const file = stateDirectory && key ? path.join(stateDirectory, `${key}.json`) : null;
  let previous;
  try { if (file) previous = JSON.parse(fs.readFileSync(file, 'utf8')); } catch {}
  if (eventName !== 'SessionStart' && previous?.model === raw && previous?.fingerprint === fingerprint) return null;
  const selection = family
    ? `Current model family: ${family}. ${profiles.notes[family]}`
    : 'Current model is unknown or unavailable. Use shared rules only, without asking the user to identify it.';
  const context = `Current model routing (supersedes earlier model-specific routing notes): ${selection}\n${profiles.shared}`;
  if (context.length > 1600) throw new Error('Model routing context exceeds budget');
  // Metadata-only deduplication; cache is never used to identify a missing current model.
  if (file) {
    let temp;
    try {
      fs.mkdirSync(stateDirectory, { recursive: true });
      temp = `${file}.${process.pid}.${crypto.randomBytes(4).toString('hex')}.tmp`;
      fs.writeFileSync(temp, JSON.stringify({ model: raw, family, fingerprint }), { mode: 0o600, flag: 'wx' });
      fs.renameSync(temp, file);
    } catch {} finally { if (temp) { try { fs.unlinkSync(temp); } catch {} } }
  }
  return { hookSpecificOutput: { hookEventName: eventName, additionalContext: context } };
}
