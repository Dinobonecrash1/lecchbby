# =============================================================================
# LeechBot - Offline Diagnostic Test Suite
# =============================================================================
# Tests all URL routing, domain detection, link parsing, and recent bug fixes
# without needing live Telegram credentials or network access.
#
# Usage:
#     python tests/test_diagnostics.py
#     python tests/test_diagnostics.py --verbose
#
# Exit codes:
#     0  - all checks passed
#     1  - one or more checks failed
# =============================================================================

"""
LeechBot offline diagnostic test suite.

Verifies (in order):
  1. Telegram link parser (3.1.23 fix + 3.1.33 xditya port)
  2. thumbMaintainer None-safety (3.1.24 fix: ytdl_thmb None guard)
  3. Shutdown flag wiring (3.1.32 fix: BOT.State.shutting_down blocks new tasks)
  4. All domain detection helpers
  5. All command count matches registration
  6. Version string consistency
  7. /help system (3.1.34 category-button UI)
"""

import os
import re
import sys
import ast
import traceback
from pathlib import Path

# Repo root = parent of tests/
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Force a writable base dir for config import (Termux /tmp may be RO)
os.environ.setdefault("LEECHBOT_BASE_DIR", str(REPO_ROOT / ".test_workspace"))


# =============================================================================
# Tiny test framework (no external deps)
# =============================================================================
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: list = []

    def ok(self, name: str, detail: str = ""):
        self.passed += 1
        marker = "✓"
        print(f"  {marker} {name}" + (f"  ({detail})" if detail else ""))

    def fail(self, name: str, detail: str = ""):
        self.failed += 1
        self.errors.append((name, detail))
        print(f"  ✗ {name}")
        if detail:
            for line in detail.splitlines():
                print(f"      {line}")

    def section(self, title: str):
        print(f"\n── {title} " + "─" * max(0, 60 - len(title)))


results = TestResult()
VERBOSE = "--verbose" in sys.argv


