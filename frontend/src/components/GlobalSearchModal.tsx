import {
  Car,
  ChevronRight,
  Search,
  UserRound,
  X,
} from "lucide-react";
import {
  useEffect,
  useRef,
  useState,
} from "react";
import type {
  FormEvent,
} from "react";

import {
  ApiError,
} from "../api/client";
import {
  globalSearch,
} from "../api/search";
import type {
  GlobalSearchResponse,
} from "../types/search";


type Props = {
  onClose: () => void;
  onOpenClients: () => void;
  onOpenVehicles: () => void;
};


const sourceLabels:
  Record<string, string> = {
    avito: "Avito",
    referral:
      "По рекомендации",
    other: "Другое",
  };


function formatMileage(
  value:
    | number
    | null,
): string {
  if (value === null) {
    return "Пробег не указан";
  }

  return (
    `${value.toLocaleString("ru-RU")} км`
  );
}


function errorText(
  error: unknown,
): string {
  if (
    error instanceof ApiError
  ) {
    return error.message;
  }

  return "Не удалось выполнить поиск.";
}


export function GlobalSearchModal({
  onClose,
  onOpenClients,
  onOpenVehicles,
}: Props) {
  const inputRef =
    useRef<HTMLInputElement>(
      null,
    );


  const [
    query,
    setQuery,
  ] = useState("");


  const [
    result,
    setResult,
  ] = useState<
    GlobalSearchResponse | null
  >(null);


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {
    const timer =
      window.setTimeout(
        () => {
          inputRef.current
            ?.focus();
        },
        0,
      );

    return () => {
      window.clearTimeout(
        timer,
      );
    };
  }, []);


  useEffect(() => {
    function onKeyDown(
      event: KeyboardEvent,
    ) {
      if (
        event.key ===
        "Escape"
      ) {
        onClose();
      }
    }

    window.addEventListener(
      "keydown",
      onKeyDown,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        onKeyDown,
      );
    };
  }, [onClose]);


  async function submitSearch(
    event: FormEvent,
  ) {
    event.preventDefault();

    const value =
      query.trim();

    if (!value) {
      setResult(null);
      setError(
        "Введите имя, телефон, госномер, VIN, марку, модель или номер.",
      );

      inputRef.current
        ?.focus();

      return;
    }

    setLoading(true);
    setError("");

    try {
      const data =
        await globalSearch(
          value,
          20,
        );

      setResult(data);
    } catch (searchError) {
      setResult(null);

      setError(
        errorText(
          searchError,
        ),
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <div
      aria-modal="true"
      className="global-search-overlay"
      role="dialog"
      onMouseDown={(event) => {
        if (
          event.target ===
          event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      <section className="global-search-window">
        <header className="global-search-header">
          <div>
            <Search size={21} />

            <div>
              <strong>
                Поиск по СТО
              </strong>

              <span>
                Клиенты и автомобили
              </span>
            </div>
          </div>

          <button
            aria-label="Закрыть поиск"
            className="global-search-close"
            onClick={onClose}
            type="button"
          >
            <X size={19} />
          </button>
        </header>


        <form
          className="global-search-form"
          onSubmit={
            submitSearch
          }
        >
          <div className="global-search-input-wrap">
            <Search size={19} />

            <input
              ref={inputRef}
              placeholder="Имя, телефон, госномер, VIN, марка, модель или номер"
              value={query}
              onChange={(event) => {
                setQuery(
                  event.target.value,
                );

                setError("");
              }}
            />

            {query && (
              <button
                aria-label="Очистить"
                className="global-search-clear"
                onClick={() => {
                  setQuery("");
                  setResult(null);
                  setError("");

                  inputRef.current
                    ?.focus();
                }}
                type="button"
              >
                <X size={16} />
              </button>
            )}
          </div>

          <button
            className="global-search-submit"
            disabled={loading}
            type="submit"
          >
            {loading
              ? "Ищем..."
              : "Найти"}
          </button>
        </form>


        <div className="global-search-hint">
          Можно искать по части имени,
          номеру телефона, номеру клиента,
          госномеру, VIN, марке, модели
          или номеру автомобиля.
        </div>


        {error && (
          <div className="global-search-error">
            {error}
          </div>
        )}


        {!result &&
          !loading &&
          !error && (
          <div className="global-search-start">
            <Search size={30} />

            <strong>
              Быстрый поиск
            </strong>

            <span>
              Введите данные выше
              и нажмите «Найти».
            </span>
          </div>
        )}


        {result && (
          <div className="global-search-results">
            <div className="global-search-summary">
              <span>
                По запросу
                {" "}
                <strong>
                  «{result.query}»
                </strong>
              </span>

              <span>
                Найдено:
                {" "}
                <strong>
                  {result.total}
                </strong>
              </span>
            </div>


            {result.total === 0 && (
              <div className="global-search-empty">
                <Search size={27} />

                <strong>
                  Ничего не найдено
                </strong>

                <span>
                  Попробуйте другой
                  телефон, имя, госномер
                  или VIN.
                </span>
              </div>
            )}


            {result.clients.length >
              0 && (
              <section className="global-search-group">
                <div className="global-search-group-heading">
                  <div>
                    <UserRound
                      size={17}
                    />

                    <strong>
                      Клиенты
                    </strong>
                  </div>

                  <span>
                    {
                      result
                        .total_clients
                    }
                  </span>
                </div>


                <div className="global-search-list">
                  {result.clients.map(
                    (client) => (
                      <button
                        className="global-search-result"
                        key={
                          client
                            .client_number
                        }
                        onClick={
                          onOpenClients
                        }
                        type="button"
                      >
                        <div className="global-search-result-icon">
                          <UserRound
                            size={19}
                          />
                        </div>

                        <div className="global-search-result-main">
                          <div className="global-search-result-title">
                            <strong>
                              {
                                client
                                  .full_name
                              }
                            </strong>

                            {client
                              .internal_mark && (
                              <span
                                className="global-search-internal-mark"
                                title="Внутренняя метка клиента"
                              >
                                😈
                              </span>
                            )}
                          </div>

                          <span>
                            Клиент №
                            {
                              client
                                .client_number
                            }
                            {" · "}
                            {
                              client
                                .phone_primary
                            }
                          </span>

                          {client
                            .phone_secondary && (
                            <span>
                              Второй телефон:
                              {" "}
                              {
                                client
                                  .phone_secondary
                              }
                            </span>
                          )}

                          <small>
                            Источник:
                            {" "}
                            {sourceLabels[
                              client.source
                            ] ??
                              client.source}
                          </small>
                        </div>

                        <div className="global-search-result-open">
                          <span>
                            Клиенты
                          </span>

                          <ChevronRight
                            size={17}
                          />
                        </div>
                      </button>
                    ),
                  )}
                </div>
              </section>
            )}


            {result.vehicles.length >
              0 && (
              <section className="global-search-group">
                <div className="global-search-group-heading">
                  <div>
                    <Car size={17} />

                    <strong>
                      Автомобили
                    </strong>
                  </div>

                  <span>
                    {
                      result
                        .total_vehicles
                    }
                  </span>
                </div>


                <div className="global-search-list">
                  {result.vehicles.map(
                    (vehicle) => (
                      <button
                        className="global-search-result"
                        key={
                          vehicle
                            .vehicle_number
                        }
                        onClick={
                          onOpenVehicles
                        }
                        type="button"
                      >
                        <div className="global-search-result-icon">
                          <Car size={19} />
                        </div>

                        <div className="global-search-result-main">
                          <div className="global-search-result-title">
                            <strong>
                              {
                                vehicle.brand
                              }
                              {" "}
                              {
                                vehicle.model
                              }
                            </strong>

                            <span className="global-search-plate">
                              {
                                vehicle
                                  .license_plate
                              }
                            </span>
                          </div>

                          <span>
                            Автомобиль №
                            {
                              vehicle
                                .vehicle_number
                            }

                            {vehicle.year !==
                              null &&
                              ` · ${vehicle.year} г.`}
                          </span>

                          <span>
                            {vehicle.vin
                              ? `VIN: ${vehicle.vin}`
                              : "VIN не указан"}
                            {" · "}
                            {formatMileage(
                              vehicle
                                .mileage,
                            )}
                          </span>

                          <small>
                            Владелец:
                            {" "}
                            {
                              vehicle
                                .current_owner_name
                            }
                            {" · "}
                            клиент №
                            {
                              vehicle
                                .current_owner_client_number
                            }
                          </small>
                        </div>

                        <div className="global-search-result-open">
                          <span>
                            Автомобили
                          </span>

                          <ChevronRight
                            size={17}
                          />
                        </div>
                      </button>
                    ),
                  )}
                </div>
              </section>
            )}
          </div>
        )}
      </section>
    </div>
  );
}