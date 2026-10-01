import {
  Archive,
  KeyRound,
  Plus,
  RotateCcw,
  Save,
  ShieldCheck,
  Trash2,
  UserRound,
  Users,
  X,
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
  archiveEmployeeAccess,
  changePassword,
  createEmployeeAccess,
  getProfile,
  listEmployeeAccess,
  restoreEmployeeAccess,
  updateEmployeeAccess,
  updateProfile,
} from "../api/account";
import {
  getCurrentUser,
} from "../api/auth";
import {
  ApiError,
} from "../api/client";
import type {
  EmployeeAccess,
  EmployeeAccessCreatePayload,
  EmployeeAccessUpdatePayload,
} from "../types/account";
import type {
  CurrentUser,
  UserRole,
} from "../types/auth";


type Props = {
  currentUser: CurrentUser;

  onUserChanged: (
    user: CurrentUser,
  ) => void;
};


type SettingsTab =
  | "profile"
  | "employees"
  | "security";


type EmployeeFilter =
  | "active"
  | "access"
  | "no_access"
  | "archive";


type EmployeeForm = {
  full_name: string;
  rate_percent: string;

  is_active: boolean;
  grant_access: boolean;

  login: string;
  role: UserRole;

  phone: string;
  temporary_password: string;
};


const roleNames: Record<
  UserRole,
  string
> = {
  owner: "Владелец",
  admin: "Администратор",
  mechanic: "Механик",
  tech_admin: "Служебная роль",
};


