# Project State

## What's Working
- **Backend API**: All Phase 1 endpoints operational (tickets, orders, vouchers, auth, payments)
- **Order flow**: Paid and complimentary orders create correctly with proper status handling
- **Voucher system**: Bulk generation with custom prefixes, validation, single-use claiming
- **Admin dashboard**: JWT-protected order listing with 7 filter columns + CSV export
- **Frontend**: Public ticket grid, order detail page, admin login + dashboard
- **Test suite**: 14 smoke tests passing against in-memory SQLite

## What's Not Built Yet
- Application flow for Startup/Press passes (Phase 2)
- Email system (Phase 2)
- In-order ticket upgrades (Phase 2)
- Referral tracking + social sharing (Phase 3)
- Google Sheets live sync (Phase 3)
- Mobile check-in app (Phase 3)
- Analytics dashboard (Phase 3)

## What Needs Setup Before Running
- PostgreSQL database for non-test usage
- Stripe API keys in `.env`
- `frontend/.env.local` with `NEXT_PUBLIC_API_URL`

## Key Decisions
- **EUR cents as integers** for all prices — no floating point money
- **Python 3.12** required (3.14 breaks pydantic-core wheel build)
- **Custom GUID type** instead of PostgreSQL-specific UUID — enables SQLite testing
- **Direct bcrypt** instead of passlib — passlib incompatible with bcrypt 5.x
- **Phased build** — smoke test each phase before proceeding
