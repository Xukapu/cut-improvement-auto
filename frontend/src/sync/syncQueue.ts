import {
  ApiError,
} from "../api/client";

import {
  createSyncUuid,
  getDeviceKey,
  pushSyncOperation,
} from "../api/sync";

import {
  emitServerState,
  enqueueSyncOperation,
  getPendingSyncCount,
  listPendingSyncOperations,
  removeSyncOperation,
  updateSyncOperationError,
} from "../offline/offlineStore";

import type {
  SyncFlushResult,
  SyncOperationKind,
  SyncQueuedOperation,
} from "../types/sync";


let activeFlush:
  Promise<SyncFlushResult> | null =
    null;


export async function queueSyncOperation(
  kind: SyncOperationKind,
  entityId: string,
  payload:
    Record<string, unknown>,
): Promise<SyncQueuedOperation> {
  const operation:
    SyncQueuedOperation = {
      operation_id:
        createSyncUuid(),

      device_key:
        getDeviceKey(),

      entity_id:
        entityId,

      kind,
      payload,

      created_at:
        Date.now(),

      attempts: 0,

      last_error: null,
  };

  await enqueueSyncOperation(
    operation,
  );

  return operation;
}


function emitSyncCompleted(
  synced: number,
): void {
  if (synced <= 0) {
    return;
  }

  window.dispatchEvent(
    new CustomEvent(
      "cut-sync-completed",
      {
        detail: {
          synced,
        },
      },
    ),
  );
}


async function runFlush():
  Promise<SyncFlushResult> {
  const operations =
    await listPendingSyncOperations();

  let synced = 0;
  let failed = 0;


  for (
    const operation
    of operations
  ) {
    try {
      await pushSyncOperation(
        operation,
      );

      await removeSyncOperation(
        operation.operation_id,
      );

      synced += 1;

      emitServerState(
        true,
      );
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Не удалось синхронизировать операцию.";

      await updateSyncOperationError(
        operation.operation_id,
        message,
      );

      failed += 1;

      if (
        error instanceof ApiError &&
        (
          error.status === 0 ||
          error.status >= 500
        )
      ) {
        emitServerState(
          false,
        );

        break;
      }
    }
  }


  const result:
    SyncFlushResult = {
      synced,
      failed,

      pending:
        await getPendingSyncCount(),
  };


  emitSyncCompleted(
    synced,
  );


  return result;
}


export async function flushSyncQueue():
  Promise<SyncFlushResult> {
  if (activeFlush) {
    return activeFlush;
  }

  activeFlush =
    runFlush();

  try {
    return await activeFlush;
  } finally {
    activeFlush = null;
  }
}