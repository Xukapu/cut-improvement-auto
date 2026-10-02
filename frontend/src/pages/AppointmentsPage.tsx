import {
  CalendarClock,
  Edit3,
  Plus,
  RotateCcw,
  UserX,
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
  createAppointment,
  listAppointments,
  updateAppointment,
} from "../api/appointments";

import {
  ApiError,
} from "../api/client";

import {
  listClients,
} from "../api/clients";

import {
  listVehicles,
} from "../api/vehicles";

import {
  listPendingSyncOperations,
} from "../offline/offlineStore";

import type {
  Appointment,
  AppointmentInput,
  AppointmentStatus,
} from "../types/appointment";

import type {
  Client,
} from "../types/client";

import type {
  Vehicle,
} from "../types/vehicle";

import {
  formatDate,
  formatTime,
  todayIso,
} from "../utils/format";


type FormState = {
  client_id: string;
  vehicle_id: string;

  appointment_date: string;
  appointment_time: string;

  reason: string;
  comment: string;

  status:
    AppointmentStatus;
};


function errorMessage(
  error: unknown,
): string {
  if (
    error instanceof ApiError
  ) {
    return error.message;
  }

  if (
    error instanceof Error &&
    error.message
  ) {
    return error.message;
  }

  return (
    "Не удалось выполнить операцию."
  );
}


function appointmentLabel(
  appointment:
    Appointment,
): string {
  return appointment.sync_pending
    ? "Ожидает синхронизации"
    : `Запись №${appointment.appointment_number}`;
}


function clientLabel(
  client: Client,
): string {
  return client.sync_pending
    ? `${client.full_name} · ожидает синхронизации`
    : `№${client.client_number} · ${client.full_name}`;
}


