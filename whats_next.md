# What's Next

## Original Goal
Build a complete ticketing system for Proof of Talk 2026 with 8 ticket types, admin dashboard, Stripe payments, voucher codes, referral tracking, email comms, and mobile check-in.

## Done
- Phase 1: Project scaffold, DB models, API routes, Stripe integration, admin dashboard, voucher system (14 tests)
- Phase 2: Application flow (Press/Startup), email service (SendGrid), in-order upgrades (14 tests)
- Phase 3: Referral tracking + leaderboard, QR codes, social sharing cards, Google Sheets sync (11 tests)

## Now
1. Mobile check-in app: QR scanner page, mark attendance, offline mode
2. Analytics dashboard: sales by type, revenue over time, conversion funnel
3. Referral rewards automation (sell X tickets → auto-upgrade ambassador)
4. Waitlist management for sold-out ticket types
5. Deploy to production (Docker compose, env setup)

## Soon
- Multi-currency support (EUR + stablecoin)
- Attendee self-service portal (view/transfer tickets)
- Batch email campaigns from admin

## Later
- Event day live dashboard (check-in rate, capacity)
- Post-event feedback collection
- Multi-event support (reusable platform)
