# TC002 — Happy Path: Cairo to Bali (Budget Travel)

**Stages:** 1 (Planning) → 2 (Selection) → 3 (Booking)
**Budget tier:** Budget (~$1,500 total)
**Trip:** 10 nights, economy class
**Pass condition:** Booking confirmed with valid flight and hotel references.

---

## Turn 1

**User:**
> I want to go to Bali from Cairo for 10 nights in July. My total budget is $1,500. I'm traveling solo and on a tight budget — I don't mind a hostel or basic hotel.

**Expected Response — Stage 1: Planning**

The assistant presents a travel plan. Check for all of the following:

- Acknowledges the trip: Cairo → Bali, 10 nights in July
- States total budget ($1,500) and shows a three-way split — a significant portion goes to flights given the long-haul route (mock data default: ~50% flights for Bali)
- Describes July weather in Bali accurately: coolest and driest month, 4 rain days, peak tourist season (~29°C high) — consistent with mock data
- Notes that July is within the best time to visit window (May–September)
- Acknowledges the budget constraint and confirms the trip is feasible at the budget tier
- Names at least one recommended airline for CAI→DPS route (Emirates, Qatar Airways, Turkish Airlines, or EgyptAir appear in mock data)
- Mentions at least one budget-friendly area: Kuta (avg $40/night) or Canggu (avg $60/night)
- Ends with a question asking the user to approve or adjust the plan

**Must not include:**
- Luxury hotel suggestions given the explicitly stated budget preference
- Any claim that Bali is unaffordable on $1,500 (budget tier daily costs are $25–$50/day per mock data)

---

## Turn 2

**User:**
> That works for me, proceed.

**Expected Response — Stage 2: Selection**

The assistant presents ranked flight and hotel options. Check for all of the following:

**Flights section:**
- Lists up to 3 Cairo → Bali (CAI → DPS) economy options
- All listed flights are within the flight budget slice
- EgyptAir MS970 ($520, 2 stops via BKK/SIN) or Turkish Airlines TK66 ($650, 1 stop) should appear as budget options
- Each option shows: airline, duration, stops, price, and baggage
- The recommended pick accounts for the budget constraint (cheapest viable option)

**Hotels section:**
- Lists up to 3 budget-friendly Bali hotel options
- Options reflect the budget tier: Kuta Beach Hostel ($15/night), Ubud Inn Cottage ($35/night), The Lawn Canggu ($55/night) are the relevant mock properties
- Each option shows: name, area, nightly rate, total for 10 nights, key amenities
- Total hotel cost is within the hotel budget slice
- The recommended pick is appropriate for a solo budget traveler

**Combined costs:**
- Flight + hotel total must not exceed $1,500
- Remaining budget for activities is stated

Ends by asking the user to approve both or provide feedback.

---

## Turn 3

**User:**
> Perfect. Book it all.

**Expected Response — Stage 3: Pre-Booking Itinerary**

- Summarizes selected flight and hotel with costs
- Shows total cost breakdown and remaining activity budget
- Asks for explicit confirmation before booking

**Must not include:**
- Confirmation references (booking not yet executed)

---

## Turn 4

**User:**
> Confirmed, go ahead.

**Expected Response — Booking Confirmation**

- Confirms flight booked with a booking reference
- Confirms hotel booked with a booking reference
- Final cost summary showing totals and remaining budget
- Closes the session with thanks
