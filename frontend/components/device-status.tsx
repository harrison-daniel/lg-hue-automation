"use client";

import { useEffect, useState } from "react";
import { getDeviceStatus, type DeviceStatus } from "@/lib/api";

export default function DeviceStatusBar() {
  const [devices, setDevices] = useState<DeviceStatus[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function fetchStatus() {
      try {
        const data = await getDeviceStatus();
        setDevices(data.devices);
        setError(false);
      } catch {
        setError(true);
      }
    }

    fetchStatus();
    const interval = setInterval(fetchStatus, 30_000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="flex items-center gap-2 text-sm" style={{ color: "var(--text-secondary)" }}>
        <span
          className="inline-block w-2 h-2 rounded-full"
          style={{ background: "var(--error)" }}
        />
        Backend unreachable
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-4">
      {devices.map((device) => (
        <div
          key={device.entity_id}
          className="flex items-center gap-2 text-sm"
          style={{ color: "var(--text-secondary)" }}
        >
          <span
            className="inline-block w-2 h-2 rounded-full"
            style={{
              background: device.online ? "var(--success)" : "var(--error)",
            }}
          />
          {device.name}
        </div>
      ))}
    </div>
  );
}
