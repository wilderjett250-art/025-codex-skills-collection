#!/usr/bin/env python3
"""Export portable Skills and a credential-free Codex configuration snapshot.

Run against a reviewed, clean checkout. This does not export account sessions,
knowledge stores, plugin caches, application binaries, or virtual environments.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib
from urllib.parse import urlsplit, parse_qs

parser = argparse.ArgumentParser()
parser.add_argument('--home', type=Path, required=True)
parser.add_argument('--canonical-root', type=Path)
parser.add_argument('--date', required=True)
args = parser.parse_args()
repo = Path(__file__).resolve().parent.parent
home = args.home.resolve()
config = tomllib.loads((home / 'config.toml').read_text(encoding='utf-8-sig'))
catalog = json.loads((home / 'skill-library/catalog.json').read_text(encoding='utf-8-sig'))
excluded_dirs = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.cache', 'dist', 'build'}
excluded_suffixes = {'.pyc', '.db', '.sqlite', '.sqlite3', '.log'}
changed = []
adapted = []
# These already-portable variants retain the same workflow without installation
# paths and historical machine acceptance claims. The current state is inventoried
# separately; it is never converted into another machine's acceptance evidence.
portable_variants = {'photoshop-editing', 'davinci-resolve-color', 'autocad-cad-homework'}

def text_bytes(data):
    try:
        return data.decode('utf-8-sig').replace('\r\n', '\n').encode('utf-8')
    except UnicodeError:
        return data

def save(destination, data):
    data = text_bytes(data)
    if destination.exists() and text_bytes(destination.read_bytes()) == data:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    changed.append(destination.relative_to(repo).as_posix())

def files(root):
    for directory, subdirs, names in os.walk(root):
        subdirs[:] = [name for name in subdirs if name not in excluded_dirs]
        for name in names:
            p = Path(directory) / name
            if p.suffix.lower() in excluded_suffixes or name.startswith('.env') or name == '.DS_Store':
                continue
            yield p

for skill in catalog['skills']:
    source = Path(skill['skillPath']).parent
    relative = skill.get('relativePath') or skill['directory']
    target = repo / ('skills' if skill['source'] == 'active' else 'skill-library/leaves') / relative
    for p in files(source):
        rel = p.relative_to(source)
        if skill['name'] in portable_variants and (rel.as_posix() == 'SKILL.md' or rel.as_posix() == 'scripts/check_environment.py'):
            adapted.append((target / rel).relative_to(repo).as_posix())
            continue
        data = p.read_bytes()
        if p.suffix.lower() in {'.md', '.txt', '.yaml', '.yml', '.json'}:
            text = data.decode('utf-8-sig')
            # Bundle canonical instructions referenced by machine-local bridge Skills.
            references = sorted(set(re.findall(r'E:\\codex-home\\skills\\([a-z0-9-]+)', text)))
            for name in references:
                if not args.canonical_root or not (args.canonical_root / name / 'SKILL.md').is_file():
                    raise RuntimeError(f'Missing canonical Skill dependency: {name}')
                canonical = args.canonical_root / name
                for cp in files(canonical):
                    save(target / 'canonical' / name / cp.relative_to(canonical), cp.read_bytes())
                text = text.replace('E:\\codex-home\\skills\\' + name, 'canonical/' + name).replace('\\SKILL.md', '/SKILL.md')
            data = text.encode('utf-8')
        if skill['name'] == 'local-experience' and rel.as_posix() == 'scripts/search-experience.ps1':
            adapted.append((target / rel).relative_to(repo).as_posix())
            continue
        if skill['name'] == 'skill-library-router' and rel.as_posix() == 'SKILL.md':
            # The repository exposes the same selection policy through a portable
            # Node entrypoint. Preserve that adapter rather than a Windows default.
            adapted.append((target / rel).relative_to(repo).as_posix())
            continue
        save(target / rel, data)

for p in (home / 'skill-library/scripts').iterdir():
    if p.is_file() and p.suffix in {'.mjs', '.ps1'}:
        # Retain the cross-platform activity location; local fixed I: paths are
        # represented by an environment-variable name in the global preset.
        if p.name in {'activity-core.mjs', 'activity.test.mjs', 'route-task.test.mjs'}:
            adapted.append('skill-library/scripts/' + p.name)
            continue
        save(repo / 'skill-library/scripts' / p.name, p.read_bytes())

for name in ['routing-profile.json', 'discovery-profile.json', 'sources-lock.json']:
    p = home / 'skill-library' / name
    if p.exists():
        save(repo / 'skill-library' / name, p.read_bytes())

rules = (home / 'AGENTS.md').read_text(encoding='utf-8-sig')
rules = re.sub(r'C:/Users/[^/]+/\.codex', '<codex-home>', rules)
save(repo / 'presets/global/AGENTS.md', rules.encode('utf-8'))

allowed = {'model', 'model_reasoning_effort', 'model_reasoning_summary', 'model_verbosity',
           'approval_policy', 'sandbox_mode', 'web_search', 'service_tier',
           'model_context_window', 'model_auto_compact_token_limit', 'suppress_unstable_features_warning',
           'personality', 'plan_mode_reasoning_effort', 'check_for_update_on_startup', 'approvals_reviewer'}
defaults = {k: v for k, v in config.items() if k in allowed and isinstance(v, (str, int, bool))}
lines = ['# Credential-free defaults; review before merging into config.toml.']
def literal(value):
    return json.dumps(value, ensure_ascii=False)
for key, value in defaults.items():
    lines.append(f'{key} = {literal(value)}')
for section in ['features', 'analytics', 'windows', 'memories', 'desktop']:
    values = {k: v for k, v in config.get(section, {}).items()
              if isinstance(v, (str, bool, int)) or isinstance(v, list) and all(isinstance(x, str) for x in v)}
    if values:
        lines.extend(['', f'[{section}]'])
        lines.extend(f'{k} = {literal(v)}' for k, v in values.items())
save(repo / 'presets/global/config.defaults.toml', ('\n'.join(lines) + '\n').encode('utf-8'))

state = []
for name, server in config.get('mcp_servers', {}).items():
    if name == 'personal_knowledge':
        continue
    entry = {'name': name, 'enabled': server.get('enabled', True),
             'transport': 'http' if 'url' in server else 'stdio',
             'environmentKeys': sorted(server.get('env', {}).keys())}
    if 'url' in server:
        u = urlsplit(server['url'])
        entry['urlWithoutCredentials'] = f'{u.scheme}://{u.netloc}{u.path}'
        entry['credentialQueryKeys'] = sorted(parse_qs(u.query).keys())
    else:
        entry['commandKind'] = re.split(r'[/\\]', server.get('command', ''))[-1]
        entry['requiresLocalCommandConfiguration'] = True
    state.append(entry)
save(repo / 'mcp/local-state.json', (json.dumps({'snapshotDate': args.date,
     'excluded': ['personal_knowledge'], 'servers': state}, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))

plugins = [{'id': name, 'enabled': entry.get('enabled', True)}
           for name, entry in config.get('plugins', {}).items()]
save(repo / 'presets/plugins.json', (json.dumps(plugins, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
settings_scope = {'snapshotDate': args.date, 'exportedTopLevelSettings': sorted(defaults),
                  'exportedSections': ['features', 'analytics', 'windows', 'memories', 'desktop'],
                  'exportedSeparately': ['plugins', 'MCP states', 'AGENTS.md', 'PostToolUse metadata hook'],
                  'excludedMachineSettings': ['project trust paths', 'notification executable paths',
                    'marketplace filesystem locations', 'shell environment values', 'hook trust hashes'],
                  'shellEnvironmentKeys': sorted(config.get('shell_environment_policy', {}).get('set', {})),
                  'knowledgeDataIncluded': False}
save(repo / 'presets/global/settings-scope.json', (json.dumps(settings_scope, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))

report = {'snapshotDate': args.date, 'skillCount': len(catalog['skills']),
          'mcpCountWithoutKnowledge': len(state), 'pluginPresetCount': len(plugins),
          'globalRulesSourceSha256': hashlib.sha256((home / 'AGENTS.md').read_bytes()).hexdigest(),
          'globalRulesPortableSha256': hashlib.sha256((repo / 'presets/global/AGENTS.md').read_bytes()).hexdigest(),
          'changedFiles': sorted(set(subprocess.check_output(['git', 'ls-files', '--modified', '--others', '--exclude-standard'], cwd=repo, text=True).splitlines())),
          'portableAdaptations': sorted(set(adapted)),
          'excludedContent': ['knowledge data', 'account credentials', 'sessions', 'plugin caches',
                              'application binaries', 'virtual environments', 'local experience manual']}
save(repo / 'presets/sync-manifest.json', (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
print(json.dumps({'skills': len(catalog['skills']), 'mcpStateEntries': len(state),
                  'changedFiles': len(set(changed)), 'portableAdaptations': len(set(adapted))}))
