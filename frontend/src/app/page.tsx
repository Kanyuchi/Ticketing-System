"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getTicketTypes, TicketType } from "@/lib/api";
import TicketCard from "@/components/TicketCard";

function HomeContent() {
  const searchParams = useSearchParams();
  const refCode = searchParams.get("ref");
  const [tickets, setTickets] = useState<TicketType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Store referral code for order attribution
    if (refCode) {
      sessionStorage.setItem("referral_code", refCode);
    }
    getTicketTypes()
      .then(setTickets)
      .catch(() => setTickets([]))
      .finally(() => setLoading(false));
  }, [refCode]);

  return (
    <main className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-4 border-b border-gray-200">
        <div className="text-xl font-bold tracking-tight">Proof of Talk</div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">EUR</span>
          <button className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
            Sign Up
          </button>
          <button className="px-4 py-2 text-sm bg-[var(--accent-orange)] text-white rounded-lg hover:opacity-90">
            Log In
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="text-center py-12">
        <h1 className="text-5xl font-serif italic mb-2">Levels of Access</h1>
        <p className="text-gray-600">Choose the level that matches your intent.</p>
      </section>

      {/* Ticket Grid */}
      <section className="max-w-7xl mx-auto px-8 pb-16">
        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading tickets...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} referralCode={refCode || undefined} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-gray-500">Loading...</div>}>
      <HomeContent />
    </Suspense>
  );
}
