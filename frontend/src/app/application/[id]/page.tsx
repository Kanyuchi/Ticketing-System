"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getApplication, Application } from "@/lib/api";

export default function ApplicationStatusPage() {
  const params = useParams();
  const [app, setApp] = useState<Application | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      getApplication(params.id as string)
        .then(setApp)
        .finally(() => setLoading(false));
    }
  }, [params.id]);

  if (loading) return <div className="p-12 text-center">Loading...</div>;
  if (!app) return <div className="p-12 text-center text-red-500">Application not found</div>;

  const statusColor = {
    pending: "bg-yellow-100 text-yellow-700",
    approved: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
  }[app.status];

  return (
    <main className="min-h-screen bg-[var(--background)] p-8">
      <div className="max-w-xl mx-auto bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
        <h1 className="text-2xl font-bold mb-1">Application Status</h1>
        <p className="text-sm text-gray-500 mb-6">Submitted {new Date(app.created_at).toLocaleDateString()}</p>

        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Name</span>
            <span>{app.name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Email</span>
            <span>{app.email}</span>
          </div>
          {app.company && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Company</span>
              <span>{app.company}</span>
            </div>
          )}
          {app.publication && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Publication</span>
              <span>{app.publication}</span>
            </div>
          )}
          {app.startup_name && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Startup</span>
              <span>{app.startup_name}</span>
            </div>
          )}
        </div>

        <div className="border-t pt-4">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-sm font-medium">Status:</span>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor}`}>
              {app.status.toUpperCase()}
            </span>
          </div>

          {app.status === "pending" && (
            <p className="text-sm text-gray-500">Your application is being reviewed. We'll notify you by email once a decision is made.</p>
          )}

          {app.status === "approved" && app.voucher_code && (
            <div className="bg-green-50 rounded-xl p-4">
              <p className="text-sm font-medium text-green-800 mb-2">Your pass code:</p>
              <div className="bg-white rounded-lg px-4 py-3 text-center">
                <span className="text-2xl font-mono font-bold text-[var(--accent-orange)]">{app.voucher_code}</span>
              </div>
              <p className="text-xs text-green-600 mt-2">Use this code on the <a href="/" className="underline">ticket page</a> to claim your pass.</p>
            </div>
          )}

          {app.status === "approved" && !app.voucher_code && (
            <div className="bg-green-50 rounded-xl p-4">
              <p className="text-sm text-green-800">Your application has been approved! You can now <a href="/" className="underline font-medium">purchase your ticket</a>.</p>
            </div>
          )}

          {app.status === "rejected" && (
            <div className="bg-red-50 rounded-xl p-4">
              <p className="text-sm text-red-800">Unfortunately, your application was not approved.</p>
              {app.rejection_reason && (
                <p className="text-sm text-red-600 mt-2"><strong>Reason:</strong> {app.rejection_reason}</p>
              )}
              <p className="text-xs text-red-500 mt-2">You can still purchase other ticket types on the <a href="/" className="underline">ticket page</a>.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
