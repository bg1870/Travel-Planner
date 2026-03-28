# TC003 — Plan Rejection: Budget Reallocation Request

**Stages:** 1 (Planning) → 1 (Retry with constraints) → 2 (Selection)
**Destination:** Cairo → Istanbul
**Budget:** $2,000 total, 5 nights
**Focus:** User rejects the initial plan and requests a different budget split. The revised plan must reflect the new constraint without dropping the original destination/dates.

---

## Turn 1

**User:**
> Plan a trip from Cairo to Istanbul. Traveling May 5–10, budget $2,000. I'm mid-range, prefer evenings free for exploring.

**Expected Response — Stage 1: Initial Plan**

- Acknowledges: Cairo → Istanbul, May 5–10 (5 nights)
- Budget split shown (approximately: ~35% flights ~$700, ~40% hotels ~$800, ~25% activities ~$500 based on Istanbul defaults)
- May weather described accurately: warm, comfortable for sightseeing, ~22°C highs
- Notes May is within best time to visit (April–May, September–October)
- Airlines mentioned: Turkish Airlines, EgyptAir (both in mock data for CAI→IST)
- Neighborhood recommendations mention Sultanahmet or Beyoglu given sightseeing preference
- Ends with approval question

---

## Turn 2

**User:**
> The budget split doesn't work for me — I want to spend more on the hotel and less on activities. Can you allocate $900 to hotels and only $300 to activities?

**Expected Response — Stage 1 Retry: Revised Plan**

The assistant presents a revised plan that incorporates the user's constraint. Check for all of the following:

- Explicitly acknowledges the new budget split request
- Revised split shows: flights ~$800, hotels ~$900, activities ~$300 (the user-specified values; flights may absorb the difference)
- All other trip details (destination, dates, budget total) remain unchanged
- The revised hotel allocation ($900 ÷ 5 nights = $180/night max) is noted as the per-night ceiling — consistent with Istanbul hotel options like Pera Palace ($220) being above budget or Hotel Sultanahmet Palace ($110) being within budget
- Ends with approval question

**Must not include:**
- Dropping or changing the destination, dates, or total budget
- Reverting to the original budget split
- Rejecting the user's request as infeasible without offering an alternative

---

## Turn 3

**User:**
> Yes, that's better. Approve.

**Expected Response — Stage 2: Selection**

- Flight options for CAI → IST within the flight slice (~$800 ceiling)
  - Turkish Airlines TK695 ($280), TK697 ($310), EgyptAir MS737 ($250), Pegasus PC502 ($160) are all within budget
  - Business class TK699 ($850) must NOT appear (exceeds flight slice)
- Hotel options within $180/night ceiling
  - Hotel Sultanahmet Palace ($110/night × 5 = $550 total) ✓
  - The House Hotel Karakoy ($130/night × 5 = $650 total) ✓
  - Pera Palace Hotel ($220/night × 5 = $1,100 total) ✗ — should not be recommended as it exceeds the hotel slice
  - Taksim Square Hotel ($80/night), Kadikoy Port Hotel ($55/night) ✓
- Combined costs must not exceed $2,000

**Must not include:**
- Any hotel priced above $900 total (the user's hotel ceiling)
- Any reference to the original budget split

---

## Constraint Accumulation Verification

If the user then rejects again in Stage 2, the next re-spawn must carry BOTH the May 5–10 date constraint AND the $900/$300 hotel/activities split. This can be verified by a follow-up rejection turn if needed.
