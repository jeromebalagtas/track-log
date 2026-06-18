# FMCSA Hours of Service Rules (Assessment Scope)

Source: *Interstate Truck Driver's Guide to Hours of Service* (FMCSA, April 2022, 49 CFR Part 395).

## Who must comply

Drivers of commercial motor vehicles (CMVs) in interstate commerce, and intrastate if state adopted federal rules.

## Property-carrying limits (implemented)

| Rule | Limit | Code reference |
|------|-------|----------------|
| Driving limit | 11 hours after 10 consecutive hours off duty | 395.3(a)(1) |
| Driving window | May not drive after 14th hour after coming on duty | 395.3(a)(2) |
| Rest break | 30 minutes off duty after 8 hours driving | 395.3(a)(3)(ii) |
| Daily rest | 10 consecutive hours off duty before next shift | 395.3(a)(1) |
| 70-hour / 8-day | Max 70 hours on duty in any 8 consecutive days | 395.3(b)(2) |

**On-duty time** = driving + on-duty not driving (loading, fueling, inspections).

**Off-duty** = rest periods; **sleeper berth** used for 10-hour resets in this app.

## 70-hour / 8-day rolling calculation

Per paper log recap section:

- **A.** Total on-duty hours last 7 days including today
- **B.** Hours available tomorrow = 70 − A
- **C.** Total on-duty hours last 8 days including today

If driver took a **34-hour restart**, cycle resets to 60/70 hours available (not auto-applied in planner unless user sets `cycle_used_hours` to 0 after restart).

## Driver's Daily Log — required fields

1. Date, route (from/to), mileage
2. **Graph grid** — 24 hours, 15-minute increments, four rows:
   - Off Duty
   - Sleeper Berth
   - Driving
   - On Duty (not driving)
3. **Remarks** — location and time of each duty status change (home terminal time)
4. **Recap** — 70/8 or 60/7 totals

## Assessment-specific assumptions

- Average road speed: **55 mph** (when converting miles to drive time)
- Fuel stop: **30 min on-duty** every **1,000 miles**
- Pickup: **1 hr on-duty** at pickup location
- Dropoff: **1 hr on-duty** at dropoff location
- Trip starts **6:00 AM** local unless overridden
- No adverse driving extension (+2 hr drive / +2 hr window)
- No short-haul exceptions

## Sleeper berth provision (simplified)

Full split sleeper rules (7+3, 8+2, etc.) are not implemented. The app uses a single **10-hour sleeper berth** rest to reset the 11-hour and 14-hour clocks.

## Not in scope

- Adverse driving conditions exception
- CDL / non-CDL short-haul exceptions
- 16-hour short-haul exception
- Passenger-carrying limits (10 hr drive / 15 hr window)
- ELD hardware / FMCSA registered device output format
