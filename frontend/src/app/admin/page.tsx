"use client";

import { useEffect, useState } from "react";
import {
  adminLogin,
  getOrders,
  exportOrdersCsv,
  createVouchersBulk,
  getTicketTypes,
  getApplications,
  reviewApplication,
  sendEmail,
  createReferral,
  getReferralLeaderboard,
  performCheckIn,
  getCheckIns,
  getCheckInStats,
  getAnalyticsDashboard,
  getWaitlist,
  notifyWaitlist,
  Order,
  TicketType,
  Application,
  ReferralData,
  CheckInData,
  CheckInStats,
  AnalyticsDashboard,
  WaitlistEntry,
} from "@/lib/api";

type Tab = "orders" | "applications" | "vouchers" | "referrals" | "email" | "checkin" | "analytics" | "waitlist";

export default function AdminDashboard() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [activeTab, setActiveTab] = useState<Tab>("orders");

  const [orders, setOrders] = useState<Order[]>([]);
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  // Applications
  const [applications, setApplications] = useState<Application[]>([]);
  const [appFilter, setAppFilter] = useState<string>("");
  const [reviewingId, setReviewingId] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState("");

  // Voucher generation
  const [voucherTypeId, setVoucherTypeId] = useState("");
  const [voucherPrefix, setVoucherPrefix] = useState("POT26");
  const [voucherCount, setVoucherCount] = useState(10);
  const [generatedCodes, setGeneratedCodes] = useState<string[]>([]);

  // Referrals
  const [referrals, setReferrals] = useState<ReferralData[]>([]);
  const [newRefName, setNewRefName] = useState("");
  const [newRefEmail, setNewRefEmail] = useState("");
  const [newRefCode, setNewRefCode] = useState("");

  // Email
  const [emailTo, setEmailTo] = useState("");
  const [emailSubject, setEmailSubject] = useState("");
  const [emailBody, setEmailBody] = useState("");
  const [emailSent, setEmailSent] = useState(false);

  // Check-in
  const [checkIns, setCheckIns] = useState<CheckInData[]>([]);
  const [checkInStats, setCheckInStats] = useState<CheckInStats | null>(null);
  const [checkInOrderId, setCheckInOrderId] = useState("");
  const [checkInMessage, setCheckInMessage] = useState("");

  // Analytics
  const [analytics, setAnalytics] = useState<AnalyticsDashboard | null>(null);

  // Waitlist
  const [waitlistEntries, setWaitlistEntries] = useState<WaitlistEntry[]>([]);
  const [waitlistTypeFilter, setWaitlistTypeFilter] = useState("");

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

  useEffect(() => {
    if (!token || activeTab !== "referrals") return;
    getReferralLeaderboard(token).then(setReferrals);
  }, [token, activeTab]);

  useEffect(() => {
    if (!token || activeTab !== "applications") return;
    const params: Record<string, string> = {};
    if (appFilter) params.status = appFilter;
    getApplications(token, params).then(setApplications);
  }, [token, activeTab, appFilter]);

  useEffect(() => {
    if (!token || activeTab !== "checkin") return;
    Promise.all([
      getCheckIns(token).then(setCheckIns),
      getCheckInStats(token).then(setCheckInStats),
    ]);
  }, [token, activeTab]);

  useEffect(() => {
    if (!token || activeTab !== "analytics") return;
    getAnalyticsDashboard(token).then(setAnalytics);
  }, [token, activeTab]);

  useEffect(() => {
    if (!token || activeTab !== "waitlist") return;
    getWaitlist(token, waitlistTypeFilter || undefined).then(setWaitlistEntries);
  }, [token, activeTab, waitlistTypeFilter]);

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

  async function handleReview(appId: string, status: "approved" | "rejected") {
    try {
      await reviewApplication(token, appId, {
        status,
        rejection_reason: status === "rejected" ? rejectionReason : undefined,
      });
      setReviewingId(null);
      setRejectionReason("");
      // Refresh
      const params: Record<string, string> = {};
      if (appFilter) params.status = appFilter;
      const updated = await getApplications(token, params);
      setApplications(updated);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Review failed");
    }
  }

  async function handleCreateReferral() {
    if (!newRefName || !newRefEmail) return;
    try {
      await createReferral(token, { owner_name: newRefName, owner_email: newRefEmail, code: newRefCode || undefined });
      setNewRefName(""); setNewRefEmail(""); setNewRefCode("");
      getReferralLeaderboard(token).then(setReferrals);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to create referral");
    }
  }

  async function handleCheckIn() {
    if (!checkInOrderId.trim()) return;
    setCheckInMessage("");
    try {
      const result = await performCheckIn(token, { order_id: checkInOrderId.trim() });
      setCheckInMessage(`✓ Checked in ${result.attendee_name} (${result.ticket_type})`);
      setCheckInOrderId("");
      getCheckIns(token).then(setCheckIns);
      getCheckInStats(token).then(setCheckInStats);
    } catch (err: unknown) {
      setCheckInMessage(err instanceof Error ? err.message : "Check-in failed");
    }
  }

  async function handleNotifyWaitlist(ticketTypeId: string) {
    try {
      const result = await notifyWaitlist(token, ticketTypeId, 1);
      alert(`Notified ${result.notified} people: ${result.emails.join(", ")}`);
      getWaitlist(token, waitlistTypeFilter || undefined).then(setWaitlistEntries);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Notification failed");
    }
  }

  async function handleSendEmail(e: React.FormEvent) {
    e.preventDefault();
    try {
      await sendEmail(token, { to_email: emailTo, subject: emailSubject, body: emailBody });
      setEmailSent(true);
      setTimeout(() => setEmailSent(false), 3000);
      setEmailTo("");
      setEmailSubject("");
      setEmailBody("");
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to send email");
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
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-3 text-sm" />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4 text-sm" />
          <button type="submit" className="w-full py-2.5 bg-[var(--accent-orange)] text-white rounded-lg font-medium hover:opacity-90">Log In</button>
        </form>
      </main>
    );
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: "orders", label: "Orders" },
    { key: "applications", label: "Applications" },
    { key: "vouchers", label: "Vouchers" },
    { key: "referrals", label: "Referrals" },
    { key: "checkin", label: "Check-in" },
    { key: "analytics", label: "Analytics" },
    { key: "waitlist", label: "Waitlist" },
    { key: "email", label: "Send Email" },
  ];

  return (
    <main className="min-h-screen bg-[var(--background)] p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          {activeTab === "orders" && (
            <button onClick={handleExportCsv} className="px-4 py-2 bg-[#2d2d2d] text-white rounded-lg text-sm hover:opacity-90">Export CSV</button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-white rounded-lg p-1 border border-gray-100 w-fit">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.key ? "bg-[var(--accent-orange)] text-white" : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Orders Tab */}
        {activeTab === "orders" && (
          <>
            <div className="bg-white rounded-xl p-4 mb-6 grid grid-cols-2 md:grid-cols-4 gap-3 border border-gray-100">
              <input placeholder="Search name..." onChange={(e) => updateFilter("name", e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              <input placeholder="Search email..." onChange={(e) => updateFilter("email", e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              <input placeholder="Search company..." onChange={(e) => updateFilter("company", e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              <input placeholder="Voucher code..." onChange={(e) => updateFilter("voucher_code", e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              <select onChange={(e) => updateFilter("order_status", e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="cancelled">Cancelled</option>
                <option value="refunded">Refunded</option>
              </select>
              <select onChange={(e) => updateFilter("payment_status", e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
                <option value="">All Payments</option>
                <option value="unpaid">Unpaid</option>
                <option value="paid">Paid</option>
                <option value="complimentary">Complimentary</option>
                <option value="refunded">Refunded</option>
              </select>
            </div>

            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
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
                          <span className={`px-2 py-0.5 rounded text-xs ${order.status === "confirmed" ? "bg-green-100 text-green-700" : order.status === "cancelled" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>{order.status}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 rounded text-xs ${order.payment_status === "paid" || order.payment_status === "complimentary" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>{order.payment_status}</span>
                        </td>
                        <td className="px-4 py-3 text-right">{order.total_eur === 0 ? "Free" : `\u20AC${(order.total_eur / 100).toFixed(2)}`}</td>
                      </tr>
                    ))}
                    {orders.length === 0 && (
                      <tr><td colSpan={8} className="px-4 py-8 text-center text-gray-400">No orders found</td></tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}

        {/* Applications Tab */}
        {activeTab === "applications" && (
          <>
            <div className="bg-white rounded-xl p-4 mb-6 border border-gray-100 flex gap-3">
              <select value={appFilter} onChange={(e) => setAppFilter(e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
                <option value="">All Applications</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            <div className="space-y-4">
              {applications.map((app) => (
                <div key={app.id} className="bg-white rounded-xl p-5 border border-gray-100">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-bold">{app.name}</h3>
                      <p className="text-sm text-gray-500">{app.email}{app.company ? ` - ${app.company}` : ""}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${app.status === "approved" ? "bg-green-100 text-green-700" : app.status === "rejected" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>
                      {app.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm mb-3">
                    {app.title && <div><span className="text-gray-400">Title:</span> {app.title}</div>}
                    {app.publication && <div><span className="text-gray-400">Publication:</span> {app.publication}</div>}
                    {app.portfolio_url && <div><span className="text-gray-400">Portfolio:</span> <a href={app.portfolio_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Link</a></div>}
                    {app.startup_name && <div><span className="text-gray-400">Startup:</span> {app.startup_name}</div>}
                    {app.startup_website && <div><span className="text-gray-400">Website:</span> <a href={app.startup_website} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Link</a></div>}
                    {app.startup_stage && <div><span className="text-gray-400">Stage:</span> {app.startup_stage}</div>}
                  </div>

                  {app.reason && <p className="text-sm text-gray-600 mb-3 bg-gray-50 rounded-lg p-3">{app.reason}</p>}

                  {app.voucher_code && (
                    <div className="text-sm mb-3"><span className="text-gray-400">Voucher Code:</span> <span className="font-mono font-bold text-[var(--accent-orange)]">{app.voucher_code}</span></div>
                  )}

                  {app.status === "pending" && (
                    <div className="flex gap-2 mt-3 pt-3 border-t">
                      {reviewingId === app.id ? (
                        <div className="flex gap-2 items-center w-full">
                          <input
                            placeholder="Rejection reason (optional)"
                            value={rejectionReason}
                            onChange={(e) => setRejectionReason(e.target.value)}
                            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm"
                          />
                          <button onClick={() => handleReview(app.id, "rejected")} className="px-3 py-2 bg-red-500 text-white rounded-lg text-sm">Confirm Reject</button>
                          <button onClick={() => setReviewingId(null)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">Cancel</button>
                        </div>
                      ) : (
                        <>
                          <button onClick={() => handleReview(app.id, "approved")} className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:opacity-90">Approve</button>
                          <button onClick={() => setReviewingId(app.id)} className="px-4 py-2 bg-red-500 text-white rounded-lg text-sm hover:opacity-90">Reject</button>
                        </>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {applications.length === 0 && (
                <div className="bg-white rounded-xl p-8 border border-gray-100 text-center text-gray-400">No applications found</div>
              )}
            </div>
          </>
        )}

        {/* Vouchers Tab */}
        {activeTab === "vouchers" && (
          <div className="bg-white rounded-xl p-6 border border-gray-100">
            <h2 className="text-lg font-bold mb-4">Generate Voucher Codes</h2>
            <div className="flex flex-wrap gap-3 items-end">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Ticket Type</label>
                <select value={voucherTypeId} onChange={(e) => setVoucherTypeId(e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
                  <option value="">Select type...</option>
                  {ticketTypes.map((tt) => (<option key={tt.id} value={tt.id}>{tt.name}</option>))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Prefix</label>
                <input value={voucherPrefix} onChange={(e) => setVoucherPrefix(e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm w-32" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Count</label>
                <input type="number" value={voucherCount} onChange={(e) => setVoucherCount(Number(e.target.value))} className="px-3 py-2 border border-gray-200 rounded-lg text-sm w-20" min={1} max={500} />
              </div>
              <button onClick={handleGenerateVouchers} className="px-4 py-2 bg-[var(--accent-orange)] text-white rounded-lg text-sm hover:opacity-90">Generate</button>
            </div>
            {generatedCodes.length > 0 && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500 mb-2">Generated {generatedCodes.length} codes:</p>
                <div className="font-mono text-xs space-y-1 max-h-40 overflow-y-auto">
                  {generatedCodes.map((code) => (<div key={code}>{code}</div>))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Referrals Tab */}
        {activeTab === "referrals" && (
          <div className="space-y-6">
            {/* Create Referral */}
            <div className="bg-white rounded-xl p-6 border border-gray-100">
              <h2 className="text-lg font-bold mb-4">Create Referral Code</h2>
              <div className="flex flex-wrap gap-3 items-end">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Ambassador Name *</label>
                  <input value={newRefName} onChange={(e) => setNewRefName(e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Email *</label>
                  <input type="email" value={newRefEmail} onChange={(e) => setNewRefEmail(e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Custom Code (optional)</label>
                  <input value={newRefCode} onChange={(e) => setNewRefCode(e.target.value)} placeholder="Auto-generated" className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
                </div>
                <button onClick={handleCreateReferral} className="px-4 py-2 bg-[var(--accent-orange)] text-white rounded-lg text-sm hover:opacity-90">Create</button>
              </div>
            </div>

            {/* Leaderboard */}
            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="text-lg font-bold">Referral Leaderboard</h2>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left">
                  <tr>
                    <th className="px-4 py-3 font-medium">#</th>
                    <th className="px-4 py-3 font-medium">Ambassador</th>
                    <th className="px-4 py-3 font-medium">Code</th>
                    <th className="px-4 py-3 font-medium text-right">Clicks</th>
                    <th className="px-4 py-3 font-medium text-right">Orders</th>
                    <th className="px-4 py-3 font-medium text-right">Revenue</th>
                    <th className="px-4 py-3 font-medium text-right">Conv. Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {referrals.map((ref, i) => (
                    <tr key={ref.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-bold text-gray-400">{i + 1}</td>
                      <td className="px-4 py-3">
                        <div>{ref.owner_name}</div>
                        <div className="text-xs text-gray-400">{ref.owner_email}</div>
                      </td>
                      <td className="px-4 py-3 font-mono text-[var(--accent-orange)]">{ref.code}</td>
                      <td className="px-4 py-3 text-right">{ref.clicks}</td>
                      <td className="px-4 py-3 text-right">{ref.orders_count}</td>
                      <td className="px-4 py-3 text-right">{ref.revenue_eur === 0 ? "-" : `\u20AC${(ref.revenue_eur / 100).toFixed(2)}`}</td>
                      <td className="px-4 py-3 text-right">{ref.conversion_rate ? `${(ref.conversion_rate * 100).toFixed(1)}%` : "-"}</td>
                    </tr>
                  ))}
                  {referrals.length === 0 && (
                    <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">No referrals yet</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Check-in Tab */}
        {activeTab === "checkin" && (
          <div className="space-y-6">
            {/* Stats Bar */}
            {checkInStats && (
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded-xl p-5 border border-gray-100 text-center">
                  <div className="text-3xl font-bold">{checkInStats.total_confirmed}</div>
                  <div className="text-xs text-gray-500 mt-1">Confirmed Orders</div>
                </div>
                <div className="bg-white rounded-xl p-5 border border-gray-100 text-center">
                  <div className="text-3xl font-bold text-green-600">{checkInStats.total_checked_in}</div>
                  <div className="text-xs text-gray-500 mt-1">Checked In</div>
                </div>
                <div className="bg-white rounded-xl p-5 border border-gray-100 text-center">
                  <div className="text-3xl font-bold text-[var(--accent-orange)]">{(checkInStats.check_in_rate * 100).toFixed(1)}%</div>
                  <div className="text-xs text-gray-500 mt-1">Check-in Rate</div>
                </div>
              </div>
            )}

            {/* Scanner Input */}
            <div className="bg-white rounded-xl p-6 border border-gray-100">
              <h2 className="text-lg font-bold mb-4">Scan / Enter Order ID</h2>
              <div className="flex gap-3 items-end">
                <input
                  value={checkInOrderId}
                  onChange={(e) => setCheckInOrderId(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleCheckIn()}
                  placeholder="Paste or scan order ID..."
                  className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono"
                />
                <button onClick={handleCheckIn} className="px-6 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:opacity-90">Check In</button>
              </div>
              {checkInMessage && (
                <p className={`mt-3 text-sm ${checkInMessage.startsWith("✓") ? "text-green-600" : "text-red-500"}`}>{checkInMessage}</p>
              )}
            </div>

            {/* Recent Check-ins */}
            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="text-lg font-bold">Recent Check-ins</h2>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left">
                  <tr>
                    <th className="px-4 py-3 font-medium">Order #</th>
                    <th className="px-4 py-3 font-medium">Name</th>
                    <th className="px-4 py-3 font-medium">Email</th>
                    <th className="px-4 py-3 font-medium">Ticket</th>
                    <th className="px-4 py-3 font-medium">Checked In At</th>
                    <th className="px-4 py-3 font-medium">By</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {checkIns.map((ci) => (
                    <tr key={ci.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono">{ci.order_number}</td>
                      <td className="px-4 py-3">{ci.attendee_name}</td>
                      <td className="px-4 py-3">{ci.attendee_email}</td>
                      <td className="px-4 py-3">{ci.ticket_type}</td>
                      <td className="px-4 py-3">{new Date(ci.checked_in_at).toLocaleString()}</td>
                      <td className="px-4 py-3 text-gray-500">{ci.checked_in_by || "-"}</td>
                    </tr>
                  ))}
                  {checkIns.length === 0 && (
                    <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">No check-ins yet</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && analytics && (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl p-5 border border-gray-100 text-center">
                <div className="text-3xl font-bold">{analytics.total_revenue_eur === 0 ? "€0" : `€${(analytics.total_revenue_eur / 100).toLocaleString()}`}</div>
                <div className="text-xs text-gray-500 mt-1">Total Revenue</div>
              </div>
              <div className="bg-white rounded-xl p-5 border border-gray-100 text-center">
                <div className="text-3xl font-bold">{analytics.total_orders}</div>
                <div className="text-xs text-gray-500 mt-1">Total Orders</div>
              </div>
              <div className="bg-white rounded-xl p-5 border border-gray-100 text-center">
                <div className="text-3xl font-bold text-green-600">{analytics.total_confirmed}</div>
                <div className="text-xs text-gray-500 mt-1">Confirmed</div>
              </div>
              <div className="bg-white rounded-xl p-5 border border-gray-100 text-center">
                <div className="text-3xl font-bold text-[var(--accent-orange)]">{analytics.total_checked_in}</div>
                <div className="text-xs text-gray-500 mt-1">Checked In</div>
              </div>
            </div>

            {/* Sales by Type */}
            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="text-lg font-bold">Sales by Ticket Type</h2>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left">
                  <tr>
                    <th className="px-4 py-3 font-medium">Ticket Type</th>
                    <th className="px-4 py-3 font-medium">Category</th>
                    <th className="px-4 py-3 font-medium text-right">Sold</th>
                    <th className="px-4 py-3 font-medium text-right">Total</th>
                    <th className="px-4 py-3 font-medium text-right">Revenue</th>
                    <th className="px-4 py-3 font-medium">Progress</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {analytics.sales_by_type.map((s) => (
                    <tr key={s.ticket_type} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium">{s.ticket_type}</td>
                      <td className="px-4 py-3"><span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{s.category}</span></td>
                      <td className="px-4 py-3 text-right">{s.quantity_sold}</td>
                      <td className="px-4 py-3 text-right">{s.quantity_total ?? "∞"}</td>
                      <td className="px-4 py-3 text-right">{s.revenue_eur === 0 ? "-" : `€${(s.revenue_eur / 100).toLocaleString()}`}</td>
                      <td className="px-4 py-3">
                        {s.quantity_total ? (
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div className="bg-[var(--accent-orange)] h-2 rounded-full" style={{ width: `${Math.min(100, (s.quantity_sold / s.quantity_total) * 100)}%` }} />
                          </div>
                        ) : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Conversion Funnel */}
            <div className="bg-white rounded-xl p-6 border border-gray-100">
              <h2 className="text-lg font-bold mb-4">Conversion Funnel</h2>
              <div className="flex items-center gap-4 text-sm">
                <div className="text-center flex-1">
                  <div className="text-2xl font-bold">{analytics.funnel.total_visits}</div>
                  <div className="text-xs text-gray-500">Referral Visits</div>
                </div>
                <div className="text-gray-300 text-2xl">→</div>
                <div className="text-center flex-1">
                  <div className="text-2xl font-bold">{analytics.funnel.total_orders}</div>
                  <div className="text-xs text-gray-500">Orders ({(analytics.funnel.visit_to_order_rate * 100).toFixed(1)}%)</div>
                </div>
                <div className="text-gray-300 text-2xl">→</div>
                <div className="text-center flex-1">
                  <div className="text-2xl font-bold text-green-600">{analytics.funnel.total_confirmed}</div>
                  <div className="text-xs text-gray-500">Confirmed ({(analytics.funnel.order_to_confirmed_rate * 100).toFixed(1)}%)</div>
                </div>
                <div className="text-gray-300 text-2xl">→</div>
                <div className="text-center flex-1">
                  <div className="text-2xl font-bold text-[var(--accent-orange)]">{analytics.funnel.total_checked_in}</div>
                  <div className="text-xs text-gray-500">Checked In</div>
                </div>
              </div>
            </div>

            {/* Top Referrers */}
            {analytics.top_referrers.length > 0 && (
              <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100">
                  <h2 className="text-lg font-bold">Top Referrers</h2>
                </div>
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-left">
                    <tr>
                      <th className="px-4 py-3 font-medium">#</th>
                      <th className="px-4 py-3 font-medium">Ambassador</th>
                      <th className="px-4 py-3 font-medium">Code</th>
                      <th className="px-4 py-3 font-medium text-right">Orders</th>
                      <th className="px-4 py-3 font-medium text-right">Revenue</th>
                      <th className="px-4 py-3 font-medium text-right">Conv.</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {analytics.top_referrers.map((r, i) => (
                      <tr key={r.code} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-bold text-gray-400">{i + 1}</td>
                        <td className="px-4 py-3">{r.owner_name}</td>
                        <td className="px-4 py-3 font-mono text-[var(--accent-orange)]">{r.code}</td>
                        <td className="px-4 py-3 text-right">{r.orders_count}</td>
                        <td className="px-4 py-3 text-right">€{(r.revenue_eur / 100).toLocaleString()}</td>
                        <td className="px-4 py-3 text-right">{(r.conversion_rate * 100).toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Waitlist Tab */}
        {activeTab === "waitlist" && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-4 mb-2 border border-gray-100 flex gap-3 items-end">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Filter by Ticket Type</label>
                <select value={waitlistTypeFilter} onChange={(e) => setWaitlistTypeFilter(e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
                  <option value="">All Types</option>
                  {ticketTypes.map((tt) => (<option key={tt.id} value={tt.id}>{tt.name}</option>))}
                </select>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left">
                  <tr>
                    <th className="px-4 py-3 font-medium">#</th>
                    <th className="px-4 py-3 font-medium">Name</th>
                    <th className="px-4 py-3 font-medium">Email</th>
                    <th className="px-4 py-3 font-medium">Ticket Type</th>
                    <th className="px-4 py-3 font-medium">Notified</th>
                    <th className="px-4 py-3 font-medium">Joined</th>
                    <th className="px-4 py-3 font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {waitlistEntries.map((entry) => (
                    <tr key={entry.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-bold text-gray-400">{entry.position}</td>
                      <td className="px-4 py-3">{entry.name}</td>
                      <td className="px-4 py-3">{entry.email}</td>
                      <td className="px-4 py-3">{entry.ticket_type_name}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-xs ${entry.notified ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                          {entry.notified ? "Yes" : "No"}
                        </span>
                      </td>
                      <td className="px-4 py-3">{new Date(entry.created_at).toLocaleDateString()}</td>
                      <td className="px-4 py-3">
                        {!entry.notified && (
                          <button onClick={() => handleNotifyWaitlist(entry.ticket_type_id)} className="px-3 py-1 bg-[var(--accent-orange)] text-white rounded text-xs hover:opacity-90">Notify</button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {waitlistEntries.length === 0 && (
                    <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">No waitlist entries</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Email Tab */}
        {activeTab === "email" && (
          <div className="bg-white rounded-xl p-6 border border-gray-100 max-w-xl">
            <h2 className="text-lg font-bold mb-4">Send Email</h2>
            {emailSent && <p className="text-green-600 text-sm mb-4">Email sent successfully!</p>}
            <form onSubmit={handleSendEmail} className="space-y-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">To</label>
                <input type="email" value={emailTo} onChange={(e) => setEmailTo(e.target.value)} required placeholder="attendee@example.com" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Subject</label>
                <input value={emailSubject} onChange={(e) => setEmailSubject(e.target.value)} required placeholder="Proof of Talk 2026 - ..." className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Body (HTML supported)</label>
                <textarea value={emailBody} onChange={(e) => setEmailBody(e.target.value)} required rows={6} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              </div>
              <button type="submit" className="px-6 py-2.5 bg-[var(--accent-orange)] text-white rounded-lg text-sm font-medium hover:opacity-90">Send Email</button>
            </form>
          </div>
        )}
      </div>
    </main>
  );
}
