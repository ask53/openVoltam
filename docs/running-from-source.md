# Running OpenVoltam from source

These instructions are for running OpenVoltam directly with Python, on any operating system. If you are on Windows 10 or 11 and just want to use the software, the [installer](../README.md#download-windows) is easier.

> **Tip:** we recommend avoiding virtual machines, which can cause headaches with USB and serial port communication. But this software is free to use, so you are welcome to make your own decisions :)

## Requirements

- **Python 3.12 or newer**
- A way to create virtual environments (these instructions use `venv`, which comes with most Python installations)
- A way to install Python packages (these instructions use `pip`)
- Optional: [git](https://git-scm.com/), to clone the repositories. You can also download them as ZIP files instead.

Throughout this guide, `python` means *whatever command runs Python 3.12+ on your computer*. Common ones are `py` (Windows), `python`, `python3`, or `python3.12`. Check yours with:

```bash
python --version
```

## 1. Get the OpenVoltam code

With git:

```bash
git clone https://github.com/ask53/openVoltam.git
cd openVoltam
```

Without git: on the [repository page](https://github.com/ask53/openVoltam), click **Code → Download ZIP**, unzip it, and open a terminal in the unzipped folder.

From now on, **"the main OpenVoltam folder"** means the folder that contains `OpenVoltam.py`.

## 2. Create and activate a virtual environment

This is optional but highly recommended. In the main OpenVoltam folder:

```bash
python -m venv venv
```

This creates a folder called `venv`. Activate it:

| System | Command |
|---|---|
| Linux / macOS | `source venv/bin/activate` |
| Windows (Command Prompt) | `venv\Scripts\activate.bat` |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |

Your prompt should now start with `(venv)`. You need to activate it again every time you open a new terminal.

## 3. Install the Python packages

```bash
pip install -r requirements.txt
```

This installs everything **except** the `potentiostat` library from IO Rodeo, which is required but is not in `requirements.txt` (see below).

## 4. Install the potentiostat library

OpenVoltam uses IO Rodeo's `potentiostat` library to talk to the device. It is **always required**, even if you have no device: OpenVoltam uses a background process for saving, reading, and exporting files, and that process imports this library.

There are two options:

### Option A — the version OpenVoltam uses (needed to run tests on a real device)

OpenVoltam uses a newer version of the library than the one on PyPI. Install it from the `develop` branch of the [IO Rodeo potentiostat repository](https://github.com/iorodeo/potentiostat):

```bash
# run this somewhere outside the OpenVoltam folder
git clone -b develop https://github.com/iorodeo/potentiostat.git
cd potentiostat/software/python/potentiostat
pip install .        # with your OpenVoltam virtual environment still active
```

Without git: on the repository page, switch the branch to **develop** (not the default branch!), click **Code → Download ZIP**, unzip it, then `cd` into `software/python/potentiostat` and run `pip install .`.

### Option B — the PyPI version (fine for working on the interface)

```bash
pip install iorodeo-potentiostat
```

This is enough to open the app, create methods and sessions, and work on the interface, but you may not be able to connect to a device.

## 5. Tell OpenVoltam how to run Python

OpenVoltam starts its background process with a Python command, which you set by hand. Open `global_scripts/ov_globals.py` in a text editor and check the settings near the top:

1. `PROC_RUN_FROM` must be set to `PROC_RUN_FROM_PYTHON` (this is the default):
   ```python
   PROC_RUN_FROM = PROC_RUN_FROM_PYTHON
   #PROC_RUN_FROM = PROC_RUN_FROM_EXE
   ```
2. Exactly one `PROC_PYTHON_CMD` line must be uncommented, and it must be the command that runs Python on your computer. If you are using an activated virtual environment, `'python'` works on every operating system:
   ```python
   #PROC_PYTHON_CMD = 'py'
   PROC_PYTHON_CMD = 'python'
   ```
3. Save the file.

> ⚠️ The default is `'py'`, which only exists on Windows. If it's wrong for your system, **the app still opens, but saving, opening, and exporting files will not work.**
>
> Please don't include your local edits to `ov_globals.py` in a pull request unless the change is intentional.

## 6. Launch OpenVoltam

Every time:

1. Open a terminal in **the main OpenVoltam folder**. This matters: OpenVoltam finds its icons and its background process using paths relative to this folder.
2. Activate the virtual environment (step 2).
3. Run:
   ```bash
   python -m OpenVoltam
   ```

You should see a splash screen and then the welcome window.

## Troubleshooting

| Problem | Likely cause |
|---|---|
| `ModuleNotFoundError: No module named 'PyQt6'` (or another package) | The virtual environment isn't active, or step 3 wasn't run inside it. |
| `ModuleNotFoundError: No module named 'potentiostat'` | Step 4 was skipped or run in a different environment. |
| `ModuleNotFoundError: No module named 'global_scripts'` | You launched from a folder other than the main OpenVoltam folder. |
| The app opens but saving/opening a session does nothing or shows an error | `PROC_PYTHON_CMD` in `ov_globals.py` is wrong for your system (step 5). |
| Icons are missing | You launched from a folder other than the main OpenVoltam folder. |
| The interface is in Spanish | The language is stored in `external/settings.txt`. Change it in the settings window (⚙ on the welcome screen). |
| On Linux, Qt errors about the `xcb` platform plugin | Install your distribution's Qt/X11 libraries (for example `libxkbcommon-x11-0` and `libxcb-cursor0` on Debian/Ubuntu). |

Still stuck? [Open an issue](https://github.com/ask53/openVoltam/issues/new/choose) — problems with the setup instructions count as bugs too.
