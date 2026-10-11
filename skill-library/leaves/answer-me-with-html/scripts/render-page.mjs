import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const directory = path.dirname(fileURLToPath(import.meta.url));
const policy = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'";

export function renderPage({ input, output }) {
  if (!input || !output || !path.isAbsolute(input) || !path.isAbsolute(output) || path.extname(output).toLowerCase() !== '.html') {
    throw new Error('Use absolute input and a new absolute .html output path');
  }
  if (fs.existsSync(output)) throw new Error('Output exists; preserve recovery state and choose a new version');
  const stat = fs.statSync(input);
  if (!stat.isFile() || stat.size > 256 * 1024) throw new Error('Draft must be a file no larger than 256 KiB');
  const draft = fs.readFileSync(input, 'utf8');
  if (/^\s*`{3,}\s*(?:html|svg)\b/im.test(draft) || /<\s*\/?(?:script|iframe|object|embed|link|style|img|svg|math|base)\b/i.test(draft)) {
    throw new Error('Executable/raw HTML and SVG are not supported by the safe wrapper');
  }
  if (/!\[[^\]]*\]\s*[([]/.test(draft) || /^\s*`{3,}[^\n]*\b(?:src|file)\s*=/im.test(draft)) {
    throw new Error('Image or source-file embedding needs a separately authorized route');
  }
  const outDir = path.dirname(output);
  fs.mkdirSync(outDir, { recursive: true });
  // Use a private per-render runtime directory: never override an existing user's am config.
  const runtime = fs.mkdtempSync(path.join(outDir, '.am-render-'));
  fs.writeFileSync(path.join(runtime, 'config.json'), `${JSON.stringify({ open: false, update_check: false })}\n`, { flag: 'wx' });
  const temporary = path.join(runtime, `${randomUUID()}.html`);
  const started = performance.now();
  const child = spawnSync(process.execPath, [path.join(directory, 'am.mjs'), 'render', input, '-o', temporary, '--no-open'], {
    cwd: path.dirname(input), env: { ...process.env, AM_HOME: runtime, AM_NO_OPEN: '1', CI: '1' },
    encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 20000, windowsHide: true,
  });
  try {
    if (child.error || child.status !== 0 || !fs.existsSync(temporary)) throw new Error('Renderer failed; review the draft with component-specific help');
    let html = fs.readFileSync(temporary, 'utf8');
    if (!/<head\b[^>]*>/i.test(html)) throw new Error('Renderer did not produce an HTML document');
    html = html.replace(/<head\b[^>]*>/i, match => `${match}\n<meta http-equiv="Content-Security-Policy" content="${policy}">`);
    fs.writeFileSync(temporary, html);
    // Hard-link creation is atomic and fails if another process created the output; never overwrite.
    fs.linkSync(temporary, output);
    return { output, bytes: Buffer.byteLength(html), draftChars: Array.from(draft).length,
      elapsedMs: Math.round(performance.now()-started), warnings: (child.stdout.match(/(?:STE|code) \d+ warnings?/g) || []),
      offlinePolicy: true, browserOpened: false, updateChecksEnabled: false };
  } finally {
    // Only this invocation's confirmed scratch directory is removed, never an existing output/config.
    if (path.dirname(fs.realpathSync(runtime)) !== fs.realpathSync(outDir)) throw new Error('Scratch cleanup scope changed; preserve for inspection');
    fs.rmSync(runtime, { recursive: true, force: true });
  }
}

function main(args) {
  let input, output;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--input' && args[i+1]) input = args[++i];
    else if (args[i] === '--out' && args[i+1]) output = args[++i];
    else throw new Error('Usage: render-page.mjs --input <absolute.md> --out <absolute-new.html>');
  }
  process.stdout.write(`${JSON.stringify(renderPage({ input, output }))}\n`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(process.argv.slice(2)); }
  catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