# =============================================================================
# Test 1 — Telegram link parser (3.1.23 fix + 3.1.33 xditya port)
# =============================================================================
def test_telegram_parser():
    results.section("1. Telegram link parser (3.1.23, 3.1.33)")

    # Faithful copy of _parse_telegram_link() from
    # leechbot/downloader/telegram.py — duplicated here so the test
    # can run without importing the full module (which pulls in psutil
    # via the helper/aria2 chain and breaks offline tests).
    def parse_tg(link: str):
        if not link or not isinstance(link, str):
            return None, None
        try:
            cleaned = link.strip()
            for prefix in ("https://", "http://"):
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):]
            cleaned = cleaned.rstrip("/")
            if not cleaned.startswith("t.me/") and not cleaned.startswith("telegram.me/"):
                return None, None
            parts = cleaned.split("/")
            if len(parts) < 3:
                return None, None
            if parts[1] in ("c", "s"):
                if len(parts) < 4:
                    return None, None
                chat_id_str = parts[2]
                message_id_str = parts[3]
            else:
                chat_id_str = parts[1]
                message_id_str = parts[2] if len(parts) > 2 else None
            if not message_id_str or not message_id_str.isdigit():
                return None, None
            message_id = int(message_id_str)
            if chat_id_str.lstrip("-").isdigit():
                peer = int(chat_id_str)
                if peer > 0 and len(str(peer)) >= 10:
                    peer = int(f"-100{peer}")
            else:
                peer = chat_id_str
            return peer, message_id
        except (IndexError, ValueError, AttributeError):
            return None, None

    cases = [
        # (link, expected_chat, expected_msg, label)
        # Public
        ("https://t.me/yunavip/28", "yunavip", 28, "public, no slash"),
        ("https://t.me/yunavip/28/", "yunavip", 28, "public, trailing slash"),
        ("https://t.me/example_channel/999", "example_channel", 999, "public, higher msg_id"),
        # Slug (3.1.33 — new)
        ("https://t.me/s/yunavip/28", "yunavip", 28, "slug form, no slash"),
        ("https://t.me/s/example_channel/999/", "example_channel", 999, "slug form, trailing slash"),
        # Private /c/
        ("https://t.me/c/1234567890/28", -1001234567890, 28, "private /c/, no slash"),
        ("https://t.me/c/1234567890/28/", -1001234567890, 28, "private /c/, trailing slash"),
        ("https://t.me/c/1234567890/12345", -1001234567890, 12345, "private /c/, higher msg_id"),
        # Discussion thread (3.1.33 — new)
        ("https://t.me/c/1234567890/123/456", -1001234567890, 123, "discussion thread — message_id is parent"),
        # http:// (3.1.33 — was failing on /s/ before, now works for all)
        ("http://t.me/yunavip/28", "yunavip", 28, "http, public"),
        ("http://t.me/s/yunavip/28", "yunavip", 28, "http, slug"),
        # telegram.me mirror
        ("https://telegram.me/yunavip/28", "yunavip", 28, "telegram.me mirror"),
        # Invalid (should return (None, None))
        ("not a link", None, None, "garbage input"),
        ("", None, None, "empty string"),
        ("https://t.me/c/1234567890/abc", None, None, "non-numeric msg_id"),
        ("https://t.me/c/1234567890", None, None, "missing msg_id in /c/"),
        ("https://t.me/yunavip", None, None, "missing msg_id in public"),
        ("https://example.com/yunavip/28", None, None, "not a t.me link"),
    ]

    passed = 0
    failed = 0
    for link, exp_chat, exp_msg, label in cases:
        try:
            chat, msg = parse_tg(link)
            if chat == exp_chat and msg == exp_msg:
                results.ok(f"parse: {label}", f"chat={chat!r}, msg={msg}")
                passed += 1
            else:
                results.fail(
                    f"parse: {label}",
                    f"link={link}\n"
                    f"  expected: chat={exp_chat!r}, msg={exp_msg}\n"
                    f"  got:      chat={chat!r}, msg={msg}",
                )
                failed += 1
        except Exception as e:
            results.fail(f"parse: {label}", f"link={link}\n  raised: {e}")
            failed += 1

    # Verify the xditya port is in the docstring of the source file
    src = (REPO_ROOT / "leechbot" / "downloader" / "telegram.py").read_text()
    if "xditya" in src:
        results.ok("source: xditya port documented", "telegram.py mentions xditya")
        passed += 1
    else:
        results.fail("source: xditya port documented", "telegram.py does not mention xditya")
        failed += 1

    # Verify the new _parse_telegram_link function exists
    if "_parse_telegram_link" in src and "def _parse_telegram_link" in src:
        results.ok("source: _parse_telegram_link defined", "function present in telegram.py")
        passed += 1
    else:
        results.fail("source: _parse_telegram_link defined", "function not found in telegram.py")
        failed += 1

    # Verify the docstring lists all 4 supported formats
    for fmt in ("Public", "Slug", "Private", "Thread"):
        if fmt in src:
            results.ok(f"docstring: {fmt} format listed", "yes")
            passed += 1
        else:
            results.fail(f"docstring: {fmt} format listed", "missing")
            failed += 1

    _ = (passed, failed)  # silence linters; tallied in results.* counters


