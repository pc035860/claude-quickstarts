**Language / 語言:** [English](README.md) | [繁體中文](README.zh-TW.md)

# Autonomous Coding Agent Demo

A minimal harness demonstrating long-running autonomous coding with the Claude Agent SDK. This demo implements a two-agent pattern (initializer + coding agent) that can build complete applications over multiple sessions.

## Prerequisites

**Required:** Install the latest versions of both Claude Code and the Claude Agent SDK:

### Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

### Install Python Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management. You can use either `uv` or traditional `pip`:

**Option 1 - Using uv (Recommended):**

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv pip install -r requirements.txt
```

**Option 2 - Using pip:**

```bash
pip install -r requirements.txt
```

### Verify Installations

```bash
claude --version  # Should be latest version

# If using uv:
uv pip show claude-agent-sdk  # Check SDK is installed

# If using pip:
pip show claude-agent-sdk  # Check SDK is installed
```

**Authentication:** Set ONE of the following:

Option 1 - Standard API key from [console.anthropic.com](https://console.anthropic.com/):
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Option 2 - Claude Code OAuth token (from `claude setup-token`):
```bash
export CLAUDE_CODE_OAUTH_TOKEN='your-claude-code-auth-token'
```

## Quick Start

**Using uv (Recommended):**

```bash
uv run python autonomous_agent_demo.py --project-dir ./my_project
```

**Using traditional Python:**

```bash
python autonomous_agent_demo.py --project-dir ./my_project
```

For testing with limited iterations:
```bash
# With uv:
uv run python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3

# With traditional Python:
python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
```

To start a project with a custom app specification file:
```bash
# With uv:
uv run python autonomous_agent_demo.py --project-dir ./my_project --app-spec ./specs/my_app_spec.txt

# With traditional Python:
python autonomous_agent_demo.py --project-dir ./my_project --app-spec ./specs/my_app_spec.txt
```

To customize the number of features to generate (for faster demos):
```bash
# With uv:
uv run python autonomous_agent_demo.py --project-dir ./my_project --feature-count 50

# With traditional Python:
python autonomous_agent_demo.py --project-dir ./my_project --feature-count 50
```

## Important Timing Expectations

> **Warning: This demo takes a long time to run!**

- **First session (initialization):** The agent generates a `feature_list.json` with test cases (default: 200). This takes several minutes and may appear to hang - this is normal. The agent is writing out all the features.

- **Subsequent sessions:** Each coding iteration can take **5-15 minutes** depending on complexity.

- **Full app:** Building all features typically requires **many hours** of total runtime across multiple sessions.

**Tip:** The default 200 features parameter is designed for comprehensive coverage. If you want faster demos, use the `--feature-count` command-line option (e.g., `--feature-count 50` for a quicker demo).

## How It Works

### Two-Agent Pattern

1. **Initializer Agent (Session 1):** 
   - Reads `app_spec.txt` (from project directory or specified via `--app-spec`)
   - Creates `feature_list.json` with test cases (default: 200, customizable via `--feature-count`)
   - Sets up project structure
   - Initializes git
   - Copies the app spec file to the project directory for future reference

2. **Coding Agent (Sessions 2+):** 
   - Reads `app_spec.txt` from the project directory to understand the overall specification
   - Picks up where the previous session left off
   - Implements features one by one
   - Marks them as passing in `feature_list.json`

### Session Management

- Each session runs with a fresh context window
- Progress is persisted via `feature_list.json` and git commits
- The agent auto-continues between sessions (3 second delay)
- Press `Ctrl+C` to pause; run the same command to resume

## Security Model

This demo uses a defense-in-depth security approach (see `security.py` and `client.py`):

1. **OS-level Sandbox:** Bash commands run in an isolated environment
2. **Filesystem Restrictions:** File operations restricted to the project directory only
3. **Bash Allowlist:** Only specific commands are permitted:
   - File inspection: `ls`, `cat`, `head`, `tail`, `wc`, `grep`, `find`, `echo`, `jq`
   - File operations: `cp`, `mv`, `mkdir`, `chmod`, `tee`, `xargs`
   - Directory: `pwd`, `cd`
   - Node.js: `npm`, `node`, `npx`, `pnpm`
   - Supabase & Deno: `supabase`, `deno`
   - Network utilities: `curl`
   - Version control: `git`
   - Process management: `ps`, `lsof`, `sleep`, `pkill`, `kill` (dev processes only)
   - Script execution: `init.sh`
   - Shell builtins: `set`

Commands not in the allowlist are blocked by the security hook.

## Project Structure

```
autonomous-coding/
├── autonomous_agent_demo.py  # Main entry point
├── agent.py                  # Agent session logic
├── client.py                 # Claude SDK client configuration
├── security.py               # Bash command allowlist and validation
├── progress.py               # Progress tracking utilities
├── prompts.py                # Prompt loading utilities
├── prompts/
│   ├── app_spec.txt          # Application specification
│   ├── initializer_prompt.md # First session prompt
│   └── coding_prompt.md      # Continuation session prompt
└── requirements.txt          # Python dependencies
```

## Generated Project Structure

After running, your project directory will contain:

```
my_project/
├── feature_list.json         # Test cases (source of truth)
├── app_spec.txt              # Copied specification
├── init.sh                   # Environment setup script
├── claude-progress.txt       # Session progress notes
├── .claude_settings.json     # Security settings
└── [application files]       # Generated application code
```

## Running the Generated Application

After the agent completes (or pauses), you can run the generated application:

```bash
cd generations/my_project

