# Project State

## What's Working
- **Backend API**: All Phase 1 + Phase 2 endpoints operational
- **Order flow**: Paid and complimentary orders with proper status handling
- **Voucher system**: Bulk generation, validation, single-use claiming
- **Application system**: Submit for Press/Startup, admin review (approve/reject), auto-voucher on Press approval
- **Email service**: SendGrid integration with templates for confirmations, approvals, rejections, custom admin emails (falls back to logging without API key)
- **Ticket upgrades**: Calculate price diff, Stripe checkout for upgrade payment
- **Admin dashboard**: Tabbed UI — Orders (filters + CSV), Applications (review), Vouchers (generate), Send Email
- **Frontend**: Public ticket grid, application forms, order/application status pages
- **Test suite**: 28 smoke tests passing (14 Phase 1 + 14 Phase 2)

## What's Not Built Yet
- Referral tracking + social sharing (Phase 3)
- Google Sheets live sync (Phase 3)
- Mobile check-in app (Phase 3)
- Analytics dashboard (Phase 3)
- Waitlist management
- Multi-currency support
- Attendee self-service portal

## What Needs Setup Before Running
- PostgreSQL database for non-test usage
- Stripe API keys in `.env`
- SendGrid API key in `.env` (optional — stubs without it)
- `frontend/.env.local` with `NEXT_PUBLIC_API_URL`

## Key Decisions
- **EUR cents as integers** for all prices — no floating point money
- **Python 3.12** required (3.14 breaks pydantic-core wheel build)
- **Custom GUID type** instead of PostgreSQL-specific UUID — enables SQLite testing
- **Direct bcrypt** instead of passlib — passlib incompatible with bcrypt 5.x
- **Phased build** — smoke test each phase before proceeding
- **Email stub pattern** — email service logs instead of sending when no API key is set