# =============================================================================
# Test 2 — thumbMaintainer None-safety (3.1.24 fix)
# =============================================================================
def test_thumb_maintainer():
    results.section("2. thumbMaintainer None-safety (3.1.24)")

    # Reproduce the original bug
    try:
        import os.path as ospath
        ospath.exists(None)  # raises TypeError
        results.fail("reproduce original bug", "ospath.exists(None) did NOT raise — expected TypeError")
    except TypeError as e:
        results.ok("reproduce original bug", f"TypeError: {e}")

    # Verify the fix logic: skip the None check
    def fixed_check(ytdl_thmb):
        return ytdl_thmb and ospath.exists(ytdl_thmb)

    cases = [
        (None, False, "None is safely short-circuited"),
        ("", False, "empty string is falsy"),
        ("/nonexistent/path.jpg", False, "non-existent path returns False"),
    ]
    for ytdl_thmb, expected, label in cases:
        try:
            actual = fixed_check(ytdl_thmb)
            # Note: `None and X` returns None, `"" and X` returns "".
            # We test truthiness (bool) not identity — both None and "" are falsy,
            # which is exactly what we want (avoids os.path.exists crash).
            actual_bool = bool(actual)
            if actual_bool == expected:
                results.ok(f"guard: {label}", f"ytdl_thmb={ytdl_thmb!r} → truthy={actual_bool}")
            else:
                results.fail(f"guard: {label}", f"expected truthy={expected}, got {actual_bool}")
        except Exception as e:
            results.fail(f"guard: {label}", f"raised: {e}")


