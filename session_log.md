# Session Log

## 2026-03-26 20:15 — Phase 1 MVP: Full project scaffold + backend + frontend + tests
- Initialized git repo with monorepo structure: `backend/` (FastAPI) + `frontend/` (Next.js)
- Built backend: SQLAlchemy async models (TicketType, Order, OrderItem, Attendee, Voucher, AdminUser)
- Created custom GUID type for cross-database UUID compatibility (Postgres + SQLite)
- Implemented API routes: auth (JWT), tickets (CRUD), orders (create/list/filter), vouchers (bulk create/validate), payments (Stripe checkout + webhook)
- Built order service with full business logic: attendee upsert, voucher claiming, complimentary auto-confirm, inventory tracking
- Created frontend: public ticket grid (matching Proof of Talk design), order confirmation page, admin dashboard with filters, CSV export, voucher generator
- Wrote 14 smoke tests covering: health, ticket listing, paid/complimentary order creation, order lookup, admin login/auth, filtered order listing, CSV export, voucher bulk creation, voucher validation + claiming, invalid voucher rejection
- All 14 tests passing
- Fixed passlib/bcrypt 5.x incompatibility by switching to direct bcrypt usage
- Fixed PostgreSQL UUID type portability by creating custom GUID TypeDecorator
