# TC006 — Both Flight and Hotel Rejected

**Stages:** 1 (Planning) → 2 (Selection) → 2 (Full retry with accumulated constraints)
**Destination:** Cairo → Istanbul
**Budget:** $1,800 total, 4 nights
**Focus:** User rejects both flight and hotel with separate constraints. Both agents re-run and must each incorporate their respective new constraints.

---

## Turn 1

**User:**
> I want to go from Cairo to Istanbul for 4 nights in September. Budget is $1,800. I prefer morning departures and a central hotel.

**Expected Response — Stage 1: Plan**

- Cairo → Istanbul, 4 nights in September
- September weather: warm, crowds thinning, 26°C — from mock data
- Notes September is within best time to visit
- Budget split (~35% flights ≈ $630, ~40% hotels ≈ $720 / 4 nights ≈ $180/night, ~25% activities ≈ $450)
- Airlines for CAI→IST: Turkish Airlines, EgyptAir, Pegasus — from mock data
- Central neighborhood recommendations: Sultanahmet or Taksim (central, avg $100–$110/night)
- Morning departure preference noted
- Ends with approval question

---

## Turn 2

**User:**
> Approved.

**Expected Response — Stage 2: Selection**

**Flights presented (within ~$630 flight slice, morning preference):**
- Turkish Airlines TK695: departs 08:00, $280 ✓ (morning, within budget)
- EgyptAir MS737: departs 07:15, $250 ✓ (morning, within budget)
- Turkish Airlines TK697: departs 17:00, $310 — may appear as an option but not preferred
- Pegasus PC502: departs 13:30, $160 — not a morning departure
- Pegasus PC504: departs 05:00, $140 — early but may count as morning
- Business class TK699 ($850) must NOT appear

**Hotels presented (within ~$720 total / $180/night, central preference):**
- Hotel Sultanahmet Palace ($110/night × 4 = $440 total, Sultanahmet) ✓
- Taksim Square Hotel ($80/night × 4 = $320 total, Taksim) ✓
- The House Hotel Karakoy ($130/night × 4 = $520 total, Beyoglu) ✓
- Pera Palace Hotel ($220/night × 4 = $880 total) — exceeds slice, should not appear
- Four Seasons Sultanahmet ($350/night × 4 = $1,400 total) must NOT appear

Ends with approval question for both.

---

## Turn 3

**User:**
> I don't like either option. For flights, no EgyptAir — I've had bad experiences. And for hotels, I want breakfast included, that's non-negotiable.

**Expected Response — Both Rejected, Full Retry**

The assistant acknowledges both rejections and presents updated options for each. Check for all of the following:

**General:**
- Explicitly states that both the flight and hotel selections have been updated
- Previous options from Turn 2 are not re-presented

**New flight options (constraints: morning departures + no EgyptAir):**
- EgyptAir MS737 must NOT appear
- EgyptAir MS739 must NOT appear
- Valid morning options remaining: Turkish Airlines TK695 (08:00, $280), Pegasus PC504 (05:00, $140)
- If TK697 (17:00) or PC502 (13:30) appear, they must NOT be the recommended pick given the morning preference
- The recommended pick is from Turkish Airlines or Pegasus only

**New hotel options (constraints: breakfast included + central):**
- Hotels without breakfast included must NOT be the recommended pick (Taksim Square Hotel has only "breakfast_available" not "breakfast_included" — it should be flagged or deprioritized)
- Hotels with breakfast included from mock data within budget:
  - Hotel Sultanahmet Palace ($110/night, breakfast_included) ✓
  - Bosphorus Palace Hotel ($95/night, breakfast_included, but in Besiktas — less central) ✓
  - Kadikoy Port Hotel ($55/night, breakfast_included, but on Asian side) — may appear with distance caveat
- Previously shown hotels without breakfast (Taksim Square, House Hotel Karakoy) must not be presented as satisfying the constraint

**Must not include:**
- Any EgyptAir flight
- Hotels without breakfast included as the recommended pick
- Re-presentation of any option from Turn 2's initial selection

Ends with approval question for both updated selections.
