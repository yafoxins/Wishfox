export type Priority = "low" | "medium" | "high";
export type WishStatus = "planned" | "ordered" | "gifted";
export type Visibility = "public" | "unlisted" | "private";

export interface User {
  id: number;
  display_name: string;
  username: string;
  tg_username?: string | null;
  custom_username?: string | null;
  avatar_url?: string | null;
  bio?: string | null;
  locale?: string | null;
  requires_custom_username?: boolean;
}

export interface PublicUser {
  id: number;
  display_name: string;
  username: string;
  avatar_url?: string | null;
  bio?: string | null;
}

export interface Wish {
  id: number;
  wishlist_id: number;
  title: string;
  description?: string | null;
  url?: string | null;
  price?: string | null;
  image_url?: string | null;
  tags: string[];
  priority: Priority;
  status: WishStatus;
  position: number;
}

export interface Wishlist {
  id: number;
  title: string;
  visibility: Visibility;
  cover_url?: string | null;
  wishes: Wish[];
}

export interface WishFilters {
  q?: string;
  priority?: Priority;
  status?: WishStatus;
  tags?: string[];
  price_min?: number;
  price_max?: number;
  sort?: "created_at" | "priority" | "price" | "position";
  page?: number;
  per_page?: number;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

export interface Subscription {
  id: number;
  follower_id: number;
  target_user_id: number;
  target?: User;
}

export interface FeedItem {
  actor: User;
  wish: Wish;
  action: "created" | "updated";
  created_at: string;
}

export interface Notification {
  id: number;
  type: "wish_created" | "wish_updated";
  payload: Record<string, unknown>;
  is_sent: boolean;
  created_at: string;
  sent_at?: string | null;
}

export interface LinkPreview {
  url: string;
  title?: string | null;
  description?: string | null;
  image?: string | null;
}
