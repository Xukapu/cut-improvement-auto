import { apiRequest } from "./client";
import type { CurrentUser } from "../types/auth";

export type LoginPayload = {
  login: string;
  password: string;
};

export async function login(
  payload: LoginPayload,
): Promise<CurrentUser> {
  await apiRequest<unknown>(
    "/api/v1/auth/login",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );

  return getCurrentUser();
}

export function getCurrentUser():
  Promise<CurrentUser> {
  return apiRequest<CurrentUser>(
    "/api/v1/auth/me",
  );
}

export async function logout():
  Promise<void> {
  await apiRequest<void>(
    "/api/v1/auth/logout",
    {
      method: "POST",
      skipJson: true,
    },
  );
}