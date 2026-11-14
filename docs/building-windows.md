# Building the Windows executable and installer

These instructions are for **maintainers making a release**. They turn the Python code into Windows executables with [PyInstaller](https://pyinstaller.org/), then bundle them into an installer with [InstallForge](https://installforge.net/).

The build produces **two** executables:

| Executable | Built from | Recipe |
|---|---|---|
| `process.exe` | `processes/process.py` | `processes/process.spec` |
| `OpenVoltam.exe` | `OpenVoltam.py` | `OpenVoltam.spec` |

`process.exe` is the background process that the app uses for saving, reading, exporting, and device runs (see [project-structure.md](project-structure.md#the-background-process)).

> **Note:** `process.exe` is a build output and is **not stored in the repository**. Build it with step 2 below whenever you make a release.

## Before you start

- A Windows 10 or 11 computer with OpenVoltam [running from source](running-from-source.md), including the `develop` version of the potentiostat library.
- PyInstaller, installed in the same virtual environment: `pip install pyinstaller`
- InstallForge, for the final installer.
- Update the version number and release date (`VERSION` and `RELEASE`) shown on the welcome screen.

## 1. Reset the settings file

Set `external/settings.txt` to the defaults a new user should start with, for example:

```json
{
    "language": "eng"
}
```

This file is copied into the build, so whatever it contains is what new users will get.

## 2. Build `process.exe`

```bash
cd processes
py -m PyInstaller process.spec
```

This creates `processes/dist/process.exe`. Move it into the `external` folder:

```
external/process.exe
```

## 3. Point the app at `process.exe`

In `global_scripts/ov_globals.py`, switch the background process to the executable:

```python
#PROC_RUN_FROM = PROC_RUN_FROM_PYTHON
PROC_RUN_FROM = PROC_RUN_FROM_EXE
```

## 4. Check the background process

From the main OpenVoltam folder, run `py -m OpenVoltam`. Create, save, and reopen a session, and do a test run with a device if you can (see [testing.md](testing.md)). If it works, continue. Otherwise, debug before going further.

## 5. Build `OpenVoltam.exe`

From the main OpenVoltam folder:

```bash
py -m PyInstaller OpenVoltam.spec
```

This creates `dist/OpenVoltam/`, containing `OpenVoltam.exe` and an `_internal` folder.

## 6. Copy the `external` folder next to the executable

OpenVoltam looks for `external/` relative to the folder it runs from. Copy `dist/OpenVoltam/_internal/external` and paste it into `dist/OpenVoltam/`, so that you have:

```
dist/OpenVoltam/
├── OpenVoltam.exe
├── _internal/
└── external/        ← copied here
    ├── process.exe
    ├── settings.txt
    ├── icons/
    └── styles/
```

## 7. Test the executable

Run `dist/OpenVoltam/OpenVoltam.exe` and work through the [testing checklist](testing.md#3-interface-walkthrough-no-device), plus a [device test](testing.md#4-device-test) if possible.

## 8. Build the installer

Use InstallForge to bundle the contents of `dist/OpenVoltam/` into an installer that can be distributed.

## After the build

Undo the build-only changes so that the repository stays ready for running from source:

- Set `PROC_RUN_FROM` back to `PROC_RUN_FROM_PYTHON` in `ov_globals.py`.
- Don't commit `external/process.exe`, or the `build/` and `dist/` folders. They are ignored by `.gitignore`.
