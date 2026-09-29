import fs from 'node:fs';
import { routeTask } from './route-core.mjs';
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
try {
  const request = JSON.parse(fs.readFileSync(0, 'utf8').replace(/^\uFEFF/, ''));
  const result = routeTask(request.prompt, readJson(request.catalogPath), readJson(request.profilePath), request.limit);
  process.stdout.write(JSON.stringify(result));
} catch (error) {
  process.stderr.write(`Skill routing failed: ${error.message}\n`);
  process.exitCode = 1;
}
