const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export interface TicketType {
  id: string;
  name: string;
  category: string;
  description: string | null;
  price_eur: number; // cents
  is_complimentary: boolean;
  requires_application: boolean;
  quantity_total: number | null;
  quantity_sold: number;
  is_active: boolean;
  sort_order: number;
}

export interface OrderItem {
  id: string;
  ticket_type_id: string;
  quantity: number;
  unit_price_eur: number;
}

export interface Attendee {
  id: string;
  email: string;
  name: string;
  company: string | null;
  title: string | null;
}

export interface Order {
  id: string;
  order_number: string;
  attendee: Attendee;
  status: string;
  payment_status: string;
  total_eur: number;
  voucher_code: string | null;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

// Public endpoints
export const getTicketTypes = () => request<TicketType[]>("/tickets/types");

export const createOrder = (data: {
  attendee: { email: string; name: string; company?: string; title?: string };
  items: { ticket_type_id: string; quantity: number }[];
  voucher_code?: string;
  referral_code?: string;
}) => request<Order>("/orders", { method: "POST", body: JSON.stringify(data) });

export const getOrder = (id: string) => request<Order>(`/orders/${id}`);

export const validateVoucher = (code: string) =>
  request<{ valid: boolean; ticket_type_id: string }>(`/vouchers/validate/${code}`);

export const createCheckout = (orderId: string) =>
  request<{ checkout_url: string; session_id: string }>(`/payments/create-checkout/${orderId}`, {
    method: "POST",
  });

// Admin endpoints (require auth token)
function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}

export const adminLogin = (email: string, password: string) =>
  request<{ access_token: string; token_type: string }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const getOrders = (token: string, params?: Record<string, string>) => {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return request<Order[]>(`/orders${qs}`, { headers: authHeaders(token) });
};

export const exportOrdersCsv = (token: string, params?: Record<string, string>) => {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetch(`${API_BASE}/orders/export/csv${qs}`, { headers: authHeaders(token) });
};

export const createVouchersBulk = (
  token: string,
  data: { ticket_type_id: string; prefix: string; count: number }
) =>
  request<Array<{ id: string; code: string }>>("/vouchers/bulk", {
    method: "POST",
    body: JSON.stringify(data),
    headers: authHeaders(token),
  });

export const getVouchers = (token: string, ticketTypeId?: string) => {
  const qs = ticketTypeId ? `?ticket_type_id=${ticketTypeId}` : "";
  return request<Array<{ id: string; code: string; is_used: boolean; used_by_email: string | null }>>(
    `/vouchers${qs}`,
    { headers: authHeaders(token) }
  );
};

// Applications
export interface Application {
  id: string;
  ticket_type_id: string;
  status: "pending" | "approved" | "rejected";
  name: string;
  email: string;
  company: string | null;
  title: string | null;
  reason: string | null;
  publication: string | null;
  portfolio_url: string | null;
  startup_name: string | null;
  startup_website: string | null;
  startup_stage: string | null;
  voucher_code: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  rejection_reason: string | null;
  created_at: string;
}

export const submitApplication = (data: Record<string, unknown>) =>
  request<Application>("/applications", { method: "POST", body: JSON.stringify(data) });

export const getApplication = (id: string) => request<Application>(`/applications/${id}`);

export const getApplications = (token: string, params?: Record<string, string>) => {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return request<Application[]>(`/applications${qs}`, { headers: authHeaders(token) });
};

export const reviewApplication = (token: string, id: string, data: { status: string; rejection_reason?: string }) =>
  request<Application>(`/applications/${id}/review`, {
    method: "POST",
    body: JSON.stringify(data),
    headers: authHeaders(token),
  });

// Emails
export const sendEmail = (token: string, data: { to_email: string; subject: string; body: string }) =>
  request<{ sent: boolean }>("/emails/send", {
    method: "POST",
    body: JSON.stringify(data),
    headers: authHeaders(token),
  });

// Upgrades
export const calculateUpgrade = (data: { order_id: string; new_ticket_type_id: string }) =>
  request<{ order_id: string; current_ticket: string; new_ticket: string; price_difference: number }>(
    "/upgrades/calculate",
    { method: "POST", body: JSON.stringify(data) }
  );

export const createUpgradeCheckout = (data: { order_id: string; new_ticket_type_id: string; discount_code?: string }) =>
  request<{ checkout_url: string } | { upgraded: boolean; order_id: string }>(
    "/upgrades/checkout",
    { method: "POST", body: JSON.stringify(data) }
  );

// Referrals
export interface ReferralData {
  id: string;
  code: string;
  owner_name: string;
  owner_email: string;
  clicks: number;
  orders_count: number;
  revenue_eur: number;
  conversion_rate?: number;
}

export const createReferral = (token: string, data: { owner_name: string; owner_email: string; code?: string }) =>
  request<ReferralData>("/referrals", { method: "POST", body: JSON.stringify(data), headers: authHeaders(token) });

export const getReferrals = (token: string) =>
  request<ReferralData[]>("/referrals", { headers: authHeaders(token) });

export const getReferralLeaderboard = (token: string) =>
  request<ReferralData[]>("/referrals/leaderboard", { headers: authHeaders(token) });

// Sharing
export const getShareMeta = (orderId: string) =>
  request<{ share_text: string; card_url: string; event_url: string; twitter_url: string; linkedin_url: string }>(
    `/sharing/meta/${orderId}`
  );

export const getQrUrl = (orderId: string) => `${API_BASE}/sharing/qr/${orderId}`;
export const getShareCardUrl = (orderId: string) => `${API_BASE}/sharing/card/${orderId}`;