const emptyEmployeeForm:
  EmployeeForm = {
    full_name: "",
    rate_percent: "0",

    is_active: true,
    grant_access: false,

    login: "",
    role: "mechanic",

    phone: "",
    temporary_password: "",
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


export function SettingsPage({
  currentUser,
  onUserChanged,
}: Props) {
  const owner =
    currentUser.role === "owner";

  const [
    tab,
    setTab,
  ] = useState<SettingsTab>(
    "profile",
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    pageError,
    setPageError,
  ] = useState("");


  const [
    firstName,
    setFirstName,
  ] = useState("");

  const [
    lastName,
    setLastName,
  ] = useState("");

  const [
    phone,
    setPhone,
  ] = useState("");

  const [
    profileSaving,
    setProfileSaving,
  ] = useState(false);

  const [
    profileMessage,
    setProfileMessage,
  ] = useState("");


  const [
    currentPassword,
    setCurrentPassword,
  ] = useState("");

  const [
    newPassword,
    setNewPassword,
  ] = useState("");

  const [
    passwordConfirm,
    setPasswordConfirm,
  ] = useState("");

  const [
    passwordSaving,
    setPasswordSaving,
  ] = useState(false);

  const [
    passwordMessage,
    setPasswordMessage,
  ] = useState("");


  const [
    employees,
    setEmployees,
  ] = useState<EmployeeAccess[]>(
    [],
  );

  const [
    employeeFilter,
    setEmployeeFilter,
  ] = useState<EmployeeFilter>(
    "active",
  );

  const [
    employeesLoading,
    setEmployeesLoading,
  ] = useState(false);

  const [
    employeesError,
    setEmployeesError,
  ] = useState("");

  const [
    actionEmployee,
    setActionEmployee,
  ] = useState<number | null>(
    null,
  );


  const [
    showCreateEmployee,
    setShowCreateEmployee,
  ] = useState(false);

  const [
    createForm,
    setCreateForm,
  ] = useState<EmployeeForm>({
    ...emptyEmployeeForm,
  });

  const [
    createSaving,
    setCreateSaving,
  ] = useState(false);


  const [
    editingEmployee,
    setEditingEmployee,
  ] = useState<EmployeeAccess | null>(
    null,
  );

  const [
    editForm,
    setEditForm,
  ] = useState<EmployeeForm>({
    ...emptyEmployeeForm,
  });

  const [
    editSaving,
    setEditSaving,
  ] = useState(false);


  const activeCount = useMemo(
    () =>
      employees.filter(
        (employee) =>
          !employee.archived,
      ).length,
    [employees],
  );


  const accessCount = useMemo(
    () =>
      employees.filter(
        (employee) =>
          !employee.archived &&
          employee.access_enabled,
      ).length,
    [employees],
  );


  const noAccessCount = useMemo(
    () =>
      employees.filter(
        (employee) =>
          !employee.archived &&
          !employee.access_enabled,
      ).length,
    [employees],
  );


  const archiveCount = useMemo(
    () =>
      employees.filter(
        (employee) =>
          employee.archived,
      ).length,
    [employees],
  );


  const visibleEmployees = useMemo(
    () => {
      if (
        employeeFilter ===
        "archive"
      ) {
        return employees.filter(
          (employee) =>
            employee.archived,
        );
      }

      if (
        employeeFilter ===
        "access"
      ) {
        return employees.filter(
          (employee) =>
            !employee.archived &&
            employee.access_enabled,
        );
      }

      if (
        employeeFilter ===
        "no_access"
      ) {
        return employees.filter(
          (employee) =>
            !employee.archived &&
            !employee.access_enabled,
        );
      }

      return employees.filter(
        (employee) =>
          !employee.archived,
      );
    },
    [
      employees,
      employeeFilter,
    ],
  );


  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setPageError("");

      try {
        const profile =
          await getProfile();

        if (!active) {
          return;
        }

        setFirstName(
          profile.first_name ?? "",
        );

        setLastName(
          profile.last_name ?? "",
        );

        setPhone(
          profile.phone ?? "",
        );
      } catch (error) {
        if (active) {
          setPageError(
            errorText(
              error,
              "Не удалось загрузить настройки.",
            ),
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, []);


  useEffect(() => {
    if (
      !owner ||
      tab !== "employees"
    ) {
      return;
    }

    let active = true;

    async function loadEmployees() {
      setEmployeesLoading(true);
      setEmployeesError("");

      try {
        const data =
          await listEmployeeAccess();

        if (active) {
          setEmployees(data);
        }
      } catch (error) {
        if (active) {
          setEmployeesError(
            errorText(
              error,
              "Не удалось загрузить сотрудников.",
            ),
          );
        }
      } finally {
        if (active) {
          setEmployeesLoading(false);
        }
      }
    }

    void loadEmployees();

    return () => {
      active = false;
    };
  }, [
    owner,
    tab,
  ]);


  async function refreshEmployees() {
    if (!owner) {
      return;
    }

    setEmployeesLoading(true);
    setEmployeesError("");

    try {
      const data =
        await listEmployeeAccess();

      setEmployees(data);
    } catch (error) {
      setEmployeesError(
        errorText(
          error,
          "Не удалось загрузить сотрудников.",
        ),
      );
    } finally {
      setEmployeesLoading(false);
    }
  }


  async function handleProfileSave(
    event: FormEvent,
  ) {
    event.preventDefault();

    const cleanFirst =
      firstName.trim();

    const cleanLast =
      lastName.trim();

    const cleanPhone =
      phone.trim();

    setPageError("");
    setProfileMessage("");

    if (
      !cleanFirst ||
      !cleanLast
    ) {
      setPageError(
        "Укажите имя и фамилию.",
      );

      return;
    }

    if (
      cleanPhone.length < 5
    ) {
      setPageError(
        "Укажите номер телефона.",
      );

      return;
    }

    setProfileSaving(true);

    try {
      await updateProfile({
        first_name: cleanFirst,
        last_name: cleanLast,
        phone: cleanPhone,
      });

      const user =
        await getCurrentUser();

      onUserChanged(user);

      setProfileMessage(
        "Данные профиля сохранены.",
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось сохранить профиль.",
        ),
      );
    } finally {
      setProfileSaving(false);
    }
  }


  async function handlePasswordSave(
    event: FormEvent,
  ) {
    event.preventDefault();

    setPageError("");
    setPasswordMessage("");

    if (!currentPassword) {
      setPageError(
        "Введите текущий пароль.",
      );

      return;
    }

    if (
      newPassword.length < 12
    ) {
      setPageError(
        "Новый пароль должен содержать минимум 12 символов.",
      );

      return;
    }

    if (
      newPassword !==
      passwordConfirm
    ) {
      setPageError(
        "Новые пароли не совпадают.",
      );

      return;
    }

    setPasswordSaving(true);

    try {
      const result =
        await changePassword(
          currentPassword,
          newPassword,
        );

      setCurrentPassword("");
      setNewPassword("");
      setPasswordConfirm("");

      setPasswordMessage(
        result.message,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось изменить пароль.",
        ),
      );
    } finally {
      setPasswordSaving(false);
    }
  }


  async function handleCreateEmployee(
    event: FormEvent,
  ) {
    event.preventDefault();

    setEmployeesError("");

    const fullName =
      createForm.full_name.trim();

    if (!fullName) {
      setEmployeesError(
        "Укажите имя сотрудника.",
      );

      return;
    }

    if (
      createForm.grant_access &&
      !createForm.login.trim()
    ) {
      setEmployeesError(
        "Для доступа укажите логин.",
      );

      return;
    }

    if (
      createForm.grant_access &&
      createForm
        .temporary_password
        .length < 12
    ) {
      setEmployeesError(
        "Временный пароль должен содержать минимум 12 символов.",
      );

      return;
    }

    const payload:
      EmployeeAccessCreatePayload = {
        full_name: fullName,
        rate_percent:
          createForm.rate_percent,
        grant_access:
          createForm.grant_access,
        role: createForm.role,
        phone:
          createForm.phone.trim() ||
          null,
      };

    if (
      createForm.grant_access
    ) {
      payload.login =
        createForm.login.trim();

      payload.temporary_password =
        createForm
          .temporary_password;
    }

    setCreateSaving(true);

    try {
      await createEmployeeAccess(
        payload,
      );

      setCreateForm({
        ...emptyEmployeeForm,
      });

      setShowCreateEmployee(
        false,
      );

      setEmployeeFilter(
        "active",
      );

      await refreshEmployees();
    } catch (error) {
      setEmployeesError(
        errorText(
          error,
          "Не удалось создать сотрудника.",
        ),
      );
    } finally {
      setCreateSaving(false);
    }
  }


  function openEmployeeEditor(
    employee: EmployeeAccess,
  ) {
    setEditingEmployee(
      employee,
    );

    setEditForm({
      full_name:
        employee.full_name,

      rate_percent:
        String(
          employee
            .current_rate_percent,
        ),

      is_active:
        employee.is_active,

      grant_access:
        employee.access_enabled,

      login:
        employee.login ?? "",

      role:
        employee.role ??
        "mechanic",

      phone:
        employee.phone ?? "",

      temporary_password: "",
    });

    setEmployeesError("");
  }


  async function handleEmployeeSave(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!editingEmployee) {
      return;
    }

    setEmployeesError("");

    if (
      !editForm.full_name.trim()
    ) {
      setEmployeesError(
        "Укажите имя сотрудника.",
      );

      return;
    }

    if (
      editForm.grant_access &&
      !editingEmployee
        .access_exists &&
      !editForm.login.trim()
    ) {
      setEmployeesError(
        "Для нового доступа укажите логин.",
      );

      return;
    }

    if (
      editForm.grant_access &&
      !editingEmployee
        .access_exists &&
      editForm
        .temporary_password
        .length < 12
    ) {
      setEmployeesError(
        "Для нового доступа нужен временный пароль минимум 12 символов.",
      );

      return;
    }

    if (
      editForm
        .temporary_password &&
      editForm
        .temporary_password
        .length < 12
    ) {
      setEmployeesError(
        "Новый пароль должен содержать минимум 12 символов.",
      );

      return;
    }

    const payload:
      EmployeeAccessUpdatePayload = {
        full_name:
          editForm.full_name.trim(),

        rate_percent:
          editForm.rate_percent,

        is_active:
          editForm.is_active,

        grant_access:
          editForm.grant_access,
    };

    if (
      editingEmployee
        .access_exists ||
      editForm.grant_access
    ) {
      payload.login =
        editForm.login.trim() ||
        null;

      payload.phone =
        editForm.phone.trim() ||
        null;

      if (
        editingEmployee.role !==
        "tech_admin"
      ) {
        payload.role =
          editForm.role;
      }
    }

    if (
      editForm
        .temporary_password
    ) {
      payload.temporary_password =
        editForm
          .temporary_password;
    }

    setEditSaving(true);

    try {
      await updateEmployeeAccess(
        editingEmployee
          .employee_number,
        payload,
      );

      setEditingEmployee(null);

      await refreshEmployees();
    } catch (error) {
      setEmployeesError(
        errorText(
          error,
          "Не удалось сохранить сотрудника.",
        ),
      );
    } finally {
      setEditSaving(false);
    }
  }


  async function handleArchive(
    employee: EmployeeAccess,
  ) {
    const approved =
      window.confirm(
        `Удалить сотрудника «${employee.full_name}» из активной системы?\n\n` +
        "Его работы, начисления, ставки и история останутся. " +
        "Сотрудник будет перемещён в архив.",
      );

    if (!approved) {
      return;
    }

    setActionEmployee(
      employee.employee_number,
    );

    setEmployeesError("");

    try {
      await archiveEmployeeAccess(
        employee.employee_number,
      );

      if (
        editingEmployee
          ?.employee_number ===
        employee.employee_number
      ) {
        setEditingEmployee(null);
      }

      await refreshEmployees();
    } catch (error) {
      setEmployeesError(
        errorText(
          error,
          "Не удалось удалить сотрудника.",
        ),
      );
    } finally {
      setActionEmployee(null);
    }
  }


  async function handleRestore(
    employee: EmployeeAccess,
  ) {
    setActionEmployee(
      employee.employee_number,
    );

    setEmployeesError("");

    try {
      await restoreEmployeeAccess(
        employee.employee_number,
      );

      await refreshEmployees();
    } catch (error) {
      setEmployeesError(
        errorText(
          error,
          "Не удалось восстановить сотрудника.",
        ),
      );
    } finally {
      setActionEmployee(null);
    }
  }


  if (loading) {
    return (
      <section className="settings-loading">
        Загружаем настройки...
      </section>
    );
  }


  return (
    <section className="settings-page">
      <div className="settings-tabs">
        <button
          className={
            tab === "profile"
              ? "settings-tab settings-tab-active"
              : "settings-tab"
          }
          onClick={() => {
            setTab("profile");
            setPageError("");
          }}
          type="button"
        >
          <UserRound size={17} />
          Мой профиль
        </button>

        {owner && (
          <button
            className={
              tab === "employees"
                ? "settings-tab settings-tab-active"
                : "settings-tab"
            }
            onClick={() => {
              setTab("employees");
              setPageError("");
            }}
            type="button"
          >
            <Users size={17} />
            Сотрудники и доступ
          </button>
        )}

        <button
          className={
            tab === "security"
              ? "settings-tab settings-tab-active"
              : "settings-tab"
          }
          onClick={() => {
            setTab("security");
            setPageError("");
          }}
          type="button"
        >
          <ShieldCheck size={17} />
          Безопасность
        </button>
      </div>


      {pageError && (
        <div className="settings-error">
          {pageError}
        </div>
      )}


      {tab === "profile" && (
        <div className="settings-columns">
          <form
            className="settings-card"
            onSubmit={
              handleProfileSave
            }
          >
            <div className="settings-card-heading">
              <div>
                <span>
                  Личные данные
                </span>

                <h2>
                  Мой профиль
                </h2>
              </div>

              <UserRound size={22} />
            </div>

            <div className="settings-form-grid">
              <label>
                <span>Имя</span>

                <input
                  value={firstName}
                  onChange={(event) => {
                    setFirstName(
                      event.target.value,
                    );
                  }}
                />
              </label>

              <label>
                <span>Фамилия</span>

                <input
                  value={lastName}
                  onChange={(event) => {
                    setLastName(
                      event.target.value,
                    );
                  }}
                />
              </label>

              <label className="settings-field-wide">
                <span>
                  Номер телефона
                </span>

                <input
                  autoComplete="tel"
                  placeholder="+7 ..."
                  value={phone}
                  onChange={(event) => {
                    setPhone(
                      event.target.value,
                    );
                  }}
                />
              </label>
            </div>

            <div className="settings-account-note">
              <span>
                Логин
              </span>

              <strong>
                {currentUser.login}
              </strong>

              <span>
                Роль
              </span>

              <strong>
                {
                  roleNames[
                    currentUser.role
                  ]
                }
              </strong>
            </div>

            {profileMessage && (
              <div className="settings-success">
                {profileMessage}
              </div>
            )}

            <div className="settings-actions">
              <button
                className="primary-button"
                disabled={
                  profileSaving
                }
                type="submit"
              >
                <Save size={16} />

                {profileSaving
                  ? "Сохраняем..."
                  : "Сохранить данные"}
              </button>
            </div>
          </form>


          <form
            className="settings-card"
            onSubmit={
              handlePasswordSave
            }
          >
            <div className="settings-card-heading">
              <div>
                <span>
                  Доступ
                </span>

                <h2>
                  Изменить пароль
                </h2>
              </div>

              <KeyRound size={22} />
            </div>

            <p className="settings-description">
              Для смены пароля сначала
              подтвердите действующий
              пароль.
            </p>

            <div className="settings-form-grid">
              <label className="settings-field-wide">
                <span>
                  Текущий пароль
                </span>

                <input
                  autoComplete="current-password"
                  type="password"
                  value={
                    currentPassword
                  }
                  onChange={(event) => {
                    setCurrentPassword(
                      event.target.value,
                    );
                  }}
                />
              </label>

              <label className="settings-field-wide">
                <span>
                  Новый пароль
                </span>

                <input
                  autoComplete="new-password"
                  minLength={12}
                  type="password"
                  value={newPassword}
                  onChange={(event) => {
                    setNewPassword(
                      event.target.value,
                    );
                  }}
                />
              </label>

              <label className="settings-field-wide">
                <span>
                  Повторите новый пароль
                </span>

                <input
                  autoComplete="new-password"
                  minLength={12}
                  type="password"
                  value={
                    passwordConfirm
                  }
                  onChange={(event) => {
                    setPasswordConfirm(
                      event.target.value,
                    );
                  }}
                />
              </label>
            </div>

            <div className="settings-hint">
              Минимум 12 символов.
              После успешной смены
              остальные старые сессии
              будут завершены.
            </div>

            {passwordMessage && (
              <div className="settings-success">
                {passwordMessage}
              </div>
            )}

            <div className="settings-actions">
              <button
                className="primary-button"
                disabled={
                  passwordSaving ||
                  !currentPassword ||
                  !newPassword ||
                  !passwordConfirm
                }
                type="submit"
              >
                <KeyRound size={16} />

                {passwordSaving
                  ? "Меняем..."
                  : "Изменить пароль"}
              </button>
            </div>
          </form>
        </div>
      )}


      {tab === "employees" &&
        owner && (
        <div className="settings-employees">
          <div className="settings-section-toolbar">
            <div>
              <span className="card-kicker">
                Персонал
              </span>

              <h2>
                Сотрудники и доступ
              </h2>

              <p>
                Удаление сотрудника
                переносит его в архив.
                История работ и начислений
                сохраняется.
              </p>
            </div>

            <button
              className="primary-button"
              onClick={() => {
                setShowCreateEmployee(
                  true,
                );

                setCreateForm({
                  ...emptyEmployeeForm,
                });
              }}
              type="button"
            >
              <Plus size={17} />
              Новый сотрудник
            </button>
          </div>


          <div className="employee-filter-bar">
            <button
              className={
                employeeFilter ===
                "active"
                  ? "employee-filter employee-filter-active"
                  : "employee-filter"
              }
              onClick={() => {
                setEmployeeFilter(
                  "active",
                );
              }}
              type="button"
            >
              Активные
              <span>
                {activeCount}
              </span>
            </button>

            <button
              className={
                employeeFilter ===
                "access"
                  ? "employee-filter employee-filter-active"
                  : "employee-filter"
              }
              onClick={() => {
                setEmployeeFilter(
                  "access",
                );
              }}
              type="button"
            >
              С доступом
              <span>
                {accessCount}
              </span>
            </button>

            <button
              className={
                employeeFilter ===
                "no_access"
                  ? "employee-filter employee-filter-active"
                  : "employee-filter"
              }
              onClick={() => {
                setEmployeeFilter(
                  "no_access",
                );
              }}
              type="button"
            >
              Без доступа
              <span>
                {noAccessCount}
              </span>
            </button>

            <button
              className={
                employeeFilter ===
                "archive"
                  ? "employee-filter employee-filter-active"
                  : "employee-filter"
              }
              onClick={() => {
                setEmployeeFilter(
                  "archive",
                );
              }}
              type="button"
            >
              <Archive size={14} />
              Архив
              <span>
                {archiveCount}
              </span>
            </button>
          </div>


          {employeesError && (
            <div className="settings-error">
              {employeesError}
            </div>
          )}


          {showCreateEmployee && (
            <form
              className="settings-card settings-editor-card"
              onSubmit={
                handleCreateEmployee
              }
            >
              <div className="settings-card-heading">
                <div>
                  <span>
                    Новый сотрудник
                  </span>

                  <h2>
                    Карточка сотрудника
                  </h2>
                </div>

                <button
                  aria-label="Закрыть"
                  className="settings-close"
                  onClick={() => {
                    setShowCreateEmployee(
                      false,
                    );
                  }}
                  type="button"
                >
                  <X size={18} />
                </button>
              </div>


              <div className="settings-form-grid">
                <label className="settings-field-wide">
                  <span>
                    Имя сотрудника
                  </span>

                  <input
                    value={
                      createForm
                        .full_name
                    }
                    onChange={(event) => {
                      setCreateForm(
                        (value) => ({
                          ...value,
                          full_name:
                            event
                              .target
                              .value,
                        }),
                      );
                    }}
                  />
                </label>

                <label>
                  <span>
                    Ставка, %
                  </span>

                  <input
                    max="100"
                    min="0"
                    step="0.01"
                    type="number"
                    value={
                      createForm
                        .rate_percent
                    }
                    onChange={(event) => {
                      setCreateForm(
                        (value) => ({
                          ...value,
                          rate_percent:
                            event
                              .target
                              .value,
                        }),
                      );
                    }}
                  />
                </label>

                <label className="settings-checkbox">
                  <input
                    checked={
                      createForm
                        .grant_access
                    }
                    type="checkbox"
                    onChange={(event) => {
                      setCreateForm(
                        (value) => ({
                          ...value,
                          grant_access:
                            event
                              .target
                              .checked,
                        }),
                      );
                    }}
                  />

                  <span>
                    Выдать доступ
                    к системе
                  </span>
                </label>
              </div>


              {createForm
                .grant_access && (
                <div className="settings-access-fields">
                  <label>
                    <span>
                      Логин
                    </span>

                    <input
                      autoComplete="off"
                      value={
                        createForm.login
                      }
                      onChange={(event) => {
                        setCreateForm(
                          (value) => ({
                            ...value,
                            login:
                              event
                                .target
                                .value,
                          }),
                        );
                      }}
                    />
                  </label>

                  <label>
                    <span>
                      Роль
                    </span>

                    <select
                      value={
                        createForm.role
                      }
                      onChange={(event) => {
                        const role =
                          event.target
                            .value as UserRole;

                        setCreateForm(
                          (value) => ({
                            ...value,
                            role,
                          }),
                        );
                      }}
                    >
                      <option value="mechanic">
                        Механик
                      </option>

                      <option value="admin">
                        Администратор
                      </option>

                      <option value="owner">
                        Владелец
                      </option>
                    </select>
                  </label>

                  <label>
                    <span>
                      Телефон
                    </span>

                    <input
                      value={
                        createForm.phone
                      }
                      onChange={(event) => {
                        setCreateForm(
                          (value) => ({
                            ...value,
                            phone:
                              event
                                .target
                                .value,
                          }),
                        );
                      }}
                    />
                  </label>

                  <label>
                    <span>
                      Временный пароль
                    </span>

                    <input
                      autoComplete="new-password"
                      minLength={12}
                      type="password"
                      value={
                        createForm
                          .temporary_password
                      }
                      onChange={(event) => {
                        setCreateForm(
                          (value) => ({
                            ...value,
                            temporary_password:
                              event
                                .target
                                .value,
                          }),
                        );
                      }}
                    />
                  </label>
                </div>
              )}


              <div className="settings-actions">
                <button
                  className="settings-secondary"
                  onClick={() => {
                    setShowCreateEmployee(
                      false,
                    );
                  }}
                  type="button"
                >
                  Отмена
                </button>

                <button
                  className="primary-button"
                  disabled={
                    createSaving
                  }
                  type="submit"
                >
                  <Save size={16} />

                  {createSaving
                    ? "Создаём..."
                    : "Создать сотрудника"}
                </button>
              </div>
            </form>
          )}


          {editingEmployee && (
            <form
              className="settings-card settings-editor-card"
              onSubmit={
                handleEmployeeSave
              }
            >
              <div className="settings-card-heading">
                <div>
                  <span>
                    Сотрудник №
                    {
                      editingEmployee
                        .employee_number
                    }
                  </span>

                  <h2>
                    Настройка сотрудника
                  </h2>
                </div>

                <button
                  aria-label="Закрыть"
                  className="settings-close"
                  onClick={() => {
                    setEditingEmployee(
                      null,
                    );
                  }}
                  type="button"
                >
                  <X size={18} />
                </button>
              </div>


              <div className="settings-form-grid">
                <label className="settings-field-wide">
                  <span>
                    Имя сотрудника
                  </span>

                  <input
                    value={
                      editForm.full_name
                    }
                    onChange={(event) => {
                      setEditForm(
                        (value) => ({
                          ...value,
                          full_name:
                            event
                              .target
                              .value,
                        }),
                      );
                    }}
                  />
                </label>

                <label>
                  <span>
                    Ставка, %
                  </span>

                  <input
                    max="100"
                    min="0"
                    step="0.01"
                    type="number"
                    value={
                      editForm
                        .rate_percent
                    }
                    onChange={(event) => {
                      setEditForm(
                        (value) => ({
                          ...value,
                          rate_percent:
                            event
                              .target
                              .value,
                        }),
                      );
                    }}
                  />
                </label>

                <label className="settings-checkbox">
                  <input
                    checked={
                      editForm.is_active
                    }
                    type="checkbox"
                    onChange={(event) => {
                      setEditForm(
                        (value) => ({
                          ...value,
                          is_active:
                            event
                              .target
                              .checked,
                          grant_access:
                            event
                              .target
                              .checked
                              ? value
                                  .grant_access
                              : false,
                        }),
                      );
                    }}
                  />

                  <span>
                    Сотрудник работает
                  </span>
                </label>

                <label className="settings-checkbox">
                  <input
                    checked={
                      editForm
                        .grant_access
                    }
                    disabled={
                      !editForm.is_active
                    }
                    type="checkbox"
                    onChange={(event) => {
                      setEditForm(
                        (value) => ({
                          ...value,
                          grant_access:
                            event
                              .target
                              .checked,
                        }),
                      );
                    }}
                  />

                  <span>
                    Доступ к системе
                  </span>
                </label>
              </div>


              {(editingEmployee
                .access_exists ||
                editForm
                  .grant_access) && (
                <div className="settings-access-fields">
                  <label>
                    <span>
                      Логин
                    </span>

                    <input
                      value={
                        editForm.login
                      }
                      onChange={(event) => {
                        setEditForm(
                          (value) => ({
                            ...value,
                            login:
                              event
                                .target
                                .value,
                          }),
                        );
                      }}
                    />
                  </label>


                  {editingEmployee.role ===
                  "tech_admin" ? (
                    <label>
                      <span>
                        Роль
                      </span>

                      <input
                        disabled
                        value="Служебная роль"
                      />
                    </label>
                  ) : (
                    <label>
                      <span>
                        Роль
                      </span>

                      <select
                        value={
                          editForm.role
                        }
                        onChange={(event) => {
                          const role =
                            event.target
                              .value as UserRole;

                          setEditForm(
                            (value) => ({
                              ...value,
                              role,
                            }),
                          );
                        }}
                      >
                        <option value="mechanic">
                          Механик
                        </option>

                        <option value="admin">
                          Администратор
                        </option>

                        <option value="owner">
                          Владелец
                        </option>
                      </select>
                    </label>
                  )}


                  <label>
                    <span>
                      Телефон
                    </span>

                    <input
                      value={
                        editForm.phone
                      }
                      onChange={(event) => {
                        setEditForm(
                          (value) => ({
                            ...value,
                            phone:
                              event
                                .target
                                .value,
                          }),
                        );
                      }}
                    />
                  </label>

                  <label>
                    <span>
                      Новый пароль
                    </span>

                    <input
                      autoComplete="new-password"
                      placeholder={
                        editingEmployee
                          .access_exists
                          ? "Оставьте пустым, если не меняем"
                          : "Минимум 12 символов"
                      }
                      type="password"
                      value={
                        editForm
                          .temporary_password
                      }
                      onChange={(event) => {
                        setEditForm(
                          (value) => ({
                            ...value,
                            temporary_password:
                              event
                                .target
                                .value,
                          }),
                        );
                      }}
                    />
                  </label>
                </div>
              )}


              <div className="settings-actions">
                <button
                  className="settings-secondary"
                  onClick={() => {
                    setEditingEmployee(
                      null,
                    );
                  }}
                  type="button"
                >
                  Отмена
                </button>

                <button
                  className="primary-button"
                  disabled={editSaving}
                  type="submit"
                >
                  <Save size={16} />

                  {editSaving
                    ? "Сохраняем..."
                    : "Сохранить"}
                </button>
              </div>
            </form>
          )}


          {employeesLoading ? (
            <div className="settings-loading">
              Загружаем сотрудников...
            </div>
          ) : visibleEmployees.length ===
            0 ? (
            <div className="settings-empty">
              В этом разделе
              сотрудников нет.
            </div>
          ) : (
            <div className="employee-access-grid">
              {visibleEmployees.map(
                (employee) => (
                  <article
                    className={
                      employee.archived
                        ? "employee-access-card employee-access-card-archived"
                        : "employee-access-card"
                    }
                    key={
                      employee
                        .employee_number
                    }
                  >
                    <div className="employee-access-top">
                      <div>
                        <span>
                          Сотрудник №
                          {
                            employee
                              .employee_number
                          }
                        </span>

                        <h3>
                          {
                            employee
                              .full_name
                          }
                        </h3>
                      </div>

                      <span
                        className={
                          employee.archived
                            ? "employee-state employee-state-archived"
                            : employee
                                .is_active
                              ? "employee-state employee-state-active"
                              : "employee-state"
                        }
                      >
                        {employee.archived
                          ? "Архив"
                          : employee
                              .is_active
                            ? "Работает"
                            : "Неактивен"}
                      </span>
                    </div>


                    <div className="employee-access-details">
                      <div>
                        <span>
                          Ставка
                        </span>

                        <strong>
                          {
                            employee
                              .current_rate_percent
                          }
                          %
                        </strong>
                      </div>

                      <div>
                        <span>
                          Доступ
                        </span>

                        <strong>
                          {employee
                            .access_enabled
                            ? "Включён"
                            : employee
                                .access_exists
                              ? "Отключён"
                              : "Не выдавался"}
                        </strong>
                      </div>

                      {employee.login && (
                        <div>
                          <span>
                            Логин
                          </span>

                          <strong>
                            {
                              employee
                                .login
                            }
                          </strong>
                        </div>
                      )}

                      {employee.role && (
                        <div>
                          <span>
                            Роль
                          </span>

                          <strong>
                            {
                              roleNames[
                                employee
                                  .role
                              ]
                            }
                          </strong>
                        </div>
                      )}
                    </div>


                    {employee.archived ? (
                      <div className="employee-card-actions">
                        <button
                          className="settings-secondary"
                          disabled={
                            actionEmployee ===
                            employee
                              .employee_number
                          }
                          onClick={() => {
                            void handleRestore(
                              employee,
                            );
                          }}
                          type="button"
                        >
                          <RotateCcw
                            size={14}
                          />
                          Восстановить
                        </button>
                      </div>
                    ) : (
                      <div className="employee-card-actions">
                        <button
                          className="settings-secondary"
                          onClick={() => {
                            openEmployeeEditor(
                              employee,
                            );
                          }}
                          type="button"
                        >
                          Настроить
                        </button>

                        <button
                          className="settings-danger"
                          disabled={
                            actionEmployee ===
                            employee
                              .employee_number
                          }
                          onClick={() => {
                            void handleArchive(
                              employee,
                            );
                          }}
                          type="button"
                        >
                          <Trash2
                            size={14}
                          />

                          {actionEmployee ===
                          employee
                            .employee_number
                            ? "Удаляем..."
                            : "Удалить"}
                        </button>
                      </div>
                    )}
                  </article>
                ),
              )}
            </div>
          )}
        </div>
      )}


      {tab === "security" && (
        <div className="settings-columns">
          <article className="settings-card">
            <div className="settings-card-heading">
              <div>
                <span>
                  Сессии
                </span>

                <h2>
                  Безопасность входа
                </h2>
              </div>

              <ShieldCheck
                size={22}
              />
            </div>

            <div className="security-info-list">
              <div>
                <strong>
                  Смена своего пароля
                </strong>

                <span>
                  Требует действующий
                  пароль, после чего
                  задаётся новый.
                </span>
              </div>

              <div>
                <strong>
                  После смены пароля
                </strong>

                <span>
                  Текущая сессия
                  остаётся активной,
                  остальные завершаются.
                </span>
              </div>

              <div>
                <strong>
                  Удаление сотрудника
                </strong>

                <span>
                  Отключает его доступ
                  и переносит в архив,
                  не удаляя историю.
                </span>
              </div>
            </div>
          </article>

          <article className="settings-card settings-future-card">
            <KeyRound size={24} />

            <div>
              <span>
                Позже
              </span>

              <h2>
                Восстановление пароля
              </h2>

              <p>
                Восстановление через
                телефон подключим вместе
                с реальной отправкой
                уведомлений клиентам.
              </p>
            </div>
          </article>
        </div>
      )}
    </section>
  );
}