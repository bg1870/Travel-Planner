# Tools and Mock Data

All tools are defined in `src/travel_planner/tools/` and registered in the `TOOL_REGISTRY` dict in `tools/__init__.py`. Mock data lives in `src/travel_planner/mock_data/` as static JSON fixtures loaded with caching via `mock_data/__init__.py`.

## Tool Registry

```python
TOOL_REGISTRY = {
    "web_search": web_search,
    "destination_lookup": destination_lookup,
    "search_flights": search_flights,
    "search_hotels": search_hotels,
    "compare_flights": compare_flights,
    "compare_hotels": compare_hotels,
    "book_flight": book_flight,
    "book_hotel": book_hotel,
    "budget_calculator": budget_calculator,
}
```

When `agents/runner.py` spawns a sub-agent, it resolves the tool names from the agent's front matter against this registry to get the actual `@tool` functions.

## Tool Reference

### Search Tools (`tools/search.py`)

#### `web_search(query: str) -> list[dict]`

Simulated web search. Matches query tokens against keys in `web_results.json` and returns matching snippets.

- **Used by**: Trip Advisor
- **Data source**: `mock_data/web_results.json`
- **Returns**: `[{title, snippet, source}, ...]`

#### `destination_lookup(city: str) -> dict`

Returns a complete destination profile for a city.

- **Used by**: Trip Advisor
- **Data source**: `mock_data/destinations.json`
- **Returns**: Full city profile including:
  - `weather_by_month`: Monthly weather (avg high/low in C, rain days, description)
  - `areas`: Neighborhoods with vibe, distance to center, avg hotel price
  - `average_costs_usd`: Daily costs by category (hotel, meals, transport) across budget tiers
  - `recommended_airlines_from`: Airlines by origin city
  - Airport code, timezone, currency

#### `search_flights(origin, destination, date, return_date?, max_price?, preferred_airlines?) -> list[dict]`

Searches mock flight data with optional filters.

- **Used by**: Flight Agent
- **Data source**: `mock_data/flights.json`
- **Filters**: `max_price` (hard budget cap), `preferred_airlines` (sort priority)
- **Returns**: Flight listings, each with:
  - `flight_id`, `airline`, `flight_number`
  - `origin`, `destination`
  - `departure_time`, `arrival_time`, `duration_hours`
  - `stops`, `stop_cities`
  - `class`, `price_usd`
  - `baggage` (carry_on_kg, checked_kg, checked_bags_included)
  - `aircraft`, `on_time_pct`

#### `search_hotels(city, check_in, check_out, max_total_budget?, preferred_areas?) -> list[dict]`

Searches mock hotel data with optional filters. Calculates nights from dates and enriches results with `total_price`.

- **Used by**: Hotel Agent
- **Data source**: `mock_data/hotels.json`
- **Filters**: `max_total_budget` (total stay cost cap), `preferred_areas` (filter by neighborhood)
- **Returns**: Hotel listings, each with:
  - `hotel_id`, `name`, `area`
  - `star_rating`, `guest_rating`
  - `price_per_night_usd`, `total_price` (calculated: nights x nightly rate)
  - `amenities` (list of strings)
  - `check_in_time`, `check_out_time`
  - `cancellation_policy`
  - `distance_to_center_km`, `description`

### Comparison Tools (`tools/compare.py`)

#### `compare_flights(flight_ids: list[str]) -> list[dict]`

Returns detailed side-by-side data for specific flight IDs. Used after search to narrow down candidates.

- **Used by**: Flight Agent
- **Data source**: `mock_data/flights.json`

#### `compare_hotels(hotel_ids: list[str]) -> list[dict]`

Returns detailed side-by-side data for specific hotel IDs. Used after search to narrow down candidates.

- **Used by**: Hotel Agent
- **Data source**: `mock_data/hotels.json`

### Booking Tools (`tools/booking.py`)

#### `book_flight(flight_id: str, passenger_name?: str) -> dict`

Executes a mock flight booking. Looks up the flight, generates a random booking reference.

