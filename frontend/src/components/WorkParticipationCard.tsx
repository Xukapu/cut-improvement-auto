import {
  Save,
  Wrench,
} from "lucide-react";
import {
  useEffect,
  useState,
} from "react";
import type {
  FormEvent,
} from "react";

import {
  getWorkParticipation,
  updateWorkParticipation,
} from "../api/workParticipation";
import {
  ApiError,
} from "../api/client";


function errorText(
  error: unknown,
): string {
  if (
    error instanceof ApiError
  ) {
    return error.message;
  }

  return (
    "Не удалось сохранить " +
    "участие в работах."
  );
}


export function WorkParticipationCard() {
  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    enabled,
    setEnabled,
  ] = useState(false);

  const [
    ratePercent,
    setRatePercent,
  ] = useState("");

  const [
    employeeNumber,
    setEmployeeNumber,
  ] = useState<
    number | null
  >(null);

  const [
    employeeName,
    setEmployeeName,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");

  const [
    message,
    setMessage,
  ] = useState("");


  useEffect(() => {
    let cancelled = false;

    const timer =
      window.setTimeout(() => {
        void getWorkParticipation()
          .then((data) => {
            if (cancelled) {
              return;
            }

            setEnabled(
              data.enabled,
            );

            setEmployeeNumber(
              data.employee_number,
            );

            setEmployeeName(
              data.employee_name,
            );

            setRatePercent(
              data.rate_percent ===
                null
                ? ""
                : String(
                    data.rate_percent,
                  ),
            );
          })
          .catch((loadError) => {
            if (cancelled) {
              return;
            }

            setError(
              errorText(
                loadError,
              ),
            );
          })
          .finally(() => {
            if (!cancelled) {
              setLoading(false);
            }
          });
      }, 0);

    return () => {
      cancelled = true;

      window.clearTimeout(
        timer,
      );
    };
  }, []);


  async function handleSave(
    event: FormEvent,
  ) {
    event.preventDefault();

    setError("");
    setMessage("");

    let rate: number | null =
      null;

    if (enabled) {
      rate = Number(
        ratePercent.replace(
          ",",
          ".",
        ),
      );

      if (
        Number.isNaN(rate) ||
        rate < 0 ||
        rate > 100
      ) {
        setError(
          "Укажите ставку от 0 до 100%.",
        );

        return;
      }
    }

    setSaving(true);

    try {
      const result =
        await updateWorkParticipation(
          {
            enabled,
            rate_percent:
              rate,
          },
        );

      setEnabled(
        result.enabled,
      );

      setEmployeeNumber(
        result.employee_number,
      );

      setEmployeeName(
        result.employee_name,
      );

      setRatePercent(
        result.rate_percent ===
          null
          ? ""
          : String(
              result.rate_percent,
            ),
      );

      setMessage(
        result.enabled
          ? (
              "Готово. В заказ-нарядах " +
              "вы доступны как исполнитель."
            )
          : (
              "Участие в работах отключено. " +
              "Доступ владельца к программе сохранён."
            ),
      );
    } catch (saveError) {
      setError(
        errorText(
          saveError,
        ),
      );
    } finally {
      setSaving(false);
    }
  }


  return (
    <form
      className="settings-card work-participation-card"
      onSubmit={
        handleSave
      }
    >
      <div className="settings-card-heading">
        <div>
          <span>
            Работа в СТО
          </span>

          <h2>
            Я тоже исполнитель
          </h2>
        </div>

        <Wrench size={22} />
      </div>


      {loading ? (
        <div className="work-participation-loading">
          Загружаем...
        </div>
      ) : (
        <>
          <label className="work-participation-toggle">
            <input
              checked={enabled}
              type="checkbox"
              onChange={(event) => {
                setEnabled(
                  event.target
                    .checked,
                );

                setMessage("");
              }}
            />

            <div>
              <strong>
                Участвую в ремонтах
                как исполнитель
              </strong>

              <span>
                В заказ-нарядах будет
                отображаться только ваше
                имя, без роли «Владелец».
              </span>
            </div>
          </label>


          <label className="work-participation-rate">
            <span>
              Ставка исполнителя, %
            </span>

            <input
              disabled={!enabled}
              max="100"
              min="0"
              placeholder="Например, 40"
              step="0.01"
              type="number"
              value={ratePercent}
              onChange={(event) => {
                setRatePercent(
                  event.target
                    .value,
                );

                setMessage("");
              }}
            />
          </label>


          {employeeNumber !==
            null && (
            <div className="work-participation-linked">
              <span>
                Карточка исполнителя
              </span>

              <strong>
                {employeeName}
              </strong>

              <small>
                Сотрудник №
                {employeeNumber}
              </small>
            </div>
          )}


          {error && (
            <div className="settings-error">
              {error}
            </div>
          )}


          {message && (
            <div className="settings-success">
              {message}
            </div>
          )}


          <div className="settings-actions">
            <button
              className="primary-button"
              disabled={saving}
              type="submit"
            >
              <Save size={16} />

              {saving
                ? "Сохраняем..."
                : "Сохранить"}
            </button>
          </div>
        </>
      )}
    </form>
  );
}