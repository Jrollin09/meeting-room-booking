# Meeting Room Booking Service

A Flask-based REST API for managing meeting room bookings, built with PostgreSQL.

## Features
- **Create & List Rooms**: Manage rooms with capacity and amenities.
- **Bookings**: Create bookings with conflict detection and business hour rules.
- **Strict Validation**: JSON Schema validation for all inputs, ensuring data integrity & preventing logic errors.
- **Idempotency**: Safe retries for booking creation using `Idempotency-Key` header.
- **Reporting**: Calculate room utilization.
- **Cancellation**: Cancel bookings with grace period rules.

## Setup

1. **Prerequisites**: Python 3.13+, PostgreSQL running locally.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Database**:
   Ensure Postgres is running on `localhost:5432` with user `postgres`, password `postgres`, and db `postgres`.
   Or set `DATABASE_URL` environment variable.
   
## Running the Application

```bash
python app.py
```
The server starts at `http://0.0.0.0:5000`.

## Running Tests

Tests are configured to use the Postgres database defined in `TEST_DATABASE_URL`.

```bash
export TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
pytest tests -v
```

**Note**: The test suite **truncates tables** in the target database. Do not run against production!

### Running Tests
We maintain a consolidated integration test suite in `tests/test_api.py` covering:
*   **Success Scenarios**: Happy paths for all endpoints.
*   **Validation**: Schema checks, type safety, invalid logic (past dates, etc.).
*   **Consistency**: Idempotency and business rule enforcement.

```bash
pytest tests/test_api.py -v
```
