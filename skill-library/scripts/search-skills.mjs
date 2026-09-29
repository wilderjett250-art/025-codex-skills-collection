// On-demand metadata search. Never reads Skill bodies, calls a model, or writes task history.
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';

const segmenter = new Intl.Segmenter('zh', { granularity: 'word' });
const stop = new Set(['the','and','for','with','this','that','from','skill','skills','帮我','一下','一个','我们','这个','如何','怎么','需要','可以','进行','是否','什么','的','了']);
const normalize = (s) => String(s ?? '').normalize('NFKC').toLowerCase();
function positiveDescription(text) {
  return String(text ?? '').split(/(?<=[.!?。！？;；])\s*/)
    .filter((part) => !/^\s*(?:not\b|do not\b|don't\b|does not\b|not for\b|不用于|不要用于|并非用于)/i.test(part))
    .join(' ');
}
function tokens(text) {
  const normalized = normalize(text);
  const segmented = [...segmenter.segment(normalized)].filter((s) => s.isWordLike)
    .map((s) => s.segment).filter((s) => s.length > 1 && !stop.has(s));
  // Segmenter does not consistently preserve specialist Chinese compounds such as
  // "漫剧" or "达芬奇". Add adjacent CJK pairs as retrieval terms without loading
  // any Skill bodies. This improves multilingual lookup while keeping normal
  // token matching and the bounded top-k result unchanged.
  const cjkBigrams = [];
  for (const run of normalized.match(/[\u3400-\u9fff]{2,}/gu) ?? []) {
    for (let index = 0; index < run.length - 1; index += 1) {
      const term = run.slice(index, index + 2);
      if (!stop.has(term)) cjkBigrams.push(term);
    }
  }
  return [...new Set([...segmented, ...cjkBigrams])];
}
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));

export function searchSkills(query, catalog, discovery = {}, options = {}) {
  const limit = options.limit ?? 3;
  if (!Number.isInteger(limit) || limit < 1 || limit > 20) throw new Error('Limit must be 1..20');
  const requested = normalize(query).trim().replace(/^\$/, '');
  const exactName = discovery.redirects?.[requested] ?? requested;
  const queryTokens = [...new Set(tokens(query))];
  const excluded = new Set(discovery.excludeDefault ?? []);
  const docs = catalog.skills.filter((s) => (!options.plane || s.plane === options.plane)
    && (!options.domain || s.domain === options.domain)
    && (!options.discipline || s.discipline === options.discipline)
    && (!options.family || s.family === options.family)
    && (!excluded.has(s.name) || s.name === exactName)).map((skill) => {
      const terms = discovery.entries?.[skill.name]?.terms ?? [];
      const weighted = [...tokens(skill.name), ...tokens(skill.name), ...tokens(positiveDescription(skill.trigger)),
        ...tokens(terms.join(' ')), ...tokens(terms.join(' ')), ...tokens((skill.aliases ?? []).join(' '))];
      const frequencies = new Map();
      for (const term of weighted) frequencies.set(term, (frequencies.get(term) ?? 0) + 1);
      return { skill, frequencies, length: weighted.length };
    });
  const averageLength = docs.reduce((total, d) => total + d.length, 0) / (docs.length || 1) || 1;
  const frequency = new Map(queryTokens.map((term) => [term, docs.filter((d) => d.frequencies.has(term)).length]));
  let ranked = docs.map(({ skill, frequencies, length }) => {
    const matched = queryTokens.filter((term) => frequencies.has(term));
    let score = 0;
    for (const term of matched) {
      const tf = frequencies.get(term), df = frequency.get(term);
      const idf = Math.log(1 + (docs.length - df + 0.5) / (df + 0.5));
      score += idf * (tf * 2.2) / (tf + 1.2 * (0.25 + 0.75 * length / averageLength));
    }
    const exact = normalize(skill.name) === exactName;
    if (exact) score += 100;
    return { name: skill.name, description: skill.trigger, path: skill.skillPath,
      canonicalPath: skill.canonicalPath, source: skill.source,
      score: Math.round(score * 100) / 100, matched, exact };
  }).filter((s) => s.score > 0).sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));
  // An exact name is a lookup, not a request for other vaguely similar workflows.
  if (ranked.some((s) => s.exact)) ranked = ranked.filter((s) => s.exact);
  return { schemaVersion: 1, advisory: true, query, status: ranked.length ? 'candidates-only' : 'no-match',
    candidateCount: ranked.length, candidates: ranked.slice(0, limit),
    next: ranked.length ? 'Compare descriptions with the actual task and platform before loading one current-stage owner.'
      : 'Rephrase once with task + object + platform when a specialist is needed; otherwise continue with available capabilities.' };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const request = JSON.parse(fs.readFileSync(0, 'utf8').replace(/^\uFEFF/, ''));
    const catalog = readJson(request.catalogPath), discovery = readJson(request.discoveryPath);
    process.stdout.write(JSON.stringify(searchSkills(request.query, catalog, discovery, request.options))
      .replace(/[^\x00-\x7f]/g, (character) => `\\u${character.charCodeAt(0).toString(16).padStart(4, '0')}`));
  } catch (error) { process.stderr.write(`Skill search failed: ${error.message}\n`); process.exitCode = 1; }
}
