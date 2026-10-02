import type {
  CurrentUser,
} from "../types/auth";

import type {
  SyncQueuedOperation,
} from "../types/sync";


const DB_NAME =
  "cut-improvement-auto-offline";

const DB_VERSION = 2;

const RESPONSE_STORE =
  "api-responses";

const OPERATION_STORE =
  "sync-operations";

const OFFLINE_SESSION_KEY =
  "cut-offline-session-v1";

const OFFLINE_SESSION_MAX_AGE_MS =
  12 * 60 * 60 * 1000;


type CachedResponse = {
  key: string;
  userId: string;
  path: string;
  payload: unknown;
  savedAt: number;
};


type StoredSyncOperation =
  SyncQueuedOperation & {
    key: string;
    userId: string;
  };


type OfflineSession = {
  user: CurrentUser;
  savedAt: number;
};


export type NetworkStateDetail = {
  online: boolean;
};


export type SyncQueueStateDetail = {
  pending: number;
};


let activeUserId:
  string | null = null;


function openDatabase():
  Promise<IDBDatabase> {
  return new Promise(
    (
      resolve,
      reject,
    ) => {
      const request =
        indexedDB.open(
          DB_NAME,
          DB_VERSION,
        );

      request.onupgradeneeded =
        () => {
          const db =
            request.result;

          if (
            !db.objectStoreNames
              .contains(
                RESPONSE_STORE,
              )
          ) {
            db.createObjectStore(
              RESPONSE_STORE,
              {
                keyPath: "key",
              },
            );
          }

          if (
            !db.objectStoreNames
              .contains(
                OPERATION_STORE,
              )
          ) {
            db.createObjectStore(
              OPERATION_STORE,
              {
                keyPath: "key",
              },
            );
          }
        };

      request.onsuccess =
        () => {
          resolve(
            request.result,
          );
        };

      request.onerror =
        () => {
          reject(
            request.error,
          );
        };
    },
  );
}


function transactionDone(
  transaction:
    IDBTransaction,
): Promise<void> {
  return new Promise(
    (
      resolve,
      reject,
    ) => {
      transaction.oncomplete =
        () => {
          resolve();
        };

      transaction.onerror =
        () => {
          reject(
            transaction.error,
          );
        };

      transaction.onabort =
        () => {
          reject(
            transaction.error,
          );
        };
    },
  );
}


function requestResult<T>(
  request: IDBRequest<T>,
): Promise<T> {
  return new Promise(
    (
      resolve,
      reject,
    ) => {
      request.onsuccess =
        () => {
          resolve(
            request.result,
          );
        };

      request.onerror =
        () => {
          reject(
            request.error,
          );
        };
    },
  );
}


function cacheKey(
  userId: string,
  path: string,
): string {
  return `${userId}:${path}`;
}


function operationKey(
  userId: string,
  operationId: string,
): string {
  return (
    `${userId}:${operationId}`
  );
}


export function setOfflineUserId(
  userId:
    string | null,
): void {
  activeUserId = userId;
}


export function getOfflineUserId():
  string | null {
  return activeUserId;
}


export function emitServerState(
  online: boolean,
): void {
  window.dispatchEvent(
    new CustomEvent<NetworkStateDetail>(
      "cut-server-state",
      {
        detail: {
          online,
        },
      },
    ),
  );
}


async function emitQueueState():
  Promise<void> {
  const pending =
    await getPendingSyncCount();

  window.dispatchEvent(
    new CustomEvent<SyncQueueStateDetail>(
      "cut-sync-queue-state",
      {
        detail: {
          pending,
        },
      },
    ),
  );
}


export async function cacheApiResponse(
  path: string,
  payload: unknown,
): Promise<void> {
  if (!activeUserId) {
    return;
  }

  try {
    const db =
      await openDatabase();

    const transaction =
      db.transaction(
        RESPONSE_STORE,
        "readwrite",
      );

    const store =
      transaction.objectStore(
        RESPONSE_STORE,
      );

    const item:
      CachedResponse = {
        key: cacheKey(
          activeUserId,
          path,
        ),

        userId:
          activeUserId,

        path,
        payload,
        savedAt: Date.now(),
      };

    store.put(item);

    await transactionDone(
      transaction,
    );

    db.close();
  } catch {
    // Локальный кэш не должен ломать основной запрос.
  }
}


export async function getCachedApiResponse<T>(
  path: string,
): Promise<
  | {
      found: true;
      payload: T;
    }
  | {
      found: false;
    }
> {
  if (!activeUserId) {
    return {
      found: false,
    };
  }

  try {
    const db =
      await openDatabase();

    const transaction =
      db.transaction(
        RESPONSE_STORE,
        "readonly",
      );

    const store =
      transaction.objectStore(
        RESPONSE_STORE,
      );

    const item =
      await requestResult<
        CachedResponse | undefined
      >(
        store.get(
          cacheKey(
            activeUserId,
            path,
          ),
        ),
      );

    await transactionDone(
      transaction,
    );

    db.close();

    if (!item) {
      return {
        found: false,
      };
    }

    return {
      found: true,
      payload:
        item.payload as T,
    };
  } catch {
    return {
      found: false,
    };
  }
}


