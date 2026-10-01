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

import type {
  NetworkStateDetail,
} from "../offline/offlineStore";


type SyncState =
  | "checking"
  | "online"
  | "offline";


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


  const check =
    useCallback(
      async () => {
        if (
          !navigator.onLine
        ) {
          setState(
            "offline",
          );

          return;
        }

        setBusy(true);

        try {
          await registerSyncDevice();

          setState(
            "online",
          );
        } catch {
          setState(
            "offline",
          );
        } finally {
          setBusy(false);
        }
      },
      [],
    );


  useEffect(() => {
    const timer =
      window.setTimeout(
        () => {
          void check();
        },
        0,
      );

    function browserOnline() {
      void check();
    }

    function browserOffline() {
      setState(
        "offline",
      );
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

    return () => {
      window.clearTimeout(
        timer,
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
    };
  }, [check]);


  return (
    <button
      className={
        `sync-status-badge sync-status-${state}`
      }
      disabled={busy}
      onClick={() => {
        void check();
      }}
      title="Проверить соединение"
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
        {busy ||
        state === "checking"
          ? "Проверяем связь..."
          : state === "online"
            ? "Онлайн · устройство подключено"
            : "Офлайн · сохранённые данные"}
      </span>
    </button>
  );
}