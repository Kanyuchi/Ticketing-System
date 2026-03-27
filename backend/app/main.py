from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    analytics, applications, auth, checkin, emails, orders, payments,
    referrals, rewards, sharing, tickets, upgrades, vouchers, waitlist,
)

app = FastAPI(title="Proof of Talk 2026 - Ticketing API", version="0.1.0")

allowed_origins = [
    settings.frontend_url,
    "http://localhost:3000",
]
# Also allow any Netlify preview deploys
if settings.frontend_url and "netlify.app" not in settings.frontend_url:
    allowed_origins.append("https://*.netlify.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(vouchers.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(emails.router, prefix="/api")
app.include_router(upgrades.router, prefix="/api")
app.include_router(referrals.router, prefix="/api")
app.include_router(sharing.router, prefix="/api")
app.include_router(checkin.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(waitlist.router, prefix="/api")
app.include_router(rewards.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
