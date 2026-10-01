import {
  AlertTriangle,
  BellRing,
  CalendarClock,
  Car,
  CheckCircle2,
  Clock3,
  Edit3,
  MessageSquareText,
  Plus,
  RefreshCw,
  Save,
  Settings2,
  Smartphone,
  Trash2,
  X,
  XCircle,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import type {
  FormEvent,
} from "react";

import {
  cancelServiceReminder,
  createServiceReminder,
  deleteCustomerNotification,
  getNotificationPreferences,
  listCustomerNotifications,
  listServiceReminders,
  prepareDueNotifications,
  updateNotificationPreferences,
  updateCustomerNotification,
} from "../api/notifications";
import {
  listClients,
} from "../api/clients";
import {
  listVehicles,
} from "../api/vehicles";
import {
  ApiError,
} from "../api/client";
import type {
  CurrentUser,
} from "../types/auth";
import type {
  Client,
} from "../types/client";
import type {
  CustomerNotification,
  NotificationKind,
  NotificationPreference,
  NotificationStatus,
  ServiceReminder,
  ServiceReminderStatus,
} from "../types/notification";
import type {
  Vehicle,
} from "../types/vehicle";


type Props = {
  currentUser: CurrentUser;
};


type Tab =
  | "queue"
  | "reminders"
  | "settings";


const statusLabels:
  Record<
    NotificationStatus,
    string
  > = {
    prepared:
      "Подготовлено",

    sent:
      "Отправлено",

    failed:
      "Ошибка",

    cancelled:
      "Отменено",
  };


const kindLabels:
  Record<
    NotificationKind,
    string
  > = {
    appointment_confirmation:
      "Подтверждение записи",

    appointment_reminder:
      "Напоминание о записи",

    service_reminder:
      "Сервисное напоминание",
  };


const reminderStatusLabels:
  Record<
    ServiceReminderStatus,
    string
  > = {
    planned:
      "Запланировано",

    completed:
      "Обработано",

    cancelled:
      "Отменено",
  };


function errorText(
  error: unknown,
  fallback: string,
): string {
  if (
    error instanceof ApiError
  ) {
    return error.message;
  }

  return fallback;
}


function formatDateTime(
  value:
    | string
    | null,
): string {
  if (!value) {
    return "—";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "ru-RU",
    {
      dateStyle: "short",
      timeStyle: "short",
    },
  ).format(date);
}


function formatDate(
  value:
    | string
    | null,
): string {
  if (!value) {
    return "—";
  }

  const date =
    new Date(
      `${value}T00:00:00`,
    );

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "ru-RU",
    {
      dateStyle: "medium",
    },
  ).format(date);
}


