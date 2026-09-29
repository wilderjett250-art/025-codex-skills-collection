import fs from 'node:fs';
import path from 'node:path';
import { activityDirectory } from './activity-core.mjs';

const daysFlag = process.argv.indexOf('--days');
const days = daysFlag < 0 ? 7 : Number(process.argv[daysFlag + 1]);
if (!Number.isInteger(days) || days < 1 || days > 365) {
  console.error('Use --days with an integer from 1 to 365.');
  process.exit(2);
}
const file = path.join(activityDirectory(), 'events.jsonl');
const lines = fs.existsSync(file) ? fs.readFileSync(file, 'utf8').split(/\r?\n/) : [];
const cutoff = Date.now() - days * 86400000;
const seen = new Set();
const bySkill = new Map();
const byServer = new Map();
let invalid = 0;
let mcpErrors = 0;
for (const line of lines) {
  if (!line) continue;
  let event;
  try { event = JSON.parse(line); } catch { invalid++; continue; }
  if (event.schemaVersion !== 1 || !['mcp_call', 'skill_load'].includes(event.kind) || typeof event.eventId !== 'string') { invalid++; continue; }
  if (seen.has(event.eventId)) continue;
  seen.add(event.eventId);
  const at = Date.parse(event.at);
  if (!Number.isFinite(at) || at < cutoff || at > Date.now() + 60000) continue;
  if (event.kind === 'skill_load' && typeof event.name === 'string') bySkill.set(event.name, (bySkill.get(event.name) || 0) + 1);
  if (event.kind === 'mcp_call' && typeof event.server === 'string') {
    byServer.set(event.server, (byServer.get(event.server) || 0) + 1);
    if (event.result === 'reported_error') mcpErrors++;
  }
}
const sorted = map => Object.fromEntries([...map].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
const report = {
  periodDays: days,
  source: file,
  skillInstructionLoads: [...bySkill.values()].reduce((sum, value) => sum + value, 0),
  mcpCalls: [...byServer.values()].reduce((sum, value) => sum + value, 0),
  mcpReportedErrors: mcpErrors,
  skills: sorted(bySkill),
  mcpServers: sorted(byServer),
  invalidLines: invalid,
  caveat: 'Local observed events only; not the Codex product activity dashboard or proof that a Skill workflow was applied.',
};
console.log(JSON.stringify(report, null, 2));