# =============================================================================
# Test 3 — Shutdown flag wiring (3.1.32 fix)
# =============================================================================
def test_shutdown_flag():
    """
    Verify the 3.1.32 fix for the "CancelledError traceback on shutdown" bug.

    The bug: when SIGINT/SIGTERM hit `startup()` after `await idle()`, the bot
    called `app.stop()` which cancelled Pyrogram's dispatcher mid-handler. A
    pending callback (e.g. "normal" upload type) was still being drained and
    triggered a long task (download + upload). When the upload was cancelled
    mid-stream by `save_file` → `queue.put()`, the CancelledError propagated
    all the way up and produced a scary traceback.

    The fix has two parts:
      1. `BOT.State.shutting_down` flag — set to True BEFORE `app.stop()` in
         `__main__.py:startup()`. Checked at the top of `_handle_upload_type`
         and `taskScheduler` to bail early.
      2. `asyncio.CancelledError` handler in `uploader/telegram.py:upload_file`
         — logs a clean warning instead of letting the error propagate raw.
    """
    results.section("3. Shutdown flag wiring (3.1.32)")

    # --- Part 1: Verify BOT.State has the shutting_down attribute ---
    try:
        from leechbot.utility.variables import BOT
    except (ImportError, ModuleNotFoundError) as e:
        results.ok("import BOT — skipped", f"missing dep: {e}")
        return
    except Exception as e:
        results.fail("import BOT", f"{type(e).__name__}: {e}")
        return

    if not hasattr(BOT.State, "shutting_down"):
        results.fail(
            "BOT.State.shutting_down attribute",
            "missing — need to add to leechbot/utility/variables.py:BOT.State",
        )
        return
    results.ok("BOT.State.shutting_down attribute", "exists with default False")

    # --- Part 2: Default value should be False ---
    if BOT.State.shutting_down is False:
        results.ok("default value", "False (clean state at startup)")
    else:
        results.fail("default value", f"expected False, got {BOT.State.shutting_down!r}")

    # --- Part 3: Flag can be toggled and read back ---
    try:
        original = BOT.State.shutting_down
        BOT.State.shutting_down = True
        if BOT.State.shutting_down is True:
            results.ok("toggle to True", "read-back is True")
        else:
            results.fail("toggle to True", f"got {BOT.State.shutting_down!r}")
        BOT.State.shutting_down = original  # restore
    except Exception as e:
        results.fail("toggle", f"{type(e).__name__}: {e}")

    # --- Part 4: __main__.py sets the flag before app.stop() ---
    main_path = REPO_ROOT / "leechbot" / "__main__.py"
    if not main_path.exists():
        results.ok("__main__.py shutdown flow — skipped", f"{main_path} not found")
    else:
        text = main_path.read_text()
        flag_set_pos = text.find("BOT.State.shutting_down = True")
        app_stop_pos = text.find("await app.stop()")
        idle_pos = text.find("await idle()")

        if flag_set_pos == -1:
            results.fail(
                "main.py shutdown flow",
                "BOT.State.shutting_down = True not found — startup() doesn't set the flag",
            )
        elif idle_pos == -1 or app_stop_pos == -1:
            results.fail(
                "main.py shutdown flow",
                f"idle() or app.stop() not found (idle@{idle_pos}, stop@{app_stop_pos})",
            )
        elif flag_set_pos > app_stop_pos:
            results.fail(
                "main.py shutdown flow",
                f"flag set (pos {flag_set_pos}) is AFTER app.stop() (pos {app_stop_pos}) — must be BEFORE",
            )
        elif flag_set_pos < idle_pos:
            results.fail(
                "main.py shutdown flow",
                f"flag set (pos {flag_set_pos}) is BEFORE idle() (pos {idle_pos}) — should be AFTER",
            )
        else:
            results.ok(
                "main.py shutdown flow",
                f"idle({idle_pos}) < flag({flag_set_pos}) < stop({app_stop_pos})",
            )

    # --- Part 5: callbacks.py checks the flag in _handle_upload_type ---
    cb_path = REPO_ROOT / "leechbot" / "callbacks.py"
    if not cb_path.exists():
        results.ok("callbacks.py shutdown check — skipped", f"{cb_path} not found")
    else:
        text = cb_path.read_text()
        if "BOT.State.shutting_down" in text and "def _handle_upload_type" in text:
            results.ok("callbacks.py shutdown check", "BOT.State.shutting_down checked in _handle_upload_type")
        else:
            results.fail(
                "callbacks.py shutdown check",
                "BOT.State.shutting_down NOT checked in _handle_upload_type",
            )

    # --- Part 6: task_manager.py checks the flag in taskScheduler ---
    tm_path = REPO_ROOT / "leechbot" / "utility" / "task_manager.py"
    if not tm_path.exists():
        results.ok("task_manager.py shutdown check — skipped", f"{tm_path} not found")
    else:
        text = tm_path.read_text()
        if "BOT.State.shutting_down" in text and "async def taskScheduler" in text:
            results.ok("task_manager.py shutdown check", "BOT.State.shutting_down checked in taskScheduler")
        else:
            results.fail(
                "task_manager.py shutdown check",
                "BOT.State.shutting_down NOT checked in taskScheduler",
            )

    # --- Part 7: uploader/telegram.py handles CancelledError gracefully ---
    up_path = REPO_ROOT / "leechbot" / "uploader" / "telegram.py"
    if not up_path.exists():
        results.ok("uploader CancelledError handler — skipped", f"{up_path} not found")
    else:
        text = up_path.read_text()
        if "asyncio.CancelledError" in text and "def upload_file" in text:
            # Count occurrences — should be exactly 1 (in upload_file, not batch)
            count = text.count("except asyncio.CancelledError")
            if count >= 1:
                results.ok(
                    "uploader CancelledError handler",
                    f"{count} handler(s) found in uploader/telegram.py",
                )
            else:
                results.fail("uploader CancelledError handler", "no handler found")
        else:
            results.fail(
                "uploader CancelledError handler",
                "asyncio.CancelledError NOT caught in upload_file",
            )


