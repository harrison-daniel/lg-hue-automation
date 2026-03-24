"use client";

import { useEffect, useState } from "react";
import { getDiagnostics, type DiagnosticsResponse } from "@/lib/api";

function getTempColor(temp: number): string {
  if (temp >= 80) return "var(--error)";
  if (temp >= 60) return "#f59e0b";
  return "var(--success)";
}

function UsageBar({ percent, label }: { percent: number; label: string }) {
  const color =
    percent >= 85 ? "var(--error)" : percent >= 70 ? "#f59e0b" : "var(--accent)";
  return (
    <div className="flex-1 min-w-[120px]">
      <div
        className="flex justify-between text-xs mb-1"
        style={{ color: "var(--text-secondary)" }}
      >
        <span>{label}</span>
        <span>{percent.toFixed(0)}%</span>
      </div>
      <div className="h-1.5 rounded-full" style={{ background: "var(--border)" }}>
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.min(percent, 100)}%`, background: color }}
        />
      </div>
    </div>
  );
}

export default function DiagnosticsPanel() {
  const [data, setData] = useState<DiagnosticsResponse | null>(null);
  const [collapsed, setCollapsed] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const d = await getDiagnostics();
        setData(d);
        setError(false);
      } catch {
        setError(true);
      }
    }
    fetchData();
    const interval = setInterval(fetchData, 30_000);
    return () => clearInterval(interval);
  }, []);

  if (error || !data) return null;

  const maxTemp =
    data.cpu_temps.length > 0
      ? Math.max(...data.cpu_temps.map((t) => t.current))
      : null;

  return (
    <div
      className="rounded-xl mb-6 animate-fade-in"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
    >
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm"
        style={{ color: "var(--text-secondary)" }}
      >
        <div className="flex items-center gap-3">
          <span>Server</span>
          {maxTemp !== null && (
            <span style={{ color: getTempColor(maxTemp) }}>
              {maxTemp.toFixed(0)}°C
            </span>
          )}
          <span>{data.uptime_human}</span>
        </div>
        <span
          className="transition-transform duration-200"
          style={{
            transform: collapsed ? "rotate(0)" : "rotate(180deg)",
          }}
        >
          ▾
        </span>
      </button>

      {!collapsed && (
        <div className="px-4 pb-4 flex flex-wrap gap-4">
          <UsageBar percent={data.cpu_percent} label="CPU" />
          <UsageBar percent={data.memory.percent} label="Memory" />
          <UsageBar percent={data.disk.percent} label="Disk" />
          {data.cpu_temps.length > 0 && (
            <div className="flex-1 min-w-[120px]">
              <div
                className="text-xs mb-1"
                style={{ color: "var(--text-secondary)" }}
              >
                Temperatures
              </div>
              <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs">
                {data.cpu_temps.map((t, i) => (
                  <span key={i} style={{ color: getTempColor(t.current) }}>
                    {t.label}: {t.current.toFixed(0)}°C
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
