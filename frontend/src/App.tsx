import {
  Bell,
  Car,
  CheckCircle2,
  ClipboardList,
  FileText,
  LogOut,
  RefreshCw,
  Search,
  ShieldCheck,
  Users,
  Wrench,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";
import type { FormEvent } from "react";

import {
  getCurrentUser,
  login,
  logout,
} from "./api/auth";
import {
  ApiError,
  apiRequest,
} from "./api/client";
import {
  getDashboard,
} from "./api/dashboard";
import "./styles/app.css";
import type {
  CurrentUser,
} from "./types/auth";
import type {
  DashboardResponse,
} from "./types/dashboard";
import type {
  HealthResponse,
} from "./types/health";
import {
  formatDate,
  formatMoney,
  formatTime,
  roleLabel,
  todayIso,
  userInitials,
} from "./utils/format";

type AuthState =
  | "checking"
  | "anonymous"
  | "authenticated";

function App() {
  const [
    authState,
    setAuthState,
  ] = useState<AuthState>(
    "checking",
  );

  const [
    currentUser,
    setCurrentUser,
  ] = useState<CurrentUser | null>(
    null,
  );

  const [
    dashboard,
    setDashboard,
  ] = useState<DashboardResponse | null>(
    null,
  );

  const [
    dashboardLoading,
    setDashboardLoading,
  ] = useState(false);

  const [
    dashboardError,
    setDashboardError,
  ] = useState("");

  const [
    backendStatus,
    setBackendStatus,
  ] = useState<
    "loading" | "online" | "offline"
  >("loading");

  const [
    loginValue,
    setLoginValue,
  ] = useState("andrey");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    loginLoading,
    setLoginLoading,
  ] = useState(false);

  const [
    loginError,
    setLoginError,
  ] = useState("");

  const reportDate = todayIso();

  const loadDashboard =
    useCallback(async () => {
      setDashboardLoading(true);
      setDashboardError("");

      try {
        const data =
          await getDashboard(
            reportDate,
          );

        setDashboard(data);
      } catch (error) {
        if (error instanceof ApiError) {
          setDashboardError(
            error.message,
          );
        } else {
          setDashboardError(
            "Не удалось загрузить рабочую панель.",
          );
        }
      } finally {
        setDashboardLoading(false);
      }
    }, [reportDate]);

  useEffect(() => {
    apiRequest<HealthResponse>(
      "/health",
    )
      .then(() => {
        setBackendStatus("online");
      })
      .catch(() => {
        setBackendStatus("offline");
      });
  }, []);

  useEffect(() => {
    getCurrentUser()
      .then((user) => {
        setCurrentUser(user);
        setAuthState(
          "authenticated",
        );
      })
      .catch((error) => {
        if (
          error instanceof ApiError &&
          error.status === 401
        ) {
          setAuthState(
            "anonymous",
          );
          return;
        }

        setBackendStatus(
          "offline",
        );
        setAuthState(
          "anonymous",
        );
      });
  }, []);

  useEffect(() => {
    if (
      authState ===
      "authenticated"
    ) {
      void loadDashboard();
    }
  }, [
    authState,
    loadDashboard,
  ]);

  async function handleLogin(
    event: FormEvent,
  ) {
    event.preventDefault();

    setLoginLoading(true);
    setLoginError("");

    try {
      const user = await login({
        login: loginValue.trim(),
        password,
      });

      setCurrentUser(user);
      setAuthState(
        "authenticated",
      );
      setPassword("");
      setBackendStatus(
        "online",
      );
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.status === 401) {
          setLoginError(
            "Неверный логин или пароль.",
          );
        } else {
          setLoginError(
            error.message,
          );
        }
      } else {
        setLoginError(
          "Не удалось выполнить вход.",
        );
      }
    } finally {
      setLoginLoading(false);
    }
  }

  async function handleLogout() {
    try {
      await logout();
    } finally {
      setCurrentUser(null);
      setDashboard(null);
      setAuthState(
        "anonymous",
      );
    }
  }

  if (
    authState ===
    "checking"
  ) {
    return (
      <main className="auth-page">
        <section className="auth-loading">
          <div className="auth-logo">
            <Wrench size={30} />
          </div>

          <strong>
            ЦУТ Improvement Auto
          </strong>

          <span>
            Проверяем сессию...
          </span>
        </section>
      </main>
    );
  }

  if (
    authState ===
    "anonymous"
  ) {
    return (
      <main className="auth-page">
        <section className="login-card">
          <div className="login-brand">
            <div className="login-logo">
              <Wrench size={30} />
            </div>

            <div>
              <div className="login-brand-name">
                ЦУТ Improvement Auto
              </div>

              <div className="login-brand-note">
                Система управления СТО
              </div>
            </div>
          </div>

          <div className="login-heading">
            <span>
              Вход в систему
            </span>

            <h1>
              Рабочее место
            </h1>

            <p>
              Введите данные своей
              учётной записи.
            </p>
          </div>

          <form
            className="login-form"
            onSubmit={
              handleLogin
            }
          >
            <label>
              <span>
                Логин
              </span>

              <input
                autoComplete="username"
                autoFocus
                value={loginValue}
                onChange={(event) => {
                  setLoginValue(
                    event.target.value,
                  );
                }}
              />
            </label>

            <label>
              <span>
                Пароль
              </span>

              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => {
                  setPassword(
                    event.target.value,
                  );
                }}
              />
            </label>

            {loginError && (
              <div className="login-error">
                {loginError}
              </div>
            )}

            <button
              className="primary-button"
              disabled={
                loginLoading ||
                !loginValue.trim() ||
                !password
              }
              type="submit"
            >
              {loginLoading
                ? "Входим..."
                : "Войти"}
            </button>
          </form>

          <div className="login-footer">
            <div
              className={
                `connection-status ${
                  backendStatus
                }`
              }
            >
              <span className="status-dot" />

              {backendStatus ===
                "online" &&
                "Сервер подключён"}

              {backendStatus ===
                "offline" &&
                "Нет связи с сервером"}

              {backendStatus ===
                "loading" &&
                "Проверка сервера..."}
            </div>
          </div>
        </section>
      </main>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Wrench size={24} />
          </div>

          <div>
            <div className="brand-name">
              ЦУТ
            </div>

            <div className="brand-subtitle">
              Improvement Auto
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button
            className=
              "nav-item nav-item-active"
            type="button"
          >
            <ClipboardList
              size={19}
            />
            Главная
          </button>

          <button
            className="nav-item"
            type="button"
          >
            <Users size={19} />
            Клиенты
          </button>

          <button
            className="nav-item"
            type="button"
          >
            <Car size={19} />
            Автомобили
          </button>

          <button
            className="nav-item"
            type="button"
          >
            <Wrench size={19} />
            Заказ-наряды
          </button>

          <button
            className="nav-item"
            type="button"
          >
            <Bell size={19} />
            Уведомления
          </button>

          <button
            className="nav-item"
            type="button"
          >
            <FileText size={19} />
            Отчёты
          </button>
        </nav>

        <div className="sidebar-footer">
          <div
            className={
              `connection-status ${
                backendStatus
              }`
            }
          >
            <span className="status-dot" />

            {backendStatus ===
              "online" &&
              "Сервер подключён"}

            {backendStatus ===
              "offline" &&
              "Нет связи с сервером"}

            {backendStatus ===
              "loading" &&
              "Проверка сервера..."}
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="page-eyebrow">
              {formatDate(
                reportDate,
              )}
            </div>

            <h1>
              Рабочая панель СТО
            </h1>
          </div>

          <div className="topbar-actions">
            <button
              className="search-button"
              type="button"
            >
              <Search size={18} />
              Поиск
            </button>

            <div className="user-menu">
              <div className="user-chip">
                {userInitials(
                  currentUser?.login ??
                    "",
                )}
              </div>

              <div className="user-info">
                <strong>
                  {currentUser?.login}
                </strong>

                <span>
                  {roleLabel(
                    currentUser?.role ??
                      "",
                  )}
                </span>
              </div>

              <button
                aria-label="Выйти"
                className=
                  "logout-button"
                onClick={
                  handleLogout
                }
                title="Выйти"
                type="button"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </header>

        <section className="welcome-panel">
          <div>
            <div className="welcome-label">
              <ShieldCheck
                size={15}
              />
              Рабочая смена
            </div>

            <h2>
              Что требует внимания
              сегодня
            </h2>

            <p>
              Здесь собрана текущая
              ситуация по записям,
              автомобилям в работе,
              готовым заказам и
              задолженности.
            </p>
          </div>

          <button
            className="refresh-button"
            disabled={
              dashboardLoading
            }
            onClick={() => {
              void loadDashboard();
            }}
            type="button"
          >
            <RefreshCw
              className={
                dashboardLoading
                  ? "spin"
                  : ""
              }
              size={20}
            />

            Обновить
          </button>
        </section>

        {dashboardError && (
          <div className=
            "dashboard-error"
          >
            {dashboardError}
          </div>
        )}

        <section className="metric-grid">
          <article className="metric-card">
            <span className="metric-label">
              Записи сегодня
            </span>

            <strong>
              {dashboardLoading &&
              !dashboard
                ? "…"
                : dashboard
                  ?.scheduled_count ??
                  0}
            </strong>

            <span className="metric-note">
              не приехали:{" "}
              {dashboard
                ?.no_show_count ??
                0}
            </span>
          </article>

          <article className="metric-card">
            <span className="metric-label">
              В работе
            </span>

            <strong>
              {dashboardLoading &&
              !dashboard
                ? "…"
                : dashboard
                  ?.in_progress_count ??
                  0}
            </strong>

            <span className="metric-note">
              заказ-наряды
            </span>
          </article>

          <article className="metric-card">
            <span className="metric-label">
              Готовы к выдаче
            </span>

            <strong>
              {dashboardLoading &&
              !dashboard
                ? "…"
                : dashboard
                  ?.ready_count ??
                  0}
            </strong>

            <span className="metric-note">
              автомобилей
            </span>
          </article>

          <article className="metric-card">
            <span className="metric-label">
              Задолженность
            </span>

            <strong className=
              "money-value"
            >
              {dashboardLoading &&
              !dashboard
                ? "…"
                : formatMoney(
                    dashboard
                      ?.debt_total ??
                      "0",
                  )}
            </strong>

            <span className="metric-note">
              текущая
            </span>
          </article>
        </section>

        <section className="workspace-grid">
          <article className="workspace-card">
            <div className="card-header">
              <div>
                <span className="card-kicker">
                  Сегодня
                </span>

                <h3>
                  Записи клиентов
                </h3>
              </div>

              <button
                className=
                  "secondary-button"
                type="button"
              >
                Новая запись
              </button>
            </div>

            {dashboardLoading &&
            !dashboard ? (
              <div className=
                "empty-state"
              >
                Загружаем записи...
              </div>
            ) : dashboard &&
              dashboard
                .appointments_today
                .length > 0 ? (
              <div className=
                "appointment-list"
              >
                {dashboard
                  .appointments_today
                  .map(
                    (appointment) => (
                      <div
                        className=
                          "appointment-row"
                        key={
                          appointment
                            .appointment_number
                        }
                      >
                        <div className=
                          "appointment-time"
                        >
                          {formatTime(
                            appointment
                              .appointment_time,
                          )}
                        </div>

                        <div className=
                          "appointment-main"
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
                                .vehicle_name
                            }
                            {appointment
                              .license_plate
                              ? ` · ${
                                  appointment
                                    .license_plate
                                }`
                              : ""}
                          </span>

                          <small>
                            {
                              appointment
                                .reason
                            }
                          </small>
                        </div>

                        <div className=
                          "appointment-number"
                        >
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
              <div className=
                "empty-state"
              >
                <ClipboardList
                  size={28}
                />

                <div>
                  <strong>
                    На сегодня записей
                    нет
                  </strong>

                  <p>
                    Здесь появятся
                    записи клиентов на
                    выбранный день.
                  </p>
                </div>
              </div>
            )}
          </article>

          <article className=
            "workspace-card"
          >
            <div className="card-header">
              <div>
                <span className=
                  "card-kicker"
                >
                  Состояние ремонта
                </span>

                <h3>
                  Автомобили
                </h3>
              </div>
            </div>

            <div className=
              "order-summary-list"
            >
              <div className=
                "order-summary-item"
              >
                <span>
                  В работе
                </span>

                <strong>
                  {dashboard
                    ?.in_progress_count ??
                    0}
                </strong>
              </div>

              <div className=
                "order-summary-item"
              >
                <span>
                  Готовы к выдаче
                </span>

                <strong>
                  {dashboard
                    ?.ready_count ??
                    0}
                </strong>
              </div>

              <div className=
                "order-summary-item"
              >
                <span>
                  Долги
                </span>

                <strong>
                  {dashboard
                    ?.debts
                    .length ??
                    0}
                </strong>
              </div>
            </div>

            {dashboard &&
              dashboard.ready.length >
                0 && (
                <div className=
                  "ready-list"
                >
                  {dashboard.ready.map(
                    (order) => (
                      <div
                        className=
                          "ready-row"
                        key={
                          order
                            .work_order_number
                        }
                      >
                        <CheckCircle2
                          size={17}
                        />

                        <div>
                          <strong>
                            Заказ-наряд №
                            {
                              order
                                .work_order_number
                            }
                          </strong>

                          <span>
                            {
                              order
                                .vehicle_name
                            }
                          </span>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}
          </article>
        </section>
      </main>
    </div>
  );
}

export default App;