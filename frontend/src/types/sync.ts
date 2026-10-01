export type SyncDevice = {
  device_key: string;
  device_name: string;
  platform: string;

  last_seen_at: string;

  last_sync_at:
    | string
    | null;
};


export type SyncStatus = {
  server_time: string;

  device_registered:
    boolean;

  device:
    | SyncDevice
    | null;
};