const colors: Record<string, string> = {
  PENDING: "var(--status-pending)",
  CONFIRMED: "var(--status-confirmed)",
  PROCESSING: "var(--status-processing)",
  COMPLETED: "var(--status-completed)",
  CANCELLED: "var(--status-cancelled)",
};

export default function StatusBadge({ status }: { status: string }) {
  const bg = colors[status] ?? "var(--glass-border)";
  return (
    <span className="status-badge" style={{ background: bg }}>
      {status}
    </span>
  );
}
