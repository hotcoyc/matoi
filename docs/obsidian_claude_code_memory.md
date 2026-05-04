# Obsidian + Claude Code: Memory and Knowledge System

A guide on integrating an Obsidian vault with Claude Code to build persistent project memory.

---

## Why This Is Needed

Claude Code has built-in memory (`~/.claude/projects/.../memory/`), but it's limited: flat `.md` files, no link graph, no visualization. An Obsidian vault solves these problems:

- **Link graph** — `[[wikilinks]]` between notes create a knowledge graph
- **Visualization** — graph view, canvas, backlinks
- **Tags and search** — instant full-text search across the entire vault
- **Plugins** — Dataview, Templater, Calendar, and 1500+ others
- **Everything in Markdown** — Claude Code natively reads and writes `.md`

---

## Method 1: Direct Access (zero setup)

Claude Code is launched from the vault directory. A vault is simply a folder with `.md` files.

### Setup

```bash
cd ~/ObsidianVault && claude
```

Create `CLAUDE.md` at the vault root:

```markdown
## Vault Conventions
- All notes use [[wikilinks]] for cross-references
- YAML frontmatter is required
- Do not delete or rename existing notes without confirmation

## Memory
- brain/Index.md — accumulated patterns and decisions
- brain/Decisions.md — architectural decisions
- brain/Patterns.md — identified patterns
- brain/Mistakes.md — mistakes to avoid
```

### Vault Structure

```
vault/
├── CLAUDE.md           # instructions for Claude Code
├── brain/              # agent memory
│   ├── Index.md
│   ├── Decisions.md
│   ├── Patterns.md
│   └── Mistakes.md
├── projects/           # projects
│   └── ai-agency-platform/
├── daily-notes/        # daily notes
└── inbox/              # inbox
```

**Pros:** zero complexity, works immediately, free
**Cons:** no structured search, only manual file reading by path

---

## Method 2: MCP Server for Obsidian

An MCP server gives Claude Code a set of tools for working with the vault: search, read, write, tags. Works from any directory.

### Option A: `obsidian-mcp` (recommended)

Works directly with files. Obsidian does not need to be running.

**Installation:**

```bash
# Requires Node.js 20+
```

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp", "/Users/ak/ObsidianVault"]
    }
  }
}
```

Restart Claude Code.

**Available tools:**
- `read-note`, `create-note`, `edit-note`, `delete-note`, `move-note`
- `search-vault` — full-text search
- `add-tags`, `remove-tags`, `rename-tag`
- `create-directory`, `list-available-vaults`

### Option B: Filesystem MCP (by Anthropic)

Minimal MCP — a standard file server:

```json
{
  "mcpServers": {
    "vault": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/ak/ObsidianVault"]
    }
  }
}
```

### Option C: `mcp-obsidian` (via REST API)

Requires Obsidian to be running with the **Local REST API** plugin.

1. In Obsidian: Settings -> Community Plugins -> install "Local REST API"
2. Enable the plugin, note the API key and port (usually 27124)
3. Configuration:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "@mseep/obsidian-mcp-server"],
      "env": {
        "OBSIDIAN_API_KEY": "your-key",
        "OBSIDIAN_API_PORT": "27124"
      }
    }
  }
}
```

> **Important:** Python-based MCP servers have a known `BrokenPipeError` bug in Claude Code CLI. Use Node.js implementations.

**MCP Pros:** structured search, works from any directory, multiple vaults
**MCP Cons:** Node.js/npx dependency, read/write access — back up your vault

---

## Method 3: Automatic Memory via Claude Code Hooks

Claude Code hooks extract insights from each session and save them to the vault. Memory grows automatically.

### Architecture

```
Session ends
  → "Stop" hook fires
    → Python script analyzes the transcript
      → Claude API (Haiku) extracts patterns/mistakes/decisions
        → Markdown notes in the vault
          → CLAUDE.md references Index.md
            → Next session reads accumulated knowledge
```

### Setup

1. Create the structure:

```bash
mkdir -p ~/ObsidianVault/claude-memory/{Patterns,Mistakes,Decisions,Context,Sessions}
```

