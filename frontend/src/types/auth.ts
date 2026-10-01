export type UserRole =
  | "owner"
  | "admin"
  | "mechanic"
  | "tech_admin";

export type CurrentUser = {
  id?: string;
  login: string;
  role: UserRole;
  is_active?: boolean;
  full_name?: string | null;
};