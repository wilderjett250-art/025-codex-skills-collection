import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { searchSkills } from './search-skills.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const catalogPath = path.join(root, 'catalog.json'), discoveryPath = path.join(root, 'discovery-profile.json');
const catalog = read(catalogPath), discovery = read(discoveryPath);
// Targeted phrasings and known-miss regressions. This is a small local retrieval
// evaluation, not a blind benchmark or measurement of model selection/UX quality.
const cases = [
  ['给创业想法确定目标用户和首版范围', 'product-discovery'],
  ['用户访谈应该询问哪些过去的行为', 'product-discovery'],
  ['数据库和服务之间的技术选型与 ADR', 'architecture-decisions'],
  ['单体还是微服务，比较维护成本', 'architecture-decisions'],
  ['注册表单的错误反馈和返回流程', 'interaction-design'],
  ['让用户流程减少重复操作', 'interaction-design'],
  ['为新网站建立视觉风格和排版', 'frontend-design'],
  ['React 组件的重复渲染问题', 'react-engineering'],
  ['Next.js 请求瀑布导致页面变慢', 'react-engineering'],
  ['Node Express 服务端错误处理', 'backend-patterns'],
  ['Playwright 购物流程自动化验收', 'e2e-testing'],
  ['先写失败测试再实现的 TDD', 'tdd-workflow'],
  ['定位间歇性故障根因并复现', 'systematic-debugging'],
  ['我有 Java 基础，想从项目业务和调用链学会读懂陌生源码', 'code-explanation'],
  ['请在 VS Code 里逐步讲解这个类负责什么、谁调用它、为什么这样写', 'code-explanation'],
  ['我想做一个App，先帮我确定给谁用和第一版做什么', 'product-discovery'],
  ['Vue页面里数据改了但是视图不更新', 'vue-engineering'],
  ['Pinia 解构出来的变量丢失响应式', 'vue-engineering'],
  ['Vue Router 改参数不重新加载数据', 'vue-engineering'],
  ['用 Vitest 验证 Vue 组件异步行为', 'vue-engineering'],
  ['Next.js Server Components 的缓存如何失效', 'nextjs-engineering'],
  ['shadcn 的 Radix 和 Base UI 弹窗如何组合', 'shadcn-ui'],
  ['Postgres 查询很慢，需要检查索引和 EXPLAIN', 'postgres-patterns'],
  ['制定上线前的测试计划和风险覆盖范围', 'qa-methodology'],
  ['为中文客户写项目方案和汇报PPT', 'cn-natural-business-writing'],
  ['为AI漫剧做分镜配音字幕剪辑并发布抖音', 'ai-manju'],
  ['给达芬奇视频做调色并导出竖屏', 'davinci-resolve-color'],
  ['用本机DaVinci Resolve建立LUT', 'davinci-resolve-color'],
  ['把口播视频加 B-roll 动效和高亮字幕', 'video-editor'],
  ['用Photoshop修RAW人像并在达芬奇调色', 'photoshop-editing'],
  ['Unity手游做离线本地服务器架构', 'unity-csharp-scripting'],
  ['我没有简历，帮我梳理职业经历，从零写一份', 'career-profile-builder'],
  ['根据这个岗位 JD 定制我的简历', 'resume-tailor'],
  ['检查我的简历能否通过 Workday ATS 解析', 'ats-resume-formatting'],
];
const checks = [];
const check = (name, passed, detail) => checks.push({ name, passed: !!passed, detail });
for (const [query, expected] of cases) {
  const result = searchSkills(query, catalog, discovery);
  check(query, result.candidates.some((s) => s.name === expected), { expected, actual: result.candidates.map((s) => s.name) });
  check(`bounded:${query}`, result.candidates.length <= 3 && result.candidates.every((s) => fs.existsSync(s.path)));
}
for (const query of ['给达芬奇视频做调色并导出竖屏', '用本机DaVinci Resolve建立LUT']) {
  const result = searchSkills(query, catalog, discovery);
  check(`explicit DaVinci owner:${query}`, result.candidates[0]?.name === 'davinci-resolve-color', result.candidates);
}
for (const [query, expected] of [['taste-skill', 'frontend-design'], ['$tdd-workflow', 'tdd-workflow'], ['open-design', 'open-design']]) {
  const result = searchSkills(query, catalog, discovery);
  check(`exact:${query}`, result.candidates.length === 1 && result.candidates[0].name === expected);
}
check('unrelated has no candidate', searchSkills('石头重量谜语', catalog, discovery).candidates.length === 0);
check('generic exclusions', !searchSkills('design coding standards', catalog, discovery).candidates.some((s) => discovery.excludeDefault.includes(s.name)));
const vueSpecific = searchSkills('Vue 3 组合式API组件最佳实践', catalog, discovery);
check('negative boundary terms do not outrank Vue owner', vueSpecific.candidates[0]?.name === 'vue-engineering'
  && !vueSpecific.candidates.find((s) => s.name === 'react-engineering')?.matched.includes('vue'), vueSpecific.candidates);
const filtered = searchSkills('React', catalog, discovery, { discipline: 'code-engineering' });
check('discipline filter', filtered.candidates.every((s) => catalog.skills.find((x) => x.name === s.name).discipline === 'code-engineering'));
for (const query of ['用户访谈 MVP', 'taste-skill', 'literal $(echo unsafe) `text` "quotes"']) {
  const request = { query, catalogPath, discoveryPath };
  const child = spawnSync(process.execPath, [path.join(root, 'scripts/search-skills.mjs')], { input: JSON.stringify(request), encoding: 'utf8' });
  let result; try { result = JSON.parse(child.stdout); } catch {}
  check(`CLI:${query}`, child.status === 0 && result?.query === query && JSON.stringify(result) === JSON.stringify(searchSkills(query, catalog, discovery)));
}
if (process.platform === 'win32') {
  for (const shell of ['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe', 'pwsh']) {
    for (const query of ['目标用户 首版范围', 'taste-skill', 'literal $(echo unsafe) `text` "quotes"']) {
      const command = `$ProgressPreference='SilentlyContinue'; [Console]::OutputEncoding = New-Object Text.UTF8Encoding($false); & '${path.join(root, 'scripts/find-skills.ps1').replaceAll("'", "''")}' -Query '${query.replaceAll("'", "''")}' -AsJson`;
      const child = spawnSync(shell, ['-NoProfile', '-EncodedCommand', Buffer.from(command, 'utf16le').toString('base64')],
        { encoding: 'utf8', timeout: 20000, windowsHide: true });
      let result; try { result = JSON.parse(child.stdout); } catch {}
      check(`${shell}:${query}`, child.status === 0 && result?.query === query
        && JSON.stringify(result.candidates.map((s) => s.name)) === JSON.stringify(searchSkills(query, catalog, discovery).candidates.map((s) => s.name)));
    }
  }
}
const report = { passed: checks.filter((s) => s.passed).length, failed: checks.filter((s) => !s.passed).length,
  retrievalCases: cases.length, hitAt3: checks.slice(0, cases.length * 2).filter((s, i) => i % 2 === 0 && s.passed).length / cases.length,
  checks };
const index = process.argv.indexOf('--report');
if (index >= 0) fs.writeFileSync(process.argv[index + 1], JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
process.exitCode = report.failed ? 1 : 0;
