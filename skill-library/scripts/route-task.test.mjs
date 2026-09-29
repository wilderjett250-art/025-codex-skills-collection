// Behavioral regression checks. Runs read-only against the local on-demand router.
// Optional: --baseline <verified backup root> --report <new JSON path on a data drive>.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { routeTask, hasTerm } from './route-core.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const catalogPath = path.join(root, 'catalog.json');
const profilePath = path.join(root, 'routing-profile.json');
const catalog = readJson(catalogPath), profile = readJson(profilePath);
const option = (name) => { const index = process.argv.indexOf(name); return index < 0 ? null : process.argv[index + 1]; };
const original = '我们这个codex目前的skill是不是还是有可以提高的，比如说，做一个app，应该是先以产品经理的角度思考问题，设计产品，第二部是设计ui，关于ui设计有很多方向，比如说美观，比如说交互。之后才是第三步前后端第四步测试。我现在有两个问题需要你帮我决策决策，第一是找出其中的低质量skill，减少上下文消耗，以及让模型更好的工作。第二是在完善我的skill，找一些真正能帮助我，提高我vibe coding产品审美啊，体验啊，这方面的，找开源skill也可以，如果你有特别好的建议，也可以告诉我，我会采纳，你看看这个应该怎么搞';
const current = '常驻skill现在不合理，感觉可以更少，或者换一些真正有用的。先进行你得第一步吧，路由你觉得怎么不好，应该怎么修复';
const cases = [
  { id: 'original-skill-audit', prompt: original, owners: ['workspace-surface-audit'] },
  { id: 'current-followup', prompt: current, owners: ['workspace-surface-audit'] },
  { id: 'skill-meta-not-ui-work', prompt: '检查 skill 配置并推荐适合做 App 和 UI 的 skill', owners: ['workspace-surface-audit'] },
  { id: 'new-app-ui', prompt: '做一个中文记账 App，先设计产品和 UI', owners: ['frontend-design'] },
  { id: 'new-web-ui', prompt: '为新网站设计一个登录页面', owners: ['frontend-design'] },
  { id: 'existing-ui-polish', prompt: '优化现有后台 UI 的排版和对比度', owners: ['impeccable'] },
  { id: 'interaction-not-social', prompt: '帮我设计 App 的互动反馈', owners: ['impeccable'] },
  { id: 'interaction-only', prompt: '只做交互设计', owners: ['impeccable'] },
  { id: 'tiny-copy-edit', prompt: '修改按钮文案为保存', none: true },
  { id: 'password-not-word', prompt: '检查 password validation', none: true },
  { id: 'email-not-ai', prompt: '检查 email 字段', none: true },
  { id: 'javascript-not-java', prompt: '检查 JavaScript 变量名', none: true },
  { id: 'flash-not-esp32', prompt: '优化 Flash 动画', none: true },
  { id: 'ordinary-reasoning', prompt: '解释这段算法为什么会越界', none: true },
  { id: 'source-code-learning', prompt: '我想学习项目源码，请从业务任务和调用流程讲解这个文件', owners: ['code-explanation'] },
  { id: 'simple-question', prompt: '2+2等于多少', none: true },
  { id: 'compound-api-deploy', prompt: '用 FastAPI 修复接口，然后部署到服务器', owners: ['fastapi-patterns', 'deployment-patterns'] },
  { id: 'negative-deploy', prompt: '不要部署，先修复 FastAPI 接口', owners: ['fastapi-patterns'], absent: ['deployment-patterns'] },
  { id: 'negative-english', prompt: 'Do not use FastAPI; review password validation', none: true },
  { id: 'screenshot-vue', prompt: '请按照截图用 Vue 还原 UI', owners: ['ui-image-parity'], present: ['ui-to-vue'] },
  { id: 'parity-over-redesign', prompt: '按照截图重新设计 UI', owners: ['ui-image-parity'], absent: ['frontend-design'] },
  { id: 'negative-parity', prompt: '不要按照截图，重新设计 UI', owners: ['frontend-design'], absent: ['ui-image-parity'] },
  { id: 'compound-separate-surfaces', prompt: '按照截图还原 Vue 页面，再为另一个项目设计新页面', owners: ['ui-image-parity', 'frontend-design'] },
  { id: 'two-explicit-skills', prompt: '使用 $frontend-design 和 $impeccable', present: ['frontend-design', 'impeccable'], count: 2 },
  { id: 'native-route-left-to-plugin', prompt: '用 Figma 设计新界面', absent: ['frontend-design', 'impeccable'] },
  { id: 'product-contract', prompt: '把已有 PRD 拆解成工程实现约束', owners: ['product-capability'] },
  { id: 'product-discovery-not-contract', prompt: '只讨论产品定位和 MVP，不设计界面', none: true },
  { id: 'wechat-preserved', prompt: '修复微信小程序的 tabbar', owners: ['wechat-miniprogram-engineering'] },
  { id: 'esp32-preserved', prompt: '检查 ESP32-S3 串口连接', owners: ['esp32-device-ops'] },
  { id: 'word-preserved', prompt: '检查 Word 文档排版', owners: ['office-quality-gate'] },
  { id: 'social-preserved', prompt: '规划社媒互动内容日历', owners: ['social'] },
  { id: 'github-preserved', prompt: '检查 GitHub 仓库分支', owners: ['github-ops'] },
  { id: 'edge-access-preserved', prompt: '通过当前浏览器查看 GitHub 仓库', owners: ['github-ops'], access: ['external-browser'] },
  { id: 'handoff-global-no-extra-skill', prompt: '整理项目交接', none: true },
  { id: 'research-preserved', prompt: '做文献综述', owners: ['academic-research-suite'] },
  { id: 'video-preserved', prompt: '帮我剪视频并加字幕', owners: ['video-editor'] },
  { id: 'chinese-business-delivery', prompt: '为中文客户写项目方案和汇报PPT', owners: ['cn-natural-business-writing'], present: ['office-business-design'] },
  { id: 'ai-comic-drama-production', prompt: '为 AI 漫剧做分镜、配音、字幕、剪辑并发布抖音', owners: ['ai-manju', 'speech', 'video-editor', 'social'] },
  { id: 'photoshop-and-davinci', prompt: '用 Photoshop 修 RAW 人像并用达芬奇给短视频调色', owners: ['photoshop-editing', 'video-editor'], present: ['photo-toolkit'] },
  { id: 'unity-local-game-service', prompt: 'Unity 手游做离线本地服务器与私人服架构', owners: ['unity-csharp-scripting', 'backend-patterns'] },
  { id: 'unity-preserved', prompt: '修复 Unity NavMesh 动态障碍', owners: ['unity-navmesh'] },
  { id: 'career-profile-start', prompt: '我没有简历，帮我梳理职业经历，从零写一份', owners: ['career-profile-builder'] },
  { id: 'resume-job-tailor', prompt: '根据这个岗位 JD 定制我的简历', owners: ['resume-tailor'] },
  { id: 'resume-ats-parse', prompt: '检查我的简历能否通过 Workday ATS 解析', owners: ['ats-resume-formatting'] },
  { id: 'literal-shell-text', prompt: '把按钮文字改为 "$(Get-Date)" 和 `whoami`', none: true },
];