- **Used by**: Orchestrator (direct tool, not via sub-agent)
- **Data source**: `mock_data/flights.json`
- **Returns**: `{booking_reference, status, confirmed_at, flight, passenger_name}`
- **Example reference**: `"BK-A3F8K2"`

#### `book_hotel(hotel_id: str, guest_name?: str, check_in: str, check_out: str) -> dict`

Executes a mock hotel booking. Looks up the hotel, calculates total price, generates a booking reference.

- **Used by**: Orchestrator (direct tool, not via sub-agent)
- **Data source**: `mock_data/hotels.json`
- **Returns**: `{booking_reference, status, confirmed_at, hotel, guest_name, check_in, check_out, num_nights, total_price}`

### Budget Tool (`tools/budget.py`)

#### `budget_calculator(destination: str, days: int, tier: str) -> dict`

Computes a recommended budget allocation for a destination.

- **Used by**: Trip Advisor
- **Data source**: `mock_data/budget_reference.json`
- **Tiers**: `"budget"`, `"mid_range"`, `"luxury"`
- **Returns**:
  - `destination`, `days`, `tier`
  - `daily_costs`: Breakdown by category (accommodation, food, transport, activities)
  - `estimated_daily_total`, `estimated_trip_total`
  - `budget_split`: `{flights_pct, hotels_pct, activities_pct}`
  - `warnings`: Any flags (e.g., budget too low for tier)

## Tool-to-Agent Mapping

| Tool | Trip Advisor | Flight Agent | Hotel Agent | Orchestrator |
|------|:-----------:|:------------:|:-----------:|:------------:|
| `web_search` | yes | -- | -- | -- |
| `destination_lookup` | yes | -- | -- | -- |
| `budget_calculator` | yes | -- | -- | -- |
| `search_flights` | -- | yes | -- | -- |
| `compare_flights` | -- | yes | -- | -- |
| `search_hotels` | -- | -- | yes | -- |
| `compare_hotels` | -- | -- | yes | -- |
| `book_flight` | -- | -- | -- | yes |
| `book_hotel` | -- | -- | -- | yes |

Each sub-agent can only call the tools listed in its front matter. The orchestrator has booking tools bound directly (not through `spawn_agent`).

## Mock Data Fixtures

All fixtures are in `src/travel_planner/mock_data/` and loaded via the `__init__.py` data loaders with caching (loaded once, cached in memory).

### `destinations.json`

Five complete city profiles:

| City | Airport | Currency | Cost tier |
|------|---------|----------|-----------|
| Paris | CDG | EUR | High |
| Tokyo | NRT | JPY | High |
| New York | JFK | USD | High |
| Bali | DPS | IDR | Low |
| Istanbul | IST | TRY | Medium |

Each city includes:
- Weather data for all 12 months
- 5 neighborhoods with vibe descriptions and average hotel prices
- Daily cost breakdowns across budget/mid-range/luxury tiers
- Recommended airlines from various origin cities

### `flights.json`

Flight listings organized by route (e.g., `"cairo_to_paris"`). Each route has 6-8 flights with realistic variety:

- Mix of direct and connecting flights
- Morning, afternoon, and evening departures
- Budget to premium pricing
- Various airlines, aircraft types, and on-time percentages
- Baggage allowances

### `hotels.json`

Hotel listings organized by city. Each city has 6-8 hotels spanning:

- Budget through luxury price tiers
- Multiple neighborhoods per city
- 3-5 star ratings with guest ratings
- Various amenity sets (wifi, breakfast, pool, gym, etc.)
- Different cancellation policies

### `web_results.json`

Pre-canned web search results keyed by query string. Used by `web_search` to return snippets about destinations, seasonal events, visa requirements, and travel tips.

### `budget_reference.json`

Per-destination cost data used by `budget_calculator`:

- Daily costs across three tiers (budget, mid-range, luxury) broken down by: accommodation, food, transport, activities
- Default budget split percentages: flights, hotels, activities
- Cost tier classification per destination
