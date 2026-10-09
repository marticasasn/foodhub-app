# Food Hub Bot

A Windows desktop app with its own GUI that automates booking tickets for the USU Food Hub at the University of Sydney.

It finds the next available time slot of the day, waits until tickets open, and fills in the booking form through browser automation.

## Why

Food Hub tickets are released on Humanitix two hours before each session and run out within moments. Booking manually means watching the clock, refreshing the page and filling the same form every day. This project turns that routine into a single click.

## How it works

1. Reads today's slots from the event page and picks the next one that has not opened yet.
2. Sleeps until a few seconds before that slot's release time.
3. Reloads the ticket page until the "+1" button becomes active.
4. Fills in the buyer form, answers the ticket questions and submits the booking.
5. Reports every step in the GUI log. If the final page is not the confirmation page, it saves a screenshot (`resultado.png`).

## Stack

- **Python 3.10+**
- **Tkinter** for the GUI (custom dark theme, styled inputs and dropdowns, live log)
- **Camoufox**, a Playwright-based Firefox build, for browser automation
- **asyncio** + a background thread so the GUI stays responsive while the bot runs

## Installation

Requirements: Windows 10/11 and [Python 3.10+](https://www.python.org/downloads/) with "Add Python to PATH" enabled.

**Option A: installer script**

Double-click `setup.bat`. It installs the dependencies and downloads the Camoufox browser (about 200 MB, first time only).

**Option B: manual**

```bash
pip install -r requirements.txt
python -m camoufox fetch
```

## Usage

1. Launch the app by double-clicking `run.vbs` (opens the GUI without a console window), or run `python app.py`.
2. Fill in your details the first time. They are saved locally to `config.json`.
3. Click **Ejecutar Bot**.

A Firefox window will open. Keep it open and the PC online while the bot runs.

The bot can also run without the GUI once `config.json` exists:

```bash
python bot.py
```

### Notes

- Runs Monday to Friday. Sessions go from 10:00 to 14:30, so tickets open between 8:00 and 12:30.
- The event URL changes each semester. Set it with the `event_url` key in `config.json` (created on first run with the current default). If the key is missing, the default in `bot.py` is used.
- The GUI and log messages are in Spanish.

## Screenshots

<!-- TODO: add a screenshot of the GUI and/or a short GIF of a booking run -->

_Coming soon._

## Project structure

```
foodhub-app/
├── app.py            # Tkinter GUI: form, settings persistence, log, bot thread
├── bot.py            # Booking logic (slot detection, waiting, form filling)
├── requirements.txt  # Python dependencies
├── setup.bat         # One-time installer for dependencies and browser
├── run.vbs           # Launcher without a console window
└── config.json       # Your details and event URL (created on first run, git-ignored)
```

## Disclaimer

This project is a personal and educational experiment in browser automation. It is not affiliated with or endorsed by the USU, the University of Sydney or Humanitix.

Anyone using it is responsible for complying with the terms of service of the platforms involved. The author does not encourage using it in ways that give an unfair advantage over other students or that break those terms.
