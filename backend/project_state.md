# Project State — backend

## What's Working
- **Ticket types**: 8 categories (VIP Black, Investor, VIP, General, Startup, Press, Speaker, Partner)
- **Order creation**: Stripe checkout for paid, auto-confirm for complimentary
- **Voucher system**: Bulk generation, validation, single-use claiming
- **Admin dashboard**: 8 tabs — Orders (filters + CSV), Applications (review), Vouchers (generate), Referrals (create + leaderboard), Check-in (scanner + stats), Analytics (KPIs + funnel), Waitlist (filter + notify), Send Email
- **Application flow**: Press/Startup submission, admin approve/reject, auto-voucher on Press approval
- **Email service**: SendGrid with stub fallback (logs when no API key)
- **Ticket upgrades**: Calculate price diff, Stripe checkout for upgrade payment
- **Referral system**: Create codes, track clicks with redirect, attribute orders, leaderboard with conversion rates
- **Referral rewards**: Auto-tier system (Bronze 3+, Silver 5+, Gold 10+ orders) with voucher generation
- **QR codes**: Generated for confirmed orders, encodes check-in URL
- **Social sharing**: "I'm Attending" card generation (PNG), Twitter/LinkedIn share URLs
- **Google Sheets sync**: Order data pushed on creation (stubs without credentials)
- **Check-in system**: Mark attendance by order ID, duplicate prevention, batch offline sync, verify endpoint, stats tracking
- **Waitlist**: Join for sold-out types, position queue, admin notify next-in-line
- **Analytics**: Sales by type, revenue over time, conversion funnel, top referrers dashboard
- **Frontend**: Public ticket grid, application forms, order/application status, QR + social sharing, admin dashboard with 8 tabs
- **Test suite**: 58 tests passing (14 + 14 + 11 + 13 + 6 Stripe e2e)
- **Deploy config**: Dockerfiles for backend + frontend, docker-compose.yml with Postgres
- **Alembic migrations**: Complete initial migration for all 11 tables, env.py reads DB URL from app config
- **Next.js build**: Passes clean (Suspense boundary fix applied)

## What's Not Built Yet
- Alembic migrations (currently tests use SQLite in-memory, prod needs migration files)
- Mobile check-in app (QR scanning with camera, offline mode with IndexedDB)
- Event day live dashboard (real-time check-in rate, capacity gauges)
- Waitlist management for sold-out types
- Multi-currency support (EUR + stablecoin)
- Attendee self-service portal (view/update tickets)
- Referral rewards automation (auto-upgrades based on referral sales)

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
- **Referral attribution at order creation** — `referral_code` field on order schema
- **Reward tiers** — 3/5/10 order thresholds with auto-voucher generation
- **Check-in is per-order** (not per-attendee) — one QR code per order

## Current Focus
- All phases complete — 58/58 tests passing
- Next: production deployment (Docker Compose, real Stripe/SendGrid keys, DNS + SSL)