# Run the setup script created by the agent
./init.sh

# Or manually (typical for Node.js apps):
npm install
npm run dev
```

The application will typically be available at `http://localhost:3000` or similar (check the agent's output or `init.sh` for the exact URL).

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Directory for the project | `./autonomous_demo_project` |
| `--max-iterations` | Max agent iterations | Unlimited |
| `--model` | Claude model to use | `claude-sonnet-4-5-20250929` |
| `--app-spec` | Path to app spec file (only used during initialization) | `prompts/app_spec.txt` |
| `--feature-count` | Number of features to generate in feature_list.json | `200` |

## Customization

### Changing the Application

**Option 1: Edit the default spec file**
Edit `prompts/app_spec.txt` to specify a different application to build. This will be used for all new projects unless you specify a different file.

**Option 2: Use a custom spec file per project**
Use the `--app-spec` parameter to specify a different app specification file when initializing a new project:

```bash
python autonomous_agent_demo.py --project-dir ./my_project --app-spec ./specs/my_custom_spec.txt
```

This is especially useful when:
- Working with multiple projects that have different specifications
- Integrating autonomous coding into existing projects
- Testing different application designs

**Note:** Once a project is initialized, the app spec file is copied to the project directory (`app_spec.txt`). Subsequent runs will automatically use the project's own `app_spec.txt` file, so you don't need to specify `--app-spec` again.

### App Spec File Management

- **Initialization:** The app spec file is copied to the project directory during the first session
- **Subsequent sessions:** The agent automatically reads `app_spec.txt` from the project directory
- **Protection:** If a project already has `app_spec.txt`, it won't be overwritten unless you explicitly specify a different `--app-spec` file

### Adjusting Feature Count

You can customize the number of features to generate using the `--feature-count` command-line option:

```bash
# Generate 50 features for a faster demo
python autonomous_agent_demo.py --project-dir ./my_project --feature-count 50

# Generate 100 features for a medium-sized demo
python autonomous_agent_demo.py --project-dir ./my_project --feature-count 100
```

Alternatively, you can edit `prompts/initializer_prompt.md` and change the default value in the XML tag `<feature_count>200</feature_count>`.

### Modifying Allowed Commands

Edit `security.py` to add or remove commands from `ALLOWED_COMMANDS`.

## Working with Existing Projects

Autonomous coding can be integrated into existing projects using two helpful commands. These commands help you onboard new projects and add features incrementally.

