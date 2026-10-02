import {
  Cloud,
  CloudOff,
  RefreshCw,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  registerSyncDevice,
} from "../api/sync";

import {
  emitServerState,
  getPendingSyncCount,
} from "../offline/offlineStore";

import type {
  NetworkStateDetail,
  SyncQueueStateDetail,
} from "../offline/offlineStore";

import {
  flushSyncQueue,
} from "../sync/syncQueue";


type SyncState =
  | "checking"
  | "online"
  | "offline";


const AUTO_CHECK_MS = 8000;


export function SyncStatusBadge() {
  const [
    state,
    setState,
  ] = useState<SyncState>(
    navigator.onLine
      ? "checking"
      : "offline",
  );


  const [
    busy,
    setBusy,
  ] = useState(false);


  const [
    pendingCount,
    setPendingCount,
  ] = useState(0);


  const refreshPending =
    useCallback(
      async () => {
        const count =
          await getPendingSyncCount();

        setPendingCount(
          count,
        );
      },
      [],
    );


  const check =
    useCallback(
      async (
        showBusy = false,
      ) => {
        if (
          !navigator.onLine
        ) {
          setState(
            "offline",
          );

          emitServerState(
            false,
          );

          await refreshPending();

          return;
        }


        if (showBusy) {
          setBusy(true);
        }


        try {
          await registerSyncDevice();

          const result =
            await flushSyncQueue();

          setPendingCount(
            result.pending,
          );

          setState(
            "online",
          );

          emitServerState(
            true,
          );
        } catch {
          setState(
            "offline",
          );

          emitServerState(
            false,
          );

          await refreshPending();
        } finally {
          if (showBusy) {
            setBusy(false);
          }
        }
      },
      [
        refreshPending,
      ],
    );


  useEffect(() => {
    const firstCheck =
      window.setTimeout(
        () => {
          void refreshPending();
          void check(false);
        },
        0,
      );


    const interval =
      window.setInterval(
        () => {
          void check(false);
        },
        AUTO_CHECK_MS,
      );


    function browserOnline() {
      void check(true);
    }


    function browserOffline() {
      setState(
        "offline",
      );

      emitServerState(
        false,
      );

      void refreshPending();
    }


    function serverState(
      event: Event,
    ) {
      const custom =
        event as
          CustomEvent<
            NetworkStateDetail
          >;

      setState(
        custom.detail.online
          ? "online"
          : "offline",
      );
    }


    function queueState(
      event: Event,
    ) {
      const custom =
        event as
          CustomEvent<
            SyncQueueStateDetail
          >;

      setPendingCount(
        custom.detail.pending,
      );
    }


    window.addEventListener(
      "online",
      browserOnline,
    );

    window.addEventListener(
      "offline",
      browserOffline,
    );

    window.addEventListener(
      "cut-server-state",
      serverState,
    );

    window.addEventListener(
      "cut-sync-queue-state",
      queueState,
    );


    return () => {
      window.clearTimeout(
        firstCheck,
      );

      window.clearInterval(
        interval,
      );

      window.removeEventListener(
        "online",
        browserOnline,
      );

      window.removeEventListener(
        "offline",
        browserOffline,
      );

      window.removeEventListener(
        "cut-server-state",
        serverState,
      );

      window.removeEventListener(
        "cut-sync-queue-state",
        queueState,
      );
    };
  }, [
    check,
    refreshPending,
  ]);


  let label:
    string;


  if (
    busy ||
    state === "checking"
  ) {
    label =
      pendingCount > 0
        ? `Синхронизация · ожидают: ${pendingCount}`
        : "Проверяем связь...";
  } else if (
    state === "online"
  ) {
    label =
      pendingCount > 0
        ? `Онлайн · ожидают: ${pendingCount}`
        : "Онлайн · устройство подключено";
  } else {
    label =
      pendingCount > 0
        ? `Офлайн · ожидают: ${pendingCount}`
        : "Офлайн · сохранённые данные";
  }


  return (
    <button
      className={
        `sync-status-badge sync-status-${state}`
      }
      disabled={busy}
      onClick={() => {
        void check(true);
      }}
      title="Проверить соединение и синхронизацию"
      type="button"
    >
      {busy ||
      state ===
        "checking" ? (
        <RefreshCw
          className="sync-status-spin"
          size={15}
        />
      ) : state ===
        "online" ? (
        <Cloud size={15} />
      ) : (
        <CloudOff size={15} />
      )}

      <span>
        {label}
      </span>
    </button>
  );
}