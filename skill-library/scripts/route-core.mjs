// Shared by the submit hook and the PowerShell entrypoint. No Skill bodies or tools run here.
const list = (value) => value == null ? [] : Array.isArray(value) ? value : [value];
const escapeRegex = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const normalize = (value) => String(value ?? '').toLowerCase().trim();

export function hasTerm(text, term) {
  const value = normalize(term);
  if (!value) return false;
  // ASCII boundaries keep word out of password, java out of javascript, and ai out of email.
  // Chinese adjacency is intentional: "设计UI" and "FastAPI接口" remain searchable.
  const left = /^[a-z0-9_]/.test(value) ? '(?<![a-z0-9_+-])' : '';
  const right = /[a-z0-9_+#-]$/.test(value) ? '(?![a-z0-9_+#-])' : '';
  const pattern = new RegExp(left + escapeRegex(value) + right, 'g');
  const source = normalize(text);
  for (const match of source.matchAll(pattern)) {
    const prefix = source.slice(Math.max(0, match.index - 30), match.index);
    if (!/不$|(?:不要|不需要|无需|不用|暂不|别)[^，,。;；]{0,8}$|(?:do not|don't|without)\s+(?:use\s+|using\s+)?$/i.test(prefix)) return true;
  }
  return false;
}

function clausesFor(prompt) {
  // A conservative lexical aid, not a semantic parser. Existing conversation still governs scope.
  return normalize(prompt).split(/[。！？!?;；\n]+|\.(?=\s|$)/).flatMap((sentence) => {
    const example = sentence.search(/比如|例如|举例|假设|for example/);
    const requested = example < 0 ? sentence : sentence.slice(0, example);
    return requested.split(/[，,]+/).map((part) => part.trim()).filter(Boolean);
  });
}

function matchesDefinition(text, definition) {
  const aliasHit = list(definition.aliases).some((alias) => hasTerm(text, alias));
  const groups = list(definition.aliasGroups);
  const groupedHit = groups.length > 0 && groups.every((group) => list(group).some((alias) => hasTerm(text, alias)));
  return (aliasHit || groupedHit) && !list(definition.excludeAliases).some((alias) => hasTerm(text, alias));
}

const reference = (skill) => Object.fromEntries(
  ['name', 'plane', 'domain', 'discipline', 'family', 'canonicalPath', 'source', 'skillPath'].map((key) => [key, String(skill[key] ?? '')]),
);

export function routeTask(prompt, catalog, profile, limit = 5) {
  if (!Number.isInteger(limit) || limit < 1 || limit > 20) throw new Error('Limit must be an integer from 1 to 20');
  const clauses = clausesFor(prompt);
  const text = clauses.join('，');
  const namesFor = (definitions) => list(definitions).filter((d) => clauses.some((c) => matchesDefinition(c, d))).map((d) => d.name);
  const phases = namesFor(profile.phases);
  const skillMap = new Map();
  for (const skill of list(catalog.skills)) {
    if (skillMap.has(skill.name)) throw new Error(`Duplicate Skill name: ${skill.name}`);
    skillMap.set(skill.name, skill);
  }
  const getSkill = (name) => {
    const skill = skillMap.get(name);
    if (!skill) throw new Error(`Unknown routed Skill: ${name}`);
    return reference(skill);
  };
  const applies = (support) => (!list(support.whenPhases).length || list(support.whenPhases).some((p) => phases.includes(p)))
    && (!list(support.whenAliases).length || list(support.whenAliases).some((a) => hasTerm(text, a)));

  // Suppression is per clause: a screenshot task must not suppress a separate new-page request.
  const chosen = new Map();
  for (const clause of clauses) {
    const matched = list(profile.routes).filter((r) => matchesDefinition(clause, r)
      && !list(r.excludePromptAliases).some((a) => hasTerm(text, a)));
    const matchedNames = new Set(matched.map((r) => r.name));
    for (const route of matched) {
      if (!list(route.suppressedByRoutes).some((name) => matchedNames.has(name))) chosen.set(route.name, route);
    }
  }
  const routes = [...chosen.values()].sort((a, b) => (a.sequence ?? 50) - (b.sequence ?? 50) || a.name.localeCompare(b.name));
  const workUnits = [], accessSkills = [], controlSkills = [];
  const candidates = new Map();
  const order = { owner: 0, access: 1, control: 2, support: 3, candidate: 4 };
  const add = (skill, role, matched) => {
    const previous = candidates.get(skill.name);
    if (!previous || order[role] < order[previous.role]) {
      candidates.set(skill.name, { ...skill, role, matched, score: 100 - 10 * order[role] });
    }
  };
  for (const route of routes) {
    if (list(route.ownerSkills).length !== 1) throw new Error(`Route must have one owner: ${route.name}`);
    const owner = getSkill(route.ownerSkills[0]);
    const supports = list(route.supportingSkills).filter(applies).map((s) => getSkill(s.name));
    const kind = route.kind || 'capability';
    if (kind === 'capability') {
      workUnits.push({ route: route.name, plane: owner.plane, domain: owner.domain, discipline: owner.discipline,
        family: owner.family, owner, supportingSkills: supports });
      add(owner, 'owner', `route:${route.name}`);
    } else if (kind === 'access') {
      accessSkills.push(owner);
      add(owner, 'access', `route:${route.name}`);
    } else if (kind === 'control') {
      controlSkills.push(owner);
      add(owner, 'control', `route:${route.name}`);
    } else throw new Error(`Unknown route kind: ${kind}`);
    for (const support of supports) {
      if (support.plane === 'control') controlSkills.push(support);
      add(support, support.plane === 'control' ? 'control' : 'support', `support:${route.name}`);
    }
  }

  for (const skill of skillMap.values()) {
    const explicit = hasTerm(text, `$${skill.name}`);
    if (explicit) add(reference(skill), 'candidate', 'explicit-name');
    // Do not fill a valid route with loosely related extras. Names like "design" are ordinary words.
    if (routes.length) continue;
    const qualifiedName = skill.name.includes('-') && hasTerm(text, skill.name);
    const namedInvocation = clauses.some((c) => hasTerm(c, skill.name)
      && /(?:使用|调用|用\s|\buse\b|\bskill\b)/i.test(c));
    const alias = list(skill.aliases).find((a) => hasTerm(text, a));
    if (qualifiedName || namedInvocation || alias) add(reference(skill), 'candidate', alias ? `alias:${alias}` : 'name');
  }
  const all = [...candidates.values()].sort((a, b) => order[a.role] - order[b.role] || a.name.localeCompare(b.name));
  const unique = (items) => [...new Map(items.map((item) => [item.name, item])).values()];
  return {
    schemaVersion: 2, advisory: true, status: all.length ? (routes.length ? 'matched' : 'candidates-only') : 'no-match',
    projectTypes: namesFor(profile.projectTypes), phases, domains: namesFor(profile.domains),
    disciplines: namesFor(profile.disciplines), families: namesFor(profile.families),
    routes: routes.map((r) => r.name), workUnits, accessSkills: unique(accessSkills), controlSkills: unique(controlSkills),
    candidateCount: all.length, candidates: all.slice(0, limit).map((c, index) => ({ ...c, rank: index + 1 })),
    truncated: all.length > limit,
  };
}
