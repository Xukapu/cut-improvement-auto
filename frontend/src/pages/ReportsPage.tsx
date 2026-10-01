import {
  CalendarDays,
  RefreshCw,
  UserCheck,
  Users,
  Wallet,
  Wrench,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getClientReport,
  getEmployeeAccrualReport,
  getFinanceReport,
  getWorkReport,
} from "../api/reports";
import {
  ApiError,
} from "../api/client";
import type {
  CurrentUser,
} from "../types/auth";
import type {
  ClientReport,
  EmployeeAccrualReport,
  FinanceReport,
  WorkReport,
} from "../types/report";


type Props = {
  currentUser: CurrentUser;
};


type ReportTab =
  | "clients"
  | "works"
  | "finance"
  | "accruals";


const sourceLabels:
  Record<string, string> = {
    avito: "Avito",
    referral: "По рекомендации",
    other: "Другое",
  };


function isoDate(
  date: Date,
): string {
  const year =
    date.getFullYear();

  const month =
    String(
      date.getMonth() + 1,
    ).padStart(
      2,
      "0",
    );

  const day =
    String(
      date.getDate(),
    ).padStart(
      2,
      "0",
    );

  return `${year}-${month}-${day}`;
}


function todayIso(): string {
  return isoDate(
    new Date(),
  );
}


function monthStartIso(): string {
  const today =
    new Date();

  return isoDate(
    new Date(
      today.getFullYear(),
      today.getMonth(),
      1,
    ),
  );
}


