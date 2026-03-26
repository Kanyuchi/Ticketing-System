"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getTicketTypes, submitApplication, TicketType } from "@/lib/api";

export default function ApplyPage() {
  const params = useParams();
  const router = useRouter();
  const ticketTypeId = params.ticketTypeId as string;

  const [ticketType, setTicketType] = useState<TicketType | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    name: "",
    email: "",
    company: "",
    title: "",
    reason: "",
    // Press fields
    publication: "",
    portfolio_url: "",
    // Startup fields
    startup_name: "",
    startup_website: "",
    startup_stage: "",
  });

  useEffect(() => {
    getTicketTypes().then((types) => {
      const tt = types.find((t) => t.id === ticketTypeId);
      setTicketType(tt || null);
    });
  }, [ticketTypeId]);

  const isPress = ticketType?.category === "press";
  const isStartup = ticketType?.category === "startup";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name || !form.email) {
      setError("Name and email are required");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const app = await submitApplication({
        ticket_type_id: ticketTypeId,
        name: form.name,
        email: form.email,
        company: form.company || undefined,
        title: form.title || undefined,
        reason: form.reason || undefined,
        publication: form.publication || undefined,
        portfolio_url: form.portfolio_url || undefined,
        startup_name: form.startup_name || undefined,
        startup_website: form.startup_website || undefined,
        startup_stage: form.startup_stage || undefined,
      });
      router.push(`/application/${app.id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Submission failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (!ticketType) {
    return <div className="p-12 text-center text-gray-500">Loading...</div>;
  }

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm({ ...form, [key]: e.target.value });

  return (
    <main className="min-h-screen bg-[var(--background)] p-8">
      <div className="max-w-xl mx-auto">
        <a href="/" className="text-sm text-gray-500 hover:text-gray-700 mb-6 block">
          &larr; Back to tickets
        </a>

        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
          <h1 className="text-2xl font-bold mb-1">Apply for {ticketType.name}</h1>
          <p className="text-sm text-gray-500 mb-6">
            {isPress
              ? "Approved applicants receive a complimentary pass code."
              : "Approved applicants can purchase at the discounted rate."}
          </p>

          {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Full Name *</label>
                <input value={form.name} onChange={set("name")} required className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Email *</label>
                <input type="email" value={form.email} onChange={set("email")} required className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Company</label>
                <input value={form.company} onChange={set("company")} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Title</label>
                <input value={form.title} onChange={set("title")} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
            </div>

            {isPress && (
              <>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Publication / Media Outlet *</label>
                  <input value={form.publication} onChange={set("publication")} required className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Portfolio / Work URL</label>
                  <input value={form.portfolio_url} onChange={set("portfolio_url")} placeholder="https://..." className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                </div>
              </>
            )}

            {isStartup && (
              <>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Startup Name *</label>
                  <input value={form.startup_name} onChange={set("startup_name")} required className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Startup Website</label>
                  <input value={form.startup_website} onChange={set("startup_website")} placeholder="https://..." className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Stage</label>
                  <select value={form.startup_stage} onChange={set("startup_stage")} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                    <option value="">Select stage...</option>
                    <option value="pre-seed">Pre-Seed</option>
                    <option value="seed">Seed</option>
                    <option value="series-a">Series A</option>
                    <option value="series-b">Series B+</option>
                    <option value="bootstrapped">Bootstrapped</option>
                  </select>
                </div>
              </>
            )}

            <div>
              <label className="block text-xs text-gray-500 mb-1">Why should you receive this pass?</label>
              <textarea value={form.reason} onChange={set("reason")} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-[var(--accent-orange)] text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
            >
              {submitting ? "Submitting..." : "Submit Application"}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
