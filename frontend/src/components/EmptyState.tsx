interface EmptyStateProps {
  title: string;
  description: string;
  action?: React.ReactNode;
  illustration?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description, action, illustration }) => (
  <div className="cozy-card" style={{ textAlign: "center", padding: "40px 24px", display: "grid", gap: 16 }}>
    <div style={{ fontSize: 32 }}>{illustration ?? "*"}</div>
    <h2 style={{ margin: 0, fontSize: 22 }}>{title}</h2>
    <p style={{ margin: 0, color: "var(--tg-hint)", lineHeight: 1.5 }}>{description}</p>
    {action}
  </div>
);
