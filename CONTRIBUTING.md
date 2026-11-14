# Contributing to OpenVoltam

Thank you for helping! OpenVoltam is a small open source project, and every contribution counts, from a bug report to a new feature. You don't need to be a programmer to help.

English and Spanish are both welcome in issues and pull requests.

## Contents

- [Ways to contribute](#ways-to-contribute)
- [Reporting bugs](#reporting-bugs)
- [Suggesting features](#suggesting-features)
- [Setting up for development](#setting-up-for-development)
- [Making a change](#making-a-change)
- [Code guidelines](#code-guidelines)
- [Pull request checklist](#pull-request-checklist)
- [License](#license)

## Ways to contribute

- **Test it.** Install a [test release](README.md#download-windows) or [run from source](docs/running-from-source.md), use it, and tell us what breaks. Testing on operating systems other than Windows is especially helpful.
- **Report bugs.** See [below](#reporting-bugs).
- **Improve the documentation.** If something in these guides confused you, it will confuse others too. Fixes are welcome.
- **Translate.** All interface text is in `global_scripts/ov_lang.py`. Fix Spanish wording or add missing translations.
- **Write code.** Fix a bug, add a feature, or add [automated tests](docs/testing.md#ideas-for-automated-tests).

## Reporting bugs

1. **Check whether it's already reported** in the [issues list](https://github.com/ask53/openVoltam/issues), including closed issues. If it is, add a comment with your details instead of opening a new issue.
2. **Open a new issue** with the [Bug report template](https://github.com/ask53/openVoltam/issues/new/choose).
3. **Include:**
   - **Version**: shown on the welcome screen, or the commit or branch if you run from source.
   - **How you run it**: the Windows installer, or Python (and which Python version).
   - **Operating system**: for example Windows 11, or Ubuntu 24.04.
   - **Device**: RodeoStat, RodeoStat HC, or none, and the potentiostat library version if you run from source (`pip show iorodeo-potentiostat`).
   - **Steps to reproduce**: exactly what you clicked, in order, starting from opening the app.
   - **What you expected to happen, and what actually happened.**
   - **Error messages**: if you run from source, copy the full text from the terminal, especially anything starting with `Traceback`. Screenshots of the window help too.
   - **Files**: if the bug involves a specific `.ovs` or `.ovm` file and it contains nothing private, attach it (zip it first if GitHub refuses the file type).

One bug per issue, please. It makes them easier to track and close.

**Security or privacy problems** (for example, something that could expose data from a session file) should not be posted publicly. Contact the maintainers directly instead.

## Suggesting features

Open an issue with the [Feature request template](https://github.com/ask53/openVoltam/issues/new/choose). Describe the problem you're trying to solve in the lab, not only the solution you have in mind. That helps us find the best way to fit it into the app.

For big changes, please **open an issue to discuss it before writing code**, so your work fits with what the maintainers are already doing.

## Setting up for development

1. Fork the repository on GitHub and clone your fork.
2. Follow [docs/running-from-source.md](docs/running-from-source.md).
3. Read [docs/project-structure.md](docs/project-structure.md) for a map of the code.

You can work on most of the interface without a device. See [docs/testing.md](docs/testing.md) for what you can and can't test without one.

## Making a change

1. **Start from the active branch.** Active development currently happens on the `develop` branch, and `main` holds the latest released code. Branch from `develop` unless a maintainer tells you otherwise:
   ```bash
   git remote add upstream https://github.com/ask53/openVoltam.git
   git fetch upstream
   git checkout -b my-change upstream/develop
   ```
2. **Make your change** in small, focused commits with clear messages, for example `Fix crash when deleting the last sample`.
3. **Test it** following [docs/testing.md](docs/testing.md). At minimum, do the launch check and the parts of the walkthrough your change touches.
4. **Push to your fork and open a pull request** against `develop`. Describe what you changed and why, how you tested it (and on which OS), and link the issue it fixes (`Fixes #12`).

### Keep these out of your commits

Some files change on your computer just from running OpenVoltam. Check `git status` and `git diff` before committing, and leave these out unless changing them is the point of your pull request:

| File | Why it changes |
|---|---|
| `global_scripts/ov_globals.py` | You set `PROC_PYTHON_CMD` (or `PROC_RUN_FROM`) for your computer |
| `external/settings.txt` | The app saves your language choice here |
| `external/process.exe`, `build/`, `dist/` | Windows build outputs (ignored by `.gitignore`) |
| Your `.ovs` / `.ovm` test files | Keep them in a folder outside the repository |

To undo an accidental change to a file: `git restore <file>`.

## Code guidelines

Follow the style of the code that's already there. In particular:

- **Windows** go in `wins/`, one class per file. Start new windows from `wins/_TEMPLATE_WIN.py`.
- **Plots and embedded widgets** go in `embeds/`.
- **Interface text** never goes directly in a window. Add it to `global_scripts/ov_lang.py` in **both** English (`'eng'`) and Spanish (`'esp'`), and apply it in the window's `set_text()` method. If you can't write the Spanish, copy the English text and mention it in your pull request so someone can translate it.
- **Constants** (dictionary keys, limits, file paths) go in `global_scripts/ov_globals.py` rather than being repeated as literal strings.
- **Slow work, file saves, and device communication** go through the background process in `processes/process.py`, so the interface doesn't freeze.
- **Supported devices** and their limits are defined in `devices/supportedDevices.py`.
- **Comment the why.** The codebase is heavily commented, so keep it that way for the next contributor.
- **Dependencies**: if you add a package, add it with a pinned version to `requirements.txt` and explain why in your pull request.

## Pull request checklist

- [ ] The pull request targets `develop` and contains one focused change.
- [ ] OpenVoltam launches and the parts I changed work ([docs/testing.md](docs/testing.md)).
- [ ] No local-only changes to `ov_globals.py` or `settings.txt`, and no test files or build outputs.
- [ ] New interface text is in `ov_lang.py` in English and Spanish.
- [ ] Documentation is updated if behavior or setup changed.

## License

OpenVoltam is licensed under the [GNU General Public License v3.0](LICENSE). By contributing, you agree that your contributions will be licensed under the same license.