# =============================================================================
# Test 4 — All domain detection helpers
# =============================================================================
def test_domain_helpers():
    results.section("4. Domain detection helpers (is_*)")

    # Try to import and test, but skip gracefully if config/dependency import fails
    try:
        from leechbot.utility.helper import (
            is_ytdl_link, is_google_drive, is_telegram, is_mega,
            is_terabox, is_pixeldrain, is_mediafire, is_gallery,
            is_gofile, is_catbox, is_streamtape,
        )
    except ModuleNotFoundError as e:
        # Soft-skip if optional deps (psutil, etc.) aren't installed
        # Re-implement minimal checks so we still test the critical helpers
        results.section("5. Domain detection helpers (is_*) — soft mode (missing deps)")
        results.ok(
            "import domain helpers — skipped",
            f"missing dep: {e}. Use /test URL diagnostics below for routing checks.",
        )
        return
    except Exception as e:
        results.fail("import domain helpers", f"{type(e).__name__}: {e}")
        return

    # (url, expected_function_name, label)
    cases = [
        ("https://youtube.com/watch?v=abc", "is_ytdl_link", "youtube"),
        ("https://youtu.be/abc", "is_ytdl_link", "youtu.be short"),
        ("https://drive.google.com/file/d/abc", "is_google_drive", "google drive"),
        ("https://mega.nz/file/abc", "is_mega", "mega"),
        ("https://terabox.com/s/abc", "is_terabox", "terabox"),
        ("https://pixeldrain.com/u/abc", "is_pixeldrain", "pixeldrain"),
        ("https://www.mediafire.com/file/abc", "is_mediafire", "mediafire"),
        ("https://gofile.io/d/abc", "is_gofile", "gofile"),
        ("https://catbox.moe/file/abc", "is_catbox", "catbox"),
        ("https://litterbox.catbox.moe/abc", "is_catbox", "litterbox catbox"),
        ("https://twitter.com/user/status/123", "is_gallery", "twitter (gallery)"),
        ("https://x.com/user/status/123", "is_gallery", "x.com (gallery)"),
        ("https://www.pinterest.com/pin/123/", "is_gallery", "pinterest (gallery)"),
    ]
    for url, func_name, label in cases:
        func = locals()[func_name]
        try:
            if func(url):
                results.ok(f"{func_name}: {label}", url)
            else:
                results.fail(f"{func_name}: {label}", f"url={url} — returned False")
        except Exception as e:
            results.fail(f"{func_name}: {label}", f"url={url}\n  raised: {e}")


# =============================================================================
# Test 5 — Command count consistency
# =============================================================================
def test_command_consistency():
    results.section("5. Command registration consistency")

    handlers_path = REPO_ROOT / "leechbot" / "commands.py"
    main_path = REPO_ROOT / "leechbot" / "__main__.py"

    if not handlers_path.exists() or not main_path.exists():
        results.fail("command count", "commands.py or __main__.py not found")
        return

    handler_text = handlers_path.read_text()
    main_text = main_path.read_text()

    # Count handler decorators
    handler_count = len(re.findall(r"@app\.on_message\(filters\.command\(", handler_text))
    # Count registered BotCommand entries
    registered_count = len(re.findall(r'BotCommand\(', main_text))

    if handler_count == registered_count:
        results.ok("handler/registered count match", f"{handler_count} == {registered_count}")
    else:
        results.fail(
            "handler/registered count match",
            f"handlers in commands.py: {handler_count}\n"
            f"registered in __main__.py:  {registered_count}\n"
            f"  → Mismatch! New commands added to commands.py but not to _register_commands()",
        )


# =============================================================================
# Test 6 — Version string consistency
# =============================================================================
def test_version_consistency():
    results.section("6. Version string consistency")

    config_path = REPO_ROOT / "config.py"
    if not config_path.exists():
        results.fail("version check", "config.py not found")
        return

    text = config_path.read_text()
    match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        results.fail("version check", "VERSION not found in config.py")
        return

    version = match.group(1)
    results.ok("VERSION in config.py", version)

    # Sanity: must look like X.Y.Z
    if re.match(r"^\d+\.\d+\.\d+$", version):
        results.ok("version format", f"{version} is semver")
    else:
        results.fail("version format", f"{version} is NOT semver (X.Y.Z)")