### Onboarding a New Project

Use the `/onboard-project` command to analyze an existing project and generate an `app_spec.txt` file:

1. **Prepare your project**
   - Ensure your project is accessible (can be a symbolic link in `generations/` directory)
   - Have any PRD, spec, or documentation files ready

2. **Run the command**
   ```
   /onboard-project
   ```

3. **Provide information when prompted**
   - Project path (absolute or relative)
   - Output location for `app_spec.txt` (defaults to project root)
   - API keys, secrets, or credentials setup instructions (if needed)

4. **Review the generated spec**
   - The command will analyze your project structure, codebase, and documentation
   - It will generate a comprehensive `app_spec.txt` following the format in `prompts/app_spec.example.txt`
   - If any information is uncertain, the command will ask for clarification

**What the command does:**
- Explores project structure, codebase, and documentation in parallel
- Identifies technology stack (frontend, backend, database, integrations)
- Extracts features from PRD/spec files and code analysis
- Collects authentication and configuration requirements
- Generates a complete `app_spec.txt` with all necessary sections

**After onboarding:**
- The `app_spec.txt` file is ready for autonomous coding initialization
- You can start the autonomous agent with: `python autonomous_agent_demo.py --project-dir ./your_project`

### Adding New Features to an Existing Project

Use the `/add-feature` command to add new functionality to a project that already has `app_spec.txt`:

1. **Prepare feature information**
   - Have a clear description of the new feature
   - Provide any PRD or spec documents if available

2. **Run the command**
   ```
   /add-feature
   ```

3. **Provide information when prompted**
   - Project path (must have `app_spec.txt` already)
   - New feature description or requirements
   - PRD/spec file paths (optional)

4. **Review the updated feature list**
   - The command will analyze the new feature requirements
   - It will explore existing codebase to understand integration points
   - It will break down the feature into appropriately-sized `feature_list.json` items
   - Each item will be sized to complete at least 1 in a single session

**What the command does:**
- Reads existing `app_spec.txt` and `feature_list.json`
- Explores codebase to understand existing patterns and architecture
- Analyzes new feature requirements and integration points
- Breaks down complex features into manageable items:
  - Backend API development (1-2 items)
  - Frontend UI components (1-2 items)
  - Integration testing (1 item)
  - Styling and UX polish (1 item)
- Updates `feature_list.json` without modifying existing items

**After adding features:**
- New feature items are added to `feature_list.json` with `"passes": false`
- You can continue autonomous coding: `python autonomous_agent_demo.py --project-dir ./your_project`
- The agent will work on the new feature items in priority order

**Best Practices:**
- Keep feature descriptions clear and specific
- Provide PRD/spec documents when available for better analysis
- Review the generated feature items to ensure they're appropriately sized
- The command will ask for clarification if anything is uncertain

## Troubleshooting

**"Appears to hang on first run"**
This is normal. The initializer agent is generating detailed test cases (default: 200), which takes significant time. Watch for `[Tool: ...]` output to confirm the agent is working. To reduce generation time, use `--feature-count` with a smaller number (e.g., `--feature-count 50`).

**"App spec file not found"**
If you specify `--app-spec` with a custom path, make sure the file exists. The path can be relative to the current directory or absolute. Example:
```bash
# Relative path
python autonomous_agent_demo.py --project-dir ./my_project --app-spec ./specs/my_spec.txt

# Absolute path
python autonomous_agent_demo.py --project-dir ./my_project --app-spec /path/to/my_spec.txt
```

**"Command blocked by security hook"**
The agent tried to run a command not in the allowlist. This is the security system working as intended. If needed, add the command to `ALLOWED_COMMANDS` in `security.py`.

**"No Claude auth configured"**
Set ONE of the following in your shell environment:
- Standard API key: `export ANTHROPIC_API_KEY='your-api-key-here'`
- Claude Code OAuth token: `export CLAUDE_CODE_OAUTH_TOKEN='your-claude-code-auth-token'`

## License

Internal Anthropic use.
