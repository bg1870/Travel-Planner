# Agents

The system has four agents: one orchestrator and three sub-agents. The orchestrator runs persistently across the conversation. Sub-agents are ephemeral -- created per task, destroyed after returning.

## Agent Registry

Agents are defined as **Markdown files with YAML front matter** in `src/travel_planner/prompts/agents/`. The `agents/registry.py` module loads these at startup:

1. Reads each `.md` file in the agents directory
2. Parses YAML front matter (id, model, tools, max_tool_calls, timeout)
3. Extracts the Markdown body as the system prompt
4. Builds a summary of all agents (id, required inputs, outputs) for injection into the orchestrator prompt via the `{{AGENT_REGISTRY}}` placeholder

Adding a new agent requires only creating a new `.md` file. No code changes needed.

### Front Matter Schema

```yaml
---
id: agent_id              # Used in spawn_agent(agent_id, ...)
model: claude-haiku-4-5   # LLM model for this agent
tools:                     # Tools this agent can call
  - tool_name_1
  - tool_name_2
max_tool_calls: 3          # Upper bound on tool invocations
timeout: 120s              # Per-invocation timeout
---
```

### Agent Spawning

The `spawn_agent` tool in `agents/runner.py`:

1. Looks up the agent definition from the registry by `agent_id`
2. Resolves tool references to actual `@tool` functions from `TOOL_REGISTRY`
3. Creates a fresh ReAct agent via `create_react_agent(model, tools, prompt=system_prompt)`
4. Invokes it with the orchestrator-provided prompt as a `HumanMessage`
5. Extracts the final `AIMessage` content and returns it as plain text

Each sub-agent runs its own internal tool loop (up to `max_tool_calls` iterations) before returning.

---

## Orchestrator

| Property | Value |
|----------|-------|
| Model | `claude-sonnet-4-6` |
| Tools | `spawn_agent`, `load_skill`, `book_flight`, `book_hotel` |
| Prompt | `prompts/orchestrator.system.md` |
| Persistence | Stateful across the conversation via LangGraph state |

The orchestrator is the only agent the user interacts with. It:

- Gathers travel details from the user (origin, destination, dates, budget, preferences)
- Delegates research and selection to sub-agents via `spawn_agent`
- Constructs **filtered prompts** for each sub-agent (context firewall)
- Manages 3-stage checkpoint flow (plan, select, book)
- Tracks rejection constraints across retries
- Validates coherence between agent results (e.g., late flight arrival vs. hotel check-in)
- Executes bookings directly using `book_flight` and `book_hotel` tools
- Loads the booking skill prompt on demand via `load_skill("booking")`

### Orchestrator Tools

| Tool | Source | Purpose |
|------|--------|---------|
| `spawn_agent(agent_id, prompt)` | `agents/runner.py` | Spawn a sub-agent with a filtered prompt |
| `load_skill(skill_name)` | `skills/loader.py` | Load a skill prompt for progressive capability disclosure |
| `book_flight(flight_id, passenger_name?)` | `tools/booking.py` | Execute a mock flight booking |
| `book_hotel(hotel_id, guest_name?, check_in, check_out)` | `tools/booking.py` | Execute a mock hotel booking |

### System Prompt Structure

The orchestrator system prompt (`prompts/orchestrator.system.md`) defines:

- **Identity**: Travel Planner Orchestrator coordinating sub-agents through approval flow
- **3-stage pipeline**: Planning, Selection, Booking (see [Orchestration Flow](ORCHESTRATION_FLOW.md))
- **Context filtering rules**: What to include/exclude in each agent's prompt
- **Coherence checks**: Cross-agent validation (arrival times, budget overflow)
- **Behavioral guardrails**: Never book without confirmation, never pass total budget to sub-agents, never show previously rejected options
- **Error handling**: Report failures, escalate after 3 rejections, flag conflicts

The `{{AGENT_REGISTRY}}` placeholder is replaced at startup with a summary of all registered sub-agents and their required inputs/outputs.

---

## Trip Advisor Agent