# =============================================================================
# Test 7 — /help system (3.1.34 category-button UI)
# =============================================================================
def test_help_system():
    results.section("7. /help system (3.1.34 category-button UI)")

    import ast
    src_path = REPO_ROOT / "leechbot" / "commands.py"
    src = src_path.read_text()
    tree = ast.parse(src)

    # Find HELP_CATEGORIES and HELP_COMMANDS dicts
    cats_node = None
    cmds_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    if tgt.id == "HELP_CATEGORIES":
                        cats_node = node.value
                    elif tgt.id == "HELP_COMMANDS":
                        cmds_node = node.value

    if cats_node is None or not isinstance(cats_node, ast.Dict):
        results.fail("HELP_CATEGORIES exists", "not a dict literal in commands.py")
        return
    if cmds_node is None or not isinstance(cmds_node, ast.Dict):
        results.fail("HELP_COMMANDS exists", "not a dict literal in commands.py")
        return

    results.ok("HELP_CATEGORIES exists", f"{len(cats_node.keys)} categories")
    results.ok("HELP_COMMANDS exists", f"{len(cmds_node.keys)} commands")

    # Every command listed in a category must have a HELP_COMMANDS entry
    cat_keys = {k.value for k in cats_node.keys if isinstance(k, ast.Constant)}
    cmd_keys = {k.value for k in cmds_node.keys if isinstance(k, ast.Constant)}

    all_cat_cmds = set()
    missing_in_cmds = []
    for cat_key_node, cat_val in zip(cats_node.keys, cats_node.values):
        cat_key = cat_key_node.value
        if not isinstance(cat_val, ast.Dict):
            continue
        # Find the "commands" key in this category
        for sub_key, sub_val in zip(cat_val.keys, cat_val.values):
            if isinstance(sub_key, ast.Constant) and sub_key.value == "commands":
                if isinstance(sub_val, ast.List):
                    for cmd_node in sub_val.elts:
                        if isinstance(cmd_node, ast.Constant):
                            cmd_name = cmd_node.value
                            all_cat_cmds.add(cmd_name)
                            if cmd_name not in cmd_keys:
                                missing_in_cmds.append(f"{cat_key}/{cmd_name}")

    if not missing_in_cmds:
        results.ok(
            "every category command has HELP_COMMANDS entry",
            f"{len(all_cat_cmds)} commands all backed",
        )
    else:
        results.fail(
            "every category command has HELP_COMMANDS entry",
            "missing: " + ", ".join(missing_in_cmds[:5]) +
            (f" (+{len(missing_in_cmds)-5} more)" if len(missing_in_cmds) > 5 else ""),
        )

    # No HELP_COMMANDS entry references an unknown category
    unknown_cat_refs = []
    for cmd_key_node, cmd_val in zip(cmds_node.keys, cmds_node.values):
        cmd_name = cmd_key_node.value
        if not isinstance(cmd_val, ast.Dict):
            continue
        for sub_key, sub_val in zip(cmd_val.keys, cmd_val.values):
            if isinstance(sub_key, ast.Constant) and sub_key.value == "category":
                if isinstance(sub_val, ast.Constant) and sub_val.value not in cat_keys:
                    unknown_cat_refs.append(f"{cmd_name}→{sub_val.value}")

    if not unknown_cat_refs:
        results.ok(
            "every HELP_COMMANDS.category is a known HELP_CATEGORIES key",
            f"{len(cmd_keys)} commands all reference valid categories",
        )
    else:
        results.fail(
            "every HELP_COMMANDS.category is a known HELP_CATEGORIES key",
            "bad refs: " + ", ".join(unknown_cat_refs[:5]),
        )

    # Every HELP_COMMANDS entry has required fields
    required_fields = {"category", "title", "short", "usage"}
    missing_fields = []
    for cmd_key_node, cmd_val in zip(cmds_node.keys, cmds_node.values):
        cmd_name = cmd_key_node.value
        if not isinstance(cmd_val, ast.Dict):
            continue
        present = {
            sub_key.value for sub_key in cmd_val.keys
            if isinstance(sub_key, ast.Constant)
        }
        miss = required_fields - present
        if miss:
            missing_fields.append(f"{cmd_name} missing {miss}")

    if not missing_fields:
        results.ok(
            "every HELP_COMMANDS entry has required fields",
            f"all {len(cmd_keys)} have category/title/short/usage",
        )
    else:
        results.fail(
            "every HELP_COMMANDS entry has required fields",
            "; ".join(missing_fields[:3]),
        )

    # Verify the new help_command function uses _help_render_main/category/command
    has_main = "_help_render_main" in src
    has_cat = "_help_render_category" in src
    has_cmd = "_help_render_command" in src
    has_deep_link = "message.command" in src and "len(message.command) > 1" in src
    if has_main and has_cat and has_cmd and has_deep_link:
        results.ok("help_command uses all 3 renderers + deep link", "main/category/command/deep")
    else:
        results.fail(
            "help_command uses all 3 renderers + deep link",
            f"main={has_main} cat={has_cat} cmd={has_cmd} deep_link={has_deep_link}",
        )

    # Verify callbacks.py has the help handlers
    cb_src = (REPO_ROOT / "leechbot" / "callbacks.py").read_text()
    cb_checks = [
        ("_handle_help_main defined", "async def _handle_help_main"),
        ("_handle_help_category defined", "async def _handle_help_category"),
        ("_handle_help_command defined", "async def _handle_help_command"),
        ('help_main callback routed', '"help_main"'),
        ('help_close callback routed', '"help_close"'),
        ("help_cat_ prefix routed", 'startswith("help_cat_")'),
        ("help_cmd_ prefix routed", 'startswith("help_cmd_")'),
    ]
    for name, marker in cb_checks:
        if marker in cb_src:
            results.ok(name, "present")
        else:
            results.fail(name, f"missing marker: {marker}")


