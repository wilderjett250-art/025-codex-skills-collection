// Deterministic local checks only: no provider SDK, model call, network or GUI operation.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {searchSkills} from './search-skills.mjs';

const library=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const home=path.dirname(library);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const catalog=read(path.join(library,'catalog.json'));
const discovery=read(path.join(library,'discovery-profile.json'));
const candidates=(query,options)=>searchSkills(query,catalog,discovery,options).candidates;
const names=(query,options)=>candidates(query,options).map(x=>x.name);
const text=name=>fs.readFileSync(catalog.skills.find(x=>x.name===name).skillPath,'utf8');

test('disk inventory and canonical identities are complete and unique',()=>{
  const disk=[];
  for(const root of [path.join(home,'skills'),path.join(library,'leaves')]){
    for(const d of fs.readdirSync(root,{withFileTypes:true})){
      // Windows junctions are valid existing skill folders; match the builder's traversal.
      const directory=path.join(root,d.name);
      if(d.name==='.system'||!fs.existsSync(directory)||!fs.statSync(directory).isDirectory())continue;
      const p=path.join(root,d.name,'SKILL.md');if(fs.existsSync(p))disk.push(path.resolve(p));
    }
  }
  assert.deepEqual(new Set(catalog.skills.map(s=>path.resolve(s.skillPath))),new Set(disk));
  assert.equal(new Set(catalog.skills.map(s=>s.name)).size,catalog.skills.length);
  assert.equal(new Set(catalog.skills.map(s=>s.canonicalPath)).size,catalog.skills.length);
  assert.equal(catalog.skills.filter(s=>s.source==='active').length,10);
  assert.equal(catalog.skills.filter(s=>s.source==='library').length,292);
  for(const s of catalog.skills)assert.equal(typeof s.allowImplicitInvocation,'boolean');
});

test('mind-atlas is reachable by exact name and its real Chinese task',()=>{
  assert.deepEqual(names('mind-atlas'),['mind-atlas']);
  assert.equal(names('整理这个项目全貌，做个可以交互的思维导图')[0],'mind-atlas');
  assert.equal(names('把模块关系做成脑图')[0],'mind-atlas');
});

test('legacy invocation restrictions survive catalog generation and retrieval',()=>{
  for(const n of ['artifact-tool-excel-legacy','python-spreadsheet-fallback','python-docx-local','pptxgenjs-slides']){
    assert.equal(catalog.skills.find(s=>s.name===n).allowImplicitInvocation,false);
    assert.deepEqual(names(n),[n]);
  }
  assert.ok(!names('创建一个带公式的Excel销售报表').includes('artifact-tool-excel-legacy'));
  assert.ok(!names('编辑 XLSX 单元格').includes('python-spreadsheet-fallback'));
  assert.ok(names('用 openpyxl 编辑 XLSX 单元格').includes('python-spreadsheet-fallback'));
  assert.ok(names('XLSX editing',{primaryRuntimeUnavailable:true}).includes('python-spreadsheet-fallback'));
  assert.ok(!names('不要使用 openpyxl，优先官方表格').includes('python-spreadsheet-fallback'));
  assert.ok(names('用本机DaVinci Resolve建立LUT').includes('davinci-resolve-color'));
  assert.ok(names('Photoshop RAW 人像精修').includes('photoshop-editing'));
});

test('near-miss words do not masquerade as a platform match',()=>{
  assert.ok(!names('请逐行讲解这份源码帮助我学习').some(n=>['超能力','douyin-upload'].includes(n)));
  assert.ok(!names('用户访谈应该询问哪些过去的行为').includes('超能力'));
  assert.ok(!names('搜索我已有的知识库，找一下部署记录').includes('external-browser'));
  assert.ok(names('搜索我已有的知识库，找一下部署记录').includes('knowledge-ops'));
  assert.ok(!names('不抢鼠标，把本机百度网盘里的ZIP上传').includes('douyin-upload'));
  assert.ok(!names('修正配置文件里的一个拼写错误').some(n=>['api-design','cisco-ios-patterns','workspace-surface-audit'].includes(n)));
  assert.ok(names('用抖音上传工具发布短视频').includes('douyin-upload'));
  assert.ok(names('操作我已打开的Edge网页，读取表格').includes('external-browser'));
});

