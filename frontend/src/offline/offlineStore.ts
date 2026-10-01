import type {
  CurrentUser,
} from "../types/auth";


const DB_NAME =
  "cut-improvement-auto-offline";

const DB_VERSION = 1;

const RESPONSE_STORE =
  "api-responses";

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


type OfflineSession = {
  user: CurrentUser;
  savedAt: number;
};


export type NetworkStateDetail = {
  online: boolean;
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


export function setOfflineUserId(
  userId:
    string | null,
): void {
  activeUserId = userId;
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
    // Кэш не должен ломать основной запрос.
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
  activeUserId = null;

  localStorage.removeItem(
    OFFLINE_SESSION_KEY,
  );

  await new Promise<void>(
    (resolve) => {
      const request =
        indexedDB.deleteDatabase(
          DB_NAME,
        );

      request.onsuccess =
        () => {
          resolve();
        };

      request.onerror =
        () => {
          resolve();
        };

      request.onblocked =
        () => {
          resolve();
        };
    },
  );
}