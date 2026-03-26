"use client";

import { useEffect, useState } from "react";
import {
  adminLogin,
  getOrders,
  exportOrdersCsv,
  createVouchersBulk,
  getTicketTypes,
  Order,
  TicketType,
} from "@/lib/api";

export default function AdminDashboard() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");

  const [orders, setOrders] = useState<Order[]>([]);
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  // Voucher generation
  const [voucherTypeId, setVoucherTypeId] = useState("");
  const [voucherPrefix, setVoucherPrefix] = useState("POT26");
  const [voucherCount, setVoucherCount] = useState(10);
  const [generatedCodes, setGeneratedCodes] = useState<string[]>([]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoginError("");
    try {
      const { access_token } = await adminLogin(email, password);
      setToken(access_token);
    } catch (err: unknown) {
      setLoginError(err instanceof Error ? err.message : "Login failed");
    }
  }

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      getOrders(token, filters).then(setOrders),
      getTicketTypes().then(setTicketTypes),
    ]).finally(() => setLoading(false));
  }, [token, filters]);

  async function handleExportCsv() {
    const res = await exportOrdersCsv(token, filters);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "orders.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function handleGenerateVouchers() {
    if (!voucherTypeId) return;
    try {
      const vouchers = await createVouchersBulk(token, {
        ticket_type_id: voucherTypeId,
        prefix: voucherPrefix,
        count: voucherCount,
      });
      setGeneratedCodes(vouchers.map((v) => v.code));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to generate vouchers");
    }
  }

  function updateFilter(key: string, value: string) {
    setFilters((prev) => {
      const next = { ...prev };
      if (value) next[key] = value;
      else delete next[key];
      return next;
    });
  }

  if (!token) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-[var(--background)]">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 w-full max-w-sm">
          <h1 className="text-xl font-bold mb-6">Admin Login</h1>
          {loginError && <p className="text-red-500 text-sm mb-4">{loginError}</p>}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-3 text-sm"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4 text-sm"
          />
          <button
            type="submit"
            className="w-full py-2.5 bg-[var(--accent-orange)] text-white rounded-lg font-medium hover:opacity-90"
          >
            Log In
          </button>
        </form>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[var(--background)] p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          <button onClick={handleExportCsv} className="px-4 py-2 bg-[#2d2d2d] text-white rounded-lg text-sm hover:opacity-90">
            Export CSV
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-4 mb-6 grid grid-cols-2 md:grid-cols-4 gap-3 border border-gray-100">
          <input
            placeholder="Search name..."
            onChange={(e) => updateFilter("name", e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
          />
          <input
            placeholder="Search email..."
            onChange={(e) => updateFilter("email", e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
          />
          <input
            placeholder="Search company..."
            onChange={(e) => updateFilter("company", e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
          />
          <input
            placeholder="Voucher code..."
            onChange={(e) => updateFilter("voucher_code", e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
          />
          <select
            onChange={(e) => updateFilter("order_status", e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="cancelled">Cancelled</option>
            <option value="refunded">Refunded</option>
          </select>
          <select
            onChange={(e) => updateFilter("payment_status", e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
          >
            <option value="">All Payments</option>
            <option value="unpaid">Unpaid</option>
            <option value="paid">Paid</option>
            <option value="complimentary">Complimentary</option>
            <option value="refunded">Refunded</option>
          </select>
        </div>

        {/* Orders Table */}
        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden mb-8">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading...</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium">Order #</th>
                  <th className="px-4 py-3 font-medium">Name</th>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">Company</th>
                  <th className="px-4 py-3 font-medium">Voucher</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Payment</th>
                  <th className="px-4 py-3 font-medium text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {orders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono">{order.order_number}</td>
                    <td className="px-4 py-3">{order.attendee.name}</td>
                    <td className="px-4 py-3">{order.attendee.email}</td>
                    <td className="px-4 py-3">{order.attendee.company || "-"}</td>
                    <td className="px-4 py-3 font-mono">{order.voucher_code || "-"}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${
                          order.status === "confirmed"
                            ? "bg-green-100 text-green-700"
                            : order.status === "cancelled"
                            ? "bg-red-100 text-red-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {order.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${
                          order.payment_status === "paid" || order.payment_status === "complimentary"
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {order.payment_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {order.total_eur === 0
                        ? "Free"
                        : `\u20AC${(order.total_eur / 100).toFixed(2)}`}
                    </td>
                  </tr>
                ))}
                {orders.length === 0 && (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-gray-400">
                      No orders found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Voucher Generator */}
        <div className="bg-white rounded-xl p-6 border border-gray-100">
          <h2 className="text-lg font-bold mb-4">Generate Voucher Codes</h2>
          <div className="flex flex-wrap gap-3 items-end">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Ticket Type</label>
              <select
                value={voucherTypeId}
                onChange={(e) => setVoucherTypeId(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
              >
                <option value="">Select type...</option>
                {ticketTypes.map((tt) => (
                  <option key={tt.id} value={tt.id}>
                    {tt.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Prefix</label>
              <input
                value={voucherPrefix}
                onChange={(e) => setVoucherPrefix(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm w-32"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Count</label>
              <input
                type="number"
                value={voucherCount}
                onChange={(e) => setVoucherCount(Number(e.target.value))}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm w-20"
                min={1}
                max={500}
              />
            </div>
            <button
              onClick={handleGenerateVouchers}
              className="px-4 py-2 bg-[var(--accent-orange)] text-white rounded-lg text-sm hover:opacity-90"
            >
              Generate
            </button>
          </div>
          {generatedCodes.length > 0 && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-2">Generated {generatedCodes.length} codes:</p>
              <div className="font-mono text-xs space-y-1 max-h-40 overflow-y-auto">
                {generatedCodes.map((code) => (
                  <div key={code}>{code}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