export async function enqueueSyncOperation(
  operation:
    SyncQueuedOperation,
): Promise<void> {
  if (!activeUserId) {
    throw new Error(
      "Нет активного пользователя для offline-очереди.",
    );
  }

  const db =
    await openDatabase();

  const transaction =
    db.transaction(
      OPERATION_STORE,
      "readwrite",
    );

  const store =
    transaction.objectStore(
      OPERATION_STORE,
    );

  const stored:
    StoredSyncOperation = {
      ...operation,

      key: operationKey(
        activeUserId,
        operation.operation_id,
      ),

      userId:
        activeUserId,
  };

  store.put(stored);

  await transactionDone(
    transaction,
  );

  db.close();

  await emitQueueState();
}


export async function listPendingSyncOperations():
  Promise<SyncQueuedOperation[]> {
  if (!activeUserId) {
    return [];
  }

  const db =
    await openDatabase();

  const transaction =
    db.transaction(
      OPERATION_STORE,
      "readonly",
    );

  const store =
    transaction.objectStore(
      OPERATION_STORE,
    );

  const items =
    await requestResult<
      StoredSyncOperation[]
    >(
      store.getAll(),
    );

  await transactionDone(
    transaction,
  );

  db.close();

  return items
    .filter(
      (item) =>
        item.userId ===
        activeUserId,
    )
    .sort(
      (
        left,
        right,
      ) =>
        left.created_at -
        right.created_at,
    )
    .map(
      ({
        key: _key,
        userId: _userId,
        ...operation
      }) => operation,
    );
}


export async function getPendingSyncCount():
  Promise<number> {
  const items =
    await listPendingSyncOperations();

  return items.length;
}


export async function removeSyncOperation(
  operationId: string,
): Promise<void> {
  if (!activeUserId) {
    return;
  }

  const db =
    await openDatabase();

  const transaction =
    db.transaction(
      OPERATION_STORE,
      "readwrite",
    );

  transaction
    .objectStore(
      OPERATION_STORE,
    )
    .delete(
      operationKey(
        activeUserId,
        operationId,
      ),
    );

  await transactionDone(
    transaction,
  );

  db.close();

  await emitQueueState();
}


export async function updateSyncOperationError(
  operationId: string,
  errorMessage: string,
): Promise<void> {
  if (!activeUserId) {
    return;
  }

  const db =
    await openDatabase();

  const transaction =
    db.transaction(
      OPERATION_STORE,
      "readwrite",
    );

  const store =
    transaction.objectStore(
      OPERATION_STORE,
    );

  const key =
    operationKey(
      activeUserId,
      operationId,
    );

  const item =
    await requestResult<
      StoredSyncOperation | undefined
    >(
      store.get(key),
    );

  if (item) {
    store.put({
      ...item,

      attempts:
        item.attempts + 1,

      last_error:
        errorMessage,
    });
  }

  await transactionDone(
    transaction,
  );

  db.close();

  await emitQueueState();
}


export function saveOfflineSession(
  user: CurrentUser,
): void {
  activeUserId = user.id;

  const value:
    OfflineSession = {
      user,
      savedAt: Date.now(),
    };

  localStorage.setItem(
    OFFLINE_SESSION_KEY,
    JSON.stringify(value),
  );
}


export function loadOfflineSession():
  CurrentUser | null {
  const raw =
    localStorage.getItem(
      OFFLINE_SESSION_KEY,
    );

  if (!raw) {
    return null;
  }

  try {
    const value =
      JSON.parse(
        raw,
      ) as OfflineSession;

    if (
      !value.user ||
      !value.user.id ||
      !value.savedAt
    ) {
      localStorage.removeItem(
        OFFLINE_SESSION_KEY,
      );

      return null;
    }

    if (
      Date.now() -
        value.savedAt >
      OFFLINE_SESSION_MAX_AGE_MS
    ) {
      localStorage.removeItem(
        OFFLINE_SESSION_KEY,
      );

      activeUserId = null;

      return null;
    }

    activeUserId =
      value.user.id;

    return value.user;
  } catch {
    localStorage.removeItem(
      OFFLINE_SESSION_KEY,
    );

    return null;
  }
}


export async function clearOfflineData():
  Promise<void> {
  const userId =
    activeUserId;

  activeUserId = null;

  localStorage.removeItem(
    OFFLINE_SESSION_KEY,
  );

  if (!userId) {
    return;
  }

  try {
    const db =
      await openDatabase();

    const transaction =
      db.transaction(
        RESPONSE_STORE,
        "readwrite",
      );

    const store =
      transaction.objectStore(
        RESPONSE_STORE,
      );

    const items =
      await requestResult<
        CachedResponse[]
      >(
        store.getAll(),
      );

    for (const item of items) {
      if (
        item.userId ===
        userId
      ) {
        store.delete(
          item.key,
        );
      }
    }

    await transactionDone(
      transaction,
    );

    db.close();
  } catch {
    // Выход из системы не должен ломаться из-за IndexedDB.
  }
}