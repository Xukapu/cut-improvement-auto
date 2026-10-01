import {
  Bell,
  CalendarClock,
  Car,
  ClipboardList,
  FileText,
  LogOut,
  Search,
  Settings as SettingsIcon,
  Users,
  Wrench,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";
import type {
  FormEvent,
} from "react";

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
import {
  DashboardAppointmentsCard,
} from "./components/DashboardAppointmentsCard";
import {
  DashboardAttentionCard,
} from "./components/DashboardAttentionCard";
import {
  DashboardVehicleStateCard,
} from "./components/DashboardVehicleStateCard";
import {
  AppointmentsPage,
} from "./pages/AppointmentsPage";
import {
  ClientsPage,
} from "./pages/ClientsPage";
import {
  SettingsPage,
} from "./pages/SettingsPage";
import {
  VehiclesPage,
} from "./pages/VehiclesPage";
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
  roleLabel,
  todayIso,
  userInitials,
} from "./utils/format";


type AuthState =
  | "checking"
  | "anonymous"
  | "authenticated";


type Section =
  | "dashboard"
  | "clients"
  | "vehicles"
  | "appointments"
  | "workorders"
  | "notifications"
  | "reports"
  | "settings";


const sectionTitles: Record<
  Section,
  string
> = {
  dashboard: "Рабочая панель СТО",
  clients: "Клиенты",
  vehicles: "Автомобили",
  appointments: "Записи",
  workorders: "Заказ-наряды",
  notifications: "Уведомления",
  reports: "Отчёты",
  settings: "Настройки",
};


function App() {
  const [
    authState,
    setAuthState,
  ] = useState<AuthState>("checking");

  const [
    currentUser,
    setCurrentUser,
  ] = useState<CurrentUser | null>(
    null,
  );

  const [
    section,
    setSection,
  ] = useState<Section>(
    "dashboard",
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
        setDashboardError(
          error instanceof ApiError
            ? error.message
            : "Не удалось загрузить рабочую панель.",
        );
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
          setAuthState("anonymous");
          return;
        }

        setBackendStatus("offline");
        setAuthState("anonymous");
      });
  }, []);


  useEffect(() => {
    if (
      authState !==
      "authenticated"
    ) {
      return;
    }

    let active = true;

    getDashboard(reportDate)
      .then((data) => {
        if (!active) {
          return;
        }

        setDashboard(data);
        setDashboardError("");
        setDashboardLoading(false);
      })
      .catch((error) => {
        if (!active) {
          return;
        }

        setDashboardError(
          error instanceof ApiError
            ? error.message
            : "Не удалось загрузить рабочую панель.",
        );

        setDashboardLoading(false);
      });

    return () => {
      active = false;
    };
  }, [
    authState,
    reportDate,
  ]);


  async function handleLogin(
    event: FormEvent,
  ) {
    event.preventDefault();

    setLoginLoading(true);
    setLoginError("");

    try {
      const user = await login({
        login:
          loginValue.trim(),
        password,
      });

      setCurrentUser(user);
      setAuthState(
        "authenticated",
      );
      setPassword("");
      setBackendStatus("online");
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.status === 401
      ) {
        setLoginError(
          "Неверный логин или пароль.",
        );
      } else if (
        error instanceof ApiError
      ) {
        setLoginError(
          error.message,
        );
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
      setSection("dashboard");
      setAuthState("anonymous");
    }
  }


  function navClass(
    target: Section,
  ): string {
    return section === target
      ? "nav-item nav-item-active"
      : "nav-item";
  }


  if (
    authState === "checking"
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
    authState === "anonymous"
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
            onSubmit={handleLogin}
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
                autoComplete="current-password"
                type="password"
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
            className={navClass(
              "dashboard",
            )}
            onClick={() => {
              setSection(
                "dashboard",
              );
            }}
            type="button"
          >
            <ClipboardList
              size={19}
            />
            Главная
          </button>

          <button
            className={navClass(
              "clients",
            )}
            onClick={() => {
              setSection("clients");
            }}
            type="button"
          >
            <Users size={19} />
            Клиенты
          </button>

          <button
            className={navClass(
              "vehicles",
            )}
            onClick={() => {
              setSection("vehicles");
            }}
            type="button"
          >
            <Car size={19} />
            Автомобили
          </button>

          <button
            className={navClass(
              "appointments",
            )}
            onClick={() => {
              setSection(
                "appointments",
              );
            }}
            type="button"
          >
            <CalendarClock
              size={19}
            />
            Записи
          </button>

          <button
            className={navClass(
              "workorders",
            )}
            onClick={() => {
              setSection(
                "workorders",
              );
            }}
            type="button"
          >
            <Wrench size={19} />
            Заказ-наряды
          </button>

          <button
            className={navClass(
              "notifications",
            )}
            onClick={() => {
              setSection(
                "notifications",
              );
            }}
            type="button"
          >
            <Bell size={19} />
            Уведомления
          </button>

          <button
            className={navClass(
              "reports",
            )}
            onClick={() => {
              setSection("reports");
            }}
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
              {
                sectionTitles[
                  section
                ]
              }
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
                  {currentUser
                    ?.full_name ||
                    currentUser
                      ?.login}
                </strong>

                <span>
                  {roleLabel(
                    currentUser?.role ??
                      "",
                  )}
                </span>
              </div>

              <button
                aria-label="Настройки"
                className={
                  section ===
                  "settings"
                    ? "settings-top-button settings-top-button-active"
                    : "settings-top-button"
                }
                onClick={() => {
                  setSection(
                    "settings",
                  );
                }}
                title="Настройки"
                type="button"
              >
                <SettingsIcon
                  size={18}
                />
              </button>

              <button
                aria-label="Выйти"
                className="logout-button"
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


        {section ===
          "dashboard" && (
          <>
            <DashboardAttentionCard
              dashboard={dashboard}
              loading={
                dashboardLoading
              }
              onRefresh={() => {
                void loadDashboard();
              }}
            />

            {dashboardError && (
              <div className="dashboard-error">
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
                  {dashboard
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
                  {dashboard
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

                <strong className="money-value">
                  {formatMoney(
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
              <DashboardAppointmentsCard
                onOpenAppointments={() => {
                  setSection(
                    "appointments",
                  );
                }}
              />

              <DashboardVehicleStateCard
                dashboard={dashboard}
              />
            </section>
          </>
        )}


        {section === "clients" &&
          currentUser && (
            <ClientsPage
              currentUser={
                currentUser
              }
            />
          )}


        {section ===
          "vehicles" && (
          <VehiclesPage />
        )}


        {section ===
          "appointments" && (
          <AppointmentsPage />
        )}


        {section ===
          "settings" &&
          currentUser && (
            <SettingsPage
              currentUser={
                currentUser
              }
              onUserChanged={
                setCurrentUser
              }
            />
          )}


        {(section ===
          "workorders" ||
          section ===
            "notifications" ||
          section ===
            "reports") && (
          <section className="placeholder-page">
            <Wrench size={36} />

            <h2>
              Раздел уже на очереди
            </h2>

            <p>
              Backend для него уже
              существует. Интерфейс
              подключим следующим
              широким блоком.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}


export default App;