# What's Next

## Original Goal
Build a complete ticketing system for Proof of Talk 2026 with 8 ticket types, admin dashboard, Stripe payments, voucher codes, referral tracking, email comms, and mobile check-in.

## Done
- Phase 1 MVP: project scaffold, DB models, API routes, Stripe integration, admin dashboard, voucher system, 14 passing smoke tests

## Now
1. Set up PostgreSQL and run `seed.py` to verify full stack end-to-end
2. Start Phase 2: Application flow for Startup Pass (form + payment) and Press Pass (form only, approval → code)
3. Build email service (SendGrid integration for confirmations, voucher delivery)
4. Add in-order upsell/upgrade functionality (upgrade within same order, discount code on price diff)
5. Write Phase 2 smoke tests

## Soon
- Referral tracking system with unique links/codes
- Social sharing with custom "I'm Attending" cards
- Google Sheets API integration for live sales sync

## Later
- Mobile check-in app (QR scanning, offline mode)
- Analytics dashboard (sales by type, conversion rates, revenue forecasting)
- Waitlist management for sold-out ticket types
- Multi-currency support (EUR + stablecoin)
- Attendee self-service portal
