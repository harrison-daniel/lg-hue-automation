import DeviceStatusBar from "./device-status";

export default function Header() {
  return (
    <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Home Control</h1>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          LG TV + Philips Hue
        </p>
      </div>
      <DeviceStatusBar />
    </header>
  );
}