export function NotificationsPage({
  currentUser,
}: Props) {
  const canManage =
    currentUser.role === "owner" ||
    currentUser.role === "admin" ||
    currentUser.role ===
      "tech_admin";


  const [
    tab,
    setTab,
  ] = useState<Tab>(
    "queue",
  );

  const [
    clients,
    setClients,
  ] = useState<Client[]>(
    [],
  );

  const [
    pageError,
    setPageError,
  ] = useState("");

  const [
    notice,
    setNotice,
  ] = useState("");


  const [
    notifications,
    setNotifications,
  ] = useState<
    CustomerNotification[]
  >([]);

  const [
    queueLoading,
    setQueueLoading,
  ] = useState(false);

  const [
    queueStatus,
    setQueueStatus,
  ] = useState<
    "" | NotificationStatus
  >("");

  const [
    queueKind,
    setQueueKind,
  ] = useState<
    "" | NotificationKind
  >("");

  const [
    queueClient,
    setQueueClient,
  ] = useState("");


  const [
    editingNotification,
    setEditingNotification,
  ] = useState<
    CustomerNotification | null
  >(null);

  const [
    editNotificationMessage,
    setEditNotificationMessage,
  ] = useState("");

  const [
    editNotificationDate,
    setEditNotificationDate,
  ] = useState("");

  const [
    editNotificationSaving,
    setEditNotificationSaving,
  ] = useState(false);

  const [
    reminders,
    setReminders,
  ] = useState<
    ServiceReminder[]
  >([]);

  const [
    remindersLoading,
    setRemindersLoading,
  ] = useState(false);

  const [
    reminderStatus,
    setReminderStatus,
  ] = useState<
    "" | ServiceReminderStatus
  >("planned");


  const [
    preferences,
    setPreferences,
  ] = useState<
    NotificationPreference | null
  >(null);

  const [
    preferencesLoading,
    setPreferencesLoading,
  ] = useState(false);

  const [
    preferencesSaving,
    setPreferencesSaving,
  ] = useState(false);

  const [
    preferencesClient,
    setPreferencesClient,
  ] = useState("");


  const [
    showReminderForm,
    setShowReminderForm,
  ] = useState(false);

  const [
    reminderClient,
    setReminderClient,
  ] = useState("");

  const [
    reminderVehicles,
    setReminderVehicles,
  ] = useState<Vehicle[]>(
    [],
  );

  const [
    reminderVehicle,
    setReminderVehicle,
  ] = useState("");

  const [
    reminderWork,
    setReminderWork,
  ] = useState("");

  const [
    reminderDueDate,
    setReminderDueDate,
  ] = useState("");

  const [
    reminderDueMileage,
    setReminderDueMileage,
  ] = useState("");

  const [
    reminderMessage,
    setReminderMessage,
  ] = useState("");

  const [
    reminderSaving,
    setReminderSaving,
  ] = useState(false);


  const loadNotifications =
    useCallback(async () => {
      setQueueLoading(true);
      setPageError("");

      try {
        const result =
          await listCustomerNotifications(
            {
              clientNumber:
                queueClient
                  ? Number(
                      queueClient,
                    )
                  : undefined,

              status:
                queueStatus ||
                undefined,

              kind:
                queueKind ||
                undefined,
            },
          );

        setNotifications(
          result,
        );
      } catch (error) {
        setPageError(
          errorText(
            error,
            "Не удалось загрузить очередь уведомлений.",
          ),
        );
      } finally {
        setQueueLoading(false);
      }
    }, [
      queueClient,
      queueKind,
      queueStatus,
    ]);


  const loadReminders =
    useCallback(async () => {
      setRemindersLoading(true);
      setPageError("");

      try {
        const result =
          await listServiceReminders(
            {
              status:
                reminderStatus ||
                undefined,
            },
          );

        setReminders(result);
      } catch (error) {
        setPageError(
          errorText(
            error,
            "Не удалось загрузить сервисные напоминания.",
          ),
        );
      } finally {
        setRemindersLoading(false);
      }
    }, [reminderStatus]);


  useEffect(() => {
    let active = true;

    const timer =
      window.setTimeout(() => {
        void listClients(
          "",
          100,
        )
          .then((result) => {
            if (active) {
              setClients(
                result.items,
              );
            }
          })
          .catch((error) => {
            if (active) {
              setPageError(
                errorText(
                  error,
                  "Не удалось загрузить клиентов.",
                ),
              );
            }
          });
      }, 0);

    return () => {
      active = false;

      window.clearTimeout(
        timer,
      );
    };
  }, []);


  useEffect(() => {
    if (
      tab !== "queue"
    ) {
      return;
    }

    const timer =
      window.setTimeout(() => {
        void loadNotifications();
      }, 0);

    return () => {
      window.clearTimeout(
        timer,
      );
    };
  }, [
    tab,
    loadNotifications,
  ]);


  useEffect(() => {
    if (
      tab !== "reminders"
    ) {
      return;
    }

    const timer =
      window.setTimeout(() => {
        void loadReminders();
      }, 0);

    return () => {
      window.clearTimeout(
        timer,
      );
    };
  }, [
    tab,
    loadReminders,
  ]);


  const queueCounts =
    useMemo(
      () => ({
        prepared:
          notifications.filter(
            (item) =>
              item.status ===
              "prepared",
          ).length,

        sent:
          notifications.filter(
            (item) =>
              item.status ===
              "sent",
          ).length,

        failed:
          notifications.filter(
            (item) =>
              item.status ===
              "failed",
          ).length,

        cancelled:
          notifications.filter(
            (item) =>
              item.status ===
              "cancelled",
          ).length,
      }),
      [notifications],
    );


  function toDateTimeLocal(
    value: string,
  ): string {
    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime(),
      )
    ) {
      return "";
    }

    const local =
      new Date(
        date.getTime() -
        date.getTimezoneOffset() *
          60_000,
      );

    return local
      .toISOString()
      .slice(0, 16);
  }


  function openNotificationEditor(
    notification:
      CustomerNotification,
  ) {
    setEditingNotification(
      notification,
    );

    setEditNotificationMessage(
      notification.message_text,
    );

    setEditNotificationDate(
      toDateTimeLocal(
        notification
          .scheduled_for,
      ),
    );

    setPageError("");
    setNotice("");
  }


  async function saveNotificationEdit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !editingNotification ||
      !canManage
    ) {
      return;
    }

    const message =
      editNotificationMessage.trim();

    if (!message) {
      setPageError(
        "Введите текст уведомления.",
      );

      return;
    }

    if (!editNotificationDate) {
      setPageError(
        "Укажите дату и время уведомления.",
      );

      return;
    }

    const scheduled =
      new Date(
        editNotificationDate,
      );

    if (
      Number.isNaN(
        scheduled.getTime(),
      )
    ) {
      setPageError(
        "Проверьте дату и время уведомления.",
      );

      return;
    }

    setEditNotificationSaving(
      true,
    );

    setPageError("");
    setNotice("");

    try {
      await updateCustomerNotification(
        editingNotification.id,
        {
          message_text:
            message,

          scheduled_for:
            scheduled.toISOString(),
        },
      );

      setEditingNotification(
        null,
      );

      await loadNotifications();

      setNotice(
        "Уведомление изменено.",
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось изменить уведомление.",
        ),
      );
    } finally {
      setEditNotificationSaving(
        false,
      );
    }
  }


  async function removeNotification(
    notification:
      CustomerNotification,
  ) {
    if (!canManage) {
      return;
    }

    if (
      !window.confirm(
        `Удалить подготовленное уведомление для ${notification.client_name ?? "клиента"}?`,
      )
    ) {
      return;
    }

    setPageError("");
    setNotice("");

    try {
      await deleteCustomerNotification(
        notification.id,
      );

      await loadNotifications();

      setNotice(
        "Уведомление удалено.",
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось удалить уведомление.",
        ),
      );
    }
  }

  async function loadPreferences(
    clientNumber: number,
  ) {
    setPreferencesLoading(
      true,
    );

    setPageError("");
    setNotice("");

    try {
      const result =
        await getNotificationPreferences(
          clientNumber,
        );

      setPreferences(
        result,
      );
    } catch (error) {
      setPreferences(null);

      setPageError(
        errorText(
          error,
          "Не удалось загрузить настройки клиента.",
        ),
      );
    } finally {
      setPreferencesLoading(
        false,
      );
    }
  }


  function changePreferencesClient(
    value: string,
  ) {
    setPreferencesClient(
      value,
    );

    setPreferences(null);

    if (!value) {
      return;
    }

    void loadPreferences(
      Number(value),
    );
  }


  async function savePreferences(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !preferences ||
      !canManage
    ) {
      return;
    }

    setPreferencesSaving(
      true,
    );

    setPageError("");
    setNotice("");

    try {
      const result =
        await updateNotificationPreferences(
          preferences
            .client_number,

          {
            sms_enabled:
              preferences
                .sms_enabled,

            max_enabled:
              preferences
                .max_connected
                ? preferences
                    .max_enabled
                : false,

            appointment_confirmation_enabled:
              preferences
                .appointment_confirmation_enabled,

            appointment_reminder_enabled:
              preferences
                .appointment_reminder_enabled,

            service_reminder_enabled:
              preferences
                .service_reminder_enabled,
          },
        );

      setPreferences(
        result,
      );

      setNotice(
        "Настройки уведомлений клиента сохранены.",
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось сохранить настройки уведомлений.",
        ),
      );
    } finally {
      setPreferencesSaving(
        false,
      );
    }
  }


  function changePreference(
    field:
      | "sms_enabled"
      | "max_enabled"
      | "appointment_confirmation_enabled"
      | "appointment_reminder_enabled"
      | "service_reminder_enabled",

    checked: boolean,
  ) {
    setPreferences(
      (current) =>
        current
          ? {
              ...current,
              [field]:
                checked,
            }
          : current,
    );

    setNotice("");
  }


  function openReminderForm() {
    setReminderClient("");
    setReminderVehicle("");
    setReminderVehicles([]);
    setReminderWork("");
    setReminderDueDate("");
    setReminderDueMileage("");
    setReminderMessage("");
    setPageError("");
    setNotice("");

    setShowReminderForm(
      true,
    );
  }


  async function changeReminderClient(
    value: string,
  ) {
    setReminderClient(
      value,
    );

    setReminderVehicle("");
    setReminderVehicles([]);

    if (!value) {
      return;
    }

    try {
      const result =
        await listVehicles(
          "",
          100,
          Number(value),
        );

      setReminderVehicles(
        result.items,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось загрузить автомобили клиента.",
        ),
      );
    }
  }


  async function saveReminder(
    event: FormEvent,
  ) {
    event.preventDefault();

    const clientNumber =
      Number(
        reminderClient,
      );

    const vehicleNumber =
      Number(
        reminderVehicle,
      );

    const workName =
      reminderWork.trim();

    const message =
      reminderMessage.trim();

    if (
      !clientNumber ||
      !vehicleNumber
    ) {
      setPageError(
        "Выберите клиента и автомобиль.",
      );

      return;
    }

    if (!workName) {
      setPageError(
        "Укажите работу для напоминания.",
      );

      return;
    }

    if (
      !reminderDueDate &&
      !reminderDueMileage
    ) {
      setPageError(
        "Укажите дату и/или пробег для напоминания.",
      );

      return;
    }

    if (!message) {
      setPageError(
        "Введите текст сообщения клиенту.",
      );

      return;
    }

    setReminderSaving(true);
    setPageError("");
    setNotice("");

    try {
      await createServiceReminder({
        client_number:
          clientNumber,

        vehicle_number:
          vehicleNumber,

        work_name:
          workName,

        due_date:
          reminderDueDate ||
          null,

        due_mileage:
          reminderDueMileage
            ? Number(
                reminderDueMileage,
              )
            : null,

        message_text:
          message,
      });

      setShowReminderForm(
        false,
      );

      setReminderStatus(
        "planned",
      );

      await loadReminders();

      setNotice(
        "Сервисное напоминание создано.",
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось создать сервисное напоминание.",
        ),
      );
    } finally {
      setReminderSaving(false);
    }
  }


  async function cancelReminder(
    reminder:
      ServiceReminder,
  ) {
    if (!canManage) {
      return;
    }

    if (
      !window.confirm(
        `Отменить напоминание «${reminder.work_name}» для ${reminder.client_name}?`,
      )
    ) {
      return;
    }

    setPageError("");
    setNotice("");

    try {
      await cancelServiceReminder(
        reminder.id,
      );

      await loadReminders();

      setNotice(
        "Напоминание отменено.",
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось отменить напоминание.",
        ),
      );
    }
  }


  async function prepareDue() {
    if (!canManage) {
      return;
    }

    setPageError("");
    setNotice("");

    try {
      const result =
        await prepareDueNotifications();

      await loadReminders();

      setNotice(
        result.prepared_count === 0
          ? "Наступивших сервисных уведомлений сейчас нет."
          : `Подготовлено уведомлений: ${result.prepared_count}.`,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось проверить сервисные напоминания.",
        ),
      );
    }
  }


  return (
    <section className="notifications-page">
      <div className="notifications-info">
        <BellRing size={21} />

        <div>
          <strong>
            Центр уведомлений
          </strong>

          <span>
            Сейчас система формирует
            очередь сообщений.
            Подключение реальной отправки
            SMS и MAX будет отдельным
            этапом.
          </span>
        </div>
      </div>


      <div className="notifications-tabs">
        <button
          className={
            tab === "queue"
              ? "notifications-tab notifications-tab-active"
              : "notifications-tab"
          }
          onClick={() => {
            setTab("queue");
          }}
          type="button"
        >
          <MessageSquareText
            size={17}
          />
          Очередь
        </button>

        <button
          className={
            tab === "reminders"
              ? "notifications-tab notifications-tab-active"
              : "notifications-tab"
          }
          onClick={() => {
            setTab(
              "reminders",
            );
          }}
          type="button"
        >
          <CalendarClock
            size={17}
          />
          Сервисные напоминания
        </button>

        <button
          className={
            tab === "settings"
              ? "notifications-tab notifications-tab-active"
              : "notifications-tab"
          }
          onClick={() => {
            setTab(
              "settings",
            );
          }}
          type="button"
        >
          <Settings2
            size={17}
          />
          Настройки клиента
        </button>
      </div>


      {pageError && (
        <div className="notifications-error">
          <AlertTriangle
            size={17}
          />
          {pageError}
        </div>
      )}


      {notice && (
        <div className="notifications-success">
          <CheckCircle2
            size={17}
          />
          {notice}
        </div>
      )}


      {tab === "queue" && (
        <section className="notifications-panel">
          <div className="notifications-panel-heading">
            <div>
              <span>
                Подготовленные и обработанные сообщения
              </span>

              <h2>
                Очередь уведомлений
              </h2>
            </div>

            <button
              className="notifications-secondary-button"
              disabled={
                queueLoading
              }
              onClick={() => {
                void loadNotifications();
              }}
              type="button"
            >
              <RefreshCw
                size={15}
              />
              Обновить
            </button>
          </div>


          <div className="notifications-summary">
            <div>
              <span>
                Подготовлено
              </span>

              <strong>
                {
                  queueCounts
                    .prepared
                }
              </strong>
            </div>

            <div>
              <span>
                Отправлено
              </span>

              <strong>
                {queueCounts.sent}
              </strong>
            </div>

            <div>
              <span>
                Ошибки
              </span>

              <strong>
                {
                  queueCounts.failed
                }
              </strong>
            </div>

            <div>
              <span>
                Отменено
              </span>

              <strong>
                {
                  queueCounts
                    .cancelled
                }
              </strong>
            </div>
          </div>


          <div className="notifications-filters">
            <label>
              <span>
                Статус
              </span>

              <select
                value={queueStatus}
                onChange={(event) => {
                  setQueueStatus(
                    event.target
                      .value as
                      | ""
                      | NotificationStatus,
                  );
                }}
              >
                <option value="">
                  Все
                </option>

                <option value="prepared">
                  Подготовлено
                </option>

                <option value="sent">
                  Отправлено
                </option>

                <option value="failed">
                  Ошибка
                </option>

                <option value="cancelled">
                  Отменено
                </option>
              </select>
            </label>


            <label>
              <span>
                Тип
              </span>

              <select
                value={queueKind}
                onChange={(event) => {
                  setQueueKind(
                    event.target
                      .value as
                      | ""
                      | NotificationKind,
                  );
                }}
              >
                <option value="">
                  Все
                </option>

                <option value="appointment_confirmation">
                  Подтверждение записи
                </option>

                <option value="appointment_reminder">
                  Напоминание о записи
                </option>

                <option value="service_reminder">
                  Сервисное напоминание
                </option>
              </select>
            </label>


            <label>
              <span>
                Клиент
              </span>

              <select
                value={queueClient}
                onChange={(event) => {
                  setQueueClient(
                    event.target
                      .value,
                  );
                }}
              >
                <option value="">
                  Все клиенты
                </option>

                {clients.map(
                  (client) => (
                    <option
                      key={
                        client
                          .client_number
                      }
                      value={
                        client
                          .client_number
                      }
                    >
                      {
                        client
                          .full_name
                      }
                    </option>
                  ),
                )}
              </select>
            </label>
          </div>


          {queueLoading &&
          notifications.length ===
            0 ? (
            <div className="notifications-empty">
              Загружаем очередь...
            </div>
          ) : notifications.length ===
            0 ? (
            <div className="notifications-empty">
              По выбранным фильтрам
              уведомлений нет.
            </div>
          ) : (
            <div className="notifications-list">
              {notifications.map(
                (item) => (
                  <article
                    className="notification-card"
                    key={item.id}
                  >
                    <div className="notification-card-top">
                      <div>
                        <strong>
                          {item.client_name ??
                            "Клиент"}
                        </strong>

                        <span>
                          {
                            kindLabels[
                              item.kind
                            ]
                          }
                        </span>
                      </div>

                      <span
                        className={
                          `notification-status notification-status-${item.status}`
                        }
                      >
                        {
                          statusLabels[
                            item.status
                          ]
                        }
                      </span>
                    </div>


                    <p className="notification-message">
                      {
                        item.message_text
                      }
                    </p>


                    <div className="notification-meta">
                      <span>
                        <Smartphone
                          size={13}
                        />
                        {item.channel ===
                        "sms"
                          ? "SMS"
                          : "MAX"}
                      </span>

                      <span>
                        <Clock3
                          size={13}
                        />
                        {formatDateTime(
                          item
                            .scheduled_for,
                        )}
                      </span>

                      {item.appointment_number !==
                        null && (
                        <span>
                          Запись №
                          {
                            item
                              .appointment_number
                          }
                        </span>
                      )}

                      {item.vehicle_number !==
                        null && (
                        <span>
                          Авто №
                          {
                            item
                              .vehicle_number
                          }
                        </span>
                      )}
                    </div>


                    {item.error_message && (
                      <div className="notification-error-text">
                        {
                          item
                            .error_message
                        }
                      </div>
                    )}

                    {canManage &&
                      item.status ===
                        "prepared" && (
                      <div className="notification-card-actions">
                        <button
                          className="notification-edit-button"
                          onClick={() => {
                            openNotificationEditor(
                              item,
                            );
                          }}
                          type="button"
                        >
                          <Edit3
                            size={15}
                          />
                          Редактировать
                        </button>

                        <button
                          className="notification-delete-button"
                          onClick={() => {
                            void removeNotification(
                              item,
                            );
                          }}
                          type="button"
                        >
                          <Trash2
                            size={15}
                          />
                          Удалить
                        </button>
                      </div>
                    )}
                  </article>
                ),
              )}
            </div>
          )}
        </section>
      )}


      {tab ===
        "reminders" && (
        <section className="notifications-panel">
          <div className="notifications-panel-heading">
            <div>
              <span>
                Напомнить клиенту о следующем обслуживании
              </span>

              <h2>
                Сервисные напоминания
              </h2>
            </div>

            <div className="notifications-heading-actions">
              {canManage && (
                <button
                  className="notifications-secondary-button"
                  onClick={() => {
                    void prepareDue();
                  }}
                  type="button"
                >
                  <RefreshCw
                    size={15}
                  />
                  Проверить сейчас
                </button>
              )}

              {canManage && (
                <button
                  className="primary-button notifications-primary-button"
                  onClick={
                    openReminderForm
                  }
                  type="button"
                >
                  <Plus size={15} />
                  Новое напоминание
                </button>
              )}
            </div>
          </div>


          <div className="notifications-filters notifications-reminder-filter">
            <label>
              <span>
                Статус
              </span>

              <select
                value={
                  reminderStatus
                }
                onChange={(event) => {
                  setReminderStatus(
                    event.target
                      .value as
                      | ""
                      | ServiceReminderStatus,
                  );
                }}
              >
                <option value="">
                  Все
                </option>

                <option value="planned">
                  Запланированные
                </option>

                <option value="completed">
                  Обработанные
                </option>

                <option value="cancelled">
                  Отменённые
                </option>
              </select>
            </label>
          </div>


          {remindersLoading &&
          reminders.length === 0 ? (
            <div className="notifications-empty">
              Загружаем напоминания...
            </div>
          ) : reminders.length ===
            0 ? (
            <div className="notifications-empty">
              Напоминаний с таким
              статусом нет.
            </div>
          ) : (
            <div className="reminder-list">
              {reminders.map(
                (reminder) => (
                  <article
                    className="reminder-card"
                    key={
                      reminder.id
                    }
                  >
                    <div className="reminder-card-top">
                      <div>
                        <span>
                          {
                            reminder
                              .client_name
                          }
                        </span>

                        <strong>
                          {
                            reminder
                              .work_name
                          }
                        </strong>
                      </div>

                      <span
                        className={
                          `reminder-status reminder-status-${reminder.status}`
                        }
                      >
                        {
                          reminderStatusLabels[
                            reminder
                              .status
                          ]
                        }
                      </span>
                    </div>


                    <div className="reminder-vehicle">
                      <Car size={14} />

                      {
                        reminder
                          .vehicle_name
                      }

                      <span>
                        Авто №
                        {
                          reminder
                            .vehicle_number
                        }
                      </span>
                    </div>


                    <div className="reminder-due">
                      <div>
                        <span>
                          По дате
                        </span>

                        <strong>
                          {formatDate(
                            reminder
                              .due_date,
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          По пробегу
                        </span>

                        <strong>
                          {reminder
                            .due_mileage ===
                          null
                            ? "—"
                            : `${reminder.due_mileage.toLocaleString("ru-RU")} км`}
                        </strong>
                      </div>
                    </div>


                    <p>
                      {
                        reminder
                          .message_text
                      }
                    </p>


                    {canManage &&
                      reminder.status ===
                        "planned" && (
                      <div className="reminder-actions">
                        <button
                          className="notifications-danger-button"
                          onClick={() => {
                            void cancelReminder(
                              reminder,
                            );
                          }}
                          type="button"
                        >
                          <XCircle
                            size={14}
                          />
                          Отменить
                        </button>
                      </div>
                    )}
                  </article>
                ),
              )}
            </div>
          )}
        </section>
      )}


      {tab ===
        "settings" && (
        <section className="notifications-panel">
          <div className="notifications-panel-heading">
            <div>
              <span>
                Каналы и виды сообщений
              </span>

              <h2>
                Настройки клиента
              </h2>
            </div>
          </div>


          <div className="notification-client-selector">
            <label>
              <span>
                Клиент
              </span>

              <select
                value={
                  preferencesClient
                }
                onChange={(event) => {
                  changePreferencesClient(
                    event.target
                      .value,
                  );
                }}
              >
                <option value="">
                  Выберите клиента
                </option>

                {clients.map(
                  (client) => (
                    <option
                      key={
                        client
                          .client_number
                      }
                      value={
                        client
                          .client_number
                      }
                    >
                      {
                        client
                          .full_name
                      }{" "}
                      ·{" "}
                      {
                        client
                          .phone_primary
                      }
                    </option>
                  ),
                )}
              </select>
            </label>
          </div>


          {preferencesLoading && (
            <div className="notifications-empty">
              Загружаем настройки...
            </div>
          )}


          {!preferencesLoading &&
            preferences && (
            <form
              className="notification-preferences"
              onSubmit={
                savePreferences
              }
            >
              <div className="notification-preference-client">
                <div>
                  <span>
                    Клиент
                  </span>

                  <strong>
                    {
                      preferences
                        .client_name
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Телефон
                  </span>

                  <strong>
                    {
                      preferences
                        .phone_primary
                    }
                  </strong>
                </div>
              </div>


              <div className="notification-preference-group">
                <div className="notification-preference-heading">
                  <strong>
                    Каналы доставки
                  </strong>

                  <span>
                    Через что можно
                    отправлять сообщения
                  </span>
                </div>

                <label className="notification-toggle">
                  <input
                    checked={
                      preferences
                        .sms_enabled
                    }
                    disabled={
                      !canManage
                    }
                    type="checkbox"
                    onChange={(event) => {
                      changePreference(
                        "sms_enabled",
                        event.target
                          .checked,
                      );
                    }}
                  />

                  <div>
                    <strong>
                      SMS
                    </strong>

                    <span>
                      На основной телефон
                      клиента
                    </span>
                  </div>
                </label>


                <label className="notification-toggle">
                  <input
                    checked={
                      preferences
                        .max_enabled
                    }
                    disabled={
                      !canManage ||
                      !preferences
                        .max_connected
                    }
                    type="checkbox"
                    onChange={(event) => {
                      changePreference(
                        "max_enabled",
                        event.target
                          .checked,
                      );
                    }}
                  />

                  <div>
                    <strong>
                      MAX
                    </strong>

                    <span>
                      {preferences
                        .max_connected
                        ? "Аккаунт MAX клиента подключён"
                        : "MAX пока не подключён к клиенту"}
                    </span>
                  </div>
                </label>
              </div>


              <div className="notification-preference-group">
                <div className="notification-preference-heading">
                  <strong>
                    Какие сообщения отправлять
                  </strong>

                  <span>
                    Настраиваются отдельно
                    для каждого клиента
                  </span>
                </div>


                <label className="notification-toggle">
                  <input
                    checked={
                      preferences
                        .appointment_confirmation_enabled
                    }
                    disabled={
                      !canManage
                    }
                    type="checkbox"
                    onChange={(event) => {
                      changePreference(
                        "appointment_confirmation_enabled",
                        event.target
                          .checked,
                      );
                    }}
                  />

                  <div>
                    <strong>
                      Подтверждение записи
                    </strong>

                    <span>
                      Сообщение после
                      создания записи
                    </span>
                  </div>
                </label>


                <label className="notification-toggle">
                  <input
                    checked={
                      preferences
                        .appointment_reminder_enabled
                    }
                    disabled={
                      !canManage
                    }
                    type="checkbox"
                    onChange={(event) => {
                      changePreference(
                        "appointment_reminder_enabled",
                        event.target
                          .checked,
                      );
                    }}
                  />

                  <div>
                    <strong>
                      Напоминание о записи
                    </strong>

                    <span>
                      Подготавливается
                      перед приездом клиента
                    </span>
                  </div>
                </label>


                <label className="notification-toggle">
                  <input
                    checked={
                      preferences
                        .service_reminder_enabled
                    }
                    disabled={
                      !canManage
                    }
                    type="checkbox"
                    onChange={(event) => {
                      changePreference(
                        "service_reminder_enabled",
                        event.target
                          .checked,
                      );
                    }}
                  />

                  <div>
                    <strong>
                      Сервисные напоминания
                    </strong>

                    <span>
                      Например, следующая
                      замена масла
                    </span>
                  </div>
                </label>
              </div>


              {canManage && (
                <div className="notification-preference-actions">
                  <button
                    className="primary-button notifications-primary-button"
                    disabled={
                      preferencesSaving
                    }
                    type="submit"
                  >
                    <Save size={15} />

                    {preferencesSaving
                      ? "Сохраняем..."
                      : "Сохранить настройки"}
                  </button>
                </div>
              )}
            </form>
          )}
        </section>
      )}


      {editingNotification && (
        <div className="notification-modal-backdrop">
          <form
            className="notification-modal notification-edit-modal"
            onSubmit={
              saveNotificationEdit
            }
          >
            <div className="notification-modal-heading">
              <div>
                <span>
                  Очередь уведомлений
                </span>

                <h2>
                  Редактировать уведомление
                </h2>
              </div>

              <button
                aria-label="Закрыть"
                className="notification-icon-button"
                onClick={() => {
                  setEditingNotification(
                    null,
                  );
                }}
                type="button"
              >
                <X size={18} />
              </button>
            </div>


            <div className="notification-edit-client">
              <div>
                <span>
                  Клиент
                </span>

                <strong>
                  {editingNotification
                    .client_name ??
                    "—"}
                </strong>
              </div>

              <div>
                <span>
                  Тип
                </span>

                <strong>
                  {
                    kindLabels[
                      editingNotification
                        .kind
                    ]
                  }
                </strong>
              </div>

              <div>
                <span>
                  Канал
                </span>

                <strong>
                  {editingNotification
                    .channel ===
                  "sms"
                    ? "SMS"
                    : "MAX"}
                </strong>
              </div>
            </div>


            <div className="notification-form-grid">
              <label className="notification-wide">
                <span>
                  Дата и время *
                </span>

                <input
                  required
                  type="datetime-local"
                  value={
                    editNotificationDate
                  }
                  onChange={(event) => {
                    setEditNotificationDate(
                      event.target
                        .value,
                    );
                  }}
                />
              </label>


              <label className="notification-wide">
                <span>
                  Текст уведомления *
                </span>

                <textarea
                  maxLength={2000}
                  required
                  rows={7}
                  value={
                    editNotificationMessage
                  }
                  onChange={(event) => {
                    setEditNotificationMessage(
                      event.target
                        .value,
                    );
                  }}
                />
              </label>
            </div>


            <div className="notification-modal-note">
              Клиент, тип и канал
              уведомления не меняются.
              Можно изменить текст
              и время отправки.
            </div>


            <div className="notification-modal-actions">
              <button
                className="notifications-secondary-button"
                onClick={() => {
                  setEditingNotification(
                    null,
                  );
                }}
                type="button"
              >
                Отмена
              </button>

              <button
                className="primary-button notifications-primary-button"
                disabled={
                  editNotificationSaving
                }
                type="submit"
              >
                <Save size={15} />

                {editNotificationSaving
                  ? "Сохраняем..."
                  : "Сохранить изменения"}
              </button>
            </div>
          </form>
        </div>
      )}

      {showReminderForm && (
        <div className="notification-modal-backdrop">
          <form
            className="notification-modal"
            onSubmit={
              saveReminder
            }
          >
            <div className="notification-modal-heading">
              <div>
                <span>
                  Следующее обслуживание
                </span>

                <h2>
                  Новое сервисное напоминание
                </h2>
              </div>

              <button
                aria-label="Закрыть"
                className="notification-icon-button"
                onClick={() => {
                  setShowReminderForm(
                    false,
                  );
                }}
                type="button"
              >
                <X size={18} />
              </button>
            </div>


            <div className="notification-form-grid">
              <label className="notification-wide">
                <span>
                  Клиент *
                </span>

                <select
                  required
                  value={
                    reminderClient
                  }
                  onChange={(event) => {
                    void changeReminderClient(
                      event.target
                        .value,
                    );
                  }}
                >
                  <option value="">
                    Выберите клиента
                  </option>

                  {clients.map(
                    (client) => (
                      <option
                        key={
                          client
                            .client_number
                        }
                        value={
                          client
                            .client_number
                        }
                      >
                        {
                          client
                            .full_name
                        }{" "}
                        ·{" "}
                        {
                          client
                            .phone_primary
                        }
                      </option>
                    ),
                  )}
                </select>
              </label>


              <label className="notification-wide">
                <span>
                  Автомобиль *
                </span>

                <select
                  disabled={
                    !reminderClient
                  }
                  required
                  value={
                    reminderVehicle
                  }
                  onChange={(event) => {
                    setReminderVehicle(
                      event.target
                        .value,
                    );
                  }}
                >
                  <option value="">
                    Выберите автомобиль
                  </option>

                  {reminderVehicles.map(
                    (vehicle) => (
                      <option
                        key={
                          vehicle
                            .vehicle_number
                        }
                        value={
                          vehicle
                            .vehicle_number
                        }
                      >
                        {
                          vehicle.brand
                        }{" "}
                        {
                          vehicle.model
                        }{" "}
                        ·{" "}
                        {
                          vehicle
                            .license_plate
                        }
                      </option>
                    ),
                  )}
                </select>
              </label>


              <label className="notification-wide">
                <span>
                  Что напомнить *
                </span>

                <input
                  placeholder="Например: замена масла"
                  required
                  value={
                    reminderWork
                  }
                  onChange={(event) => {
                    setReminderWork(
                      event.target
                        .value,
                    );
                  }}
                />
              </label>


              <label>
                <span>
                  Дата
                </span>

                <input
                  type="date"
                  value={
                    reminderDueDate
                  }
                  onChange={(event) => {
                    setReminderDueDate(
                      event.target
                        .value,
                    );
                  }}
                />
              </label>


              <label>
                <span>
                  Пробег, км
                </span>

                <input
                  min="0"
                  step="1"
                  type="number"
                  value={
                    reminderDueMileage
                  }
                  onChange={(event) => {
                    setReminderDueMileage(
                      event.target
                        .value,
                    );
                  }}
                />
              </label>


              <label className="notification-wide">
                <span>
                  Текст клиенту *
                </span>

                <textarea
                  placeholder="Например: Подошёл срок замены масла. Запишитесь в ЦУТ Improvement Auto."
                  required
                  rows={5}
                  value={
                    reminderMessage
                  }
                  onChange={(event) => {
                    setReminderMessage(
                      event.target
                        .value,
                    );
                  }}
                />
              </label>
            </div>


            <div className="notification-modal-note">
              Можно указать дату,
              пробег или оба условия.
              Напоминание сработает,
              когда наступит хотя бы
              одно из них.
            </div>


            <div className="notification-modal-actions">
              <button
                className="notifications-secondary-button"
                onClick={() => {
                  setShowReminderForm(
                    false,
                  );
                }}
                type="button"
              >
                Отмена
              </button>

              <button
                className="primary-button notifications-primary-button"
                disabled={
                  reminderSaving
                }
                type="submit"
              >
                <Save size={15} />

                {reminderSaving
                  ? "Создаём..."
                  : "Создать напоминание"}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}