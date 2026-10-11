## Qt Specific

### Enable UIA in Qt 5.x

Qt 5.x accessibility is disabled by default in some builds (especially 5.7–5.14). Set the environment variable **before** launching. Qt 6.x enables accessibility by default — skip this step for Qt 6.

```python
# conftest.py — add at module top
import os
os.environ["QT_ACCESSIBILITY"] = "1"
```

Or export it in CI:

```yaml
env:
  QT_ACCESSIBILITY: "1"
```

### Add Stable Identifiers to Qt Widgets

```cpp
// Preferred: both objectName and accessibleName
void setTestId(QWidget* w, const char* id) {
    w->setObjectName(id);
    w->setAccessibleName(id);  // becomes UIA Name property
}

// In your dialog constructor:
setTestId(ui->usernameEdit, "usernameInput");
setTestId(ui->passwordEdit, "passwordInput");
setTestId(ui->loginButton,  "btnLogin");
setTestId(ui->errorLabel,   "lblError");
```

Centralise all IDs in a header to avoid typos:

```cpp
// test_ids.h
#define TID_USERNAME   "usernameInput"
#define TID_PASSWORD   "passwordInput"
#define TID_BTN_LOGIN  "btnLogin"
#define TID_LBL_ERROR  "lblError"
```

### Qt-Specific Quirks

**QComboBox** — the dropdown is a separate top-level window:

```python
from pywinauto import Desktop

def select_combo_item(page, combo_spec, item_text):
    page.click(combo_spec)
    # Dropdown appears as a new root-level window
    # class_name varies by Qt version — verify with Accessibility Insights
    # Qt 5.x: "Qt5QWindowIcon"  |  Qt 6.x: "Qt6QWindowIcon" — verify with Accessibility Insights
    popup = Desktop(backend="uia").window(class_name_re="Qt[56]QWindowIcon")
    popup.wait("visible", timeout=5)
    popup.child_window(title=item_text).click_input()
```

**QMessageBox / QDialog** — also separate top-level windows:

```python
dlg = page.wait_window("Confirm")          # wait for dialog title
dlg.child_window(title="OK").click_input() # click button inside it
```

**QTableWidget / QTableView** — row/cell access:

```python
table = page.by_id("tblUsers").wrapper_object()
cell  = table.cell(row=0, column=1)
print(cell.window_text())
```

**Self-drawn controls** (`paintEvent`-only, `QGraphicsView`, `QOpenGLWidget`) — UIA cannot see their internals. Use the Fallback section below.

