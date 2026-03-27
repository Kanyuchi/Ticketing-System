from pydantic import BaseModel


class SalesByType(BaseModel):
    ticket_type: str
    category: str
    quantity_sold: int
    quantity_total: int | None
    revenue_eur: int  # cents


class RevenueOverTime(BaseModel):
    date: str  # YYYY-MM-DD
    revenue_eur: int
    order_count: int


class ConversionFunnel(BaseModel):
    total_visits: int  # referral clicks
    total_orders: int
    total_confirmed: int
    total_checked_in: int
    visit_to_order_rate: float
    order_to_confirmed_rate: float


class TopReferrer(BaseModel):
    code: str
    owner_name: str
    orders_count: int
    revenue_eur: int
    conversion_rate: float


class AnalyticsDashboard(BaseModel):
    total_revenue_eur: int
    total_orders: int
    total_confirmed: int
    total_checked_in: int
    sales_by_type: list[SalesByType]
    revenue_over_time: list[RevenueOverTime]
    funnel: ConversionFunnel
    top_referrers: list[TopReferrer]
