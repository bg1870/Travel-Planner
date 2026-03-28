# TC008 — Booking Cancellation at Final Confirmation

**Stages:** 1 → 2 → 3 (user cancels at confirmation checkpoint)
**Destination:** Cairo → Bali
**Budget:** $2,500 total, 7 nights
**Focus:** The user reaches the final booking confirmation step and cancels. The system must not execute any booking and must offer a clear path forward.

---

## Setup — Turns 1–3 (Abbreviated)

Run these as prerequisites to reach Stage 3.

**Turn 1 — User:**
> I want to plan a trip from Cairo to Bali, 7 nights in August. Budget $2,500, mid-range.

**Turn 1 — Expected Response:** Travel plan with August weather (hot, dry, ideal — 3 rain days from mock data), mid-range budget split (~50% flights ≈ $1,250, ~30% hotels ≈ $750 / 7 nights ≈ $107/night, ~20% activities ≈ $500). Airlines mentioned: Emirates, Qatar Airways, Singapore Airlines. Areas: Seminyak or Canggu for mid-range. Approval question.

**Turn 2 — User:** `Approved.`

**Turn 2 — Expected Response:** Flights (CAI→DPS within ~$1,250: Emirates EK930 $720, Qatar Airways QR1388 $790, Turkish Airlines TK66 $650, Singapore Airlines SQ483 $880) and hotels within ~$750 total ($107/night ceiling):
- The Lawn Canggu ($55/night × 7 = $385) ✓
- Alila Seminyak ($130/night × 7 = $910) — slightly over
- Ubud Inn Cottage ($35/night × 7 = $245) ✓
- Kuta Beach Hostel ($15/night × 7 = $105) ✓

Approval question for both.

**Turn 3 — User:** `Both look great, let's proceed.`

**Turn 3 — Expected Response (Stage 3 — Pre-Booking Itinerary):** Complete itinerary summary with selected flight details (airline, number, times, price), hotel details (name, area, check-in/check-out, total cost), total combined cost, remaining activities budget, and an explicit confirmation request before any booking is made.

---

## Turn 4 — Cancellation

**User:**
> Actually, hold on — don't book yet. I want to reconsider the hotel.

**Expected Response — Cancellation Acknowledged**

Check for all of the following:

- Confirms that no booking has been made — neither flight nor hotel
- Does not present booking references (no booking was executed)
- Offers a clear path forward, such as:
  - "I can re-run the hotel search with new criteria — what would you like to change?"
  - Or returns the user to the hotel selection from Stage 2
- The previously approved flight selection is preserved (not lost)
- The system does not restart from Stage 1 unless the user explicitly asks

**Must not include:**
- Any booking reference numbers (the booking was not made)
- A message stating "your flight has been booked" or "your hotel has been booked"
- Losing the approved flight selection

---

## Turn 5 — Re-specifying Hotel Preference

**User:**
> I'd like a hotel with a pool and beach access. Can you find something like that within my budget?

**Expected Response — Hotel Retry from Stage 3 Return**

- Acknowledges the new hotel constraint: pool + beach access
- Presents updated hotel options from mock data with pool and beach_access amenities:
  - The Legian Seminyak ($180/night × 7 = $1,260 total) — exceeds $750 slice; must note this
  - Mulia Resort Nusa Dua ($200/night × 7 = $1,400 total) — exceeds slice; must note this
  - Alila Seminyak ($130/night × 7 = $910 total, has pool and beach_access) — over but closest
- If all pool + beach_access options exceed the hotel budget slice, the assistant must communicate this and offer options (increase budget, reduce nights, or select without beach access)
- The approved flight is still referenced and preserved throughout

**Must not include:**
- Booking anything without a new explicit confirmation
- Presenting options without pool and beach_access as satisfying the constraint
- Dropping the flight selection
