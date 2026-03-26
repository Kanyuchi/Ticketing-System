"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { TicketType, createOrder } from "@/lib/api";

const DARK_CATEGORIES = ["vip_black", "general"];
const ORANGE_CATEGORIES = ["investor", "startup"];

function getCardStyle(category: string) {
  if (DARK_CATEGORIES.includes(category)) {
    return "bg-[#2d2d2d] text-white";
  }
  if (ORANGE_CATEGORIES.includes(category)) {
    return "bg-[#e8742a] text-white";
  }
  // VIP, press, speaker, partner
  return "bg-white text-[#1a1a1a] border border-gray-200";
}

function getPriceColor(category: string) {
  if (DARK_CATEGORIES.includes(category)) return "text-[#e8742a]";
  if (ORANGE_CATEGORIES.includes(category)) return "text-white";
  return "text-[#e8742a]";
}

function getButtonStyle(category: string) {
  if (DARK_CATEGORIES.includes(category) || ORANGE_CATEGORIES.includes(category)) {
    return "bg-white text-[#1a1a1a] hover:bg-gray-100";
  }
  return "bg-[#e8742a] text-white hover:opacity-90";
}

export default function TicketCard({ ticket }: { ticket: TicketType }) {
  const router = useRouter();
  const [quantity, setQuantity] = useState(1);
  const [buying, setBuying] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", company: "", title: "" });
  const [error, setError] = useState("");

  const priceDisplay =
    ticket.price_eur === 0
      ? "Complimentary"
      : `\u20AC ${(ticket.price_eur / 100).toLocaleString("en", { minimumFractionDigits: 2 })}`;

  const isSoldOut =
    ticket.quantity_total !== null && ticket.quantity_sold >= ticket.quantity_total;

  async function handleBuy() {
    if (!showForm) {
      setShowForm(true);
      return;
    }
    if (!form.name || !form.email) {
      setError("Name and email are required");
      return;
    }
    setBuying(true);
    setError("");
    try {
      const order = await createOrder({
        attendee: {
          email: form.email,
          name: form.name,
          company: form.company || undefined,
          title: form.title || undefined,
        },
        items: [{ ticket_type_id: ticket.id, quantity }],
      });
      router.push(`/order/${order.id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create order");
    } finally {
      setBuying(false);
    }
  }

  const cardStyle = getCardStyle(ticket.category);
  const priceColor = getPriceColor(ticket.category);
  const btnStyle = getButtonStyle(ticket.category);

  return (
    <div className={`rounded-2xl p-6 flex flex-col gap-4 ${cardStyle}`}>
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-bold">{ticket.name}</h3>
        {ticket.requires_application && (
          <span className="text-xs px-2 py-1 rounded bg-black/10">(Application Based)</span>
        )}
      </div>

      <div>
        <p className="text-sm opacity-70">Admittance price:</p>
        <p className={`text-2xl font-bold ${priceColor}`}>{priceDisplay}</p>
      </div>

      {!isSoldOut && !ticket.requires_application && (
        <div className="flex items-center gap-3">
          <span className="text-sm opacity-70">Passes:</span>
          <button
            onClick={() => setQuantity(Math.max(1, quantity - 1))}
            className="w-8 h-8 rounded-full border border-current/20 flex items-center justify-center"
          >
            -
          </button>
          <span className="w-6 text-center">{quantity}</span>
          <button
            onClick={() => setQuantity(quantity + 1)}
            className="w-8 h-8 rounded-full border border-current/20 flex items-center justify-center"
          >
            +
          </button>
        </div>
      )}

      {showForm && (
        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Full Name *"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="px-3 py-2 rounded-lg text-sm text-black border border-gray-300"
          />
          <input
            type="email"
            placeholder="Email *"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="px-3 py-2 rounded-lg text-sm text-black border border-gray-300"
          />
          <input
            type="text"
            placeholder="Company"
            value={form.company}
            onChange={(e) => setForm({ ...form, company: e.target.value })}
            className="px-3 py-2 rounded-lg text-sm text-black border border-gray-300"
          />
          <input
            type="text"
            placeholder="Title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="px-3 py-2 rounded-lg text-sm text-black border border-gray-300"
          />
        </div>
      )}

      {error && <p className="text-red-400 text-sm">{error}</p>}

      <div className="flex gap-2 mt-auto">
        {isSoldOut ? (
          <span className="text-sm opacity-50">Sold Out</span>
        ) : ticket.requires_application ? (
          <button className={`flex-1 py-2.5 rounded-lg text-sm font-medium ${btnStyle}`}>
            Apply Now
          </button>
        ) : (
          <>
            <button
              onClick={handleBuy}
              disabled={buying}
              className={`flex-1 py-2.5 rounded-lg text-sm font-medium ${btnStyle} disabled:opacity-50`}
            >
              {buying ? "Processing..." : showForm ? "Confirm" : "Buy Now"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