2. Configure hooks in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/memory_extractor.py"
          }
        ]
      }
    ]
  }
}
```

3. Create the script `~/.claude/hooks/memory_extractor.py`:
   - Receives JSON via stdin (session_id, project directory)
   - Sends the transcript to the Claude API (Haiku — ~$0.01/session)
   - Creates `.md` files with YAML frontmatter
   - Updates `Index.md`

4. Export the API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

5. Add to the project's `CLAUDE.md`:

```markdown
## Project Memory
- ~/ObsidianVault/claude-memory/Index.md — accumulated patterns
- ~/ObsidianVault/claude-memory/Context/ — project context
- ~/ObsidianVault/claude-memory/Decisions/ — architectural decisions
- ~/ObsidianVault/claude-memory/Mistakes/ — known mistakes
```

**Pros:** fully automatic, grows with each session, cheap (~$0.01/session)
**Cons:** requires an API key, complex initial setup (~1-2 hours), needs periodic cleanup

---

## Method 4: Ready-Made Vault Templates

### Obsidian Mind (`breferrari/obsidian-mind`)

The most complete ready-made solution: a vault template with 5 hooks, 18 slash commands, and 9 sub-agents.

```bash
npm install -g shardmind
mkdir my-vault && cd my-vault
shardmind install github:breferrari/obsidian-mind
```

**What's included:**
- `CLAUDE.md` — complete agent manual
- `brain/` folder — goals, decisions, patterns, mistakes, memories
- 5 lifecycle hooks: SessionStart, UserPromptSubmit, PostToolUse, PreCompact, Stop
- 18 commands: `/om-standup`, `/om-dump`, `/om-wrap-up`, `/om-weekly`
- 9 sub-agents: brag-spotter, vault-librarian, cross-linker
- Multi-agent compatibility (Claude Code, Codex CLI, Gemini CLI)

### claude-code-memory-setup (`lucasrosati/claude-code-memory-setup`)

Focused on token savings. Claims a 71.5x reduction in spending.

**Three layers:**
1. **Obsidian Zettelkasten** — atomic notes with wikilinks
2. **Graphify** — AST parsing of the codebase → `graph.json` (332 nodes from 126 files = 172 KB)
3. **Chat Import Pipeline** — auto-import of Claude conversations into the vault

```bash
pip install graphifyy && graphify install
graphify . --obsidian --obsidian-dir ~/vault/graphify/project-name
```

---

## Method 5: Obsidian Plugins with Claude Code

### Claudian (`YishenTu/claudian`)

An Obsidian plugin that embeds Claude Code directly into the sidebar. The vault = the agent's working directory.

### Agent Client

A plugin for running Claude Code, Codex, and Gemini CLI inside Obsidian (requires Obsidian 1.12+).

---

## Comparison Table

| Method | Complexity | Time | Automation | Best For |
|--------|-----------|------|------------|----------|
| Direct access | Minimal | 5 min | None | Quick start |
| MCP server | Low | 10-15 min | Partial | Searching the vault from any project |
| Hooks + memory extractor | High | 1-2 hours | Full | Long-term work |
| Obsidian Mind (template) | Medium | 30 min | Full | Comprehensive "out of the box" solution |
| Plugins in Obsidian | Low | 10 min | None | Working inside Obsidian |

---

## Recommendation for AI Agency Platform

### Step-by-Step Plan

**Phase 1 — now (5 minutes):**
- Create a vault (or use an existing one)
- Add `CLAUDE.md` with instructions
- Launch `claude` from the vault directory when you need to work with memory

**Phase 2 — during active development (15 minutes):**
- Connect `obsidian-mcp` as an MCP server
- Claude Code gains access to the vault from any working directory

**Phase 3 — during regular work (1-2 hours):**
- Set up hooks for automatic insight extraction
- Or try Obsidian Mind as a ready-made template

### Key Understanding

The vault **does not need** to be loaded entirely into context. Claude Code opens only the needed files, and `CLAUDE.md` serves as a "map" to the knowledge. This is fundamentally different from RAG — here the agent decides what to read on its own.

---

## Links

- [obsidian-mcp (StevenStavrakis)](https://github.com/StevenStavrakis/obsidian-mcp)
- [mcp-obsidian (MarkusPfundstein)](https://github.com/MarkusPfundstein/mcp-obsidian)
- [Obsidian Mind](https://github.com/breferrari/obsidian-mind)
- [claude-code-memory-setup](https://github.com/lucasrosati/claude-code-memory-setup)
- [Claudian plugin](https://github.com/YishenTu/claudian)
- [claude-knowledge-graph](https://github.com/NAMYUNWOO/claude-knowledge-graph)
- [@modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers)
