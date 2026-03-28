# TC001 — Happy Path: Cairo to Paris (Mid-Range Budget)

**Stages:** 1 (Planning) → 2 (Selection) → 3 (Booking)
**Budget tier:** Mid-range (~$3,000 total)
**Trip:** 7 nights, economy class
**Pass condition:** Booking confirmed with valid flight and hotel references.

---

## Turn 1

**User:**
> I want to plan a trip to Paris from Cairo. Traveling April 10–17, budget around $3,000, just me. I prefer morning flights and I'd like to stay somewhere central.

**Expected Response — Stage 1: Planning**

The assistant presents a travel plan. Check for all of the following:

- Acknowledges the trip: Cairo → Paris, April 10–17, 7 nights
- States total budget ($3,000) and shows a three-way split — a portion for flights, hotels, and activities (approximate split: ~35% flights / ~45% hotels / ~20% activities based on mock data)
- Mentions April weather in Paris: pleasant spring, parks in bloom, ~16°C highs — consistent with mock data
- Notes that April is within the best time to visit window (April–June)
- Names recommended airlines for this route: Air France and EgyptAir (both appear in mock data for CAI→CDG)
- Mentions at least one central neighborhood such as Le Marais or Saint-Germain-des-Pres
- Ends with a question asking the user to approve or adjust the plan

**Must not include:**
- A specific flight booking or hotel booking at this stage
- The user's full $3,000 budget revealed to sub-agents (budget is split internally)

---

## Turn 2

**User:**
> Looks good, let's go with that.

**Expected Response — Stage 2: Selection**

The assistant presents ranked flight and hotel options. Check for all of the following:

**Flights section:**
- Lists up to 3 Cairo → Paris (CAI → CDG) economy flight options
- Each option includes: airline name, flight number, departure/arrival times, duration, number of stops, price in USD, and baggage allowance
- At least one Air France option is listed (present in mock data as CAI-CDG-001, CAI-CDG-005, CAI-CDG-008)
- Prices are within the flight budget slice (not exceeding the allocated flight portion of $3,000)
- Identifies a recommended pick with a brief justification (e.g., best balance of price, timing, and reliability)
- Morning departure options are highlighted given the user's stated preference

**Hotels section:**
- Lists up to 3 Paris hotel options
- Each option includes: hotel name, neighborhood, star rating, guest rating, price per night, total for 7 nights, and key amenities
- Hotels in central areas (Le Marais, Saint-Germain-des-Pres, Latin Quarter) are prioritized given the user's preference
- Total hotel cost is within the hotel budget slice
- Identifies a recommended pick

**Coherence check:**
- If a selected flight arrives late at night, the response notes whether hotel check-in accommodates the arrival time

Ends with a question asking the user to approve both selections, or to reject either/both with feedback.

---

## Turn 3

**User:**
> Both look great. Let's book them.

**Expected Response — Stage 3: Pre-Booking Itinerary**

The assistant presents a complete itinerary and asks for explicit confirmation before booking. Check for all of the following:

- Summarizes the selected flight: airline, flight number, departure and arrival times, price
- Summarizes the selected hotel: name, area, check-in April 10, check-out April 17, total cost
- Shows a cost breakdown: flight cost + hotel cost + estimated remaining budget for activities
- Total cost does not exceed $3,000
- Explicitly asks the user to confirm (e.g., "Shall I go ahead and book?" or "Please confirm to proceed")

**Must not include:**
- Booking confirmation references (no booking has happened yet)

---

## Turn 4

**User:**
> Yes, confirm the booking.

**Expected Response — Booking Confirmation**

The assistant confirms both bookings are complete. Check for all of the following:

- States that the flight has been booked and provides a booking reference (format: any alphanumeric reference string)
- States that the hotel has been booked and provides a booking reference
- Shows the final cost summary: flight cost + hotel cost + remaining budget
- Thanks the user and closes the session

**Must not include:**
- Prompting for another confirmation
- Any mention of an error or failure (both bookings use valid mock IDs)
