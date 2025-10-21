import { DragDropContext, Draggable, Droppable, type DropResult } from "@hello-pangea/dnd";
import { useEffect, useMemo, useState } from "react";

import type { Wish, WishStatus, Priority } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { FilterBar } from "../components/FilterBar";
import { WishCard } from "../components/WishCard";

interface WishlistFilters {
  search: string;
  priority?: Priority;
  status?: WishStatus;
}

interface WishlistPageProps {
  wishes: Wish[];
  filters: WishlistFilters;
  onFiltersChange: (filters: WishlistFilters) => void;
  onAdd?: () => void;
  onReorder?: (ordered: Wish[]) => void;
  onEdit?: (wish: Wish) => void;
  t: (key: string) => string;
}

export const WishlistPage: React.FC<WishlistPageProps> = ({ wishes, filters, onFiltersChange, onAdd, onReorder, onEdit, t }) => {
  const [ordered, setOrdered] = useState<Wish[]>([...wishes]);

  useEffect(() => {
    setOrdered([...wishes]);
  }, [wishes]);

  const filtered = useMemo(() => {
    return ordered
      .filter((wish) => {
        if (filters.priority && wish.priority !== filters.priority) return false;
        if (filters.status && wish.status !== filters.status) return false;
        if (filters.search) {
          const haystack = `${wish.title} ${wish.description ?? ""} ${wish.tags.join(" ")}`.toLowerCase();
          if (!haystack.includes(filters.search.toLowerCase())) return false;
        }
        return true;
      })
      .sort((a, b) => a.position - b.position);
  }, [filters.priority, filters.search, filters.status, ordered]);

  const allowReorder = Boolean(onReorder) && !filters.priority && !filters.status && !filters.search;

  const handleDragEnd = (result: DropResult) => {
    if (!allowReorder || !result.destination) return;
    const items = Array.from(ordered);
    const [moved] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, moved);
    setOrdered(items);
    onReorder?.(items);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <FilterBar
        search={filters.search}
        onSearchChange={(value) => onFiltersChange({ ...filters, search: value })}
        priority={filters.priority}
        status={filters.status}
        onPriorityChange={(value) => onFiltersChange({ ...filters, priority: value })}
        onStatusChange={(value) => onFiltersChange({ ...filters, status: value })}
        t={t}
      />

      {filtered.length === 0 ? (
        <EmptyState
          title={t("wishlist.empty_title")}
          description={t("wishlist.empty_body")}
          illustration="*"
          action={
            onAdd ? (
              <button
                type="button"
                onClick={onAdd}
                style={{
                  padding: "12px 20px",
                  borderRadius: "18px",
                  background: "var(--tg-button)",
                  color: "var(--tg-button-text)",
                  fontWeight: 600,
                }}
              >
                {t("wishlist.add_button")}
              </button>
            ) : undefined
          }
        />
      ) : allowReorder ? (
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="wishlist">
            {(provided) => (
              <div ref={provided.innerRef} {...provided.droppableProps} style={{ display: "grid", gap: 16 }}>
                {ordered.map((wish, index) => (
                  <Draggable draggableId={String(wish.id)} index={index} key={wish.id}>
                    {(dragProvided) => (
                      <div ref={dragProvided.innerRef} {...dragProvided.draggableProps} {...dragProvided.dragHandleProps}>
                        <WishCard wish={wish} onEdit={onEdit} />
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      ) : (
        filtered.map((wish) => <WishCard key={wish.id} wish={wish} onEdit={onEdit} />)
      )}
    </div>
  );
};
