import {
  CalendarClock,
} from "lucide-react";
import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getDashboard,
} from "../api/dashboard";

import type {
  DashboardResponse,
} from "../types/dashboard";

import {
  formatDate,
  formatTime,
  todayIso,
} from "../utils/format";


type Props = {
  onOpenAppointments: () => void;
};


function addDays(
  isoDate: string,
  days: number,
): string {
  const [
    year,
    month,
    day,
  ] = isoDate
    .split("-")
    .map(Number);

  const date =
    new Date(
      year,
      month - 1,
      day,
    );

  date.setDate(
    date.getDate() + days,
  );

  const nextYear =
    String(
      date.getFullYear(),
    );

  const nextMonth =
    String(
      date.getMonth() + 1,
    ).padStart(2, "0");

  const nextDay =
    String(
      date.getDate(),
    ).padStart(2, "0");

  return (
    `${nextYear}-${nextMonth}-${nextDay}`
  );
}


export function DashboardAppointmentsCard({
  onOpenAppointments,
}: Props) {
  const today =
    todayIso();

  const tomorrow =
    useMemo(
      () => addDays(
        today,
        1,
      ),
      [today],
    );

  const [
    selectedDay,
    setSelectedDay,
  ] = useState<
    "today" | "tomorrow"
  >("today");

  const [
    data,
    setData,
  ] = useState<
    DashboardResponse | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  const selectedDate =
    selectedDay === "today"
      ? today
      : tomorrow;


  useEffect(() => {
    let active = true;

    getDashboard(
      selectedDate,
    )
      .then((response) => {
        if (!active) {
          return;
        }

        setData(response);
        setError("");
        setLoading(false);
      })
      .catch(() => {
        if (!active) {
          return;
        }

        setError(
          "Не удалось загрузить записи.",
        );

        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [
    selectedDate,
  ]);


  function chooseDay(
    day: "today" | "tomorrow",
  ) {
    if (
      selectedDay === day
    ) {
      return;
    }

    setLoading(true);
    setError("");
    setSelectedDay(day);
  }


  const appointments =
    data?.appointments_today ??
    [];


  return (
    <article className="workspace-card">
      <div className="card-header">
        <div>
          <div className="dashboard-day-switch">
            <button
              className={
                selectedDay ===
                "today"
                  ? "dashboard-day-button dashboard-day-button-active"
                  : "dashboard-day-button"
              }
              onClick={() => {
                chooseDay(
                  "today",
                );
              }}
              type="button"
            >
              Сегодня
            </button>

            <button
              className={
                selectedDay ===
                "tomorrow"
                  ? "dashboard-day-button dashboard-day-button-active"
                  : "dashboard-day-button"
              }
              onClick={() => {
                chooseDay(
                  "tomorrow",
                );
              }}
              type="button"
            >
              Завтра
            </button>
          </div>

          <h3>
            Записи клиентов
          </h3>

          <span className="dashboard-preview-date">
            {formatDate(
              selectedDate,
            )}
          </span>
        </div>

        <button
          className="secondary-button"
          onClick={
            onOpenAppointments
          }
          type="button"
        >
          Новая запись
        </button>
      </div>


      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}


      {loading ? (
        <div className="empty-state dashboard-preview-loading">
          Загружаем записи...
        </div>
      ) : appointments.length >
        0 ? (
        <div className="appointment-list">
          {appointments.map(
            (appointment) => (
              <div
                className="appointment-row"
                key={
                  appointment
                    .appointment_number
                }
              >
                <div className="appointment-time">
                  {formatTime(
                    appointment
                      .appointment_time,
                  )}
                </div>

                <div className="appointment-main">
                  <strong>
                    {
                      appointment
                        .client_name
                    }
                  </strong>

                  <span>
                    {
                      appointment
                        .vehicle_name
                    }
                    {" · "}
                    {
                      appointment
                        .license_plate
                    }
                  </span>

                  <small>
                    {
                      appointment
                        .reason
                    }
                  </small>
                </div>

                <div className="appointment-number">
                  Запись №
                  {
                    appointment
                      .appointment_number
                  }
                </div>
              </div>
            ),
          )}
        </div>
      ) : (
        <div className="empty-state">
          <CalendarClock
            size={28}
          />

          <div>
            <strong>
              {selectedDay ===
              "today"
                ? "На сегодня записей нет"
                : "На завтра записей нет"}
            </strong>

            <p>
              {selectedDay ===
              "today"
                ? "Рабочий день пока свободен."
                : "На следующий день пока ничего не запланировано."}
            </p>
          </div>
        </div>
      )}
    </article>
  );
}