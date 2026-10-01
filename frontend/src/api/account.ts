import {
  apiRequest,
} from "./client";

import type {
  EmployeeAccess,
  EmployeeAccessCreatePayload,
  EmployeeAccessUpdatePayload,
  MessageResponse,
  Profile,
  ProfileUpdatePayload,
} from "../types/account";


export function getProfile():
  Promise<Profile> {
  return apiRequest<Profile>(
    "/api/v1/account/profile",
  );
}


export function updateProfile(
  payload: ProfileUpdatePayload,
): Promise<Profile> {
  return apiRequest<Profile>(
    "/api/v1/account/profile",
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<MessageResponse> {
  return apiRequest<MessageResponse>(
    "/api/v1/account/password",
    {
      method: "PUT",
      body: JSON.stringify({
        current_password:
          currentPassword,
        new_password:
          newPassword,
      }),
    },
  );
}


export function listEmployeeAccess():
  Promise<EmployeeAccess[]> {
  return apiRequest<
    EmployeeAccess[]
  >(
    "/api/v1/account/employees",
  );
}


export function createEmployeeAccess(
  payload:
    EmployeeAccessCreatePayload,
): Promise<EmployeeAccess> {
  return apiRequest<EmployeeAccess>(
    "/api/v1/account/employees",
    {
      method: "POST",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updateEmployeeAccess(
  employeeNumber: number,
  payload:
    EmployeeAccessUpdatePayload,
): Promise<EmployeeAccess> {
  return apiRequest<EmployeeAccess>(
    `/api/v1/account/employees/${employeeNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function archiveEmployeeAccess(
  employeeNumber: number,
): Promise<EmployeeAccess> {
  return apiRequest<EmployeeAccess>(
    `/api/v1/account/employees/${employeeNumber}`,
    {
      method: "DELETE",
    },
  );
}


export function restoreEmployeeAccess(
  employeeNumber: number,
): Promise<EmployeeAccess> {
  return apiRequest<EmployeeAccess>(
    `/api/v1/account/employees/${employeeNumber}/restore`,
    {
      method: "POST",
    },
  );
}


export function resetEmployeePassword(
  employeeNumber: number,
  newPassword: string,
): Promise<MessageResponse> {
  return apiRequest<MessageResponse>(
    `/api/v1/account/employees/${employeeNumber}/reset-password`,
    {
      method: "POST",
      body: JSON.stringify({
        new_password:
          newPassword,
      }),
    },
  );
}