# Documentation

Technical documentation for the multi-agent travel planning system. Each document reflects the **current state of the codebase**.

## Documents

| # | Document | Description |
|---|----------|-------------|
| 1 | [Architecture](ARCHITECTURE.md) | System topology, 2-node ReAct graph, orchestrator-delegates pattern, agent spawning |
| 2 | [Agents](AGENTS.md) | All 4 agents: orchestrator, trip advisor, flight agent, hotel agent. Registry pattern, tools, input/output contracts |
| 3 | [Orchestration Flow](ORCHESTRATION_FLOW.md) | 3-stage pipeline, human-in-the-loop checkpoints, rejection handling, progressive skill loading |
| 4 | [Context Engineering](CONTEXT_ENGINEERING.md) | Per-agent context filtering, snapshot + tail compaction, ephemeral sub-agents, context firewall |
| 5 | [Session Management](SESSION_MANAGEMENT.md) | Session lifecycle, file structure, conversation entries, custom LangGraph checkpointer |
| 6 | [Tools and Mock Data](TOOLS_AND_MOCK_DATA.md) | All 9 tools, mock data fixtures, data loaders |

## Reading Order

Start with **Architecture** for the system shape. **Agents** and **Orchestration Flow** explain what each component does and how they interact. **Context Engineering** covers the information-filtering design. **Session Management** and **Tools and Mock Data** are implementation details.
