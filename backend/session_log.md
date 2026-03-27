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
