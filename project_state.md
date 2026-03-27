# Project State

## What's Working
- **Backend API**: All Phase 1 + 2 + 3 endpoints operational
- **Order flow**: Paid and complimentary orders with proper status handling
- **Voucher system**: Bulk generation, validation, single-use claiming
- **Application system**: Submit for Press/Startup, admin review, auto-voucher on Press approval
- **Email service**: SendGrid integration with templates (stubs without API key)
- **Ticket upgrades**: Calculate price diff, Stripe checkout for upgrade payment
- **Referral system**: Create codes, track clicks with redirect, attribute orders, leaderboard with conversion rates
- **QR codes**: Generated for confirmed orders, encodes check-in URL
- **Social sharing**: "I'm Attending" card generation (PNG), Twitter/LinkedIn share URLs
- **Google Sheets sync**: Order data pushed on creation (stubs without credentials)
- **Admin dashboard**: 5 tabs — Orders (filters + CSV), Applications (review), Vouchers (generate), Referrals (create + leaderboard), Send Email
- **Frontend**: Public ticket grid, application forms, order/application status, QR + social sharing on confirmed orders
- **Test suite**: 39 smoke tests passing (14 + 14 + 11)

## What's Not Built Yet
- Mobile check-in app (QR scanning, offline mode)
- Analytics dashboard (sales by type, conversion rates, revenue forecasting)
- Waitlist management for sold-out ticket types
- Multi-currency support (EUR + stablecoin)
- Attendee self-service portal
- Referral rewards automation (sell X → auto-upgrade)

## What Needs Setup Before Running
- PostgreSQL database for non-test usage
- Stripe API keys in `.env`
- SendGrid API key in `.env` (optional)
- Google service account JSON + Sheet ID in `.env` (optional)
- `frontend/.env.local` with `NEXT_PUBLIC_API_URL`

## Key Decisions
- **EUR cents as integers** for all prices
- **Python 3.12** required
- **Custom GUID type** for cross-database UUID portability
- **Direct bcrypt** instead of passlib
- **Phased build** with smoke tests gating each phase
- **Stub pattern** for external services (email, sheets) — log instead of send when unconfigured
- **Referral attribution at order creation** — `referral_code` field on order schema, stored in session storage on frontend
