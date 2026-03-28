# TC005 — Hotel Rejection Only

**Stages:** 1 (Planning) → 2 (Selection) → 2 (Hotel retry, flight preserved)
**Destination:** Cairo → Tokyo
**Budget:** $3,500 total, 8 nights
**Focus:** User approves the flight but rejects the hotel. Only the hotel agent re-runs. The previously approved flight must not change.

---

## Turn 1

**User:**
> Plan a trip from Cairo to Tokyo. I want to go for 8 nights in November. Total budget $3,500. Mid-range. I'd like to stay somewhere traditional, ideally near temples or cultural sites.

**Expected Response — Stage 1: Plan**

- Cairo → Tokyo, 8 nights in November
- November weather: cool and pleasant, autumn colors peak, ~17°C — from mock data
- Notes November is within best time to visit (March–May, October–November)
- Budget split (~40% flights, ~40% hotels, ~20% activities — Tokyo defaults)
  - Flight allocation: ~$1,400
  - Hotel allocation: ~$1,400 (÷ 8 nights ≈ $175/night ceiling)
  - Activities: ~$700
- Airlines for CAI→NRT: Turkish Airlines, Emirates, EgyptAir, Qatar Airways, Etihad — from mock data
- Neighborhood recommendation: Asakusa mentioned for traditional/cultural vibe ($90/night avg — within budget)
- Ends with approval question

---

## Turn 2

**User:**
> That plan looks good, approve it.

**Expected Response — Stage 2: Selection**

**Flights presented:**
- Up to 3 options within ~$1,400 flight slice
- Turkish Airlines TK52 ($780, 1 stop IST, 15.5h) ✓
- EgyptAir MS960 ($680, 1 stop BKK, 15.5h) ✓
- Etihad EY654 ($750, 1 stop AUH, 15h) ✓
- Emirates EK924 ($850, 1 stop DXB, 14.5h) ✓
- Qatar Airways QR1300 ($920, 1 stop DOH, 13.5h) — may be near ceiling
- Turkish Airlines Business TK54 ($2,800) must NOT appear

**Hotels presented:**
- Up to 3 options within ~$1,400 total hotel budget (≈$175/night)
- Asakusa area prioritized for traditional/cultural preference:
  - Khaosan Tokyo Asakusa ($45/night × 8 = $360 total) ✓ — budget, cultural area
- Other options within budget:
  - Shinjuku Granbell Hotel ($120/night × 8 = $960 total) ✓
  - Hotel Gracery Shinjuku ($140/night × 8 = $1,120 total) ✓
  - CITAN Hostel ($50/night × 8 = $400 total) ✓
- Park Hyatt Tokyo ($380/night × 8 = $3,040) must NOT appear
- The Peninsula Tokyo ($450/night × 8 = $3,600) must NOT appear

Ends with approval question for both.

---

## Turn 3

**User:**
> Flight is great, I'll take it. But the hotels don't feel traditional enough — I want somewhere with a Japanese aesthetic, breakfast included, and ideally in Asakusa. No hostels.

**Expected Response — Hotel Retry Only**

The assistant acknowledges the partial approval and re-presents hotel options only. Check for all of the following:

- Explicitly confirms the flight selection is locked in (states the flight, airline, price)
- Presents new hotel options with constraints applied:
  - Must have a Japanese/traditional aesthetic
  - Must include breakfast
  - Preferred area: Asakusa
  - No hostels (rules out Khaosan Tokyo Asakusa)
- If mock data has no Asakusa hotel with breakfast included within budget, the assistant must:
  - State clearly that no exact match was found
  - Offer the closest alternatives (e.g., nearby area, or traditional-feeling hotel with breakfast elsewhere in Tokyo)
  - Not invent hotel properties that don't exist in the mock data
- Does not re-present the hostel option

**Must not include:**
- New flight options or any change to the approved flight
- Hostels
- Hotels already rejected (Khaosan Tokyo Asakusa)
- Invented hotel properties not in the mock data

---

## Constraint Accumulation Check

On a hypothetical second hotel rejection with a new constraint (e.g., "must have a pool"), the re-run must carry ALL three constraints: no hostels + breakfast included + Asakusa preference. No constraint is dropped.
