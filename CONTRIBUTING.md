# 🤝 CONTRIBUTING.md — How to Contribute

Thanks for your interest in LeechBot! This guide explains how to contribute effectively.

---

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- A Telegram bot token (for testing)
- System deps: `ffmpeg`, `aria2`, `p7zip-full`

### Setup

```bash
git clone https://github.com/Shineii86/LeechBot.git
cd LeechBot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python3 -m leechbot
```

---

## Development Workflow

### 1. Fork & Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

- Follow existing code patterns (see `AGENTS.md` for conventions)
- Keep changes focused — one feature/fix per PR
- Test manually with the bot

### 3. Update CHANGELOG.md

Every change must be recorded:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature description

### Fixed
- Bug fix description
```

**Add new entries at the top.** Never edit or delete existing entries.

### 4. Commit

```bash
git add -A
git commit -m "feat: description" # or "fix:", "docs:", "refactor:"
```

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `refactor:` — code restructuring
- `chore:` — maintenance tasks

### 5. Push & PR

```bash
git push origin feature/my-feature
```

Open a Pull Request against `main`.

---

## Code Guidelines

### Python Style

- No linter configured — follow existing patterns
- Async/await everywhere (this is an asyncio app)
- `logger = logging.getLogger(__name__)` at module top
- Type hints on function signatures preferred
- Docstrings on public functions

### File Structure

Every new `.py` file must have the standard header:

```python
# =============================================================================
# Telegram Leech Bot - [Module Name]
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================
```

### State Management

- Global state goes in `leechbot/utility/variables.py`
- Import existing classes, don't create new state singletons
- Mutate class attributes directly

### Error Handling

- Wrap risky operations in try/except
- Log errors with `logger.error()`
- FloodWait: `await sleep(e.value + 1)` + retry (max 10 times)
- Don't silently swallow exceptions

---

## What to Work On

### Good First Issues

- Add more downloader adapters (new file hosting sites)
- Improve error messages for users
- Add unit tests (none exist yet!)
- Dashboard improvements (new features, better UX)
- Documentation improvements

### Areas Needing Help

| Area | Status | Notes |
|------|--------|-------|
| Unit tests | ❌ None | Would need mocking for Pyrogram |
| CI/CD | ❌ None | GitHub Actions would be great |
| Type hints | ⚠️ Partial | Some files have them, many don't |
| i18n | ❌ None | English only |
| Docker | ✅ Done | `Dockerfile` + `docker-compose.yml` with all deps |
| Web dashboard | ✅ Basic | Could add more controls |

---

## Pull Request Checklist

Before submitting:

- [ ] Code follows existing patterns
- [ ] CHANGELOG.md updated (new entry at top)
- [ ] Manual testing done
- [ ] No secrets committed (`.env`, tokens, etc.)
- [ ] Commit messages use conventional format
- [ ] PR description explains what and why

---

## Reporting Issues

Use [GitHub Issues](https://github.com/Shineii86/LeechBot/issues) with:

- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Bot logs (check DUMP channel)
- Python version, OS, deployment method (VPS/Colab)

---

## License

By contributing, you agree your code will be licensed under the [MIT License](LICENSE).