export function AppointmentsPage() {
  const [
    date,
    setDate,
  ] = useState(
    todayIso(),
  );

  const [
    items,
    setItems,
  ] = useState<
    Appointment[]
  >([]);

  const [
    clients,
    setClients,
  ] = useState<
    Client[]
  >([]);

  const [
    vehicles,
    setVehicles,
  ] = useState<
    Vehicle[]
  >([]);

  const [
    pendingVehicleOwners,
    setPendingVehicleOwners,
  ] = useState<
    Record<string, string>
  >({});

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    pageError,
    setPageError,
  ] = useState("");

  const [
    formError,
    setFormError,
  ] = useState("");

  const [
    formOpen,
    setFormOpen,
  ] = useState(false);

  const [
    editing,
    setEditing,
  ] = useState<
    Appointment | null
  >(null);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    form,
    setForm,
  ] = useState<FormState>({
    client_id: "",
    vehicle_id: "",

    appointment_date:
      todayIso(),

    appointment_time:
      "09:00",

    reason: "",
    comment: "",

    status:
      "scheduled",
  });


  const loadData =
    useCallback(
      async (
        targetDate: string,
      ) => {
        const [
          appointmentData,
          clientData,
          vehicleData,
          operations,
        ] = await Promise.all([
          listAppointments({
            date:
              targetDate,
          }),

          listClients(
            "",
            100,
          ),

          listVehicles(
            "",
            100,
          ),

          listPendingSyncOperations(),
        ]);


        const ownerMap:
          Record<string, string> =
          {};


        for (
          const operation
          of operations
        ) {
          if (
            operation.kind !==
            "vehicle.create"
          ) {
            continue;
          }

          const ownerId =
            operation
              .payload
              .owner_client_id;

          if (
            typeof ownerId ===
            "string"
          ) {
            ownerMap[
              operation.entity_id
            ] = ownerId;
          }
        }


        setItems(
          appointmentData.items,
        );

        setClients(
          clientData.items,
        );

        setVehicles(
          vehicleData.items,
        );

        setPendingVehicleOwners(
          ownerMap,
        );

        setPageError("");
        setLoading(false);
      },
      [],
    );


  useEffect(() => {
    let active = true;

    const timer =
      window.setTimeout(
        () => {
          void loadData(
            date,
          ).catch(
            (error) => {
              if (!active) {
                return;
              }

              setPageError(
                errorMessage(
                  error,
                ),
              );

              setLoading(false);
            },
          );
        },
        0,
      );

    return () => {
      active = false;

      window.clearTimeout(
        timer,
      );
    };
  }, [
    date,
    loadData,
  ]);


  useEffect(() => {
    function handleSyncCompleted() {
      void loadData(
        date,
      ).catch(
        (error) => {
          setPageError(
            errorMessage(
              error,
            ),
          );
        },
      );
    }

    window.addEventListener(
      "cut-sync-completed",
      handleSyncCompleted,
    );

    return () => {
      window.removeEventListener(
        "cut-sync-completed",
        handleSyncCompleted,
      );
    };
  }, [
    date,
    loadData,
  ]);


  const selectedClient =
    useMemo(
      () =>
        clients.find(
          (client) =>
            client.id ===
            form.client_id,
        ) ??
        null,
      [
        clients,
        form.client_id,
      ],
    );


  const availableVehicles =
    useMemo(() => {
      if (!selectedClient) {
        return [];
      }

      return vehicles.filter(
        (vehicle) => {
          if (
            vehicle.sync_pending
          ) {
            return (
              pendingVehicleOwners[
                vehicle.id
              ] ===
              selectedClient.id
            );
          }

          if (
            selectedClient
              .sync_pending
          ) {
            return false;
          }

          return (
            vehicle
              .current_owner_client_number ===
            selectedClient
              .client_number
          );
        },
      );
    }, [
      pendingVehicleOwners,
      selectedClient,
      vehicles,
    ]);


  function vehiclesForClient(
    client: Client,
  ): Vehicle[] {
    return vehicles.filter(
      (vehicle) => {
        if (
          vehicle.sync_pending
        ) {
          return (
            pendingVehicleOwners[
              vehicle.id
            ] ===
            client.id
          );
        }

        if (
          client.sync_pending
        ) {
          return false;
        }

        return (
          vehicle
            .current_owner_client_number ===
          client.client_number
        );
      },
    );
  }


  function openCreate() {
    setFormError("");
    setEditing(null);

    const firstClient =
      clients.find(
        (client) =>
          vehiclesForClient(
            client,
          ).length > 0,
      ) ??
      clients[0] ??
      null;

    const firstVehicle =
      firstClient
        ? vehiclesForClient(
            firstClient,
          )[0] ??
          null
        : null;


    setForm({
      client_id:
        firstClient?.id ??
        "",

      vehicle_id:
        firstVehicle?.id ??
        "",

      appointment_date:
        date,

      appointment_time:
        "09:00",

      reason: "",
      comment: "",

      status:
        "scheduled",
    });

    setFormOpen(true);
  }


  function openEdit(
    appointment:
      Appointment,
  ) {
    if (
      appointment.sync_pending
    ) {
      return;
    }

    setFormError("");

    const client =
      clients.find(
        (item) =>
          !item.sync_pending &&
          item.client_number ===
            appointment
              .client_number,
      );

    const vehicle =
      vehicles.find(
        (item) =>
          !item.sync_pending &&
          item.vehicle_number ===
            appointment
              .vehicle_number,
      );


    setEditing(
      appointment,
    );

    setForm({
      client_id:
        client?.id ??
        "",

      vehicle_id:
        vehicle?.id ??
        "",

      appointment_date:
        appointment
          .appointment_date,

      appointment_time:
        appointment
          .appointment_time
          .slice(
            0,
            5,
          ),

      reason:
        appointment.reason,

      comment:
        appointment.comment ??
        "",

      status:
        appointment.status,
    });

    setFormOpen(true);
  }


  function validateForm():
    string | null {
    if (
      !selectedClient
    ) {
      return (
        "Выберите клиента."
      );
    }

    const selectedVehicle =
      availableVehicles.find(
        (vehicle) =>
          vehicle.id ===
          form.vehicle_id,
      );

    if (!selectedVehicle) {
      return (
        "Выберите автомобиль клиента."
      );
    }

    if (
      !form.appointment_date
    ) {
      return (
        "Укажите дату записи."
      );
    }

    if (
      !form.appointment_time
    ) {
      return (
        "Укажите время записи."
      );
    }

    if (
      !form.reason.trim()
    ) {
      return (
        "Укажите причину обращения."
      );
    }

    return null;
  }


  function buildUpdatePayload():
    AppointmentInput {
    if (!selectedClient) {
      throw new Error(
        "Клиент не выбран.",
      );
    }

    const selectedVehicle =
      availableVehicles.find(
        (vehicle) =>
          vehicle.id ===
          form.vehicle_id,
      );

    if (
      !selectedVehicle ||
      selectedClient
        .sync_pending ||
      selectedVehicle
        .sync_pending
    ) {
      throw new Error(
        "Запись ещё не синхронизирована.",
      );
    }

    return {
      client_number:
        selectedClient
          .client_number,

      vehicle_number:
        selectedVehicle
          .vehicle_number,

      appointment_date:
        form.appointment_date,

      appointment_time:
        form.appointment_time,

      reason:
        form.reason.trim(),

      comment:
        form.comment
          .trim() ||
        null,

      status:
        form.status,
    };
  }


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    setFormError("");

    const validation =
      validateForm();

    if (validation) {
      setFormError(
        validation,
      );

      return;
    }

    if (!selectedClient) {
      return;
    }

    const selectedVehicle =
      availableVehicles.find(
        (vehicle) =>
          vehicle.id ===
          form.vehicle_id,
      );

    if (!selectedVehicle) {
      return;
    }


    setSaving(true);


    try {
      if (editing) {
        await updateAppointment(
          editing
            .appointment_number,

          buildUpdatePayload(),
        );
      } else {
        await createAppointment({
          client_id:
            selectedClient.id,

          client_number:
            selectedClient
              .sync_pending
              ? null
              : selectedClient
                  .client_number,

          client_name:
            selectedClient
              .full_name,

          vehicle_id:
            selectedVehicle.id,

          vehicle_number:
            selectedVehicle
              .sync_pending
              ? null
              : selectedVehicle
                  .vehicle_number,

          license_plate:
            selectedVehicle
              .license_plate,

          appointment_date:
            form.appointment_date,

          appointment_time:
            form.appointment_time,

          reason:
            form.reason
              .trim(),

          comment:
            form.comment
              .trim() ||
            null,

          status:
            form.status,
        });
      }


      const targetDate =
        form.appointment_date;

      setDate(
        targetDate,
      );

      await loadData(
        targetDate,
      );

      setFormOpen(
        false,
      );

      setEditing(
        null,
      );

      setFormError("");
      setPageError("");
    } catch (error) {
      setFormError(
        errorMessage(
          error,
        ),
      );
    } finally {
      setSaving(
        false,
      );
    }
  }


  async function changeStatus(
    appointment:
      Appointment,

    status:
      AppointmentStatus,
  ) {
    if (
      appointment.sync_pending
    ) {
      return;
    }

    setPageError("");


    try {
      await updateAppointment(
        appointment
          .appointment_number,

        {
          client_number:
            appointment
              .client_number,

          vehicle_number:
            appointment
              .vehicle_number,

          appointment_date:
            appointment
              .appointment_date,

          appointment_time:
            appointment
              .appointment_time,

          reason:
            appointment.reason,

          comment:
            appointment.comment,

          status,
        },
      );

      await loadData(
        date,
      );
    } catch (error) {
      setPageError(
        errorMessage(
          error,
        ),
      );
    }
  }


  return (
    <section className="data-page">
      <div className="section-toolbar">
        <label className="date-filter">
          <span>
            Дата записей
          </span>

          <input
            type="date"
            value={date}
            onChange={(
              event,
            ) => {
              setDate(
                event.target
                  .value,
              );
            }}
          />
        </label>

        <button
          className="primary-inline-button"
          disabled={
            clients.length ===
              0 ||
            vehicles.length ===
              0
          }
          onClick={
            openCreate
          }
          type="button"
        >
          <Plus size={17} />
          Новая запись
        </button>
      </div>


      {pageError && (
        <div className="dashboard-error">
          {pageError}
        </div>
      )}


      <div className="data-card full-width-card">
        <div className="data-card-title">
          <div>
            <span className="card-kicker">
              {formatDate(
                date,
              )}
            </span>

            <h2>
              Записи клиентов
            </h2>
          </div>

          <strong className="count-badge">
            {items.length}
          </strong>
        </div>


        {loading ? (
          <div className="empty-state">
            Загружаем...
          </div>
        ) : items.length ===
          0 ? (
          <div className="empty-state">
            <CalendarClock
              size={30}
            />

            <div>
              <strong>
                На эту дату записей нет
              </strong>

              <p>
                Создай новую запись кнопкой сверху.
              </p>
            </div>
          </div>
        ) : (
          <div className="appointment-page-list">
            {items.map(
              (appointment) => (
                <article
                  className={
                    appointment
                      .status ===
                    "no_show"
                      ? "appointment-card appointment-card-muted"
                      : "appointment-card"
                  }
                  key={
                    appointment.id
                  }
                >
                  <div className="appointment-card-time">
                    {formatTime(
                      appointment
                        .appointment_time,
                    )}
                  </div>

                  <div className="appointment-card-main">
                    <strong>
                      {
                        appointment
                          .client_name
                      }
                    </strong>

                    <span>
                      {
                        appointment
                          .license_plate
                      }

                      {" · "}

                      {appointmentLabel(
                        appointment,
                      )}
                    </span>

                    <p>
                      {
                        appointment
                          .reason
                      }
                    </p>
                  </div>

                  <div className="appointment-card-actions">
                    <button
                      className="icon-action"
                      disabled={
                        Boolean(
                          appointment
                            .sync_pending,
                        )
                      }
                      onClick={() => {
                        openEdit(
                          appointment,
                        );
                      }}
                      title="Изменить"
                      type="button"
                    >
                      <Edit3
                        size={17}
                      />
                    </button>

                    {appointment
                      .status ===
                    "scheduled" ? (
                      <button
                        className="danger-soft-button"
                        disabled={
                          Boolean(
                            appointment
                              .sync_pending,
                          )
                        }
                        onClick={() => {
                          void changeStatus(
                            appointment,
                            "no_show",
                          );
                        }}
                        type="button"
                      >
                        <UserX
                          size={16}
                        />

                        Не приехал
                      </button>
                    ) : (
                      <button
                        className="secondary-button"
                        disabled={
                          Boolean(
                            appointment
                              .sync_pending,
                          )
                        }
                        onClick={() => {
                          void changeStatus(
                            appointment,
                            "scheduled",
                          );
                        }}
                        type="button"
                      >
                        <RotateCcw
                          size={16}
                        />

                        Вернуть
                      </button>
                    )}
                  </div>
                </article>
              ),
            )}
          </div>
        )}
      </div>


      {formOpen && (
        <div className="modal-backdrop">
          <form
            className="modal-card"
            onSubmit={
              submit
            }
          >
            <div className="modal-header">
              <span className="card-kicker">
                {editing
                  ? `Запись №${editing.appointment_number}`
                  : "Новая запись"}
              </span>

              <h2>
                {editing
                  ? "Изменить запись"
                  : "Записать клиента"}
              </h2>
            </div>


            {formError && (
              <div className="form-error">
                <strong>
                  Не удалось сохранить запись
                </strong>

                <span>
                  {formError}
                </span>
              </div>
            )}


            <div className="form-grid">
              <label>
                <span>
                  Клиент *
                </span>

                <select
                  required
                  value={
                    form.client_id
                  }
                  onChange={(
                    event,
                  ) => {
                    const clientId =
                      event.target
                        .value;

                    const client =
                      clients.find(
                        (item) =>
                          item.id ===
                          clientId,
                      );

                    const firstVehicle =
                      client
                        ? vehiclesForClient(
                            client,
                          )[0] ??
                          null
                        : null;

                    setFormError("");

                    setForm({
                      ...form,

                      client_id:
                        clientId,

                      vehicle_id:
                        firstVehicle
                          ?.id ??
                        "",
                    });
                  }}
                >
                  {clients.map(
                    (client) => (
                      <option
                        key={
                          client.id
                        }
                        value={
                          client.id
                        }
                      >
                        {clientLabel(
                          client,
                        )}
                      </option>
                    ),
                  )}
                </select>
              </label>


              <label>
                <span>
                  Автомобиль *
                </span>

                <select
                  required
                  value={
                    form.vehicle_id
                  }
                  onChange={(
                    event,
                  ) => {
                    setFormError("");

                    setForm({
                      ...form,

                      vehicle_id:
                        event.target
                          .value,
                    });
                  }}
                >
                  {availableVehicles
                    .length === 0 && (
                    <option value="">
                      У клиента нет автомобиля
                    </option>
                  )}

                  {availableVehicles.map(
                    (vehicle) => (
                      <option
                        key={
                          vehicle.id
                        }
                        value={
                          vehicle.id
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

                        {vehicle
                          .sync_pending
                          ? " · ожидает синхронизации"
                          : ""}
                      </option>
                    ),
                  )}
                </select>
              </label>


              <label>
                <span>
                  Дата *
                </span>

                <input
                  required
                  type="date"
                  value={
                    form
                      .appointment_date
                  }
                  onChange={(
                    event,
                  ) => {
                    setFormError("");

                    setForm({
                      ...form,

                      appointment_date:
                        event.target
                          .value,
                    });
                  }}
                />
              </label>


              <label>
                <span>
                  Время *
                </span>

                <input
                  required
                  type="time"
                  value={
                    form
                      .appointment_time
                  }
                  onChange={(
                    event,
                  ) => {
                    setFormError("");

                    setForm({
                      ...form,

                      appointment_time:
                        event.target
                          .value,
                    });
                  }}
                />
              </label>


              <label className="form-wide">
                <span>
                  Причина обращения *
                </span>

                <input
                  required
                  value={
                    form.reason
                  }
                  onChange={(
                    event,
                  ) => {
                    setFormError("");

                    setForm({
                      ...form,

                      reason:
                        event.target
                          .value,
                    });
                  }}
                />
              </label>


              <label className="form-wide">
                <span>
                  Комментарий{" "}
                  <small>
                    (необязательно)
                  </small>
                </span>

                <textarea
                  rows={3}
                  value={
                    form.comment
                  }
                  onChange={(
                    event,
                  ) => {
                    setForm({
                      ...form,

                      comment:
                        event.target
                          .value,
                    });
                  }}
                />
              </label>
            </div>


            <div className="modal-actions">
              <button
                className="secondary-button"
                disabled={
                  saving
                }
                onClick={() => {
                  setFormOpen(
                    false,
                  );

                  setFormError("");
                }}
                type="button"
              >
                Отмена
              </button>

              <button
                className="primary-inline-button"
                disabled={
                  saving
                }
                type="submit"
              >
                {saving
                  ? "Сохраняем..."
                  : "Сохранить"}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}