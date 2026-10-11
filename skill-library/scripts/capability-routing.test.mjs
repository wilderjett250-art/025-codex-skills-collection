import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { searchSkills } from './search-skills.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const catalog = read(path.join(root, 'catalog.json'));
const discovery = read(path.join(root, 'discovery-profile.json'));
// Targeted regression fixtures, not a blind benchmark or proof of model invocation.
const cases = [
  ['超级大项目如何分阶段推进并安排多人协作', 'large-project-ops'],
  ['几十个模块跨端协作，需要依赖顺序和可以交给agent的任务包', 'large-project-ops'],
  ['大型遗留系统改造，如何拆分里程碑并保证集成验收', 'large-project-ops'],
  ['从产品经理角度评估这个产品是否合理和值得做', 'product-discovery'],
  ['已有产品功能很多但用户价值不明确，评估差异化和投入产出', 'product-discovery'],
  ['产品设计是否解决真实需求，商业可行性与核心流程是什么', 'product-discovery'],
  ['现有后台看起来土，希望整体更高级而不是增加装饰', 'impeccable'],
  ['对现有页面做视觉审查，检查信息层级、字号和留白', 'impeccable'],
  ['设计一个新网站的视觉方向和审美风格', 'frontend-design'],
  ['检查产品架构是否完善，技术方案是否过度设计', 'architecture-decisions'],
  ['评估模块边界和依赖耦合，是否方便长期维护', 'architecture-decisions'],
  ['技术选型评审，要比较可用性、迁移成本和回滚条件', 'architecture-decisions'],
  ['检查前后端代码是否高效，定位接口慢和首屏慢的原因', 'benchmark-optimization-loop'],
  ['应用性能诊断：响应时间p95很差，CPU占用高，先找瓶颈', 'benchmark-optimization-loop'],
  ['跨前端后端的性能评估，吞吐量与用户等待时间如何测量', 'benchmark-optimization-loop'],
  ['审查这批代码是否混乱，职责耦合和重复实现太多', 'code-quality-review'],
  ['代码审查这个PR，检查需求一致性和可维护性', 'code-quality-review'],
  ['模块里有重复代码与过度抽象，给有证据的重构建议', 'code-quality-review'],
  ['产品测试能否证明符合需求和上线标准', 'qa-methodology'],
  ['检查需求到验收证据的对应关系，哪些行为还没验证', 'qa-methodology'],
  ['发布前质量门禁，测试策略要覆盖权限、失败恢复和数据完整性', 'qa-methodology'],
];
const boundaries = [
  ['游戏低FPS和GPU draw-call瓶颈', 'performance-optimization'],
  ['Vue 3 组合式API的响应式组件最佳实践', 'vue-engineering'],
  ['React 组件重复渲染和Next.js请求瀑布', 'react-engineering'],
  ['请逐行讲解这份源码帮助我学习', 'code-explanation'],
  ['根据岗位JD优化简历', 'resume-tailor'],
  ['Photoshop RAW 人像精修', 'photoshop-editing'],
];
const results = cases.map(([query, expected]) => {
  const candidates = searchSkills(query, catalog, discovery).candidates;
  return { query, expected, hitAt3: candidates.some(s => s.name === expected),
    boundedAndResolvable: candidates.length <= 3 && candidates.every(s => fs.existsSync(s.path)),
    actual: candidates.map(s => s.name) };
});
const boundaryResults = boundaries.map(([query, expected]) => {
  const candidates = searchSkills(query, catalog, discovery).candidates;
  return { query, expected, passed: candidates[0]?.name === expected, actual: candidates.map(s => s.name) };
});
const cli = ['产品经理 用户价值', '代码审查 可维护性', 'literal $(echo unsafe) `text` "quotes"'].map(query => {
  const child = spawnSync(process.execPath, [path.join(root, 'scripts/find-skills.mjs'),
    '--query', query, '--catalog', path.join(root, 'catalog.json'),
    '--discovery', path.join(root, 'discovery-profile.json')], { encoding: 'utf8', windowsHide: true, timeout: 10000 });
  let result; try { result = JSON.parse(child.stdout); } catch {}
  const expected = searchSkills(query, catalog, discovery).candidates.map(s => s.name);
  return { query, passed: child.status === 0 && result?.query === query
    && JSON.stringify(result.candidates.map(s => s.name)) === JSON.stringify(expected) };
});
const catalogueChecks = [
  { name: 'one canonical owner per name', passed: new Set(catalog.skills.map(s => s.name)).size === catalog.skills.length },
  { name: 'existing Impeccable canonical path preserved', passed: catalog.skills.find(s => s.name === 'impeccable')?.canonicalPath
    === 'domain/computing-digital/frontend-ui/visual-design/impeccable' },
];
const report = {
  fixtureType: 'targeted retrieval regression; not automatic-selection or product-quality evaluation',
  catalogSkillCount: catalog.skills.length,
  retrievalCases: results.length,
  hitAt3: results.filter(r => r.hitAt3).length / results.length,
  failed: results.filter(r => !r.hitAt3 || !r.boundedAndResolvable).length + boundaryResults.filter(r => !r.passed).length
    + cli.filter(r => !r.passed).length + catalogueChecks.filter(r => !r.passed).length,
  results, boundaries: boundaryResults, cli, catalogueChecks,
};
const outputIndex = process.argv.indexOf('--report');
if (outputIndex >= 0) fs.writeFileSync(process.argv[outputIndex + 1], JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
if (!process.argv.includes('--baseline')) process.exitCode = report.failed ? 1 : 0;
