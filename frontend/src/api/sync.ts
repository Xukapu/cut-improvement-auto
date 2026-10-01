import {
  apiRequest,
} from "./client";

import type {
  SyncDevice,
  SyncStatus,
} from "../types/sync";


const DEVICE_KEY =
  "cut-sync-device-key-v1";


function createUuid():
  string {
  if (
    typeof crypto
      .randomUUID ===
    "function"
  ) {
    return crypto.randomUUID();
  }

  const bytes =
    new Uint8Array(16);

  crypto.getRandomValues(
    bytes,
  );

  bytes[6] =
    (
      bytes[6] & 0x0f
    ) | 0x40;

  bytes[8] =
    (
      bytes[8] & 0x3f
    ) | 0x80;

  const hex =
    Array.from(
      bytes,
      (value) =>
        value
          .toString(16)
          .padStart(
            2,
            "0",
          ),
    );

  return (
    `${hex.slice(0, 4).join("")}-` +
    `${hex.slice(4, 6).join("")}-` +
    `${hex.slice(6, 8).join("")}-` +
    `${hex.slice(8, 10).join("")}-` +
    `${hex.slice(10, 16).join("")}`
  );
}


export function getDeviceKey():
  string {
  const existing =
    localStorage.getItem(
      DEVICE_KEY,
    );

  if (existing) {
    return existing;
  }

  const created =
    createUuid();

  localStorage.setItem(
    DEVICE_KEY,
    created,
  );

  return created;
}


function deviceName():
  string {
  const platform =
    navigator.platform ||
    "Устройство";

  return (
    `${platform} · ` +
    `${window.screen.width}×${window.screen.height}`
  ).slice(
    0,
    120,
  );
}


function devicePlatform():
  string {
  return (
    navigator.userAgent ||
    "Browser"
  ).slice(
    0,
    200,
  );
}


export function registerSyncDevice():
  Promise<SyncDevice> {
  return apiRequest<SyncDevice>(
    "/api/v1/sync/devices/register",
    {
      method: "POST",

      offlineCache:
        false,

      body: JSON.stringify({
        device_key:
          getDeviceKey(),

        device_name:
          deviceName(),

        platform:
          devicePlatform(),
      }),
    },
  );
}


export function getSyncStatus():
  Promise<SyncStatus> {
  return apiRequest<SyncStatus>(
    `/api/v1/sync/status/${getDeviceKey()}`,
    {
      offlineCache:
        false,
    },
  );
}