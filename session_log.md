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

## 2026-03-26 21:30 — Phase 2: Applications, Email, Upgrades
- Added Application model with Press-specific fields (publication, portfolio_url) and Startup-specific fields (startup_name, website, stage)
- Built application service: submit, review (approve/reject), duplicate detection, auto-voucher generation for complimentary passes on approval
- Created email service with SendGrid integration (falls back to logging in dev): order confirmation, application received/approved/rejected, custom admin emails
- Built ticket upgrade service: calculate price difference, Stripe checkout for upgrade payment, Stripe webhook handles upgrade completion
- Extended admin dashboard with tabbed UI: Orders, Applications (review with approve/reject), Vouchers, Send Email
- Created public application form pages at /apply/[ticketTypeId] with Press and Startup-specific fields
- Created application status page at /application/[id] showing approval status and voucher code
- Wired "Apply Now" buttons on ticket cards to route to application forms
- Added email triggers: application submission sends confirmation, approval sends voucher/purchase link, rejection sends notification with reason
- Wrote 14 Phase 2 smoke tests: application submission (Press/Startup), duplicate rejection, type validation, approval with voucher generation, rejection with reason, double-review prevention, admin listing, auth guards, custom email sending, upgrade calculation, downgrade prevention
- All 28 tests passing (14 Phase 1 + 14 Phase 2)
