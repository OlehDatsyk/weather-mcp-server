# Setting up the weather-mcp-server for this skill

The skill only contains instructions. The tools come from the
**weather-mcp-server** Python project, which must be installed and running
on your machine. Installing the skill does **not** install or configure the
server.

## 1. Requirements

| Item | Version / note |
|---|---|
| Python | 3.12 or newer (the project pins 3.12 in `.python-version`) |
| Python packages | From the project's `requirements.txt`: `fastmcp>=2.3.0,<3.0.0`, `httpx`, `pydantic`, `pydantic-settings`, `python-dotenv`, `loguru` (+ test packages) |
| OpenWeatherMap account | Free API key from <https://home.openweathermap.org/users/sign_up>. New keys can take up to a few hours to activate. |
| Optional | A One Call API subscription on OpenWeatherMap, if you want live data from `get_weather_alerts` |
| Optional | Node.js 18+ to use the MCP Inspector |

## 2. Install the server (once)

From inside the `weather-mcp-server` folder:

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Then open `.env` in a text editor and set your key:

```dotenv
OPENWEATHER_API_KEY=paste_your_key_here
```

The server reads `.env` from its own folder, wherever it is started from,
so you do not need to put the key in any client configuration.

Other optional settings in `.env`: `DEFAULT_UNITS`, `DEFAULT_LANG`,
`REQUEST_TIMEOUT_SECONDS`, `MAX_RETRIES`, `LOG_LEVEL`, `LOG_DIR`,
`MCP_SERVER_NAME`, `OPENWEATHER_BASE_URL`.

## 3. Connect your AI client

Use **absolute paths**. Replace `/ABS/PATH/weather-mcp-server` with your
folder. On Windows the Python path is
`C:\\ABS\\PATH\\weather-mcp-server\\.venv\\Scripts\\python.exe` (double
backslashes inside JSON).

### Claude Desktop (documented in the project README)

Edit `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`,
Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "weather": {
      "command": "/ABS/PATH/weather-mcp-server/.venv/bin/python",
      "args": ["/ABS/PATH/weather-mcp-server/server.py"]
    }
  }
}
```

Fully quit and reopen Claude Desktop.

### Claude Code

```bash
claude mcp add weather -- /ABS/PATH/weather-mcp-server/.venv/bin/python /ABS/PATH/weather-mcp-server/server.py
```

Check with `claude mcp list`. Tools then appear as
`mcp__weather__get_current_weather` and so on.

### Other MCP clients (Cursor, Windsurf, VS Code, etc.)

Any client that can launch a **stdio** MCP server can use the same
`command` + `args` pair shown above in its own MCP configuration file.
These clients have not been tested with this server.

### Remote / HTTP mode (advanced)

If the environment variable `PORT` is set, `server.py` serves MCP over
streamable HTTP on `0.0.0.0:PORT` instead of stdio (intended for hosting
platforms such as Render). The server has **no authentication** in this
mode, so anyone who can reach the URL can spend your OpenWeatherMap quota.
Only use it behind your own access control.

## 4. Install the skill

- **Claude Code:** copy the `weather-mcp-server` skill folder (the one
  containing `SKILL.md`) to `~/.claude/skills/` for all projects, or to
  `.claude/skills/` inside one project.
- **Claude apps (web / desktop):** upload the skill ZIP in the Skills
  section of Settings, if your plan supports custom skills.
- **Other agents that support SKILL.md:** place the folder in that agent's
  skills directory as described in its documentation.

## 5. Check that everything works

Ask the agent: *"Use the weather tools to get the current weather in
London, GB."* You should see a call to `get_current_weather` and an answer
that ends with "Weather data © OpenWeather".

Optional self-test, run by you in a terminal (read-only, installs
nothing):

```bash
/ABS/PATH/weather-mcp-server/.venv/bin/python scripts/verify_server.py --project /ABS/PATH/weather-mcp-server
# add  --city "London,GB"  to make one live API call
```

Or explore the server interactively:

```bash
npx @modelcontextprotocol/inspector /ABS/PATH/weather-mcp-server/.venv/bin/python /ABS/PATH/weather-mcp-server/server.py
```

## 6. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Agent says weather tools are not available | Server not registered or client not restarted. Check paths are absolute and point at the `.venv` Python. |
| `missing_api_key` error | `.env` missing, or `OPENWEATHER_API_KEY` empty / still `your_api_key_here`. |
| `upstream_api_error` HTTP 401 | Key wrong or not activated yet. Wait, then check it on the OpenWeatherMap API keys page. |
| `upstream_api_error` HTTP 429 | Free tier limit (60 calls/minute) reached. Wait a minute. |
| Alerts always empty with a "One Call" note | Your OpenWeatherMap plan does not include the One Call endpoint. Other tools still work. |
| `ImportError` mentioning `fastmcp.prompts.prompt` | fastmcp 3.x or newer installed. Reinstall with `pip install -r requirements.txt` (pins `<3.0.0`). |
| Server seems to "hang" when started by hand | Normal: it waits for an MCP client on stdin. Logs go to stderr and `logs/`. |
