# INSTRUCTION.md - Complete Beginner's Guide to Running `weather-mcp-server`

Welcome! This guide assumes **you have never used Python, Visual Studio
Code, or the Model Context Protocol (MCP) before**. Every step is written
out in full - nothing is assumed, nothing is skipped. Follow the sections
in order and you will go from "empty computer" to "running MCP server with
a connected AI client" by the end.

> ⏱️ **Estimated time:** 30-60 minutes for a first-time setup.

---

## Table of Contents

1. [Installing Python](#1-installing-python)
2. [Installing Visual Studio Code](#2-installing-visual-studio-code)
3. [Installing Git (Optional)](#3-installing-git-optional)
4. [Installing Required VS Code Extensions](#4-installing-required-vs-code-extensions)
5. [Opening the Project](#5-opening-the-project)
6. [Creating a Virtual Environment](#6-creating-a-virtual-environment)
7. [Activating the Virtual Environment](#7-activating-the-virtual-environment)
8. [Installing Dependencies](#8-installing-dependencies)
9. [Creating the .env File](#9-creating-the-env-file)
10. [Obtaining API Keys](#10-obtaining-api-keys)
11. [Configuring Environment Variables](#11-configuring-environment-variables)
12. [Running the MCP Server](#12-running-the-mcp-server)
13. [Verifying That the Server Started Successfully](#13-verifying-that-the-server-started-successfully)
14. [Connecting the Server to an MCP Client](#14-connecting-the-server-to-an-mcp-client)
15. [Example MCP Client Configuration](#15-example-mcp-client-configuration)
16. [Testing Every Available Tool](#16-testing-every-available-tool)
17. [Testing Every Available Resource](#17-testing-every-available-resource)
18. [Testing Every Available Prompt](#18-testing-every-available-prompt)
19. [Common Errors and How to Fix Them](#19-common-errors-and-how-to-fix-them)
20. [Updating Dependencies](#20-updating-dependencies)
21. [Project Folder Explanation](#21-project-folder-explanation)
22. [Architecture Overview](#22-architecture-overview)
23. [Security Best Practices](#23-security-best-practices)
24. [Frequently Asked Questions (FAQ)](#24-frequently-asked-questions-faq)
25. [Troubleshooting](#25-troubleshooting)
26. [Useful Learning Resources](#26-useful-learning-resources)
27. [Next Learning Steps](#27-next-learning-steps)

---

## 1. Installing Python

Python is the programming language this project is written in. You need
**Python 3.12 or newer**.

### 1.1 Check if Python is already installed

Open a terminal:

- **Windows:** Press `Win`, type `cmd`, press Enter.
- **macOS:** Press `Cmd + Space`, type `Terminal`, press Enter.
- **Linux:** Open your terminal application (varies by distro).

Type:

```bash
python3 --version
```

If you see something like `Python 3.12.4` or higher, you can skip to
[Section 2](#2-installing-visual-studio-code). If you see an error like
`command not found` or a version below `3.12`, continue below.

### 1.2 Install Python

| Operating System | Steps |
|---|---|
| **Windows** | Go to [python.org/downloads](https://www.python.org/downloads/). Click **Download Python 3.12.x**. Run the installer. **⚠️ IMPORTANT:** On the first installer screen, check the box **"Add python.exe to PATH"** before clicking **Install Now**. |
| **macOS** | Option A (recommended): Install [Homebrew](https://brew.sh) first, then run `brew install python@3.12` in Terminal. Option B: Download the macOS installer from [python.org/downloads](https://www.python.org/downloads/) and run it. |
| **Linux (Debian/Ubuntu)** | Run: `sudo apt update && sudo apt install python3.12 python3.12-venv python3-pip` |
| **Linux (Fedora)** | Run: `sudo dnf install python3.12` |

### 1.3 Verify the installation

Close and reopen your terminal, then run:

```bash
python3 --version
```

**Expected output:**

```
Python 3.12.4
```

Also verify `pip` (Python's package installer) is available:

```bash
python3 -m pip --version
```

**Expected output (version numbers may differ):**

```
pip 24.0 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

> 💡 **Windows users:** if `python3` doesn't work, try `python` or `py -3.12`
> instead - Windows installers sometimes register the command differently.

---

## 2. Installing Visual Studio Code

Visual Studio Code (VS Code) is the free code editor we'll use to open,
run, and debug this project.

### 2.1 Download and install

1. Go to [https://code.visualstudio.com/](https://code.visualstudio.com/).
2. Click the big **Download** button (it detects your operating system
   automatically).
3. Run the installer:
   - **Windows:** Double-click the downloaded `.exe` file. Accept the
     defaults, and make sure **"Add to PATH"** is checked.
   - **macOS:** Open the downloaded `.zip`, drag `Visual Studio Code.app`
     into your **Applications** folder.
   - **Linux:** Install the downloaded `.deb` (Debian/Ubuntu) with
     `sudo apt install ./code_*.deb`, or the `.rpm` (Fedora) with
     `sudo dnf install ./code-*.rpm`.

### 2.2 Verify the installation

Open a terminal and run:

```bash
code --version
```

**Expected output (version numbers may differ):**

```
1.90.2
f1e16e1e6214d7c44d078b1f0d10c951da4e8a29
x64
```

If `code` is not recognized, open VS Code manually, press
`Ctrl+Shift+P` (`Cmd+Shift+P` on macOS), type **"Shell Command: Install
'code' command in PATH"**, and press Enter. Restart your terminal.

---

## 3. Installing Git (Optional)

Git is only needed if you plan to **clone this project from GitHub** or
track your own changes with version control. If you already have the
project folder (e.g. downloaded as a `.zip`), you can skip this section.

### 3.1 Install Git

| Operating System | Command / Steps |
|---|---|
| **Windows** | Download from [git-scm.com/download/win](https://git-scm.com/download/win) and run the installer, accepting the defaults. |
| **macOS** | Run `brew install git`, or install [Xcode Command Line Tools](https://developer.apple.com/xcode/) with `xcode-select --install`. |
| **Linux (Debian/Ubuntu)** | `sudo apt install git` |
| **Linux (Fedora)** | `sudo dnf install git` |

### 3.2 Verify the installation

```bash
git --version
```

**Expected output (version numbers may differ):**

```
git version 2.45.1
```

### 3.3 Clone the project (if using Git)

```bash
git clone https://github.com/your-username/weather-mcp-server.git
cd weather-mcp-server
```

If you don't have Git, simply download the project as a `.zip` file and
extract it to a folder on your computer instead.

---

## 4. Installing Required VS Code Extensions

Extensions add Python support, debugging tools, and testing integration to
VS Code.

### 4.1 Required extensions

| Extension | Publisher | Purpose |
|---|---|---|
| **Python** | `ms-python.python` | Core Python language support (IntelliSense, running/debugging code). |
| **Pylance** | `ms-python.vscode-pylance` | Fast, type-aware autocompletion and error checking. |
| **Python Debugger** | `ms-python.debugpy` | Enables the "Run and Debug" (F5) functionality. |

### 4.2 Optional extension

| Extension | Publisher | Purpose |
|---|---|---|
| **Ruff** | `charliermarsh.ruff` | Fast linter/formatter to catch style issues automatically. |

### 4.3 How to install them

1. Open VS Code.
2. Click the **Extensions** icon in the left sidebar (it looks like four
   squares, one detached - or press `Ctrl+Shift+X` / `Cmd+Shift+X`).
3. In the search box, type `Python` and click **Install** on the
   Microsoft extension named **"Python"** (this automatically installs
   Pylance and the Python Debugger as dependencies).
4. Search for `Ruff` and click **Install** (optional but recommended).

> ✅ **Shortcut:** This project already includes a
> `.vscode/extensions.json` file listing these exact extensions. When you
> open the project folder in VS Code for the first time (see
> [Section 5](#5-opening-the-project)), VS Code will automatically show a
> popup: **"This workspace has extension recommendations"** - just click
> **Install All**.

---

## 5. Opening the Project

1. Open VS Code.
2. Go to **File -> Open Folder...** (macOS: **File -> Open...**).
3. Navigate to the `weather-mcp-server` folder (the one containing
   `server.py`, `README.md`, etc.) and select it.
4. Click **Select Folder** (Windows/Linux) or **Open** (macOS).

VS Code will reload with the project folder shown in the **Explorer**
sidebar on the left. You should see files like:

```
weather-mcp-server/
├── server.py
├── config.py
├── weather_service.py
├── tools.py
├── resources.py
├── prompts.py
├── schemas.py
├── logging_config.py
├── requirements.txt
├── README.md
└── ...
```

5. Open the integrated terminal: **Terminal -> New Terminal** (or press
   `` Ctrl+` ``). All commands in this guide are run in this terminal,
   from the project's root folder, unless stated otherwise.

---

## 6. Creating a Virtual Environment

A **virtual environment** ("venv") is an isolated folder containing its
own copy of Python and its own installed packages, separate from your
system-wide Python. This keeps this project's dependencies from
interfering with other Python projects on your computer.

In the VS Code terminal, make sure you're in the project's root folder,
then run:

**macOS / Linux:**

```bash
python3 -m venv .venv
```

**Windows:**

```powershell
py -3.12 -m venv .venv
```

This creates a new hidden folder named `.venv` inside your project. Nothing
will print to the terminal if it succeeds - that's normal. You can confirm
it worked by checking that the folder now exists:

```bash
ls .venv        # macOS / Linux
dir .venv       # Windows
```

**Expected output (folder names may differ slightly by OS):**

```
bin  include  lib  pyvenv.cfg
```

---

## 7. Activating the Virtual Environment

"Activating" the virtual environment tells your terminal to use the
Python and packages inside `.venv` instead of your system Python.

| Operating System / Shell | Command |
|---|---|
| **macOS / Linux (bash/zsh)** | `source .venv/bin/activate` |
| **Windows (PowerShell)** | `.venv\Scripts\Activate.ps1` |
| **Windows (Command Prompt)** | `.venv\Scripts\activate.bat` |

Run the appropriate command for your system. Once activated, you'll see
`(.venv)` appear at the beginning of your terminal prompt:

```
(.venv) user@machine weather-mcp-server %
```

> ⚠️ **PowerShell "running scripts is disabled" error?** Run this once,
> then try activating again:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

> 💡 **VS Code tip:** After creating `.venv`, VS Code often detects it
> automatically and offers to select it as your interpreter - click
> **Yes**. You can also manually select it: press `Ctrl+Shift+P`
> (`Cmd+Shift+P`), type **"Python: Select Interpreter"**, and choose the
> one located at `./.venv/bin/python` (or `.venv\Scripts\python.exe` on
> Windows). New terminals you open afterward will auto-activate it.

**You must activate the virtual environment every time you open a new
terminal to work on this project.**

---

## 8. Installing Dependencies

With the virtual environment activated, install all required Python
packages listed in `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs (among others): `fastmcp`, `httpx`, `python-dotenv`,
`pydantic`, `pydantic-settings`, `loguru`, `pytest`, and testing tools.

**Expected output (abbreviated):**

```
Collecting fastmcp>=2.3.0
  Downloading fastmcp-2.3.x-py3-none-any.whl (...)
Collecting httpx>=0.27.0
  Downloading httpx-0.27.x-py3-none-any.whl (...)
...
Successfully installed fastmcp-2.3.x httpx-0.27.x pydantic-2.7.x ...
```

### 8.1 Verify the installation

```bash
python -c "import fastmcp, httpx, pydantic, loguru; print('All core dependencies imported successfully!')"
```

**Expected output:**

```
All core dependencies imported successfully!
```

If you see an error instead, revisit [Section 7](#7-activating-the-virtual-environment)
- it's very likely your virtual environment isn't activated.

---

## 9. Creating the .env File

This project reads configuration (like your API key) from a file named
`.env` in the project's root folder. This file is **never committed to
Git** (it's listed in `.gitignore`) because it contains secrets.

A template already exists: `.env.example`. Copy it to create your own
`.env` file:

**macOS / Linux:**

```bash
cp .env.example .env
```

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Windows (Command Prompt):**

```cmd
copy .env.example .env
```

Confirm the file now exists:

```bash
ls -a          # macOS / Linux - look for ".env" in the list
dir /a         # Windows
```

You'll edit this file in [Section 11](#11-configuring-environment-variables).

---

## 10. Obtaining API Keys

This server fetches live weather data from **OpenWeatherMap**, which
requires a free API key.

### 10.1 Sign up

1. Go to
   [https://home.openweathermap.org/users/sign_up](https://home.openweathermap.org/users/sign_up).
2. Fill in the registration form (username, email, password) and submit.
3. Confirm your email address if prompted (check your inbox for a
   verification link).

### 10.2 Generate an API key

1. Log in to [https://home.openweathermap.org/](https://home.openweathermap.org/).
2. Click on your username (top-right) -> **My API keys**, or go directly to
   [https://home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys).
3. A **default** key is usually generated automatically for new accounts.
   You can use it, or click **"Generate"** to create a new one with a
   custom name (e.g. `weather-mcp-server`).
4. **Copy the key** - it looks like a long string of letters and numbers,
   for example:

   ```
   a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
   ```

> ⚠️ **New keys take time to activate.** OpenWeatherMap keys are often not
> usable immediately - activation can take anywhere from a few minutes to
> a couple of hours. If your first requests fail with an "Invalid API
> key" error, wait and try again later.

### 10.3 Free tier limits

| Limit | Value |
|---|---|
| Calls per minute | 60 |
| Calls per month | 1,000,000 |
| Forecast resolution | 3-hour steps, up to 5 days |
| Weather alerts (One Call 3.0) | May require separately subscribing to the (still free) "One Call by Call" plan |

---

## 11. Configuring Environment Variables

Open the `.env` file you created in [Section 9](#9-creating-the-env-file)
in VS Code (click it in the Explorer sidebar) and fill it in.

### 11.1 Full list of variables

| Variable | Required? | Default | Description |
|---|:---:|---|---|
| `OPENWEATHER_API_KEY` | ✅ Yes | *(none)* | Your OpenWeatherMap API key from Section 10. |
| `OPENWEATHER_BASE_URL` | No | `https://api.openweathermap.org` | Base URL for the API. Rarely needs to change. |
| `DEFAULT_UNITS` | No | `metric` | `metric` (°C), `imperial` (°F), or `standard` (Kelvin). |
| `DEFAULT_LANG` | No | `en` | Language code for weather descriptions. |
| `REQUEST_TIMEOUT_SECONDS` | No | `10` | HTTP request timeout, in seconds. |
| `MAX_RETRIES` | No | `3` | Retries for transient network failures. |
| `LOG_LEVEL` | No | `INFO` | `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. |
| `LOG_DIR` | No | `logs` | Folder where log files are written. |
| `MCP_SERVER_NAME` | No | `weather-mcp-server` | Name shown to MCP clients. |

### 11.2 Minimal working `.env`

At a minimum, set your API key:

```dotenv
OPENWEATHER_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

Save the file (`Ctrl+S` / `Cmd+S`).

### 11.3 Verify configuration loads correctly

```bash
python -c "from config import settings; print('Server name:', settings.mcp_server_name); print('API key configured:', settings.has_api_key)"
```

**Expected output:**

```
Server name: weather-mcp-server
API key configured: True
```

If `API key configured: False`, double-check your `.env` file was saved
and that you replaced the placeholder text `your_api_key_here` with your
actual key.

---

## 12. Running the MCP Server

MCP servers talk to clients over **stdio** (standard input/output), not a
web browser - so running it directly will look like it "hangs." That is
expected behavior; it means the server is alive and waiting for a client
to connect.

With your virtual environment activated, run:

```bash
python server.py
```

You should see log lines print to your terminal (Loguru writes these to
**stderr**, which still appears in your terminal window):

**Expected output:**

```
2026-07-15 12:00:00.123 | INFO     | server:_run:70 - Starting 'weather-mcp-server' (API key configured: True)
```

Leave this running for now - press `Ctrl+C` when you want to stop it.

> 🐞 **Alternative: run with the debugger.** In VS Code, press `F5` (this
> uses the **"Run Weather MCP Server"** configuration already defined in
> `.vscode/launch.json`). This lets you set breakpoints and inspect
> variables while the server runs.

---

## 13. Verifying That the Server Started Successfully

Use this checklist to confirm everything is working correctly before
connecting a real client.

| Check | Command | Expected Result |
|---|---|---|
| Python version | `python3 --version` | `Python 3.12.x` or newer |
| Virtual env active | Look at terminal prompt | Prefixed with `(.venv)` |
| Dependencies installed | `python -c "import fastmcp"` | No error |
| Config loads | `python -c "from config import settings; print(settings.has_api_key)"` | `True` |
| Server starts | `python server.py` | Logs `Starting 'weather-mcp-server'...` with no traceback |
| Log file created | `ls logs/` (after running the server) | `weather_mcp_server.log` present |
| Tests pass | `pytest` | All tests show `PASSED`, ends in green `passed` summary |

If every row above checks out, your server is fully operational and ready
to connect to a client.

---

## 14. Connecting the Server to an MCP Client

An **MCP client** is the application that actually talks to this server -
for example, Claude Desktop, or a developer tool called the **MCP
Inspector**. The server itself does nothing on its own; it waits for a
client to launch it and send requests.

### 14.1 Option A - MCP Inspector (recommended for beginners)

The MCP Inspector is a browser-based tool purpose-built for testing MCP
servers interactively, without needing a full AI application.

**Prerequisite:** [Node.js](https://nodejs.org/) (version 18 or newer)
must be installed. Check with:

```bash
node --version
```

If not installed, download it from [nodejs.org](https://nodejs.org/)
(choose the "LTS" version) and run the installer.

**Launch the Inspector** (from the project root, with your virtual
environment activated):

```bash
npx @modelcontextprotocol/inspector python server.py
```

The first run downloads the Inspector package - this can take a minute.
Once ready, you'll see:

**Expected output:**

```
🔍 MCP Inspector is up and running at http://localhost:6274 🚀
```

Open that URL in your web browser. You'll see a UI with tabs for
**Tools**, **Resources**, and **Prompts** - this is what we'll use in
Sections 16-18.

### 14.2 Option B - Claude Desktop

See [Section 15](#15-example-mcp-client-configuration) below for the full
configuration.

---

## 15. Example MCP Client Configuration

To connect this server to **Claude Desktop**, you edit its configuration
file directly.

### 15.1 Locate the configuration file

| Operating System | File Path |
|---|---|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

If the file doesn't exist yet, create it.

### 15.2 Find your absolute paths

You need the **full, absolute path** to your virtual environment's Python
executable and to `server.py`. From the project root, with the virtual
environment activated, run:

**macOS / Linux:**

```bash
echo "$(pwd)/.venv/bin/python"
echo "$(pwd)/server.py"
```

**Windows (PowerShell):**

```powershell
echo "$(pwd)\.venv\Scripts\python.exe"
echo "$(pwd)\server.py"
```

Copy the two paths that print out - you'll paste them below.

### 15.3 Example configuration

```json
{
  "mcpServers": {
    "weather": {
      "command": "/Users/yourname/projects/weather-mcp-server/.venv/bin/python",
      "args": [
        "/Users/yourname/projects/weather-mcp-server/server.py"
      ],
      "env": {
        "OPENWEATHER_API_KEY": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
      }
    }
  }
}
```

> On Windows, `"command"` would look like:
> `"C:\\Users\\yourname\\projects\\weather-mcp-server\\.venv\\Scripts\\python.exe"`
> (note the double backslashes required in JSON).

### 15.4 Restart Claude Desktop

Fully quit and reopen Claude Desktop (not just close the window). Start a
new conversation, click the 🔨 tools icon, and confirm you see the five
weather tools listed (`get_current_weather`, `get_weather_forecast`,
`compare_cities`, `get_air_quality`, `get_weather_alerts`).

---

## 16. Testing Every Available Tool

Using the **MCP Inspector** (from [Section 14.1](#141-option-a--mcp-inspector-recommended-for-beginners)),
click the **Tools** tab, select each tool below, fill in the example
arguments, and click **Run Tool**.

| # | Tool Name | Example Arguments | What It Returns |
|---|---|---|---|
| 1 | `get_current_weather` | `{"city": "London", "units": "metric"}` | Current temperature, humidity, wind, and conditions for London. |
| 2 | `get_weather_forecast` | `{"city": "Tokyo", "units": "metric", "days": 3}` | A 3-day, 3-hour-step forecast for Tokyo. |
| 3 | `compare_cities` | `{"cities": ["Paris", "New York", "Sydney"], "units": "metric"}` | Side-by-side comparison, including the warmest/coldest/most humid city. |
| 4 | `get_air_quality` | `{"city": "Cairo"}` | Air Quality Index (1-5) and pollutant concentrations. |
| 5 | `get_weather_alerts` | `{"city": "Miami"}` | Any active official severe-weather alerts. |

### 16.1 Example: testing `get_current_weather`

**Input (in the Inspector's Tools tab):**

```json
{
  "city": "London",
  "units": "metric"
}
```

**Expected output (abbreviated):**

```json
{
  "city": "London",
  "country": "GB",
  "coordinates": { "latitude": 51.5085, "longitude": -0.1257 },
  "temperature": 18.5,
  "feels_like": 18.0,
  "humidity": 60,
  "wind_speed": 3.6,
  "conditions": [
    { "id": 800, "main": "Clear", "description": "clear sky", "icon": "01d" }
  ],
  "units": "metric",
  "source": "OpenWeatherMap"
}
```

### 16.2 Testing an error case on purpose

Try `get_current_weather` with a nonsense city name to see the structured
error format:

**Input:**

```json
{ "city": "Nowhereville12345" }
```

**Expected output:**

```json
{
  "error": true,
  "error_type": "city_not_found",
  "message": "City 'Nowhereville12345' could not be found. Check spelling or try 'City,CountryCode' (e.g. 'Springfield,US').",
  "details": null
}
```

This confirms error handling works correctly - the server never crashes;
it always returns a valid, structured JSON response.

---

## 17. Testing Every Available Resource

Click the **Resources** tab in the MCP Inspector. You should see three
resources listed:

| # | Resource URI | Description |
|---|---|---|
| 1 | `weather://cities/supported` | Curated list of well-known cities. |
| 2 | `weather://units` | Supported unit systems and what they measure. |
| 3 | `weather://api/info` | Metadata about the underlying weather API. |

Click each one, then click **Read Resource**.

### 17.1 Example: reading `weather://units`

**Expected output:**

```json
{
  "default_unit_system": "metric",
  "unit_systems": {
    "metric": {
      "temperature": "Celsius (°C)",
      "wind_speed": "meters per second (m/s)",
      "pressure": "hectopascals (hPa)"
    },
    "imperial": {
      "temperature": "Fahrenheit (°F)",
      "wind_speed": "miles per hour (mph)",
      "pressure": "hectopascals (hPa)"
    },
    "standard": {
      "temperature": "Kelvin (K)",
      "wind_speed": "meters per second (m/s)",
      "pressure": "hectopascals (hPa)"
    }
  }
}
```

### 17.2 Example: reading `weather://api/info`

**Expected output (abbreviated):**

```json
{
  "provider": "OpenWeatherMap",
  "base_url": "https://api.openweathermap.org",
  "api_key_configured": true,
  "endpoints_used": {
    "current_weather": "/data/2.5/weather",
    "forecast": "/data/2.5/forecast",
    "geocoding": "/geo/1.0/direct",
    "air_pollution": "/data/2.5/air_pollution",
    "alerts": "/data/3.0/onecall (alerts field)"
  }
}
```

---

## 18. Testing Every Available Prompt

Click the **Prompts** tab in the MCP Inspector. You should see three
prompts:

| # | Prompt Name | Arguments | Purpose |
|---|---|---|---|
| 1 | `weather_summary` | `city` | Friendly plain-language weather briefing. |
| 2 | `travel_recommendation` | `city`, `days` (optional, default `3`) | Forecast-informed travel planning advice. |
| 3 | `clothing_recommendation` | `city` | What-to-wear advice based on current conditions. |

### 18.1 Example: rendering `weather_summary`

**Input:**

```json
{ "city": "Berlin" }
```

**Expected rendered prompt message (abbreviated):**

```
You are a friendly weather assistant. Use the `get_current_weather` tool
to fetch the latest conditions for 'Berlin', then write a short,
conversational summary (3-5 sentences) covering: the current temperature
and how it feels, general conditions (sunny, rainy, etc.), humidity, and
wind. Keep the tone warm and easy to read, as if giving a quick briefing
to a friend before they start their day.
```

When used inside an actual AI client (like Claude Desktop), selecting this
prompt automatically inserts this instruction into the conversation, and
the model will call the `get_current_weather` tool on its own to fulfill
it.

### 18.2 Example: rendering `travel_recommendation`

**Input:**

```json
{ "city": "Rome", "days": 4 }
```

**Expected output (abbreviated):** a message instructing the model to call
`get_weather_forecast` for a 4-day forecast and `get_weather_alerts`, then
summarize the best/worst days for sightseeing and what to pack.

---

## 19. Common Errors and How to Fix Them

| Error Message | Likely Cause | Fix |
|---|---|---|
| `command not found: python3` | Python isn't installed or not on PATH. | Reinstall Python and check "Add to PATH" ([Section 1](#1-installing-python)). |
| `ModuleNotFoundError: No module named 'fastmcp'` | Virtual environment not activated, or dependencies not installed. | Run the activation command from [Section 7](#7-activating-the-virtual-environment), then `pip install -r requirements.txt`. |
| `{"error_type": "missing_api_key", ...}` | `.env` file missing or `OPENWEATHER_API_KEY` still set to the placeholder. | Re-check [Section 11](#11-configuring-environment-variables). |
| `{"error_type": "upstream_api_error", ...}` (HTTP 401) | API key invalid, or too new to be active yet. | Double-check the key was copied correctly; wait up to a few hours for a brand-new key to activate. |
| `{"error_type": "city_not_found", ...}` | City name misspelled or too ambiguous. | Try `"City,CountryCode"` format, e.g. `"Springfield,US"`. |
| Server appears to "hang" after `python server.py` | This is expected - the server is waiting for a client over stdio. | Use the MCP Inspector or a real client to interact with it, as shown in Section 14. |
| `PermissionError` running the activation script (Windows) | PowerShell's script execution policy blocks it. | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then retry. |
| Claude Desktop doesn't show the weather tools | Config file path is wrong, JSON is invalid, or Claude wasn't fully restarted. | Re-check [Section 15](#15-example-mcp-client-configuration); validate your JSON at [jsonlint.com](https://jsonlint.com/); fully quit and reopen Claude Desktop. |
| `pytest` fails with real network errors | A test's `@respx.mock` decorator was removed or `respx` isn't installed. | Reinstall dependencies with `pip install -r requirements.txt`; don't modify the test files. |
| `ImportError` mentioning Pydantic v1 syntax | An old/incompatible Pydantic version got installed. | Run `pip install --upgrade "pydantic>=2.7.0"`. |

---

## 20. Updating Dependencies

Occasionally you may want to update the project's dependencies to their
latest compatible versions.

### 20.1 Update everything

With the virtual environment activated:

```bash
pip install --upgrade -r requirements.txt
```

### 20.2 Check what's currently installed and outdated

```bash
pip list --outdated
```

**Expected output (example):**

```
Package    Version  Latest   Type
---------- -------- -------- -----
httpx      0.27.0   0.27.2   wheel
pydantic   2.7.0    2.8.0    wheel
```

### 20.3 Update a single package

```bash
pip install --upgrade httpx
```

### 20.4 After updating, always re-run the tests

```bash
pytest
```

This confirms nothing broke as a result of the update.

> 💡 **Tip:** After significant updates, it's good practice to delete and
> recreate your virtual environment from scratch to avoid stale package
> conflicts:
> ```bash
> deactivate
> rm -rf .venv          # Windows: rmdir /s /q .venv
> python3 -m venv .venv
> source .venv/bin/activate
> pip install -r requirements.txt
> ```

---

## 21. Project Folder Explanation

| File / Folder | Purpose |
|---|---|
| `server.py` | The main entry point. Builds the MCP server and starts it. |
| `config.py` | Loads and validates settings from `.env` using Pydantic Settings. |
| `weather_service.py` | Talks to the OpenWeatherMap API; contains all HTTP logic. |
| `tools.py` | Defines the 5 MCP tools (the "actions" the AI can perform). |
| `resources.py` | Defines the 3 MCP resources (read-only reference data). |
| `prompts.py` | Defines the 3 MCP prompts (reusable conversation templates). |
| `schemas.py` | Pydantic data models used for validation and structured output. |
| `logging_config.py` | Sets up Loguru for console and file logging. |
| `requirements.txt` | List of Python packages this project depends on. |
| `.env.example` | Template for environment variables (safe to commit). |
| `.env` | Your actual secrets (API key). **Never commit this file.** |
| `pytest.ini` | Configuration for the test runner. |
| `tests/` | All automated tests. |
| `docs/` | Deeper documentation (architecture, MCP concepts). |
| `.vscode/` | VS Code settings, debug configurations, extension recommendations. |
| `README.md` | Full project documentation. |
| `LICENSE` | The project's MIT license. |

---

## 22. Architecture Overview

This project is organized in layers, so each file has one clear job:

```
MCP Client (Claude Desktop / MCP Inspector)
        │  JSON-RPC over stdio
        ▼
server.py  ->  builds the app, manages startup/shutdown
        │
   ┌────┼────────────┬─────────────┐
   ▼                 ▼             ▼
tools.py       resources.py   prompts.py
   │
   ▼
weather_service.py  ->  talks to OpenWeatherMap via HTTPX
   │
   ▼
schemas.py  ->  Pydantic models (inputs, outputs, errors)
```

**Key idea:** `weather_service.py` knows nothing about MCP, and `tools.py`
knows nothing about raw HTTP - each layer only knows about the layer
directly below it. This makes the code easier to test, debug, and extend.
For a deeper explanation, see [`docs/architecture.md`](docs/architecture.md).

---

## 23. Security Best Practices

- **Never commit your `.env` file.** It's already excluded via
  `.gitignore`, but always double-check before pushing to a public
  repository.
- **Never share your API key** in screenshots, chat messages, or code you
  paste into forums/AI tools.
- **Rotate your key if exposed.** If you accidentally leak your
  OpenWeatherMap key, generate a new one immediately from your
  [API keys dashboard](https://home.openweathermap.org/api_keys) and
  delete the old one.
- **Keep dependencies updated.** Outdated packages can carry known
  vulnerabilities - see [Section 20](#20-updating-dependencies).
- **Use a dedicated key per project.** Avoid reusing the same API key
  across multiple unrelated applications; this limits the blast radius if
  one project is compromised.
- **Review MCP client configs before restarting your AI app.** Only add
  `mcpServers` entries pointing to code you trust and understand, since
  MCP servers can execute arbitrary code on your machine.
- **Don't log secrets.** This project's `logging_config.py` never logs
  the API key itself - keep it that way if you add new log statements.

---

## 24. Frequently Asked Questions (FAQ)

**Q: Do I need to know how to code to use this project?**
A: To simply run and connect it to an AI client, no - this guide covers
every command you need. To modify or extend it, basic Python knowledge
helps.

**Q: Is the OpenWeatherMap API really free?**
A: Yes, the free tier (1,000,000 calls/month) is more than enough for
personal use and testing. See [Section 10.3](#103-free-tier-limits).

**Q: Why does `python server.py` seem to do nothing?**
A: It's working correctly - MCP servers wait silently for a client to
connect over stdio. See [Section 12](#12-running-the-mcp-server).

**Q: Can I use a different weather API instead of OpenWeatherMap?**
A: Yes, but you would need to modify `weather_service.py` to call the new
API's endpoints and adjust the parsing logic. The rest of the project
(tools, resources, prompts, schemas) would not need to change.

**Q: What's the difference between a Tool, a Resource, and a Prompt?**
A: A **Tool** is an action the AI can call (like a function). A
**Resource** is read-only data the AI can fetch (like a webpage). A
**Prompt** is a reusable, fill-in-the-blank instruction template. See
[`docs/mcp-primer.md`](docs/mcp-primer.md) for a full explanation.

**Q: Why do I get an empty list from `get_weather_alerts`?**
A: OpenWeatherMap's alert data comes from the "One Call API 3.0" endpoint,
which may require a separate (still free) subscription on your account.
The server detects this and returns a helpful note instead of crashing.

**Q: Can I run the tests without an API key?**
A: Yes - all tests use `respx` to simulate API responses offline. No key
or internet connection is required to run `pytest`.

**Q: How do I stop the server?**
A: Press `Ctrl+C` in the terminal where it's running.

**Q: Can multiple AI clients use this server at once?**
A: Each client typically launches its own instance of the server process,
so yes - each connection gets its own isolated server instance.

---

## 25. Troubleshooting

Follow this decision tree if something isn't working:

```
Is `python3 --version` showing 3.12+?
 ├─ No  -> Reinstall Python (Section 1), reboot terminal, try again.
 └─ Yes -> Continue.

Does your terminal prompt show "(.venv)"?
 ├─ No  -> Activate the virtual environment (Section 7).
 └─ Yes -> Continue.

Does `python -c "import fastmcp"` succeed with no error?
 ├─ No  -> Run `pip install -r requirements.txt` again.
 └─ Yes -> Continue.

Does `python -c "from config import settings; print(settings.has_api_key)"` print True?
 ├─ No  -> Re-check your .env file (Section 11).
 └─ Yes -> Continue.

Does `pytest` pass?
 ├─ No  -> Read the failure message carefully; check Section 19.
 └─ Yes -> Continue.

Does `python server.py` print a "Starting..." log line with no traceback?
 ├─ No  -> Copy the full error text and check Section 19 / search it online.
 └─ Yes -> Your server is healthy! Proceed to connect a client (Section 14).
```

If you're still stuck, gather the following before asking for help:

1. The exact command you ran.
2. The full error message (copy the entire terminal output).
3. Your operating system and Python version (`python3 --version`).
4. Whether your virtual environment was activated at the time.

---

## 26. Useful Learning Resources

| Topic | Resource |
|---|---|
| Python basics | [docs.python.org/3/tutorial](https://docs.python.org/3/tutorial/) |
| Visual Studio Code basics | [code.visualstudio.com/docs](https://code.visualstudio.com/docs) |
| Git & GitHub basics | [docs.github.com/get-started](https://docs.github.com/en/get-started) |
| Model Context Protocol specification | [modelcontextprotocol.io](https://modelcontextprotocol.io/) |
| FastMCP documentation | [gofastmcp.com](https://gofastmcp.com/) |
| Pydantic v2 documentation | [docs.pydantic.dev](https://docs.pydantic.dev/) |
| HTTPX documentation | [python-httpx.org](https://www.python-httpx.org/) |
| Loguru documentation | [loguru.readthedocs.io](https://loguru.readthedocs.io/) |
| Pytest documentation | [docs.pytest.org](https://docs.pytest.org/) |
| OpenWeatherMap API docs | [openweathermap.org/api](https://openweathermap.org/api) |

---

## 27. Next Learning Steps

Once you're comfortable running and connecting this server, here are good
next steps to deepen your understanding:

1. **Read the source code top-to-bottom**, starting with `schemas.py`
   (data shapes), then `weather_service.py` (business logic), then
   `tools.py` (MCP glue). This mirrors the actual architecture.
2. **Read [`docs/architecture.md`](docs/architecture.md)** for a deeper
   explanation of the layered design and error-handling strategy.
3. **Read [`docs/mcp-primer.md`](docs/mcp-primer.md)** to understand MCP's
   tools/resources/prompts model more conceptually.
4. **Modify an existing tool.** Try adding a new optional argument to
   `get_current_weather` (e.g. including a "feels like" description) and
   watch how the change flows through `schemas.py` -> `weather_service.py`
   -> `tools.py`.
5. **Add a brand-new tool.** For practice, try adding a `get_sunrise_sunset`
   tool that reuses data already returned by `get_current_weather`.
6. **Write a new test.** Add a test case in `tests/test_weather_service.py`
   for your new tool, following the existing `respx`-mocked pattern.
7. **Explore the README's "Future Improvements" section** in
   [`README.md`](README.md) for ideas like caching, alternate providers,
   or a CI pipeline - good intermediate-level projects.
8. **Build your own MCP server from scratch** for a different data source
   (e.g. a to-do list, a news API, or a stock price API) using this
   project's structure as a template.

You now have everything you need to run, test, connect, and start
extending `weather-mcp-server`. Happy building! 🌤️
