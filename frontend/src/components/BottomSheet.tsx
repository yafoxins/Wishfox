import { ReactNode } from "react";

interface BottomSheetProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export const BottomSheet: React.FC<BottomSheetProps> = ({ open, onClose, title, children }) => {
  if (!open) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(15,23,42,0.28)",
        backdropFilter: "blur(6px)",
        zIndex: 100,
        display: "flex",
        alignItems: "flex-end",
      }}
      onClick={onClose}
    >
      <div
        className="cozy-card"
        style={{
          width: "100%",
          borderBottomLeftRadius: 0,
          borderBottomRightRadius: 0,
          paddingBottom: 32,
        }}
        onClick={(event) => event.stopPropagation()}
      >
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: "0 0 16px", fontSize: 18 }}>{title}</h3>
          <button
            type="button"
            onClick={onClose}
            style={{
              borderRadius: "50%",
              width: 36,
              height: 36,
              background: "rgba(15, 23, 42, 0.08)",
              color: "var(--tg-hint)",
              fontSize: 16,
              fontWeight: 700,
            }}
          >
            X
          </button>
        </header>
        {children}
      </div>
    </div>
  );
};
