Act as a principal engineer and AI systems architect.

Design and scaffold a Python CLI project for a multi-agent AI team orchestration platform.

Project requirements:
- terminal-first CLI application
- user composes a team of AI agents from a markdown registry
- each agent has unique capabilities, system prompt, strengths, weaknesses, model policy, tools, permissions, and collaboration rules
- user can select up to 5 agents
- there are multiple PM agents with different styles (startup PM, delivery PM, enterprise PM, product strategist PM)
- PM can recommend a team composition based on the task
- agents should collaborate, disagree, debate, and propose alternatives
- debate must be structured and triggered only on meaningful conflicts
- not all selected agents must be activated for every task
- the system must be cost-aware and route different steps to different model tiers
- the platform should generate artifacts such as brief.md, decision.md, plan.md, tasks.json, conflicts.json, debate.md
- use markdown + YAML frontmatter for agent definitions
- use JSON/YAML for team configs
- store sessions and usage locally
- architecture should include CLI layer, orchestration layer, agent runtime layer, storage layer, and model gateway layer

Please provide:
1. recommended folder structure
2. pydantic domain models
3. agent markdown schema
4. team config schema
5. orchestrator class design
6. conflict detector design
7. debate engine design
8. synthesis flow
9. budget manager design
10. model gateway interface
11. starter CLI commands using Typer
12. artifact writer design
13. pseudocode for the end-to-end task pipeline
14. implementation roadmap

Focus on practical, buildable architecture. Avoid vague high-level only suggestions.