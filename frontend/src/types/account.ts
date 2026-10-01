import type {
  UserRole,
} from "./auth";


export type Profile = {
  first_name: string;
  last_name: string;
  phone: string | null;
  login: string;
  role: UserRole;
  full_name: string;
};


export type ProfileUpdatePayload = {
  first_name: string;
  last_name: string;
  phone: string;
};


export type EmployeeAccess = {
  employee_number: number;
  full_name: string;

  is_active: boolean;
  archived: boolean;

  current_rate_percent:
    | string
    | number;

  access_exists: boolean;
  access_enabled: boolean;

  user_id: string | null;
  login: string | null;
  role: UserRole | null;
  phone: string | null;
};


export type EmployeeAccessCreatePayload = {
  full_name: string;
  rate_percent: string;
  grant_access: boolean;

  login?: string | null;
  role?: UserRole;

  temporary_password?:
    | string
    | null;

  phone?: string | null;
};


export type EmployeeAccessUpdatePayload = {
  full_name?: string;
  rate_percent?: string;

  is_active?: boolean;
  grant_access?: boolean;

  login?: string | null;
  role?: UserRole;

  phone?: string | null;

  temporary_password?:
    | string
    | null;
};


export type MessageResponse = {
  message: string;
};