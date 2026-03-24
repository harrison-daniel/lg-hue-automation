export default function SceneCardSkeleton() {
  return (
    <div
      className="rounded-xl p-5 animate-shimmer"
      style={{ border: "1px solid var(--border)", minHeight: "132px" }}
    >
      <div className="flex items-center gap-3 mb-2">
        <div
          className="w-8 h-8 rounded-lg"
          style={{ background: "var(--border)" }}
        />
        <div
          className="h-5 w-24 rounded"
          style={{ background: "var(--border)" }}
        />
      </div>
      <div
        className="h-4 w-48 rounded mt-3"
        style={{ background: "var(--border)" }}
      />
    </div>
  );
}
