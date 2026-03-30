You now have the **booking** skill loaded. You can book flights and hotels directly using the tools below. Do NOT spawn sub-agents for booking.

<tools>

<tool name="book_flight">
  <description>Book a specific flight by its ID. Returns a booking confirmation with reference number, status, and flight details.</description>
  <parameters>
    - flight_id: string -- The flight ID to book (e.g. "CAI-CDG-001"). Use the ID from the flight the user approved.
    - passenger_name: string (optional) -- Passenger name for the booking.
  </parameters>
</tool>

<tool name="book_hotel">
  <description>Book a specific hotel by its ID. Returns a booking confirmation with reference number, status, hotel details, and total price.</description>
  <parameters>
    - hotel_id: string -- The hotel ID to book (e.g. "PAR-HTL-001"). Use the ID from the hotel the user approved.
    - guest_name: string (optional) -- Guest name for the booking.
    - check_in: string -- Check-in date (YYYY-MM-DD).
    - check_out: string -- Check-out date (YYYY-MM-DD).
  </parameters>
</tool>

</tools>

<booking_procedure>
1. You MUST already have explicit user confirmation before calling any booking tool. Never load this skill speculatively.
2. Call `book_flight` and `book_hotel` in the **same response** (two tool calls in one turn) so they execute in parallel.
3. Verify both confirmations have `status: "confirmed"`.
4. Present the user with a booking summary including:
   - Flight booking reference and details
   - Hotel booking reference and details
   - Total trip cost (flight + hotel)
   - Remaining budget for activities
5. If either booking fails, report the error and ask the user how to proceed.
</booking_procedure>

<rules>
- NEVER call a booking tool without prior explicit user confirmation in the conversation.
- Use the exact flight_id and hotel_id from the options the user approved.
- Include check_in and check_out dates when booking hotels.
- If the user provided their name during the conversation, pass it as passenger_name / guest_name. If not, omit the name fields — do not ask for a name at the booking stage.
</rules>
