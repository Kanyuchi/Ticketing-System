# What's Next

## Original Goal
Build a complete ticketing system for Proof of Talk 2026 with 8 ticket types, admin dashboard, Stripe payments, voucher codes, referral tracking, email comms, and mobile check-in.

## Done
- Phase 1: Project scaffold, DB models, API routes, Stripe integration, admin dashboard, voucher system (14 tests)
- Phase 2: Application flow (Press/Startup), email service (SendGrid), in-order upgrades (14 tests)
- Phase 3: Referral tracking + leaderboard, QR codes, social sharing cards, Google Sheets sync (11 tests)
- Phase 4: Mobile check-in, analytics dashboard, waitlist management, referral rewards automation, Docker deploy setup (13 tests)

## Now
1. Fix Next.js build: wrap `useSearchParams` on home page in Suspense boundary
2. Alembic migrations for production DB schema
3. Seed script update for new models (check-in, waitlist tables)
4. End-to-end manual test with real Stripe keys
5. Production deployment (Docker Compose on VPS/cloud)

## Soon
- Multi-currency support (EUR + stablecoin)
- Attendee self-service portal (view/transfer tickets)
- Batch email campaigns from admin

## Later
- Event day live dashboard (check-in rate, capacity)
- Post-event feedback collection
- Multi-event support (reusable platform)