const results = [], failures = [];
function check(name, operation) {
  try { operation(); results.push({ name, passed: true }); }
  catch (error) { failures.push({ name, error: error.message }); results.push({ name, passed: false, error: error.message }); }
}
const sorted = (values) => [...values].sort();
const env = { ...process.env };
function run(command, args, input, overrides = {}) {
  const child = spawnSync(command, args, { input, encoding: 'utf8', timeout: 10000, windowsHide: true, env: { ...env, ...overrides } });
  assert.equal(child.error, undefined, child.error?.message);
  assert.equal(child.status, 0, child.stderr);
  return child.stdout.trim();
}
const observations = [];
for (const test of cases) {
  const start = performance.now();
  const result = routeTask(test.prompt, catalog, profile, 20);
  const names = result.candidates.map((c) => c.name);
  const observation = { id: test.id, prompt: test.prompt, routes: result.routes, candidates: names, candidateCount: result.candidateCount,
    milliseconds: Math.round((performance.now() - start) * 100) / 100 };
  observations.push(observation);
  check(test.id, () => {
    if (test.none) assert.equal(result.candidateCount, 0, names.join(','));
    if (test.count != null) assert.equal(result.candidateCount, test.count);
    if (test.owners) assert.deepEqual(sorted(result.workUnits.map((w) => w.owner.name)), sorted(test.owners));
    if (test.access) assert.deepEqual(sorted(result.accessSkills.map((s) => s.name)), sorted(test.access));
    if (test.controls) assert.deepEqual(sorted(result.controlSkills.map((s) => s.name)), sorted(test.controls));
    for (const name of test.present ?? []) assert.ok(names.includes(name), `Missing ${name}`);
    for (const name of test.absent ?? []) assert.ok(!names.includes(name), `Unexpected ${name}`);
    assert.equal(result.advisory, true);
  });
  check(`${test.id}:cli-parity`, () => {
    const cli = JSON.parse(run(process.execPath, [path.join(root, 'scripts', 'route-cli.mjs')],
      JSON.stringify({ prompt: test.prompt, catalogPath, profilePath, limit: 20 })));
    assert.deepEqual(cli, result);
  });
}
for (const id of ['original-skill-audit', 'current-followup', 'password-not-word', 'literal-shell-text', 'compound-api-deploy']) {
  check(`${id}:powershell-entrypoint`, () => {
    const test = cases.find((c) => c.id === id);
    const actual = JSON.parse(run('pwsh', ['-NoProfile', '-File', path.join(root, 'scripts', 'route-task.ps1'),
      '-Prompt', test.prompt, '-Limit', '20', '-AsJson', '-CatalogPath', catalogPath, '-ProfilePath', profilePath]));
    assert.deepEqual(actual, routeTask(test.prompt, catalog, profile, 20));
  });
}
check('term-boundaries', () => {
  for (const [text, term] of [['password', 'word'], ['javascript', 'java'], ['email', 'ai'], ['impeccable-other', 'impeccable']]) assert.equal(hasTerm(text, term), false);
  assert.equal(hasTerm('设计UI', 'ui'), true);
  assert.equal(hasTerm('FastAPI接口', 'fastapi'), true);
});
check('limit-does-not-drop-work-units', () => {
  const result = routeTask('修复 FastAPI 然后部署到服务器', catalog, profile, 1);
  assert.equal(result.workUnits.length, 2);
  assert.equal(result.truncated, true);
});
check('all-profile-references-resolve', () => {
  const known = new Set(catalog.skills.map((s) => s.name));
  for (const route of profile.routes) {
    assert.equal(route.ownerSkills.length, 1);
    for (const name of [...route.ownerSkills, ...route.supportingSkills.map((s) => s.name)]) assert.ok(known.has(name), name);
  }
  for (const skill of catalog.skills) assert.ok(fs.existsSync(skill.skillPath), skill.name);
});

