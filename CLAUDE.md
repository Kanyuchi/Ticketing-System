# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Ticketing system for **Proof of Talk 2026** — an event ticketing platform with multiple ticket types (VIP Black, Investor, VIP, General, Startup, Press, Speaker, Partner), voucher codes, Stripe payments, and an admin dashboard.

## Architecture

**Monorepo** with two main directories:

- `backend/` — Python FastAPI + SQLAlchemy (async) + PostgreSQL
- `frontend/` — Next.js 16 + Tailwind CSS + TypeScript

### Backend Structure
- `app/core/` — Config (pydantic-settings), database engine, security (bcrypt + JWT), custom GUID type
- `app/models/` — SQLAlchemy ORM: TicketType, Order, OrderItem, Attendee, Voucher, AdminUser, Application, Referral, ReferralAttribution, CheckIn, WaitlistEntry
- `app/schemas/` — Pydantic request/response models
- `app/services/` — Business logic (orders, vouchers, applications, email, upgrades, referrals, QR, sheets, check-in, analytics, waitlist, rewards)
- `app/routers/` — FastAPI routes: auth, tickets, orders, vouchers, payments, applications, emails, upgrades, referrals, sharing, checkin, analytics, waitlist, rewards
- `app/core/types.py` — Custom `GUID` type for cross-database UUID compatibility (Postgres native UUID, SQLite CHAR(32))

### Key Design Decisions
- All prices stored in **EUR cents** (integer) — no floats for money
- Complimentary tickets (Speaker, Partner, Press) auto-confirm with `payment_status=complimentary`
- Voucher codes are generated with customizable prefixes (e.g., `POT26-XXXXXX`)
- Orders route through Stripe checkout for paid tickets; complimentary orders skip Stripe
- Admin auth uses JWT tokens; attendees use minimal-friction flow (name + email, no full account)

## Commands

### Backend
```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt aiosqlite greenlet

# Run tests (uses in-memory SQLite, no Postgres needed)
python -m pytest tests/ -v

# Run single test
python -m pytest tests/test_smoke.py::test_create_order_paid -v

# Run server (requires Postgres)
uvicorn app.main:app --reload

# Seed database
python seed.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

## Build Phases

The system is being built in phases. Each phase gets smoke tests before moving to the next.

- **Phase 1 (DONE)**: Core ticket types, order creation, Stripe integration, admin dashboard with filters, CSV export, voucher system (14 tests)
- **Phase 2 (DONE)**: Application flow (Startup/Press), email system, in-order upgrades (14 tests)
- **Phase 3 (DONE)**: Referral system, social sharing, QR codes, Google Sheets sync (11 tests)
- **Phase 4 (DONE)**: Mobile check-in, analytics dashboard, waitlist management, referral rewards, Docker deploy setup (13 tests)

## Testing

Tests use `aiosqlite` in-memory DB to avoid requiring Postgres. The custom `GUID` type in `app/core/types.py` handles UUID portability between Postgres and SQLite.

Default admin credentials for seed: `admin@proofoftalk.io` / `changeme123`
