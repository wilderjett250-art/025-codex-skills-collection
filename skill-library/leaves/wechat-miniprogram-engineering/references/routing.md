# Page and action routing

Use this only when a click, navigation, page registration, or state-loading path is involved.

1. Locate the visible WXML control and its binding.
2. Locate the actual handler and all early returns, permission checks, and asynchronous branches.
3. Resolve the destination against `app.json` pages, subpackages, and `tabBar`.
4. Use `wx.switchTab` for a registered tab page. Use `wx.navigateTo` only for non-tab pages that remain on the navigation stack. Check `redirectTo`, `reLaunch`, and `navigateBack` against their actual semantics when present.
5. Verify the destination page lifecycle receives the intended identifiers and loads the intended record; a successful route call alone does not prove the user workflow succeeded.

For request-backed actions, continue through request construction, environment base URL, authorization, response handling, state update, and visible result.
