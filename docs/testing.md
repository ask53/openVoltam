# Testing OpenVoltam

OpenVoltam does **not have automated tests yet** (adding some would be a very welcome contribution — see [Ideas for automated tests](#ideas-for-automated-tests)). For now, testing means checking things by hand. This page describes how, from a 30-second check to a full test with a device.

Before you start, set up OpenVoltam as described in [running-from-source.md](running-from-source.md). Run every command below from **the main OpenVoltam folder**, with your virtual environment activated.

## Levels of testing

| Level | Needs a device? | Time | When |
|---|---|---|---|
| [1. Launch check](#1-launch-check) | No | 1 min | Every change |
| [2. Background process check](#2-background-process-check) | No | 2 min | Changes to `process.py`, `ov_functions.py`, or file formats |
| [3. Interface walkthrough](#3-interface-walkthrough-no-device) | No | 15 min | Changes to any window, plot, or translation |
| [4. Device test](#4-device-test) | Yes | 30 min+ | Changes to runs, `process.py`, devices, or before a release |

## 1. Launch check

```bash
python -m OpenVoltam
```

✅ The splash screen appears, then the welcome window, with no error ("Traceback") in the terminal.

Keep the terminal visible while testing: OpenVoltam prints errors and debugging messages there, and they are the most useful part of a bug report.

## 2. Background process check

Saving, reading, exporting, and device runs all go through `processes/process.py` (see [project-structure.md](project-structure.md#the-background-process)). You can test it on its own, without the interface:

```bash
# write a minimal lab-session file
python processes/process.py overwrite test-session.ovs "{'session_name': 'test', 'samples': [], 'methods': [], 'runs': [], 'calculations': []}"

# read it back
python processes/process.py read test-session.ovs
```

✅ The first command prints the file path and the second prints the dictionary back. Nothing is printed to standard error.

If this works but saving from the interface doesn't, the problem is almost always `PROC_PYTHON_CMD` in `global_scripts/ov_globals.py` (see [running-from-source.md, step 5](running-from-source.md#5-tell-openvoltam-how-to-run-python)).

Delete `test-session.ovs` when you're done.

## 3. Interface walkthrough (no device)

Work through this checklist to exercise most of the app without a device. Use a scratch folder **outside the repository** for the files you create, so they don't end up in a commit.

**Welcome window and settings**
- [ ] Open settings (⚙) and switch the language to Español and back to English. All visible text changes.
- [ ] Close and reopen the app. The language you chose is remembered.

**Methods**
- [ ] **New method**: add a few steps (constant voltage, ramp, and a relay step if available), move them up and down, and delete one. The method plot updates.
- [ ] Save the method as a `.ovm` file. Close it, then **Open method** and check that everything was saved.

**Lab session**
- [ ] **New session**: give it a name and save it as a `.ovs` file. The main window opens.
- [ ] **Sample → New sample**: fill in the details and save. **Edit sample info** and **Delete sample** work.
- [ ] **Run → New run**: choose your method and open the run configuration. (Starting the run needs a device. Without one, check that you get a clear message rather than a crash.)
- [ ] Close the session and reopen it with **Open session**. Everything is still there.

**If you have a session file with real data** (ask the maintainers for one if you don't):
- [ ] **Analysis → Graph**, **Analyze**, **Calculate**, and **Results** open and work.
- [ ] **Run → Export** creates a CSV file containing the expected data.

**Across all windows**
- [ ] No tracebacks in the terminal.
- [ ] Repeat a few steps in Español to check for missing translations.

You don't need to do every step for every change: focus on the parts of the app your change touches, plus the launch check.

## 4. Device test

You need a RodeoStat (or RodeoStat HC) connected by USB, and the `develop` version of the potentiostat library ([Option A](running-from-source.md#option-a--the-version-openvoltam-uses-needed-to-run-tests-on-a-real-device)).

- [ ] Plug in the device, start OpenVoltam, and open (or create) a session with a sample.
- [ ] **Run → New run**: choose a method and start it. The device is found, live data appears in the run window, and the run finishes.
- [ ] The run appears in the main window, and its data survives closing and reopening the session.
- [ ] If your method uses relays, check that they switch at the right steps.
- [ ] Analyze the run and export it.
- [ ] Unplug the device in the middle of a run. OpenVoltam should show an error rather than freeze or crash.

When you report results, include the device model, operating system, and potentiostat library version (`pip show iorodeo-potentiostat`).

## Testing the Windows installer

Testers without Python can help by installing a [test release](../README.md#download-windows) and working through sections 3 and 4 above. Please [report what you find](../CONTRIBUTING.md#reporting-bugs), including things that worked.

## Testing someone else's pull request

```bash
git fetch origin pull/<PR number>/head:pr-<PR number>
git checkout pr-<PR number>
python -m OpenVoltam
```

Then run the levels of testing that fit the change, and comment on the pull request with what you tested and on which operating system.

## Ideas for automated tests

Good places to start, because they don't need the interface or a device:

- `global_scripts/ov_functions.py` — reading and writing files, unit conversions, rounding.
- `processes/process.py` — the `save` operations (adding, editing, and deleting samples, runs, and calculations) on a sample `.ovs` file.
- `embeds/stdAddFitter.py` — the standard-addition calculation, checked against known values.

If you'd like to set up `pytest` for the project, please open an issue first to discuss it with the maintainers.
