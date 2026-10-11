## Test Isolation & Sandbox

Three tiers of isolation — use the lightest tier that satisfies your needs.

### Tier 1 — Filesystem Isolation (default, always use)

Each test gets its own `APPDATA` / `LOCALAPPDATA` / `TEMP` via `subprocess.Popen` and `Application.connect()`. pytest's `tmp_path` fixture handles cleanup automatically.

```python
# conftest.py — replace the basic `app` fixture with this
import os, subprocess, pytest
from pywinauto import Application
from config import APP_PATH, APP_ARGS, APP_TITLE, LAUNCH_TIMEOUT, ACTION_TIMEOUT, ARTIFACT_DIR

@pytest.fixture(scope="function")
def app(request, tmp_path):
    """Fresh process + isolated user-data dirs per test."""
    if not APP_PATH:
        pytest.exit("APP_PATH not set", returncode=1)

    # Redirect all per-user storage to an isolated tmp directory
    sandbox_env = os.environ.copy()
    sandbox_env["QT_ACCESSIBILITY"]  = "1"
    sandbox_env["APPDATA"]           = str(tmp_path / "AppData" / "Roaming")
    sandbox_env["LOCALAPPDATA"]      = str(tmp_path / "AppData" / "Local")
    sandbox_env["TEMP"] = sandbox_env["TMP"] = str(tmp_path / "Temp")
    for p in (sandbox_env["APPDATA"], sandbox_env["LOCALAPPDATA"], sandbox_env["TEMP"]):
        os.makedirs(p, exist_ok=True)

    if not APP_TITLE:
        pytest.exit("APP_TITLE environment variable is not set", returncode=1)

    # shlex.split handles quoted args with spaces; plain split() breaks on them
    import shlex
    # Launch via subprocess so we can pass env; connect pywinauto by PID
    proc = subprocess.Popen(
        [APP_PATH] + shlex.split(APP_ARGS),
        env=sandbox_env,
    )
    pw_app = Application(backend="uia").connect(process=proc.pid, timeout=LAUNCH_TIMEOUT)
    win    = pw_app.window(title=APP_TITLE)
    win.wait("visible", timeout=LAUNCH_TIMEOUT)
    yield win

    if getattr(getattr(request.node, "rep_call", None), "failed", False):
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        try:
            win.capture_as_image().save(
                os.path.join(ARTIFACT_DIR, f"FAIL_{request.node.name}.png")
            )
        except Exception:
            pass
    try:
        win.close()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    # tmp_path is cleaned up automatically by pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, f"rep_{outcome.get_result().when}", outcome.get_result())
```

### Tier 2 — Windows Job Object (optional: process-lifetime containment)

Attach the process to a Job Object so it is **automatically terminated** when
the test fixture's job handle is GC'd. Also prevents the app from spawning
child processes that escape fixture cleanup.

> **Scope of isolation:** Job Objects do NOT virtualize filesystem access or
> block network traffic. File-write and network isolation require AppContainer,
> Windows Firewall rules, or Tier 3 (Windows Sandbox). Use Tier 2 only for
> process-lifetime and child-process containment.

Requires no extra dependencies.

```python
import ctypes, ctypes.wintypes as wt

def restrict_process(pid: int):
    """
    Attach the process to a Job Object that prevents it from:
    - spawning processes outside the job (LIMIT_KILL_ON_JOB_CLOSE)
    Does NOT block network — use Windows Firewall rules for that.
    """
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    # Minimal rights: SET_QUOTA (0x0100) | TERMINATE (0x0001)
    PROCESS_SET_QUOTA_AND_TERMINATE    = 0x0101

    kernel32 = ctypes.windll.kernel32
    job   = kernel32.CreateJobObjectW(None, None)
    hproc = kernel32.OpenProcess(PROCESS_SET_QUOTA_AND_TERMINATE, False, pid)

    # Correct struct layout — LimitFlags is at offset +16, not +44
    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", wt.LARGE_INTEGER),
            ("PerJobUserTimeLimit",     wt.LARGE_INTEGER),
            ("LimitFlags",             wt.DWORD),
            ("MinimumWorkingSetSize",   ctypes.c_size_t),
            ("MaximumWorkingSetSize",   ctypes.c_size_t),
            ("ActiveProcessLimit",      wt.DWORD),
            ("Affinity",               ctypes.c_size_t),
            ("PriorityClass",          wt.DWORD),
            ("SchedulingClass",        wt.DWORD),
        ]

    info = JOBOBJECT_BASIC_LIMIT_INFORMATION()
    info.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    ok = kernel32.SetInformationJobObject(job, 2, ctypes.byref(info), ctypes.sizeof(info))
    if not ok:
        raise ctypes.WinError()
    kernel32.AssignProcessToJobObject(job, hproc)
    kernel32.CloseHandle(hproc)
    return job  # keep alive — job closes (kills proc) when GC'd

# After proc = subprocess.Popen(...):  job = restrict_process(proc.pid)
```

