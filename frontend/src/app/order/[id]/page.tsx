"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getOrder, createCheckout, Order } from "@/lib/api";

export default function OrderPage() {
  const params = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (params.id) {
      getOrder(params.id as string)
        .then(setOrder)
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    }
  }, [params.id]);

  async function handlePay() {
    if (!order) return;
    try {
      const { checkout_url } = await createCheckout(order.id);
      window.location.href = checkout_url;
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Payment failed");
    }
  }

  if (loading) return <div className="p-12 text-center">Loading order...</div>;
  if (error) return <div className="p-12 text-center text-red-500">{error}</div>;
  if (!order) return <div className="p-12 text-center">Order not found</div>;

  const isPaid = order.payment_status === "paid" || order.payment_status === "complimentary";

  return (
    <main className="min-h-screen bg-[var(--background)] p-8">
      <div className="max-w-xl mx-auto bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
        <h1 className="text-2xl font-bold mb-1">Order {order.order_number}</h1>
        <p className="text-sm text-gray-500 mb-6">
          {new Date(order.created_at).toLocaleDateString()}
        </p>

        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Name</span>
            <span>{order.attendee.name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Email</span>
            <span>{order.attendee.email}</span>
          </div>
          {order.attendee.company && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Company</span>
              <span>{order.attendee.company}</span>
            </div>
          )}
          {order.voucher_code && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Voucher</span>
              <span className="font-mono">{order.voucher_code}</span>
            </div>
          )}
        </div>

        <div className="border-t pt-4 mb-6">
          {order.items.map((item) => (
            <div key={item.id} className="flex justify-between text-sm py-1">
              <span>
                {item.quantity}x Ticket
              </span>
              <span>
                {item.unit_price_eur === 0
                  ? "Complimentary"
                  : `\u20AC${((item.unit_price_eur * item.quantity) / 100).toFixed(2)}`}
              </span>
            </div>
          ))}
          <div className="flex justify-between font-bold mt-3 pt-3 border-t">
            <span>Total</span>
            <span>
              {order.total_eur === 0
                ? "Complimentary"
                : `\u20AC${(order.total_eur / 100).toFixed(2)}`}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 mb-6">
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              order.status === "confirmed"
                ? "bg-green-100 text-green-700"
                : order.status === "cancelled"
                ? "bg-red-100 text-red-700"
                : "bg-yellow-100 text-yellow-700"
            }`}
          >
            {order.status.toUpperCase()}
          </span>
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              isPaid ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
            }`}
          >
            {order.payment_status.toUpperCase()}
          </span>
        </div>

        {order.payment_status === "unpaid" && order.total_eur > 0 && (
          <button
            onClick={handlePay}
            className="w-full py-3 bg-[var(--accent-orange)] text-white rounded-lg font-medium hover:opacity-90"
          >
            Pay Now - {"\u20AC"}{(order.total_eur / 100).toFixed(2)}
          </button>
        )}

        {isPaid && (
          <div className="text-center text-green-600 font-medium">
            Your ticket is confirmed. See you at Proof of Talk 2026!
          </div>
        )}
      </div>
    </main>
  );
}
