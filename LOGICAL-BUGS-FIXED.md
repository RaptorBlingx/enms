# Logical Bugs Fixed

## 1. Type Mismatch in `get_machine_operating_hours`
- **Issue**: The API `/api/v1/machines/status/{id}` was returning `500 Internal Server Error`.
- **Cause**: The SQL function `get_machine_operating_hours` had a type mismatch. `COUNT(*)` returns `BIGINT`, but the function signature defined the return columns as `DECIMAL`.
- **Fix**: Added explicit casting `::DECIMAL` to the `COUNT(*)` results in `database/init/04-functions.sql`.

## 2. Data Inconsistency in Factory Summary
- **Issue**: The Factory Summary (`/api/v1/factory/summary`) reported significantly lower total energy (~600 kWh) than the Top Consumers endpoint (~16,000 kWh).
- **Symptom**: This caused the "Top Consumer" percentage to be > 100% (e.g., 2300%), which is mathematically impossible.
- **Cause**: `get_factory_summary` was querying the `energy_readings_1hour` continuous aggregate view, which may not be up-to-the-second or was missing recent data. The manual queries in the API were hitting the raw `energy_readings` table.
- **Fix**: Updated `get_factory_summary` in `database/init/04-functions.sql` to query the raw `energy_readings` table for the "Today" view. This ensures consistency with other real-time endpoints.

## 3. Hardcoded Tariff Logic Removed
- **Issue**: Previous logic assumed a fixed rate of $0.15/kWh.
- **Fix**: Verified that the system now correctly calculates costs based on dynamic tariffs (Peak: $0.25, Off-Peak: $0.10). The effective average rate observed is ~$0.175/kWh, which is correct.

## Verification
A script `scripts/verify_api_logic.py` was created and passed all checks:
- Factory Summary Energy & Cost: Consistent and Reasonable.
- Machine Status: Uptime and Cost logic valid.
- Top Consumers: Percentages sum to <= 100%.
