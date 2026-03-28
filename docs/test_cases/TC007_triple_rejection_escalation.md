# TC007 — Triple Rejection Escalation

**Stages:** 2 (Selection) — 3 consecutive rejections of the hotel
**Destination:** Cairo → Paris
**Budget:** $1,500 total, 5 nights
**Focus:** The hotel is rejected three times in a row. After the third rejection, the orchestrator must escalate rather than re-running the hotel agent again — it should suggest adjusting upstream inputs (budget, dates, or destination).

---

## Setup — Turns 1 and 2 (Abbreviated)

These turns establish Stage 1 approval and initial Stage 2 presentation. Run them as prerequisites before starting the escalation test.

**Turn 1 — User:**
> I want to go to Paris from Cairo for 5 nights in January. My total budget is $1,500. Budget travel, just flights and a cheap place to stay.

**Turn 1 — Expected Response:** A budget-tier travel plan. January weather noted as cold/grey ($90/night budget hotel avg in mock data). Budget split ~35% flights ($525), ~45% hotels ($675 / 5 nights = $135/night ceiling), ~20% activities ($300). Ends with approval question.

**Turn 2 — User:** `Approved.`

**Turn 2 — Expected Response:** Flights (CAI→CDG within $525: Turkish Airlines TK693 at $420 and Transavia TO3452 at $390 are within range) and hotel options (within $675 total/$135/night: Le Relais Montmartre $110/night, Hotel des Nations Latin Quarter $85/night, Generator Paris $65/night, Hotel Caron de Beaumarchais $155/night is slightly over). Ends with approval question.

---

## Turn 3 — First Hotel Rejection

**User:**
> The flight is fine. But I don't want any of those hotels — I need breakfast included.

**Expected Response — Hotel Retry #1**

- Confirms flight is approved and locked in
- Re-presents hotels with "breakfast included" constraint applied
- From mock data, Paris hotels with breakfast_included:
  - Hotel du Petit Moulin ($185/night × 5 = $925 total) — exceeds $675 ceiling
  - Hotel Saint-Germain ($220/night × 5 = $1,100 total) — exceeds ceiling
  - Sofitel Paris Le Faubourg ($420/night × 5 = $2,100 total) — far exceeds ceiling
  - Maison Souquet ($380/night × 5 = $1,900 total) — far exceeds ceiling
- All breakfast-included options exceed the hotel budget slice
- The assistant should communicate the conflict: no hotels with breakfast included exist within the $675 hotel ceiling, and present the nearest options with a note about the constraint
- Offers alternatives (e.g., hotels with "breakfast_available" that can be added separately, or acknowledges the budget gap)
- Ends by asking if the user wants to continue or adjust

---

## Turn 4 — Second Hotel Rejection

**User:**
> I still want breakfast included. Find something that works.

**Expected Response — Hotel Retry #2**

- Acknowledges the continued constraint
- Re-presents available breakfast-included options, acknowledging they exceed the budget ceiling
- May note the cheapest breakfast-included option: Hotel du Petit Moulin at $185/night ($925 total — $250 over the hotel slice)
- Does not drop the breakfast-included constraint
- Does not re-present hotels without breakfast as satisfying the requirement
- Ends by asking how the user would like to proceed

---

## Turn 5 — Third Hotel Rejection

**User:**
> This still isn't what I want. I need something central, with breakfast, and within my budget.

**Expected Response — Escalation (No fourth retry)**

After the third consecutive rejection of the same selection stage, the assistant must escalate rather than re-running the agent again. Check for all of the following:

- Explicitly acknowledges that the system has tried multiple times and cannot find a hotel meeting all the stated criteria within the current budget allocation
- Does NOT simply re-present the same options again
- Suggests at least one upstream adjustment to resolve the conflict, such as:
  - **Increase total budget:** e.g., "Adding $250–$300 to the budget would unlock breakfast-included options in the Latin Quarter"
  - **Reduce trip length:** e.g., "Cutting to 4 nights would lower the hotel ceiling to fit Hotel du Petit Moulin"
  - **Reallocate budget:** e.g., "Shifting $200 from the activities budget to hotels would bring Le Relais Montmartre into range if they add breakfast"
  - **Change destination:** e.g., "Istanbul has central, breakfast-included hotels well within a $1,500 budget"
- Does not book anything or proceed without user direction

**Must not include:**
- A fourth hotel agent re-run with the same constraints
- Presenting hotels without breakfast as "close enough"
- Completing the booking without resolving the constraint
