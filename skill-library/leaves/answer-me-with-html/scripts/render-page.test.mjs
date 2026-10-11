import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { renderPage } from './render-page.mjs';

const base = process.env.SKILL_ACTIVITY_TEST_ROOT || os.tmpdir();
fs.mkdirSync(base, { recursive: true });
const scratch = fs.mkdtempSync(path.join(base, 'html-render-test-'));
let checks = 0;
const check = (condition, message) => { assert.ok(condition, message); checks++; };
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
try {
  const input = path.join(scratch, 'draft.md'), output = path.join(scratch, 'page.html');
  fs.writeFileSync(input, '---\ntitle: Fixture explanation\nlang: en\n---\n## Flow\n```flow\nReader -> Renderer: draft\nRenderer -> Page: result\n```\n## Facts\n| Item | State |\n|---|---|\n| Source | Verified |\n');
  const result = renderPage({ input, output });
  const html = fs.readFileSync(output, 'utf8');
  check(result.bytes > 1000 && html.includes('Fixture explanation') && html.includes('Renderer') && html.includes('<svg'), 'Actual rendering preserves text and creates a diagram');
  check(html.includes('Content-Security-Policy') && html.includes("connect-src 'none'"), 'Offline policy present');
  check(fs.readdirSync(scratch).sort().join('|') === 'draft.md|page.html', 'Invocation-owned scratch removed, source/output retained');
  const original = hash(output);
  assert.throws(() => renderPage({ input, output }), /Output exists/); checks++;
  check(hash(output) === original, 'Existing output remains byte-identical');
  for (const draft of ['```html\n<script>alert(1)</script>\n```', '![remote](https://example.com/image.png)', '```js src=private.txt\n```', '<iframe src="https://example.com"></iframe>']) {
    fs.writeFileSync(input, draft);
    const rejectedOutput = path.join(scratch, 'rejected.html');
    assert.throws(() => renderPage({input, output: rejectedOutput}), /not supported|separately authorized/); checks++;
    check(!fs.existsSync(rejectedOutput) && !fs.readdirSync(scratch).some(name=>name.startsWith('.am-render-')), 'Rejected draft creates no page/runtime');
  }
  fs.writeFileSync(input, 'a'.repeat(256*1024+1));
  assert.throws(() => renderPage({input, output:path.join(scratch,'oversize.html')}), /256 KiB/); checks++;
  assert.throws(() => renderPage({input:'relative.md', output:path.join(scratch,'relative.html')}), /absolute/); checks++;
  assert.throws(() => renderPage({input, output:path.join(scratch,'not-html.txt')}), /absolute/); checks++;
  console.log(JSON.stringify({ checks, passed: checks, failed: 0, scope: 'Renderer/guards/source preservation; browser layout tested separately.' }));
} finally {
  if (path.dirname(fs.realpathSync(scratch)) !== fs.realpathSync(base)) throw new Error('Scratch cleanup scope changed');
  fs.rmSync(scratch, { recursive:true, force:true });
}
