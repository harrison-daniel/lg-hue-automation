"use client";

import { useState } from "react";
import { activateScene, type SceneDefinition } from "@/lib/api";

type CardState = "idle" | "loading" | "success" | "error";

interface SceneCardProps {
  scene: SceneDefinition;
  suggested?: boolean;
}

export default function SceneCard({ scene, suggested }: SceneCardProps) {
  const [state, setState] = useState<CardState>("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function handleActivate() {
    if (state === "loading") return;

    // Haptic feedback on mobile
    navigator.vibrate?.(50);

    setState("loading");
    setErrorMsg("");

    try {
      const result = await activateScene(scene.name);
      setState(result.success ? "success" : "error");
      if (!result.success) {
        setErrorMsg(result.errors.join(", ") || result.message);
      }
    } catch {
      setState("error");
      setErrorMsg("Failed to reach backend");
    }

    setTimeout(() => setState("idle"), 3000);
  }

  const borderColor =
    state === "success"
      ? "var(--success)"
      : state === "error"
        ? "var(--error)"
        : state === "loading"
          ? "var(--accent)"
          : suggested
            ? "var(--accent)"
            : "var(--border)";

  const animationClass =
    state === "loading"
      ? "animate-pulse-loading"
      : state === "success"
        ? "animate-pulse-success"
        : "";

  return (
    <button
      onClick={handleActivate}
      disabled={state === "loading"}
      className={`w-full text-left rounded-xl p-5 transition-all duration-200 animate-fade-in hover:scale-[1.02] active:scale-[0.98] ${animationClass}`}
      style={{
        background: "var(--bg-card)",
        border: `1px solid ${borderColor}`,
        cursor: state === "loading" ? "wait" : "pointer",
        opacity: suggested === false ? 0.6 : 1,
      }}
    >
      <div className="flex items-center gap-3 mb-2">
        <span className="text-2xl" role="img" aria-label={scene.display_name}>
          {scene.icon}
        </span>
        <h2 className="text-lg font-semibold">{scene.display_name}</h2>
        {suggested && state === "idle" && (
          <span
            className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded"
            style={{ background: "rgba(59, 130, 246, 0.15)", color: "var(--accent)" }}
          >
            now
          </span>
        )}
      </div>

      <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>
        {scene.description}
      </p>

      <div className="text-sm h-5">
        {state === "loading" && (
          <span style={{ color: "var(--accent)" }}>Activating...</span>
        )}
        {state === "success" && (
          <span style={{ color: "var(--success)" }}>Activated</span>
        )}
        {state === "error" && (
          <span style={{ color: "var(--error)" }}>{errorMsg}</span>
        )}
      </div>
    </button>
  );
}
