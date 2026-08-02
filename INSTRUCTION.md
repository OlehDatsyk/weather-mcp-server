# INSTRUCTION.md - Complete Beginner's Guide

Welcome! This guide walks you through running **weather-mcp-server** from a
completely empty computer, assuming you have **never** used Python, Git,
Visual Studio Code, virtual environments, a terminal, or an API before.
Follow the sections in order. Nothing is assumed.

> ⏱️ **Estimated time for first-time setup:** 30-45 minutes.

---

## Table of Contents

1. [What This Project Does](#1-what-this-project-does)
2. [Installing Python](#2-installing-python)
3. [Installing Git](#3-installing-git)
4. [Installing Visual Studio Code](#4-installing-visual-studio-code)
5. [Required VS Code Extensions](#5-required-vs-code-extensions)
6. [Opening the Project](#6-opening-the-project)
7. [Creating a Virtual Environment](#7-creating-a-virtual-environment)
8. [Activating the Virtual Environment](#8-activating-the-virtual-environment)
9. [Installing Dependencies](#9-installing-dependencies)
10. [Creating Your .env File](#10-creating-your-env-file)
11. [Getting an OpenWeatherMap API Key](#11-getting-an-openweathermap-api-key)
12. [Running the Application](#12-running-the-application)
13. [Testing the Application](#13-testing-the-application)
14. [Using Every Feature](#14-using-every-feature)
15. [Connecting to Claude Desktop](#15-connecting-to-claude-desktop)
16. [Troubleshooting](#16-troubleshooting)
17. [FAQ](#17-faq)
18. [Common Mistakes](#18-common-mistakes)
19. [Security Recommendations](#19-security-recommendations)
20. [Next Learning Steps](#20-next-learning-steps)

---

## 1. What This Project Does

`weather-mcp-server` is a small program that answers weather questions
(current conditions, forecasts, air quality, alerts) and speaks a standard
called **MCP (Model Context Protocol)**. That means AI apps like Claude
Desktop can "plug into" it and ask it weather questions on your behalf.

You do not need to understand MCP deeply to run this project - just follow
the steps below.

---

## 2. Installing Python

Python is the programming language this project is written in.

1. Go to **https://www.python.org/downloads/**
2. Click the yellow "Download Python 3.12.x" button (this project needs
   **Python 3.12 or newer**).
3. Run the installer.
   - **Windows:** On the very first installer screen, tick the box that
     says **"Add python.exe to PATH"** before clicking Install. This step
     is easy to miss and causes most beginner problems.
   - **macOS:** Run the `.pkg` installer and click through the prompts.
4. Verify the install. Open a terminal (see box below) and type:
   ```
   python --version
   ```
   On macOS you may need `python3 --version` instead. You should see
   something like `Python 3.12.4`.

> **What is a terminal?** It's a text-based way to give your computer
> commands. On Windows, search the Start Menu for **"Terminal"** or
> **"Command Prompt"**. On macOS, open **Spotlight** (Cmd+Space) and type
> **"Terminal"**.

---

## 3. Installing Git

Git is a tool for downloading and tracking changes to code. You may not
strictly need it if you already have the project folder, but it's used
throughout the developer ecosystem, so it's worth installing.

1. Go to **https://git-scm.com/downloads**
2. Download the installer for your operating system.
3. Run it, accepting the default options (the defaults are fine for
   beginners).
4. Verify the install:
   ```
   git --version
   ```

---

## 4. Installing Visual Studio Code

Visual Studio Code (VS Code) is the free code editor we'll use to open and
run this project.

1. Go to **https://code.visualstudio.com/**
2. Download and run the installer for your operating system.
3. Accept the defaults during installation.

---

## 5. Required VS Code Extensions

This project already includes a recommended-extensions list at
`.vscode/extensions.json`. When you open the project folder in VS Code for
the first time, a notification should pop up in the bottom-right corner
offering to install them. Click **Install All**.

If you don't see the notification, install these manually via the
Extensions icon on the left sidebar (the icon that looks like four
squares):

- **Python** (by Microsoft) - core Python support
- **Pylance** (by Microsoft) - smart autocomplete and type checking
- **Python Debugger** (by Microsoft) - lets you run/debug with breakpoints
- **Ruff** (by Charlie Marsh) - code linting/formatting

---

## 6. Opening the Project

1. Extract the project folder somewhere easy to find, e.g. your Desktop.
2. Open VS Code.
3. Go to **File -> Open Folder…** and select the `weather-mcp-server`
   folder (the one containing `server.py`).
4. VS Code will open with the file list on the left.

---

## 7. Creating a Virtual Environment

A **virtual environment** ("venv") is an isolated Python installation just
for this project, so its dependencies don't clash with anything else on
your computer. Always use one.

Open a terminal **inside VS Code**: **Terminal -> New Terminal** (top menu).
Then run:

**Windows:**

```
python -m venv .venv
```

**macOS:**

```
python3 -m venv .venv
```

This creates a new `.venv` folder inside the project. It only needs to be
done once.

---

## 8. Activating the Virtual Environment

Every time you work on this project in a new terminal window, activate the
virtual environment first.

**Windows (Command Prompt):**

```
.venv\Scripts\activate
```

**Windows (PowerShell):**

```
.venv\Scripts\Activate.ps1
```

> If PowerShell blocks this with a "running scripts is disabled" error, run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again.

**macOS / Linux:**

```
source .venv/bin/activate
```

You'll know it worked when you see `(.venv)` at the start of your terminal
prompt.

---

## 9. Installing Dependencies

With the virtual environment active, install everything the project needs:

```
pip install -r requirements.txt
```

This reads `requirements.txt` and downloads all required packages
(FastMCP, HTTPX, Pydantic, Loguru, Pytest, etc.). It may take a minute.

---

## 10. Creating Your .env File

The `.env` file stores your personal configuration (like your API key) and
is never shared or uploaded to GitHub.

1. In the project root, create a new file named exactly `.env`.
2. Copy the structure below into it and fill in your own API key (see next
   section):

```
OPENWEATHER_API_KEY=your_api_key_here
OPENWEATHER_BASE_URL=https://api.openweathermap.org
DEFAULT_UNITS=metric
DEFAULT_LANG=en
REQUEST_TIMEOUT_SECONDS=10
MAX_RETRIES=3
LOG_LEVEL=INFO
LOG_DIR=logs
MCP_SERVER_NAME=weather-mcp-server
```

> **Note:** This project currently ships with an example `.env.example`
> template recommended in `PROJECT_REVIEW.md`. If one exists in your copy of
> the project, you can instead just duplicate it and rename the copy to
> `.env`.

---

## 11. Getting an OpenWeatherMap API Key

The server fetches real weather data from OpenWeatherMap, which requires a
free API key.

1. Go to **https://home.openweathermap.org/users/sign_up**
2. Create a free account and confirm your email.
3. Go to the **"API keys"** tab of your account.
4. Copy the key shown there.
5. Paste it into your `.env` file as the value of `OPENWEATHER_API_KEY`.

> New keys can take up to a couple of hours to activate. If you get an
> "invalid API key" error right after signing up, wait a bit and try again.

---

## 12. Running the Application

With your virtual environment activated and `.env` configured, start the
server:

```
python server.py
```

You should see colorful log lines in the terminal confirming the server
started, something like:

```
INFO | Starting 'weather-mcp-server' (API key configured: True)
```

Press `Ctrl+C` to stop the server.

---

## 13. Testing the Application

This project includes an automated test suite. To run it:

```
pytest
```

You should see a series of green dots/`PASSED` lines and a summary at the
end like `XX passed`. This confirms the code is working correctly on your
machine without needing a real API key (tests use mocked responses).

---

## 14. Using Every Feature

The server exposes these MCP **tools** (actions an AI client can invoke):

| Tool                   | What it does                           |
| ---------------------- | -------------------------------------- |
| `get_current_weather`  | Current conditions for a city          |
| `get_weather_forecast` | 1-5 day forecast (3-hour steps)        |
| `compare_cities`       | Compare 2-10 cities side by side       |
| `get_air_quality`      | Air Quality Index and pollutant levels |
| `get_weather_alerts`   | Active official weather warnings       |

It also exposes three **resources** (reference data): a curated city list,
supported unit systems, and API metadata - and three **prompts**
(ready-made conversation starters): `weather_summary`,
`travel_recommendation`, and `clothing_recommendation`.

The easiest way to try these is via the **MCP Inspector**, a browser-based
testing tool:

```
npx @modelcontextprotocol/inspector python server.py
```

(This requires Node.js - see the FAQ if you don't have it.) It opens a web
page where you can call each tool with test inputs and see the JSON result.

---

## 15. Connecting to Claude Desktop

To use this server directly from Claude Desktop:

1. Open Claude Desktop's settings and find the MCP server configuration
   file (see Anthropic's official docs, since exact steps vary by version
   and OS).
2. Add an entry pointing to this project's `server.py`, using the **full,
   absolute path** to your project's Python interpreter
   (`.venv/bin/python` on macOS, `.venv\Scripts\python.exe` on Windows) and
   to `server.py`.
3. Restart Claude Desktop. The weather tools should now appear as
   available capabilities in a new conversation.

---

## 16. Troubleshooting

**"python is not recognized as an internal or external command" (Windows)**
Python wasn't added to PATH during install. Reinstall Python and tick
"Add python.exe to PATH", or search "Environment Variables" in the Start
Menu and add your Python install folder manually.

**"No module named fastmcp" (or similar)**
Your virtual environment isn't activated, or dependencies weren't
installed. Repeat steps 8 and 9.

**"Invalid or unauthorized API key"**
Double-check you copied the key correctly into `.env` with no extra
spaces, and that the key has finished activating (can take up to ~2 hours
after signup).

**Server starts but tools return errors about a missing API key**
Confirm `.env` is in the project root (same folder as `server.py`), spelled
exactly `.env`, and that `OPENWEATHER_API_KEY` is set.

**PowerShell won't let me activate the virtual environment**
Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once in
PowerShell, then retry.

**Tests fail immediately with import errors**
Make sure you're running `pytest` from the project root with the virtual
environment activated.

---

## 17. FAQ

**Do I need to pay for anything?**
No. OpenWeatherMap's free tier and everything else used here is free.

**Do I need to know how to code to use this?**
No - following this guide to run the server is enough. Reading the code is
only necessary if you want to modify it.

**What's the difference between `python` and `python3`?**
On some systems (mostly macOS/Linux), `python` isn't linked to Python 3 by
default, so `python3` is used instead. Windows installs usually only need
`python`.

**Can I change the temperature units?**
Yes - set `DEFAULT_UNITS` in `.env` to `metric`, `imperial`, or `standard`,
or pass `units` directly when calling a tool.

**Why did my weather alerts come back empty?**
The alerts endpoint requires a paid OpenWeatherMap "One Call API 3.0"
subscription on some accounts. The server handles this gracefully and
explains this in its response rather than failing.

---

## 18. Common Mistakes

- Forgetting to activate the virtual environment before installing
  dependencies or running the server (you'll install packages globally
  instead, or see "module not found" errors).
- Committing/uploading the `.env` file to GitHub - it contains your
  private API key.
- Editing `.env.example` (a template) instead of your actual `.env` file.
- Running `python server.py` from the wrong folder - always run it from
  the project root.
- Using an API key immediately after creating it, before it has activated.

---

## 19. Security Recommendations

- **Never** share your `.env` file, commit it to Git, or paste its
  contents into chat, forums, or screenshots.
- If you ever suspect your API key has leaked, regenerate/delete it from
  your OpenWeatherMap account immediately and update `.env` with a fresh
  one.
- Keep `.env` listed in `.gitignore` (it already is in this project) so it
  is never accidentally uploaded.
- Don't hardcode API keys directly into `.py` files - always load them
  from environment variables, as this project already does via
  `config.py`.

---

## 20. Next Learning Steps

Once you're comfortable running this project, consider:

- Reading `docs/architecture.md` to understand how the code is layered.
- Reading `docs/mcp-primer.md` to learn more about the Model Context
  Protocol itself.
- Trying to add a new tool (e.g. a "weather history" tool) by following
  the existing patterns in `tools.py` and `weather_service.py`.
- Learning the basics of Git (`git init`, `git add`, `git commit`) so you
  can track your own changes.
- Exploring FastMCP's own documentation to learn about other MCP
  primitives and transports.
