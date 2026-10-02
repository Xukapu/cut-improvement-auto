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


export type SyncOperationKind =
  | "client.create"
  | "vehicle.create"
  | "appointment.create";


export type SyncQueuedOperation = {
  operation_id: string;
  device_key: string;
  entity_id: string;

  kind: SyncOperationKind;

  payload:
    Record<string, unknown>;

  created_at: number;

  attempts: number;

  last_error:
    | string
    | null;
};


export type SyncPushResponse = {
  operation_id: string;
  entity_id: string;

  kind: SyncOperationKind;

  result_number: number;

  replayed: boolean;

  server_time: string;
};


export type SyncFlushResult = {
  synced: number;
  failed: number;
  pending: number;
};