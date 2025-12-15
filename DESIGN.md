# Meeting Room Booking Service – Design Document

## 1. Data Model (PostgreSQL)
*   **`rooms`**: `id` (PK, Serial), `name` (Unique, Case-insensitive), `capacity` (>=1), `amenities` (Array of Strings).
*   **`bookings`**: `id` (PK), `room_id` (FK), `title`, `organizer_email`, `start_time` (Timestamp), `end_time`, `status` (`confirmed`/`cancelled`).
*   **`idempotency_keys`**: `key`, `organizer_email` (Composite PK), `response_status`, `response_body`. Stores results of previous requests to enable safe retries.

## 2. Input Validation (Controller Layer)
All input validation is centralized in the Controller layer to ensure a "fail-fast" mechanism:
*   **Schema Validation**: REST payloads are validated against rigid JSON Schemas (`helpers/schemas.py`) before processing (e.g., types, required fields, format).
*   **Business Rules**: Controllers enforce logic such as date ranges (Start < End), booking durations (15m–4h), and business hours (Mon-Fri 08:00–20:00).
*   **Type Safety**: Query parameters are explicitly cast and validated (e.g., `booking_id >= 1`, `amenities` list).

## 3. Concurrency & Overlap Prevention
We strictly prevent double-bookings using **Database transactions and Row-Level Locking**:
1.  Start Transaction.
2.  **Lock Room**: `SELECT ... FROM rooms WHERE id = ? FOR UPDATE`. This serializes all booking attempts for a specific room.
3.  **Check Overlap**: Query active bookings for the room that overlap with the requested time range (`start < requested_end AND end > requested_start`).
4.  **Insert**: If no overlap, insert the new booking.
5.  Commit.

## 4. Idempotency Implementation
Guarantees strict "exactly-once" processing using the `Idempotency-Key` header:
1.  **Insert Key**: We attempt to insert `(key, organizer)` into `idempotency_keys`.
2.  **On Conflict**: If the key exists, we fetch the stored `response_body` and return it immediately (replay).
3.  **New Request**: If insertion succeeds (or we own the lock), we process the booking.
4.  **Save Result**: The final HTTP response is saved to the `idempotency_keys` table before committing the transaction.

## 5. Error Handling Strategy
Exceptions are caught at the service layer and mapped to standardized JSON responses:
*   **400 Bad Request**: Validation failures (Schema violations, past dates, logic errors).
*   **404 Not Found**: Unknown resource (Room not found).
*   **409 Conflict**: Logic conflict (Double booking, Overlap).
*   **500 Internal Error**: Unexpected server faults.

## 6. Room Utilization Calculation
Calculates the efficiency of room usage for a given time range.

**Formula**:
```
Utilization = (Total Duration of Confirmed Bookings overlapping Range) / (Total Business Hours in Range)
```

**Assumptions & Rules**:
*   **Business Hours**: Monday–Friday, 08:00–20:00 (12 hours/day).
*   **Time Range**: Only the intersection of the booking and the requested report range is counted.
*   **Exclusions**: Weekends and non-business hours are excluded from the denominator. Cancelled bookings are ignored.