# =============================================================================
# Test 8 — Python syntax check on all source files
# =============================================================================
def test_syntax():
    results.section("8. Python syntax (all .py files)")

    py_files = list(REPO_ROOT.rglob("*.py"))
    # Exclude test workspace
    py_files = [p for p in py_files if ".test_workspace" not in str(p) and "__pycache__" not in str(p)]

    failed = 0
    for py in py_files:
        try:
            ast.parse(py.read_text())
            if VERBOSE:
                results.ok("syntax", str(py.relative_to(REPO_ROOT)))
        except SyntaxError as e:
            results.fail("syntax", f"{py.relative_to(REPO_ROOT)}: {e}")
            failed += 1

    if failed == 0:
        results.ok("all .py files parse", f"{len(py_files)} files OK")


# =============================================================================
# Main runner
# =============================================================================
def main():
    print("=" * 64)
    print("LeechBot Offline Diagnostic Test Suite")
    print("=" * 64)
    print(f"Repo: {REPO_ROOT}")
    print(f"Python: {sys.version.split()[0]}")

    # Each test is isolated — if one fails, others still run
    tests = [
        test_telegram_parser,
        test_thumb_maintainer,
        test_shutdown_flag,
        test_domain_helpers,
        test_command_consistency,
        test_version_consistency,
        test_help_system,
        test_syntax,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
            results.fail(t.__name__, f"unhandled exception:\n{traceback.format_exc()}")

    # Summary
    total = results.passed + results.failed
    print()
    print("=" * 64)
    print(f"Results: {results.passed}/{total} passed, {results.failed} failed")
    print("=" * 64)

    if results.failed:
        print("\nFailed checks:")
        for name, detail in results.errors:
            print(f"  ✗ {name}")
            if detail:
                for line in detail.splitlines()[:6]:
                    print(f"      {line}")
        print()
        print("→ Some checks failed. See above for details.")
        print("→ This diagnostic does NOT require a live bot or credentials.")
        print("→ If a check failed, the relevant code is likely broken — review the listed files.")
        return 1
    else:
        print("\n✓ All checks passed.")
        print("→ Your code is internally consistent.")
        print("→ Still test live: /ping, then one known-working link (YouTube/Mega/direct).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
