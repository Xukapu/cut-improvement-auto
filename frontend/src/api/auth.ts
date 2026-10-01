import {
  ApiError,
  apiRequest,
} from "./client";

import {
  clearOfflineData,
  loadOfflineSession,
  saveOfflineSession,
  setOfflineUserId,
} from "../offline/offlineStore";

import type {
  CurrentUser,
} from "../types/auth";


export type LoginPayload = {
  login: string;
  password: string;
};


export async function login(
  payload:
    LoginPayload,
): Promise<CurrentUser> {
  await apiRequest<unknown>(
    "/api/v1/auth/login",
    {
      method: "POST",

      body: JSON.stringify(
        payload,
      ),

      offlineCache: false,
    },
  );

  return getCurrentUser();
}


export async function getCurrentUser():
  Promise<CurrentUser> {
  try {
    const user =
      await apiRequest<CurrentUser>(
        "/api/v1/auth/me",
        {
          offlineCache:
            false,
        },
      );

    saveOfflineSession(
      user,
    );

    return user;
  } catch (error) {
    if (
      error instanceof
        ApiError &&
      (
        error.status === 0 ||
        error.status >= 500
      )
    ) {
      const offlineUser =
        loadOfflineSession();

      if (offlineUser) {
        setOfflineUserId(
          offlineUser.id,
        );

        return offlineUser;
      }
    }

    if (
      error instanceof
        ApiError &&
      error.status === 401
    ) {
      await clearOfflineData();
    }

    throw error;
  }
}


export async function logout():
  Promise<void> {
  try {
    await apiRequest<void>(
      "/api/v1/auth/logout",
      {
        method: "POST",
        skipJson: true,
        offlineCache:
          false,
      },
    );
  } finally {
    await clearOfflineData();
  }
}