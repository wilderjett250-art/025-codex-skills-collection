import { eventId, recordActivity } from './activity-core.mjs';

// This hook deliberately ignores arguments, results and transcript paths.
let input = '';
for await (const chunk of process.stdin) input += chunk;

try {
  const call = JSON.parse(input);
  if (call.hook_event_name !== 'PostToolUse') process.exit(0);
  const match = /^mcp__(.+?)__(.+)$/.exec(call.tool_name || '');
  if (!match) process.exit(0);
  if (typeof call.tool_use_id !== 'string' || !call.tool_use_id) process.exit(0);
  recordActivity({
    kind: 'mcp_call',
    server: match[1],
    name: match[2],
    eventId: eventId(call.tool_use_id),
    result: call.tool_response?.isError === true ? 'reported_error' : 'completed_unclassified',
  });
} catch (error) {
  console.error(`Skill activity hook failed: ${error.message}`);
  process.exitCode = 1;
}
