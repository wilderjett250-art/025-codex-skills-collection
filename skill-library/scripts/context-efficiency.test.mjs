import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { auditContextCost } from './audit-context-cost.mjs';
import { searchSkills } from './search-skills.mjs';

const library = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const home = path.dirname(library);
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const catalog = read(path.join(library, 'catalog.json'));
const discovery = read(path.join(library, 'discovery-profile.json'));
let checks = 0;
const check = (condition, message) => { assert.ok(condition, message); checks++; };

for (const [query, expected] of [
  ['离线HTML说明 请求调用链图文说明', 'answer-me-with-html'],
  ['把复杂解释做成HTML页面和多维对比', 'answer-me-with-html'],
  ['Windows原生桌面 WPF E2E pywinauto 自动化测试', 'windows-desktop-e2e'],
  ['Qt 原生桌面 AutomationId 测试定位器', 'windows-desktop-e2e'],
  ['Skill审计 token消耗 加载成本 入口过长', 'workspace-surface-audit'],
  ['请逐行讲解这份源码帮助我学习', 'code-explanation'],
  ['Playwright购物流程自动化验收', 'e2e-testing'],
  ['React组件重复渲染和Next.js请求瀑布', 'react-engineering'],
  ['根据岗位JD优化简历', 'resume-tailor'],
]) {
  const matches = searchSkills(query, catalog, discovery).candidates;
  check(matches.length <= 3 && matches[0]?.name === expected, `Routing boundary: ${query}: ${matches.map(s=>s.name)}`);
}

const windows = catalog.skills.find(skill => skill.name === 'windows-desktop-e2e');
check(windows.canonicalPath === 'domain/computing-digital/browser-desktop/browser-automation/windows-desktop-e2e', 'Existing canonical path retained');
const references = path.join(path.dirname(windows.skillPath), 'references');
const layout = read(path.join(references, 'source-layout.json'));
const reconstructed = Buffer.concat([...layout.pieces].sort((a,b)=>a.index-b.index).map(piece =>
  fs.readFileSync(path.join(references, piece.file)).subarray(piece.offset, piece.offset+piece.length)));
check(reconstructed.length === layout.preservedBytes && crypto.createHash('sha256').update(reconstructed).digest('hex') === layout.sourceSha256, 'Original guide bytes preserved');
const html = catalog.skills.find(skill => skill.name === 'answer-me-with-html');
const htmlRoot = path.dirname(html.skillPath);
const upstream = read(path.join(htmlRoot, 'UPSTREAM.json'));
check(crypto.createHash('sha256').update(fs.readFileSync(path.join(htmlRoot, upstream.bundle))).digest('hex') === upstream.bundleSha256, 'Pinned renderer bundle integrity');
check(fs.existsSync(path.join(htmlRoot, 'LICENSE')), 'Upstream license retained');

const scratchBase = process.env.SKILL_ACTIVITY_TEST_ROOT || os.tmpdir();
fs.mkdirSync(scratchBase, { recursive: true });
const scratch = fs.mkdtempSync(path.join(scratchBase, 'context-cost-test-'));
try {
  const active = path.join(scratch, 'skills/a');
  fs.mkdirSync(active, { recursive: true });
  fs.mkdirSync(path.join(scratch, 'skill-library/leaves'), { recursive: true });
  fs.writeFileSync(path.join(scratch, 'AGENTS.md'), 'fixture rules');
  fs.writeFileSync(path.join(active, 'SKILL.md'), 'PRIVATE_BODY_MARKER 中文🙂\n[detail](references/absent.md)');
  const fixture = { skills: [{name: 'fixture', source: 'active', trigger: 'fixture description', skillPath: path.join(active, 'SKILL.md')}] };
  fs.writeFileSync(path.join(scratch, 'skill-library/catalog.json'), JSON.stringify(fixture));
  const result = auditContextCost(scratch);
  check(result.total === 1 && result.active === 1 && result.rows[0].missingReferences.length === 1, 'Structural audit counts and missing reference');
  check(!JSON.stringify(result).includes('PRIVATE_BODY_MARKER'), 'No Skill bodies in reports');
  const external = path.join(scratch, 'SKILL.md');
  fs.writeFileSync(external, 'outside allowed Skill roots');
  fixture.skills[0].skillPath = external;
  fs.writeFileSync(path.join(scratch, 'skill-library/catalog.json'), JSON.stringify(fixture));
  assert.throws(() => auditContextCost(scratch), /outside allowed Skill roots/); checks++;
  assert.throws(() => auditContextCost(scratch, 500), /limit/); checks++;
} finally {
  if (path.dirname(fs.realpathSync(scratch)) !== fs.realpathSync(scratchBase)) throw new Error('Scratch cleanup scope changed');
  fs.rmSync(scratch, { recursive: true, force: true });
}
console.log(JSON.stringify({ checks, passed: checks, failed: 0, scope: 'Retrieval, source integrity and structural audit only; not automatic model invocation or real desktop acceptance.' }));