test('Office compatibility entries keep primary and explicit local lanes separate',()=>{
  for(const [old,local,primary] of [['doc','python-docx-local','documents:documents'],['spreadsheet','python-spreadsheet-fallback','spreadsheets:Spreadsheets'],['slides','pptxgenjs-slides','presentations:Presentations']]){
    assert.ok(text(old).includes(primary));assert.ok(text(old).includes(`../${local}/SKILL.md`));
    assert.deepEqual(names(old),[old]);
  }
  assert.ok(!names('帮我做一份可以编辑的PowerPoint汇报PPT').includes('dashiai-ppt'));
  assert.ok(names('DashiAI 浏览器编辑 HTML演示').includes('dashiai-ppt'));
});

test('knowledge capture and current runtime boundaries remain explicit',()=>{
  assert.match(text('knowledge-ops'),/Search requests are read-only/);
  assert.doesNotMatch(text('knowledge-ops'),/Always update Claude Code memory/);
  assert.doesNotMatch(text('playwright-interactive'),/js_repl = true|--sandbox danger-full-access|npm init -y/);
  assert.match(text('playwright-interactive'),/Do not disable the sandbox/);
  assert.doesNotMatch(text('超能力'),/每个项目都经过这个流程|每个任务分派新鲜子代理/);
  assert.doesNotMatch(text('gh-fix-ci'),/implement only after explicit approval|suggest re-running/);
  assert.match(text('semgrep'),/--metrics=off/);
  assert.doesNotMatch(text('semgrep'),/original .* request is NOT approval|HARD GATE|250%/i);
  assert.doesNotMatch(text('dimensional-analysis'),/Any mode argument provided by the caller is ignored/);
});

test('one optional model reference leaves the common library shared',()=>{
  const p=path.join(home,'skills/skill-library-router/references/openai-model-notes.md');
  const note=fs.readFileSync(p,'utf8');
  for(const n of ['Astra','Sol','Terra','Luna'])assert.ok(note.includes(n));
  assert.match(note,/official-guidance-based/);assert.match(note,/not four benchmark-certified/);
  assert.match(note,/developers.openai.com/);
  assert.ok(!catalog.skills.some(s=>/model-profile|astra-only|luna-only/.test(s.name)));
});

test('real Node and PowerShell entrypoints preserve explicit fallback conditions',()=>{
  const query='XLSX editing';
  const expected=names(query,{primaryRuntimeUnavailable:true});
  const child=spawnSync(process.execPath,[path.join(library,'scripts/find-skills.mjs'),'--catalog',path.join(library,'catalog.json'),
    '--discovery',path.join(library,'discovery-profile.json'),'--query',query,'--primary-runtime-unavailable'],
    {encoding:'utf8',windowsHide:true,timeout:10000});
  assert.equal(child.status,0,child.stderr);
  assert.deepEqual(JSON.parse(child.stdout).candidates.map(s=>s.name),expected);
  if(process.platform==='win32'){
    for(const shell of ['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','pwsh']){
      const ps=spawnSync(shell,['-NoProfile','-File',path.join(library,'scripts/find-skills.ps1'),
        '-CatalogPath',path.join(library,'catalog.json'),'-DiscoveryPath',path.join(library,'discovery-profile.json'),
        '-Query',query,'-PrimaryRuntimeUnavailable','-AsJson'],{encoding:'utf8',windowsHide:true,timeout:20000});
      assert.equal(ps.status,0,ps.stderr);
      assert.deepEqual(JSON.parse(ps.stdout).candidates.map(s=>s.name),expected);
    }
  }
});
