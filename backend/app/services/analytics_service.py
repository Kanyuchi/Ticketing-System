from sqlalchemy import func, select, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkin import CheckIn
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.referral import Referral
from app.models.ticket_type import TicketType


async def get_sales_by_type(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(TicketType).order_by(TicketType.sort_order))
    types = result.scalars().all()
    out = []
    for tt in types:
        # Calculate revenue from confirmed order items
        rev_result = await db.execute(
            select(func.coalesce(func.sum(OrderItem.unit_price_eur * OrderItem.quantity), 0))
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                OrderItem.ticket_type_id == tt.id,
                Order.status == OrderStatus.CONFIRMED,
            )
        )
        revenue = rev_result.scalar() or 0
        out.append({
            "ticket_type": tt.name,
            "category": tt.category.value,
            "quantity_sold": tt.quantity_sold,
            "quantity_total": tt.quantity_total,
            "revenue_eur": revenue,
        })
    return out


async def get_revenue_over_time(db: AsyncSession) -> list[dict]:
    """Daily revenue for confirmed orders."""
    result = await db.execute(
        select(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total_eur).label("revenue"),
            func.count(Order.id).label("count"),
        )
        .where(Order.status == OrderStatus.CONFIRMED)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )
    rows = result.all()
    return [
        {"date": str(row.date), "revenue_eur": row.revenue or 0, "order_count": row.count}
        for row in rows
    ]


async def get_conversion_funnel(db: AsyncSession) -> dict:
    """Funnel: referral clicks → orders → confirmed → checked in."""
    clicks_result = await db.execute(select(func.coalesce(func.sum(Referral.clicks), 0)))
    total_visits = clicks_result.scalar() or 0

    orders_result = await db.execute(select(func.count()).select_from(Order))
    total_orders = orders_result.scalar() or 0

    confirmed_result = await db.execute(
        select(func.count()).select_from(Order).where(Order.status == OrderStatus.CONFIRMED)
    )
    total_confirmed = confirmed_result.scalar() or 0

    checkin_result = await db.execute(select(func.count()).select_from(CheckIn))
    total_checked_in = checkin_result.scalar() or 0

    return {
        "total_visits": total_visits,
        "total_orders": total_orders,
        "total_confirmed": total_confirmed,
        "total_checked_in": total_checked_in,
        "visit_to_order_rate": total_orders / total_visits if total_visits > 0 else 0.0,
        "order_to_confirmed_rate": total_confirmed / total_orders if total_orders > 0 else 0.0,
    }


async def get_top_referrers(db: AsyncSession, limit: int = 10) -> list[dict]:
    result = await db.execute(
        select(Referral)
        .where(Referral.orders_count > 0)
        .order_by(Referral.revenue_eur.desc())
        .limit(limit)
    )
    refs = result.scalars().all()
    return [
        {
            "code": r.code,
            "owner_name": r.owner_name,
            "orders_count": r.orders_count,
            "revenue_eur": r.revenue_eur,
            "conversion_rate": r.orders_count / r.clicks if r.clicks > 0 else 0.0,
        }
        for r in refs
    ]


async def get_dashboard(db: AsyncSession) -> dict:
    """Full analytics dashboard payload."""
    sales = await get_sales_by_type(db)
    revenue_time = await get_revenue_over_time(db)
    funnel = await get_conversion_funnel(db)
    top_refs = await get_top_referrers(db)

    total_revenue = sum(s["revenue_eur"] for s in sales)
    total_orders_result = await db.execute(select(func.count()).select_from(Order))
    total_orders = total_orders_result.scalar() or 0

    return {
        "total_revenue_eur": total_revenue,
        "total_orders": total_orders,
        "total_confirmed": funnel["total_confirmed"],
        "total_checked_in": funnel["total_checked_in"],
        "sales_by_type": sales,
        "revenue_over_time": revenue_time,
        "funnel": funnel,
        "top_referrers": top_refs,
    }