| Property | Value |
|----------|-------|
| Model | `claude-haiku-4-5` |
| Tools | `web_search`, `destination_lookup`, `budget_calculator` |
| Max tool calls | 3 |
| Timeout | 120s |
| Prompt | `prompts/agents/trip_advisor.md` |

### Purpose

Researches a destination and creates a travel plan with budget allocation. Called in Stage 1 (Planning).

### Input (from orchestrator)

The orchestrator constructs a prompt containing:
- Origin city and destination city
- Travel dates
- Total budget
- User preferences (if any)
- Rejection constraints (if re-invoked after rejection)

### Tool Loop

1. Call `destination_lookup(city)` to get the full destination profile (weather, neighborhoods, costs, airlines)
2. Call `web_search(query)` if additional context is needed (seasonal events, visa requirements)
3. Call `budget_calculator(destination, days, tier)` to compute the recommended budget split

### Output

Plain text response structured as:
- **Travel Details**: Origin, destination, dates, budget
- **Destination Overview**: Weather, highlights, practical info
- **Budget Split**: Flight allocation, hotel allocation, activities allocation
- **Recommendations**: Suggested airlines, preferred flight times, hotel areas

### Behavioral Rules

- Never interact with the user directly
- Don't invent data -- only use tool results
- Honor rejection constraints and budget overrides from prior iterations
- Maximum 3 tool calls

---

## Flight Agent

| Property | Value |
|----------|-------|
| Model | `claude-haiku-4-5` |
| Tools | `search_flights`, `compare_flights` |
| Max tool calls | 3 |
| Timeout | 120s |
| Prompt | `prompts/agents/flight_agent.md` |

### Purpose

Searches and ranks flight options within a budget slice. Called in Stage 2 (Selection).

### Input (from orchestrator)

The orchestrator constructs a prompt containing:
- Origin and destination airport codes
- Outbound and return dates
- **Flight budget slice only** (not total trip budget)
- Preferred airlines (from trip advisor recommendations)
- Preferred times
- Rejection constraints (e.g., "no flights over $600", "no layovers in city X")

### Tool Loop

1. Call `search_flights(origin, destination, date, return_date?, max_price?, preferred_airlines?)` to get matching flights
2. If many results, call `compare_flights(flight_ids)` for detailed side-by-side comparison of top candidates
3. Rank results and build output

### Output

Plain text response structured as:
- **Ranked Flight Options**: Up to 3, each with airline, flight number, times, duration, stops, price, baggage
- **Recommended Pick**: Top choice with justification
- **Search Notes**: Any constraints that limited results

### Ranking Priority

1. Within budget (hard constraint -- never recommend over budget)
2. Preferred airlines
3. Preferred departure/arrival times
4. Fewest stops
5. Shortest duration
6. Lowest price

---

## Hotel Agent

| Property | Value |
|----------|-------|
| Model | `claude-haiku-4-5` |
| Tools | `search_hotels`, `compare_hotels` |
| Max tool calls | 3 |
| Timeout | 120s |
| Prompt | `prompts/agents/hotel_agent.md` |

### Purpose

Searches and ranks hotel options within a budget slice. Called in Stage 2 (Selection).

### Input (from orchestrator)

The orchestrator constructs a prompt containing:
- Destination city
- Check-in and check-out dates
- **Hotel budget slice only** (not total trip budget)
- Preferred areas/neighborhoods (from trip advisor recommendations)
- Guest arrival info (optional -- e.g., late-night arrival requiring 24hr reception)
- Rejection constraints (e.g., "must have breakfast included", "no hotels below 4 stars")

### Tool Loop

1. Call `search_hotels(city, check_in, check_out, max_total_budget?, preferred_areas?)` to get matching hotels
2. If many results, call `compare_hotels(hotel_ids)` for detailed comparison of top candidates
3. Rank results and build output

### Output

Plain text response structured as:
- **Ranked Hotel Options**: Up to 3, each with name, area, star rating, guest rating, nightly rate, total price, amenities, cancellation policy
- **Recommended Pick**: Top choice with justification
- **Search Notes**: Any constraints that limited results

### Ranking Priority

1. Within budget (hard constraint)
2. Preferred area
3. Guest rating
4. Location / walkability (distance to center)
5. Amenities
6. Price
