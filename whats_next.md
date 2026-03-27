# What's Next

## Original Goal
Build a complete ticketing system for Proof of Talk 2026 with 8 ticket types, admin dashboard, Stripe payments, voucher codes, referral tracking, email comms, and mobile check-in.

## Done
- Phase 1: Project scaffold, DB models, API routes, Stripe integration, admin dashboard, voucher system (14 tests)
- Phase 2: Application flow (Press/Startup), email service (SendGrid), in-order upgrades (14 tests)
- Phase 3: Referral tracking + leaderboard, QR codes, social sharing cards, Google Sheets sync (11 tests)
- Phase 4: Mobile check-in, analytics dashboard, waitlist management, referral rewards, Docker deploy setup (13 tests)
- Production readiness: Next.js build fix, Alembic migrations, seed script update, Stripe e2e tests (6 tests)
- Supabase Postgres: connected, migrated, seeded — enum values_callable fix for Postgres compatibility
- Custom PDF invoices: branded A4 invoices with reportlab, download from order page + admin dashboard (4 tests)

## Now
1. Deploy backend to production (Railway / Render / VPS)
2. Deploy frontend to Vercel
3. Configure Stripe webhook endpoint + secret
4. Configure SendGrid for production emails
5. DNS + SSL setup for tickets.proofoftalk.io

## Soon
- Multi-currency support (EUR + stablecoin)
- Attendee self-service portal (view/transfer tickets)
- Batch email campaigns from admin

## Later
- Event day live dashboard (check-in rate, capacity)
- Post-event feedback collection
- Multi-event support (reusable platform)