### Tier 3 — Windows Sandbox (CI full-OS isolation)

When you need a clean Windows image per run (no leftover registry keys, no
shared GPU state, true isolation), run the **entire test suite** inside
[Windows Sandbox](https://learn.microsoft.com/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-overview).

**Requirement:** Windows 10/11 Pro or Enterprise, Virtualization enabled.

Create `e2e-sandbox.wsb` in your project root:

```xml
<Configuration>
  <MappedFolders>
    <!-- App binary (read-only) -->
    <MappedFolder>
      <HostFolder>C:\path\to\your\build\Release</HostFolder>
      <SandboxFolder>C:\app</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
    <!-- Test suite (read-write for artifacts) -->
    <MappedFolder>
      <HostFolder>C:\path\to\your\e2e_test</HostFolder>
      <SandboxFolder>C:\e2e_test</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <!--
      Windows Sandbox starts with no Python. Install it silently first,
      then install deps and run tests. Artifacts are written back to the
      host via the MappedFolder above.
    -->
    <Command>powershell -Command "
      winget install --id Python.Python.3.11 --silent --accept-package-agreements;
      $env:PATH += ';' + $env:LOCALAPPDATA + '\Programs\Python\Python311\Scripts';
      cd C:\e2e_test;
      pip install -r requirements.txt;
      pytest tests\ -v
    "</Command>
  </LogonCommand>
</Configuration>
```

Launch: `WindowsSandbox.exe e2e-sandbox.wsb`

> pywinauto and the app both run **inside** the sandbox (same session required).
> Artifacts are written back to the host via the mapped folder.

### Tier comparison

| Tier | Isolation | Setup cost | Works on CI | Use when |
|------|-----------|-----------|-------------|----------|
| 1 — `tmp_path` env redirect | Filesystem | Zero | Always | Default for all tests |
| 2 — Job Object | Process tree | Low | Always | Prevent child-process escape |
| 3 — Windows Sandbox | Full OS | Medium | Needs Pro/Enterprise image | Nightly clean-room runs |

### Prevent hanging tests

Add `pytest-timeout` to cap any single test. In `pytest.ini` set `timeout = 60` and `timeout_method = thread`. Note: `thread` method cannot kill Qt app subprocesses on Windows — add `atexit.register(lambda: [p.kill() for p in psutil.Process().children(recursive=True)])` in `conftest.py` to reap orphans.

## CI/CD Integration

```yaml
# .github/workflows/e2e-desktop.yml
name: Desktop E2E
on: [push, pull_request]

jobs:
  e2e:
    runs-on: windows-latest   # real GUI environment, no Xvfb needed
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }

      - name: Install deps
        run: pip install pywinauto pytest pytest-html Pillow

      - name: Build app
        run: cmake --build build --config Release  # adjust to your build system

      - name: Run E2E
        env:
          APP_PATH: ${{ github.workspace }}\build\Release\MyApp.exe
          APP_TITLE: "My Application"
          CI: "true"
        run: pytest tests/ --html=artifacts/report.html --self-contained-html --junitxml=artifacts/results.xml -v

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: e2e-artifacts
          path: artifacts/
          retention-days: 14
```

