"use client";

import { useEffect, useState } from "react";
import Header from "@/components/header";
import SceneCard from "@/components/scene-card";
import SceneCardSkeleton from "@/components/scene-card-skeleton";
import DiagnosticsPanel from "@/components/diagnostics-panel";
import { getScenes, type SceneDefinition } from "@/lib/api";

function getTimeOfDay(): "day" | "night" {
  const hour = new Date().getHours();
  return hour >= 6 && hour < 18 ? "day" : "night";
}

function sortScenes(scenes: SceneDefinition[], timeOfDay: string): SceneDefinition[] {
  return [...scenes].sort((a, b) => {
    // "all-off" always last
    if (a.name === "all-off") return 1;
    if (b.name === "all-off") return -1;
    // Matching time_of_day first
    const aMatch = a.time_of_day === timeOfDay || a.time_of_day === "any" ? 0 : 1;
    const bMatch = b.time_of_day === timeOfDay || b.time_of_day === "any" ? 0 : 1;
    return aMatch - bMatch;
  });
}

export default function Dashboard() {
  const [scenes, setScenes] = useState<SceneDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [timeOfDay, setTimeOfDay] = useState(getTimeOfDay);

  useEffect(() => {
    getScenes()
      .then((data) => setScenes(data.scenes))
      .catch(() => setError("Could not connect to backend. Is the server running?"))
      .finally(() => setLoading(false));
  }, []);

  // Update time of day every 60s for hour boundary transitions
  useEffect(() => {
    const interval = setInterval(() => setTimeOfDay(getTimeOfDay()), 60_000);
    return () => clearInterval(interval);
  }, []);

  const sorted = sortScenes(scenes, timeOfDay);

  return (
    <main className="min-h-screen p-6 max-w-4xl mx-auto">
      <Header />
      <DiagnosticsPanel />

      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 7 }).map((_, i) => (
            <SceneCardSkeleton key={i} />
          ))}
        </div>
      )}

      {error && (
        <div
          className="rounded-lg p-4 text-sm animate-fade-in"
          style={{
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid var(--error)",
            color: "var(--error)",
          }}
        >
          {error}
        </div>
      )}

      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {sorted.map((scene) => (
            <SceneCard
              key={scene.name}
              scene={scene}
              suggested={
                scene.time_of_day === timeOfDay || scene.time_of_day === "any"
              }
            />
          ))}
        </div>
      )}
    </main>
  );
}
