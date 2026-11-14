# Project structure

A map of the repository to help new contributors find their way around.

OpenVoltam is a desktop application written in Python with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the interface and [matplotlib](https://matplotlib.org/) for plots. It talks to the potentiostat through IO Rodeo's [`potentiostat`](https://github.com/iorodeo/potentiostat) library.

## Folders and files

```
openVoltam/
├── OpenVoltam.py          Entry point: splash screen, styles, opens the welcome window
├── OpenVoltam.spec        PyInstaller recipe for the main Windows executable
├── requirements.txt       Python dependencies (except the potentiostat library)
│
├── wins/                  One file per window
│   ├── welcome.py         First window: new/open session, new/open method, settings
│   ├── main.py            Main lab-session window: samples, runs, analysis, export
│   ├── sample.py          Create/edit a sample's details
│   ├── method.py          Create/edit a method (steps, ramps, relays)
│   ├── runConfig.py       Configure a run before starting it
│   ├── runView.py         Live view while a run is in progress
│   ├── resultsView.py     View results
│   ├── analyze.py         Step through voltammograms and analyze each one
│   ├── calculate.py       Back-calculate sample concentration (standard addition)
│   ├── settings.py        Settings window (language)
│   └── _TEMPLATE_WIN.py   Starting point for a new window
│
├── embeds/                Plots and widgets embedded inside windows
│   ├── methodPlot.py      Preview of a method's voltage profile
│   ├── runPlots.py        Plots of run data
│   ├── voltamOGram.py     Interactive voltammogram used for analysis
│   └── stdAddFitter.py    Standard-addition fit plot
│
├── processes/
│   ├── process.py         Background process: file save/read/overwrite/export and device runs
│   └── process.spec       PyInstaller recipe for process.exe
│
├── global_scripts/
│   ├── ov_globals.py      Constants and global settings (including how to launch the background process)
│   ├── ov_lang.py         All interface text, in English ('eng') and Spanish ('esp')
│   └── ov_functions.py    Helper functions shared across windows
│
├── devices/
│   └── supportedDevices.py  Supported potentiostats and their limits (RodeoStat, RodeoStat HC)
│
└── external/              Files bundled with the app
    ├── icons/             Images used in the interface
    ├── styles/styles.css  Qt stylesheet for the whole app
    └── settings.txt       User settings saved by the app (currently just the language)
```

## How the pieces fit together

```
            ┌──────────────┐
            │ OpenVoltam.py│
            └──────┬───────┘
                   ▼
            ┌──────────────┐        ┌──────────────┐
            │   welcome    │───────▶│    method    │  (.ovm files)
            └──────┬───────┘        └──────────────┘
                   ▼
            ┌──────────────┐
            │     main     │  lab session (.ovs file)
            └──────┬───────┘
     ┌──────┬──────┼────────┬──────────┬───────────┐
     ▼      ▼      ▼        ▼          ▼           ▼
  sample runConfig runView resultsView analyze  calculate
                   │
                   ▼  (QProcess, command-line arguments)
            ┌──────────────┐        ┌──────────────┐
            │  process.py  │───────▶│  RodeoStat   │ (USB serial)
            └──────────────┘        └──────────────┘
```

### The background process

Slow or risky work — device runs, exports, and most saving and reading of session and method files — is not done inside the windows. Instead, they start `processes/process.py` as a separate process using Qt's `QProcess`, passing instructions as command-line arguments (a few quick reads and writes, such as the settings file, are still done directly with the helpers in `ov_functions.py`):

```
process.py <type> <arguments...>
```

where `<type>` is one of `save`, `overwrite`, `read`, `export`, or `run`. The process sends results back by printing them to standard output, and errors to standard error. This keeps the interface responsive during slow operations and long device runs.

How the process is launched is controlled in `global_scripts/ov_globals.py`:

- `PROC_RUN_FROM = PROC_RUN_FROM_PYTHON` runs `PROC_PYTHON_CMD processes/process.py ...`. Use this when running from source.
- `PROC_RUN_FROM = PROC_RUN_FROM_EXE` runs `external/process.exe ...`. Use this for the Windows build (see [building-windows.md](building-windows.md)).

Both paths are relative, which is why OpenVoltam has to be launched from the main OpenVoltam folder.

### Data files

| Extension | Contents |
|---|---|
| `.ovm` | A method: device settings and the list of steps to run |
| `.ovs` | A lab session: samples, methods used, runs and their data, and calculations |

Both are text files in [Tabular-JSON](https://pypi.org/project/tabularjson/) format (JSON, with large data arrays written as compact tables), read and written by `get_data_from_file()` and `write_data_to_file()` in `ov_functions.py`. See the unit conversion comments in `ov_globals.py` for the units values are stored in.

### Translations

Every piece of interface text lives in `global_scripts/ov_lang.py` as a dictionary with one entry per language:

```python
SET_LANG = {'eng': 'Language',
            'esp': 'Idioma'}
```

Each window has a `set_text(lang)` method that applies the text for the current language. When adding new text to a window, add it to `ov_lang.py` in **both** languages.
