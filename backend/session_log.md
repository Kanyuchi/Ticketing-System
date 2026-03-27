# Session Log — backend

## 2026-03-26 22:33 — Project initialised
- Documentation files created by Claude Code hook

## 2026-03-27 10:30 — Phase 4: Check-in, analytics, waitlist, rewards, deploy
- Added CheckIn model + service + router — check in attendees by order ID, batch offline sync, verify endpoint, stats (rate tracking)
- Added WaitlistEntry model + service + router — join waitlist for sold-out types, leave, admin notify next-in-line
- Added analytics service + router — sales by type, revenue over time, conversion funnel, top referrers, full dashboard endpoint
- Added rewards service + router — auto-reward referrers at 3/5/10 order tiers with voucher codes, status endpoint, public tiers list
- Added Docker setup — Dockerfiles for backend + frontend, docker-compose.yml with Postgres, .env.example
- Updated admin dashboard with 3 new tabs: Check-in (scanner + stats + list), Analytics (KPIs + sales table + funnel + top referrers), Waitlist (filter + notify)
- Added API client functions for all new endpoints
- 13 new Phase 4 smoke tests — 52/52 total passing across all phases
- Registered 4 new routers in main.py: checkin, analytics, waitlist, rewards

## 2026-03-27 11:15 — Production readiness: build fix, migrations, seed, Stripe tests
- Fixed Next.js build error: wrapped useSearchParams in Suspense boundary on home page
- Set up Alembic migrations: updated alembic.ini to pull DB URL from app config (async→sync conversion), wrote complete initial migration covering all 11 tables with proper Postgres UUID types
- Updated seed.py: added quantity_total limits for ticket types (VIP Black: 50, Investor: 100, VIP: 200, General: 500, Startup: 100, Press: 50), added demo referral code, imported all models for create_all
- Added 6 Stripe end-to-end tests: checkout creation, complimentary rejection, nonexistent order 404, webhook signature validation, paid order lifecycle, complimentary auto-confirm
- 58/58 tests passing across all phases + Stripe e2e

## 2026-03-27 14:30 — Custom PDF invoice feature
- Built invoice_service.py with reportlab — branded A4 PDF with company header, invoice meta, bill-to section, line items table, subtotal/VAT/total, footer
- Added GET /api/orders/{id}/invoice endpoint on orders router — returns PDF for confirmed orders, rejects pending/nonexistent
- Updated frontend order page with "Download Invoice (PDF)" button for confirmed orders
- Updated admin orders table with Invoice column (PDF link for confirmed orders)
- Added reportlab to requirements.txt
- 4 invoice tests (confirmed order, pending rejected, nonexistent, voucher order)
- 62/62 tests passing

## 2026-03-27 15:00 — Deployment config: Render + Netlify
- Created render.yaml blueprint for backend (Python 3.12, Frankfurt region, env vars)
- Created backend/build.sh — pip install + alembic migrate + seed (idempotent)
- Created frontend/netlify.toml with @netlify/plugin-nextjs
- Updated config.py with model_validator to normalize DATABASE_URL (postgres:// → postgresql+asyncpg://)
- Updated CORS in main.py to allow Netlify preview deploys via allow_origin_regex
- Generated production JWT secret
- 62/62 tests still passing
