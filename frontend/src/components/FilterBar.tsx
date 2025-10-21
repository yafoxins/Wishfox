import { ChangeEvent } from "react";

import type { Priority, WishStatus } from "../api/types";

interface FilterBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  priority?: Priority;
  status?: WishStatus;
  onPriorityChange: (value?: Priority) => void;
  onStatusChange: (value?: WishStatus) => void;
  t: (key: string) => string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  search,
  onSearchChange,
  priority,
  status,
  onPriorityChange,
  onStatusChange,
  t,
}) => {
  const handleSearch = (event: ChangeEvent<HTMLInputElement>) => onSearchChange(event.target.value);

  const priorityOptions: Priority[] = ["low", "medium", "high"];
  const statusOptions: WishStatus[] = ["planned", "ordered", "gifted"];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 20 }}>
      {/* Search */}
      <div style={{ position: "relative" }}>
        <input
          value={search}
          onChange={handleSearch}
          placeholder={t("wishlist.search_placeholder")}
          style={{
            width: "100%",
            padding: "12px 40px 12px 40px",
            borderRadius: 14,
            border: "1px solid rgba(15,23,42,0.18)",
            outline: "none",
            background: "var(--tg-secondary-bg)",
            fontSize: 14,
            color: "var(--tg-text)",
            boxShadow: "0 2px 10px rgba(15,23,42,0.06)",
          }}
        />
        <span style={{ position: "absolute", left: 12, top: 10, opacity: 0.7 }}>
          {/* magnifier */}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" fill="var(--tg-hint)"/>
          </svg>
        </span>
        {search && (
          <button
            type="button"
            onClick={() => onSearchChange("")}
            aria-label="clear"
            style={{ position: "absolute", right: 8, top: 8, width: 28, height: 28, borderRadius: 14, background: "rgba(15,23,42,0.08)", color: "var(--tg-hint)" }}
          >
            ×
          </button>
        )}
      </div>

      {/* Priority */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {priorityOptions.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onPriorityChange(priority === option ? undefined : option)}
            className="chip"
            style={{
              background: priority === option ? "var(--tg-button)" : "var(--tg-secondary-bg)",
              color: priority === option ? "var(--tg-button-text)" : "var(--tg-text)",
              border: "1px solid rgba(15,23,42,0.16)",
              textTransform: "capitalize",
            }}
          >
            {t(`wishlist.priority.${option}`)}
          </button>
        ))}
      </div>

      {/* Status */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {statusOptions.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onStatusChange(status === option ? undefined : option)}
            className="chip"
            style={{
              background: status === option ? "var(--tg-button)" : "var(--tg-secondary-bg)",
              color: status === option ? "var(--tg-button-text)" : "var(--tg-text)",
              border: "1px solid rgba(15,23,42,0.16)",
              textTransform: "capitalize",
            }}
          >
            {t(`wishlist.status.${option}`)}
          </button>
        ))}
      </div>
    </div>
  );
};