function formatMoney(
  value:
    | string
    | number,
): string {
  const number =
    Number(value);

  if (
    Number.isNaN(number)
  ) {
    return `${value} ₽`;
  }

  return new Intl.NumberFormat(
    "ru-RU",
    {
      style: "currency",
      currency: "RUB",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
  ).format(number);
}


function formatDate(
  value: string,
): string {
  const date =
    new Date(
      `${value.slice(0, 10)}T00:00:00`,
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


function formatDateTime(
  value: string,
): string {
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


function errorText(
  error: unknown,
): string {
  if (
    error instanceof ApiError
  ) {
    return error.message;
  }

  return "Не удалось загрузить отчёт.";
}


export function ReportsPage({
  currentUser,
}: Props) {
  const isOwner =
    currentUser.role ===
    "owner";


  const [
    tab,
    setTab,
  ] = useState<ReportTab>(
    "clients",
  );


  const [
    dateFrom,
    setDateFrom,
  ] = useState(
    monthStartIso,
  );

  const [
    dateTo,
    setDateTo,
  ] = useState(
    todayIso,
  );


  const [
    clients,
    setClients,
  ] = useState<
    ClientReport | null
  >(null);

  const [
    works,
    setWorks,
  ] = useState<
    WorkReport | null
  >(null);

  const [
    finance,
    setFinance,
  ] = useState<
    FinanceReport | null
  >(null);

  const [
    accruals,
    setAccruals,
  ] = useState<
    EmployeeAccrualReport | null
  >(null);


  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");


  const loadReports =
    useCallback(async () => {
      if (
        !dateFrom ||
        !dateTo
      ) {
        return;
      }

      if (
        dateFrom > dateTo
      ) {
        setError(
          "Дата начала периода не может быть позже даты окончания.",
        );

        return;
      }

      setLoading(true);
      setError("");

      const period = {
        dateFrom,
        dateTo,
      };

      try {
        const [
          clientData,
          workData,
        ] = await Promise.all([
          getClientReport(
            period,
          ),

          getWorkReport(
            period,
          ),
        ]);

        setClients(
          clientData,
        );

        setWorks(
          workData,
        );


        if (isOwner) {
          const [
            financeData,
            accrualData,
          ] = await Promise.all([
            getFinanceReport(
              period,
            ),

            getEmployeeAccrualReport(
              period,
            ),
          ]);

          setFinance(
            financeData,
          );

          setAccruals(
            accrualData,
          );
        } else {
          setFinance(null);
          setAccruals(null);
        }
      } catch (loadError) {
        setError(
          errorText(
            loadError,
          ),
        );
      } finally {
        setLoading(false);
      }
    }, [
      dateFrom,
      dateTo,
      isOwner,
    ]);


  useEffect(() => {
    const timer =
      window.setTimeout(
        () => {
          void loadReports();
        },
        0,
      );

    return () => {
      window.clearTimeout(
        timer,
      );
    };
  }, [loadReports]);


  function setToday() {
    const today =
      todayIso();

    setDateFrom(today);
    setDateTo(today);
  }


  function setLastDays(
    days: number,
  ) {
    const end =
      new Date();

    const start =
      new Date();

    start.setDate(
      end.getDate() -
      (days - 1),
    );

    setDateFrom(
      isoDate(start),
    );

    setDateTo(
      isoDate(end),
    );
  }


  function setCurrentMonth() {
    setDateFrom(
      monthStartIso(),
    );

    setDateTo(
      todayIso(),
    );
  }


  return (
    <section className="reports-page">
      <section className="reports-period-card">
        <div className="reports-period-heading">
          <CalendarDays
            size={21}
          />

          <div>
            <strong>
              Период отчёта
            </strong>

            <span>
              Все показатели ниже
              рассчитываются для
              выбранного периода.
            </span>
          </div>
        </div>


        <div className="reports-period-controls">
          <label>
            <span>
              С
            </span>

            <input
              type="date"
              value={dateFrom}
              onChange={(event) => {
                setDateFrom(
                  event.target.value,
                );
              }}
            />
          </label>

          <label>
            <span>
              По
            </span>

            <input
              type="date"
              value={dateTo}
              onChange={(event) => {
                setDateTo(
                  event.target.value,
                );
              }}
            />
          </label>

          <button
            className="reports-refresh-button"
            disabled={loading}
            onClick={() => {
              void loadReports();
            }}
            type="button"
          >
            <RefreshCw
              size={16}
            />

            {loading
              ? "Обновляем..."
              : "Обновить"}
          </button>
        </div>


        <div className="reports-presets">
          <button
            onClick={setToday}
            type="button"
          >
            Сегодня
          </button>

          <button
            onClick={() => {
              setLastDays(7);
            }}
            type="button"
          >
            7 дней
          </button>

          <button
            onClick={() => {
              setLastDays(30);
            }}
            type="button"
          >
            30 дней
          </button>

          <button
            onClick={
              setCurrentMonth
            }
            type="button"
          >
            Этот месяц
          </button>
        </div>
      </section>


      {error && (
        <div className="reports-error">
          {error}
        </div>
      )}


      <div className="reports-tabs">
        <button
          className={
            tab === "clients"
              ? "reports-tab reports-tab-active"
              : "reports-tab"
          }
          onClick={() => {
            setTab("clients");
          }}
          type="button"
        >
          <Users size={17} />
          Клиенты
        </button>

        <button
          className={
            tab === "works"
              ? "reports-tab reports-tab-active"
              : "reports-tab"
          }
          onClick={() => {
            setTab("works");
          }}
          type="button"
        >
          <Wrench size={17} />
          Работы
        </button>

        {isOwner && (
          <button
            className={
              tab === "finance"
                ? "reports-tab reports-tab-active"
                : "reports-tab"
            }
            onClick={() => {
              setTab(
                "finance",
              );
            }}
            type="button"
          >
            <Wallet size={17} />
            Финансы
          </button>
        )}

        {isOwner && (
          <button
            className={
              tab === "accruals"
                ? "reports-tab reports-tab-active"
                : "reports-tab"
            }
            onClick={() => {
              setTab(
                "accruals",
              );
            }}
            type="button"
          >
            <UserCheck
              size={17}
            />
            Начисления
          </button>
        )}
      </div>


      {loading &&
      !clients &&
      !works && (
        <div className="reports-loading">
          Загружаем отчёты...
        </div>
      )}


      {tab === "clients" &&
        clients && (
        <section className="reports-content">
          <div className="reports-metrics reports-metrics-two">
            <article className="report-metric-card">
              <span>
                Новые за период
              </span>

              <strong>
                {
                  clients
                    .new_clients_count
                }
              </strong>
            </article>

            <article className="report-metric-card">
              <span>
                Постоянных клиентов сейчас
              </span>

              <strong>
                {
                  clients
                    .regular_clients_count
                }
              </strong>

              <small>
                Постоянный — с четвёртого
                завершённого визита
              </small>
            </article>
          </div>


          <section className="report-section-card">
            <div className="report-section-heading">
              <div>
                <span>
                  За выбранный период
                </span>

                <h2>
                  Источники клиентов
                </h2>
              </div>
            </div>

            {clients.sources.length ===
            0 ? (
              <div className="reports-empty">
                Новых клиентов
                за этот период нет.
              </div>
            ) : (
              <div className="report-source-grid">
                {clients.sources.map(
                  (source) => (
                    <article
                      key={
                        source.source
                      }
                    >
                      <span>
                        {sourceLabels[
                          source.source
                        ] ??
                          source.source}
                      </span>

                      <strong>
                        {source.count}
                      </strong>
                    </article>
                  ),
                )}
              </div>
            )}
          </section>


          <section className="report-section-card">
            <div className="report-section-heading">
              <div>
                <span>
                  Зарегистрированы в периоде
                </span>

                <h2>
                  Новые клиенты
                </h2>
              </div>

              <strong>
                {
                  clients
                    .new_clients_count
                }
              </strong>
            </div>

            {clients.new_clients.length ===
            0 ? (
              <div className="reports-empty">
                Новых клиентов нет.
              </div>
            ) : (
              <div className="report-table-wrap">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>
                        Клиент
                      </th>

                      <th>
                        Источник
                      </th>

                      <th>
                        Дата
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {clients.new_clients.map(
                      (client) => (
                        <tr
                          key={
                            client
                              .client_number
                          }
                        >
                          <td>
                            <strong>
                              {
                                client
                                  .full_name
                              }
                            </strong>

                            <span>
                              Клиент №
                              {
                                client
                                  .client_number
                              }
                            </span>
                          </td>

                          <td>
                            {sourceLabels[
                              client
                                .source
                            ] ??
                              client
                                .source}
                          </td>

                          <td>
                            {formatDateTime(
                              client
                                .created_at,
                            )}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </section>


          <section className="report-section-card">
            <div className="report-section-heading">
              <div>
                <span>
                  Клиенты с 4+ визитами
                </span>

                <h2>
                  Постоянные клиенты
                </h2>
              </div>

              <strong>
                {
                  clients
                    .regular_clients_count
                }
              </strong>
            </div>

            {clients.regular_clients
              .length === 0 ? (
              <div className="reports-empty">
                Пока нет постоянных
                клиентов.
              </div>
            ) : (
              <div className="report-table-wrap">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>
                        Клиент
                      </th>

                      <th>
                        Завершённых визитов
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {clients.regular_clients.map(
                      (client) => (
                        <tr
                          key={
                            client
                              .client_number
                          }
                        >
                          <td>
                            <strong>
                              {
                                client
                                  .full_name
                              }
                            </strong>

                            <span>
                              Клиент №
                              {
                                client
                                  .client_number
                              }
                            </span>
                          </td>

                          <td>
                            {
                              client
                                .visits
                            }
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </section>


          <section className="report-section-card">
            <div className="report-section-heading">
              <div>
                <span>
                  За выбранный период
                </span>

                <h2>
                  Рекомендации клиентов
                </h2>
              </div>

              <strong>
                {
                  clients
                    .referrals
                    .length
                }
              </strong>
            </div>

            {clients.referrals.length ===
            0 ? (
              <div className="reports-empty">
                Клиентов по рекомендации
                за период нет.
              </div>
            ) : (
              <div className="report-table-wrap">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>
                        Новый клиент
                      </th>

                      <th>
                        Кто рекомендовал
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {clients.referrals.map(
                      (item) => (
                        <tr
                          key={
                            item
                              .client_number
                          }
                        >
                          <td>
                            <strong>
                              {
                                item
                                  .client_name
                              }
                            </strong>

                            <span>
                              Клиент №
                              {
                                item
                                  .client_number
                              }
                            </span>
                          </td>

                          <td>
                            <strong>
                              {
                                item
                                  .referred_by_name
                              }
                            </strong>

                            <span>
                              Клиент №
                              {
                                item
                                  .referred_by_client_number
                              }
                            </span>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </section>
      )}


      {tab === "works" &&
        works && (
        <section className="reports-content">
          <div className="reports-metrics reports-metrics-two">
            <article className="report-metric-card">
              <span>
                Работ в отчёте
              </span>

              <strong>
                {works.total}
              </strong>
            </article>

            <article className="report-metric-card">
              <span>
                Сумма работ
              </span>

              <strong className="report-money">
                {formatMoney(
                  works.total_amount,
                )}
              </strong>
            </article>
          </div>


          <section className="report-section-card">
            <div className="report-section-heading">
              <div>
                <span>
                  С {formatDate(
                    works.date_from,
                  )} по {formatDate(
                    works.date_to,
                  )}
                </span>

                <h2>
                  Работы
                </h2>
              </div>
            </div>

            {works.items.length ===
            0 ? (
              <div className="reports-empty">
                Работ за период нет.
              </div>
            ) : (
              <div className="report-table-wrap">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>
                        Работа
                      </th>

                      <th>
                        Заказ-наряд
                      </th>

                      <th>
                        Дата
                      </th>

                      <th>
                        Стоимость
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {works.items.map(
                      (item) => (
                        <tr
                          key={
                            item
                              .work_item_number
                          }
                        >
                          <td>
                            <strong>
                              {
                                item.name
                              }
                            </strong>

                            <span>
                              Работа №
                              {
                                item
                                  .work_item_number
                              }
                            </span>
                          </td>

                          <td>
                            №
                            {
                              item
                                .work_order_number
                            }
                          </td>

                          <td>
                            {formatDateTime(
                              item
                                .recorded_at,
                            )}
                          </td>

                          <td className="report-table-money">
                            {formatMoney(
                              item.price,
                            )}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </section>
      )}


      {tab === "finance" &&
        isOwner &&
        finance && (
        <section className="reports-content">
          <div className="reports-metrics reports-metrics-four">
            <article className="report-metric-card report-metric-primary">
              <span>
                Получено оплат
              </span>

              <strong className="report-money">
                {formatMoney(
                  finance
                    .payments_received,
                )}
              </strong>
            </article>

            <article className="report-metric-card">
              <span>
                Работы
              </span>

              <strong className="report-money">
                {formatMoney(
                  finance
                    .works_total,
                )}
              </strong>
            </article>

            <article className="report-metric-card">
              <span>
                Запчасти СТО
              </span>

              <strong className="report-money">
                {formatMoney(
                  finance
                    .sto_parts_total,
                )}
              </strong>
            </article>

            <article className="report-metric-card report-metric-debt">
              <span>
                Текущая задолженность
              </span>

              <strong className="report-money">
                {formatMoney(
                  finance
                    .current_debt,
                )}
              </strong>

              <small>
                На текущий момент,
                независимо от периода
              </small>
            </article>
          </div>


          <section className="report-section-card">
            <div className="report-section-heading">
              <div>
                <span>
                  Фактически полученные оплаты
                </span>

                <h2>
                  Способы оплаты
                </h2>
              </div>
            </div>

            <div className="report-finance-breakdown">
              <article>
                <span>
                  Наличные
                </span>

                <strong>
                  {formatMoney(
                    finance
                      .cash_received,
                  )}
                </strong>
              </article>

              <article>
                <span>
                  Карта
                </span>

                <strong>
                  {formatMoney(
                    finance
                      .card_received,
                  )}
                </strong>
              </article>

              <article>
                <span>
                  Перевод
                </span>

                <strong>
                  {formatMoney(
                    finance
                      .transfer_received,
                  )}
                </strong>
              </article>
            </div>
          </section>


          <section className="report-section-card">
            <div className="report-section-heading">
              <div>
                <span>
                  Работы + запчасти СТО
                </span>

                <h2>
                  Стоимость ремонта
                  за период
                </h2>
              </div>

              <strong className="report-section-total">
                {formatMoney(
                  finance
                    .repair_total,
                )}
              </strong>
            </div>

            <div className="report-finance-lines">
              <div>
                <span>
                  Работы
                </span>

                <strong>
                  {formatMoney(
                    finance
                      .works_total,
                  )}
                </strong>
              </div>

              <div>
                <span>
                  Запчасти СТО
                </span>

                <strong>
                  {formatMoney(
                    finance
                      .sto_parts_total,
                  )}
                </strong>
              </div>

              <div className="report-finance-line-total">
                <span>
                  Всего
                </span>

                <strong>
                  {formatMoney(
                    finance
                      .repair_total,
                  )}
                </strong>
              </div>
            </div>
          </section>
        </section>
      )}


      {tab === "accruals" &&
        isOwner &&
        accruals && (
        <section className="reports-content">
          <div className="reports-metrics reports-metrics-two">
            <article className="report-metric-card">
              <span>
                Сотрудников в отчёте
              </span>

              <strong>
                {
                  accruals
                    .employees
                    .length
                }
              </strong>
            </article>

            <article className="report-metric-card report-metric-primary">
              <span>
                Всего начислено
              </span>

              <strong className="report-money">
                {formatMoney(
                  accruals
                    .grand_total,
                )}
              </strong>
            </article>
          </div>


          {accruals.employees.length ===
          0 ? (
            <div className="reports-empty reports-empty-card">
              Начислений за период нет.
            </div>
          ) : (
            <div className="report-employee-list">
              {accruals.employees.map(
                (employee) => (
                  <details
                    className="report-employee-card"
                    key={
                      employee
                        .employee_number
                    }
                    open
                  >
                    <summary>
                      <div>
                        <strong>
                          {
                            employee
                              .employee_name
                          }
                        </strong>

                        <span>
                          Сотрудник №
                          {
                            employee
                              .employee_number
                          } · работ:{" "}
                          {
                            employee
                              .works
                              .length
                          }
                        </span>
                      </div>

                      <div className="report-employee-total">
                        <span>
                          Начислено
                        </span>

                        <strong>
                          {formatMoney(
                            employee
                              .total_earnings,
                          )}
                        </strong>
                      </div>
                    </summary>


                    <div className="report-table-wrap">
                      <table className="report-table report-accrual-table">
                        <thead>
                          <tr>
                            <th>
                              Работа
                            </th>

                            <th>
                              Цена
                            </th>

                            <th>
                              Доля
                            </th>

                            <th>
                              База
                            </th>

                            <th>
                              Ставка
                            </th>

                            <th>
                              Начислено
                            </th>
                          </tr>
                        </thead>

                        <tbody>
                          {employee.works.map(
                            (work) => (
                              <tr
                                key={
                                  work
                                    .work_item_number
                                }
                              >
                                <td>
                                  <strong>
                                    {
                                      work
                                        .work_name
                                    }
                                  </strong>

                                  <span>
                                    Заказ №
                                    {
                                      work
                                        .work_order_number
                                    } ·{" "}
                                    {formatDateTime(
                                      work
                                        .recorded_at,
                                    )}
                                  </span>
                                </td>

                                <td>
                                  {formatMoney(
                                    work
                                      .work_price,
                                  )}
                                </td>

                                <td>
                                  {
                                    work
                                      .share_percent
                                  }
                                  %
                                </td>

                                <td>
                                  {formatMoney(
                                    work
                                      .share_base,
                                  )}
                                </td>

                                <td>
                                  {
                                    work
                                      .rate_percent_snapshot
                                  }
                                  %
                                </td>

                                <td className="report-table-money">
                                  {formatMoney(
                                    work
                                      .earning_amount,
                                  )}
                                </td>
                              </tr>
                            ),
                          )}
                        </tbody>
                      </table>
                    </div>


                    <div className="report-employee-footer">
                      <span>
                        База по долям:
                        {" "}
                        <strong>
                          {formatMoney(
                            employee
                              .total_share_base,
                          )}
                        </strong>
                      </span>

                      <span>
                        Начислено:
                        {" "}
                        <strong>
                          {formatMoney(
                            employee
                              .total_earnings,
                          )}
                        </strong>
                      </span>
                    </div>
                  </details>
                ),
              )}
            </div>
          )}
        </section>
      )}
    </section>
  );
}