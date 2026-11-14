# OpenVoltam

> **Status: in progress (beta).** Use at your own risk. Bugs are expected — please [report them](#reporting-bugs)!

OpenVoltam is free, open source desktop software for **running voltammetric tests and analyzing their results**. It is designed to work with the [RodeoStat potentiostat from IO Rodeo](https://iorodeo.com/pages/rodeostat).

It is an open source project by [Caminos de Agua](https://www.caminosdeagua.org) and [IO Rodeo](https://www.iorodeo.com). We believe that everyone on this planet should have access to the tools to understand what is in the water that they drink. This software is our teeny, tiny contribution.

## Contents

- [What it does](#what-it-does)
- [Download (Windows)](#download-windows)
- [Run from source (any OS)](#run-from-source-any-os)
- [Documentation](#documentation)
- [Reporting bugs](#reporting-bugs)
- [Contributing](#contributing)
- [License](#license)

## What it does

With OpenVoltam you can:

- **Create methods** (`.ovm` files) — the sequence of voltage steps, ramps, and relay actions to send to the potentiostat.
- **Run lab sessions** (`.ovs` files) — record samples, run methods on them with a connected RodeoStat, and collect the data.
- **Analyze** the resulting voltammograms (peaks, baselines, slopes, areas).
- **Calculate** concentrations using standard addition.
- **Export** data to CSV.

The interface is available in **English** and **Spanish** (change it in the settings window ⚙).

## Download (Windows)

Installers are available for **Windows 10 and 11**.

| Version | Released | Purpose |
|---|---|---|
| [0.2](https://drive.google.com/file/d/1FdVPavv_b1hBFR1BqmzhgKYj29sY_EzB/view?usp=sharing) | 06 Sep 2026 | Beta testing |
| [0.1](https://drive.google.com/file/d/1nNlRlT18m9fjE4lZMUhPBckaFG3FSlIe/view?usp=sharing) | 28 Apr 2026 | Alpha testing |

**Stable release:** we are still working on the features for our first stable release (and finding safe new homes for the many bugs we meet along the way). We aim to have it out by the middle of 2027.

## Run from source (any OS)

OpenVoltam should run on any operating system with **Python 3.12 or newer** and USB ports (we haven't tested them all, so there may be bugs). Quick version for people comfortable with Python:

```bash
git clone https://github.com/ask53/openVoltam.git
cd openVoltam
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install iorodeo-potentiostat  # or the 'develop' version — see the guide
```

Then open `global_scripts/ov_globals.py` and set `PROC_PYTHON_CMD` to the command that runs Python on your system (`'py'` on most Windows 11 machines, `'python'` inside an activated virtual environment), and launch **from the main OpenVoltam folder**:

```bash
python -m OpenVoltam
```

👉 Full step-by-step instructions, including which version of the potentiostat library to use: **[docs/running-from-source.md](docs/running-from-source.md)**

## Documentation

| Document | For |
|---|---|
| [Running from source](docs/running-from-source.md) | Anyone running OpenVoltam with Python instead of the installer |
| [Testing](docs/testing.md) | Checking that OpenVoltam (or your change) works, with or without a device |
| [Project structure](docs/project-structure.md) | Understanding how the code is organized |
| [Building the Windows installer](docs/building-windows.md) | Maintainers making a release |
| [Contributing guide](CONTRIBUTING.md) | Anyone who wants to help |

## Reporting bugs

Found a bug? Thank you — please tell us!

1. Check the [existing issues](https://github.com/ask53/openVoltam/issues) to see if it has already been reported.
2. If not, [open a new issue](https://github.com/ask53/openVoltam/issues/new/choose) and choose **Bug report**. The form asks for the details we need: OpenVoltam version, operating system, how you run it (installer or Python), device, steps to reproduce, and any error messages.

Bug reports in English or Spanish are both welcome. See the [contributing guide](CONTRIBUTING.md#reporting-bugs) for tips on writing a useful report.

## Contributing

Contributions of all kinds are welcome: bug reports, testing on new operating systems, translations, documentation, and code. Start with **[CONTRIBUTING.md](CONTRIBUTING.md)**.

## License

OpenVoltam is licensed under the [GNU General Public License version 3.0](LICENSE). We chose this license for two main reasons:

1. To protect us from the situation in which a large corporation takes the software, copyrights it, and then sues us for distributing it for free; and
2. To keep it open source, accessible, modifiable, and sharable.