const baselineRoot = option('--baseline');
if (baselineRoot) {
  for (const observation of observations) {
    const raw = run('pwsh', ['-NoProfile', '-File', path.join(baselineRoot, 'skill-library', 'scripts', 'route-task.ps1'),
      '-Prompt', observation.prompt, '-Limit', '5', '-AsJson',
      '-CatalogPath', path.join(baselineRoot, 'skill-library', 'catalog.json'),
      '-ProfilePath', path.join(baselineRoot, 'skill-library', 'routing-profile.json')]);
    const old = JSON.parse(raw);
    observation.before = { routes: old.routes, candidateCount: old.candidateCount, candidates: old.candidates.map((c) => c.name) };
  }
}
const report = { checkedAt: new Date().toISOString(), scope: 'Local on-demand lexical routing and real CLI entries; not a product-design quality evaluation',
  passed: results.length - failures.length, failed: failures.length, promptCount: cases.length, results, observations };
const reportPath = option('--report');
if (reportPath) {
  assert.equal(fs.existsSync(reportPath), false, 'Do not overwrite prior evidence');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
}
console.log(JSON.stringify({ passed: report.passed, failed: report.failed, promptCount: report.promptCount, failures, report: reportPath }, null, 2));
if (failures.length) process.exitCode = 1;
