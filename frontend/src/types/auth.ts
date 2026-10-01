export type UserRole =
  | "owner"
  | "admin"
  | "mechanic"
  | "tech_admin";

export type CurrentUser = {
  id: string;
  full_name: string;
  first_name?: string | null;
  last_name?: string | null;
  phone?: string | null;
  login: string;
  role: UserRole;
  is_active: boolean;
};