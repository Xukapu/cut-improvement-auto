import {
  CalendarClock,
  Edit3,
  Plus,
  RotateCcw,
  UserX,
} from "lucide-react";
import {
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
  client_number: string;
  vehicle_number: string;
  appointment_date: string;
  appointment_time: string;
  reason: string;
  comment: string;
  status: AppointmentStatus;
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
    client_number: "",
    vehicle_number: "",
    appointment_date:
      todayIso(),
    appointment_time:
      "09:00",
    reason: "",
    comment: "",
    status: "scheduled",
  });


  // ----------------------------------------------------------
  // Загружаем список записей, клиентов и автомобилей
  // ----------------------------------------------------------

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const [
          appointmentData,
          clientData,
          vehicleData,
        ] = await Promise.all([
          listAppointments({
            date,
          }),
          listClients(
            "",
            100,
          ),
          listVehicles(
            "",
            100,
          ),
        ]);

        if (!active) {
          return;
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

        setPageError("");
        setLoading(false);
      } catch (error) {
        if (!active) {
          return;
        }

        setPageError(
          errorMessage(error),
        );

        setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [
    date,
  ]);


  // ----------------------------------------------------------
  // Машины только выбранного клиента
  // ----------------------------------------------------------

  const availableVehicles =
    useMemo(() => {
      const clientNumber =
        Number(
          form.client_number,
        );

      if (
        !clientNumber
      ) {
        return [];
      }

      return vehicles.filter(
        (vehicle) =>
          vehicle
            .current_owner_client_number ===
          clientNumber,
      );
    }, [
      form.client_number,
      vehicles,
    ]);


  async function refresh(
    targetDate = date,
  ) {
    const appointmentData =
      await listAppointments({
        date: targetDate,
      });

    setItems(
      appointmentData.items,
    );
  }


  // ----------------------------------------------------------
  // Новая запись
  // ----------------------------------------------------------

  function openCreate() {
    setFormError("");
    setEditing(null);

    const firstClient =
      clients[0] ??
      null;

    const firstVehicle =
      firstClient
        ? vehicles.find(
            (vehicle) =>
              vehicle
                .current_owner_client_number ===
              firstClient
                .client_number,
          )
        : null;

    setForm({
      client_number:
        firstClient
          ? String(
              firstClient
                .client_number,
            )
          : "",

      vehicle_number:
        firstVehicle
          ? String(
              firstVehicle
                .vehicle_number,
            )
          : "",

      appointment_date:
        date,

      appointment_time:
        "09:00",

      reason: "",
      comment: "",
      status: "scheduled",
    });

    setFormOpen(true);
  }


  // ----------------------------------------------------------
  // Редактирование существующей записи
  // ----------------------------------------------------------

  function openEdit(
    appointment: Appointment,
  ) {
    setFormError("");

    setEditing(
      appointment,
    );

    setForm({
      client_number:
        String(
          appointment
            .client_number,
        ),

      vehicle_number:
        String(
          appointment
            .vehicle_number,
        ),

      appointment_date:
        appointment
          .appointment_date,

      appointment_time:
        appointment
          .appointment_time
          .slice(0, 5),

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


  // ----------------------------------------------------------
  // Проверка формы перед отправкой
  // ----------------------------------------------------------

  function validateForm():
    string | null {
    if (
      !form.client_number
    ) {
      return (
        "Выберите клиента."
      );
    }

    if (
      !form.vehicle_number
    ) {
      return (
        "Выберите автомобиль клиента."
      );
    }

    const selectedVehicle =
      availableVehicles.find(
        (vehicle) =>
          String(
            vehicle
              .vehicle_number,
          ) ===
          form.vehicle_number,
      );

    if (!selectedVehicle) {
      return (
        "Выбранный автомобиль " +
        "не принадлежит этому клиенту."
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


  function buildPayload():
    AppointmentInput {
    return {
      client_number:
        Number(
          form.client_number,
        ),

      vehicle_number:
        Number(
          form.vehicle_number,
        ),

      appointment_date:
        form.appointment_date,

      appointment_time:
        form.appointment_time,

      reason:
        form.reason.trim(),

      comment:
        form.comment.trim() ||
        null,

      status:
        form.status,
    };
  }


  // ----------------------------------------------------------
  // Сохранение
  // ----------------------------------------------------------

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

    setSaving(true);

    try {
      if (editing) {
        await updateAppointment(
          editing
            .appointment_number,
          buildPayload(),
        );
      } else {
        await createAppointment(
          buildPayload(),
        );
      }

      const targetDate =
        form.appointment_date;

      await refresh(
        targetDate,
      );

      setDate(
        targetDate,
      );

      setFormOpen(false);
      setEditing(null);
      setFormError("");
      setPageError("");
    } catch (error) {
      setFormError(
        errorMessage(error),
      );
    } finally {
      setSaving(false);
    }
  }


  // ----------------------------------------------------------
  // Не приехал / вернуть
  // ----------------------------------------------------------

  async function changeStatus(
    appointment: Appointment,
    status: AppointmentStatus,
  ) {
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

      await refresh();
    } catch (error) {
      setPageError(
        errorMessage(error),
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
                event.target.value,
              );
            }}
          />
        </label>

        <button
          className=
            "primary-inline-button"
          disabled={
            clients.length === 0 ||
            vehicles.length === 0
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
        <div className=
          "dashboard-error"
        >
          {pageError}
        </div>
      )}


      <div className=
        "data-card full-width-card"
      >
        <div className=
          "data-card-title"
        >
          <div>
            <span className=
              "card-kicker"
            >
              {formatDate(date)}
            </span>

            <h2>
              Записи клиентов
            </h2>
          </div>

          <strong className=
            "count-badge"
          >
            {items.length}
          </strong>
        </div>


        {loading ? (
          <div className=
            "empty-state"
          >
            Загружаем...
          </div>
        ) : items.length ===
          0 ? (
          <div className=
            "empty-state"
          >
            <CalendarClock
              size={30}
            />

            <div>
              <strong>
                На эту дату записей нет
              </strong>

              <p>
                Создай новую запись
                кнопкой сверху.
              </p>
            </div>
          </div>
        ) : (
          <div className=
            "appointment-page-list"
          >
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
                    appointment
                      .appointment_number
                  }
                >
                  <div className=
                    "appointment-card-time"
                  >
                    {formatTime(
                      appointment
                        .appointment_time,
                    )}
                  </div>

                  <div className=
                    "appointment-card-main"
                  >
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
                      }{" "}
                      · Запись №
                      {
                        appointment
                          .appointment_number
                      }
                    </span>

                    <p>
                      {
                        appointment
                          .reason
                      }
                    </p>
                  </div>

                  <div className=
                    "appointment-card-actions"
                  >
                    <button
                      className=
                        "icon-action"
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
                        className=
                          "danger-soft-button"
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
                        className=
                          "secondary-button"
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
        <div className=
          "modal-backdrop"
        >
          <form
            className=
              "modal-card"
            onSubmit={submit}
          >
            <div className=
              "modal-header"
            >
              <span className=
                "card-kicker"
              >
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
              <div className=
                "form-error"
              >
                <strong>
                  Не удалось сохранить запись
                </strong>

                <span>
                  {formError}
                </span>
              </div>
            )}


            <div className=
              "form-grid"
            >
              <label>
                <span>
                  Клиент *
                </span>

                <select
                  required
                  value={
                    form.client_number
                  }
                  onChange={(
                    event,
                  ) => {
                    const client =
                      event.target
                        .value;

                    const firstVehicle =
                      vehicles.find(
                        (vehicle) =>
                          String(
                            vehicle
                              .current_owner_client_number,
                          ) ===
                          client,
                      );

                    setFormError("");

                    setForm({
                      ...form,
                      client_number:
                        client,

                      vehicle_number:
                        firstVehicle
                          ? String(
                              firstVehicle
                                .vehicle_number,
                            )
                          : "",
                    });
                  }}
                >
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
                        №
                        {
                          client
                            .client_number
                        }{" "}
                        ·{" "}
                        {
                          client
                            .full_name
                        }
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
                    form.vehicle_number
                  }
                  onChange={(
                    event,
                  ) => {
                    setFormError("");

                    setForm({
                      ...form,
                      vehicle_number:
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


              <label className=
                "form-wide"
              >
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


              <label className=
                "form-wide"
              >
                <span>
                  Комментарий
                  {" "}
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


            <div className=
              "modal-actions"
            >
              <button
                className=
                  "secondary-button"
                disabled={saving}
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
                className=
                  "primary-inline-button"
                disabled={saving}
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