import {
  Archive,
  ArchiveRestore,
  Edit3,
  Plus,
  Search,
  UserRound,
} from "lucide-react";
import {
  useEffect,
  useState,
} from "react";
import type { FormEvent } from "react";

import { ApiError } from "../api/client";
import {
  archiveClient,
  createClient,
  listArchivedClients,
  listClients,
  restoreClient,
  setClientInternalMark,
  updateClient,
} from "../api/clients";
import {
  listVehicles,
} from "../api/vehicles";
import type {
  CurrentUser,
} from "../types/auth";
import type {
  ArchivedClient,
  ArchiveReason,
  Client,
  ClientSource,
} from "../types/client";
import type {
  Vehicle,
} from "../types/vehicle";

type Props = {
  currentUser: CurrentUser;
};

type FormState = {
  full_name: string;
  phone_primary: string;
  phone_secondary: string;
  source: ClientSource;
  referred_by_client_number: string;
  notes: string;
};

const emptyForm: FormState = {
  full_name: "",
  phone_primary: "",
  phone_secondary: "",
  source: "other",
  referred_by_client_number: "",
  notes: "",
};

function sourceLabel(
  source: ClientSource,
): string {
  const labels: Record<
    ClientSource,
    string
  > = {
    avito: "Avito",
    referral: "По рекомендации",
    other: "Другое",
  };

  return labels[source];
}

function getError(
  error: unknown,
): string {
  return error instanceof ApiError
    ? error.message
    : "Произошла ошибка.";
}

export function ClientsPage({
  currentUser,
}: Props) {
  const [
    items,
    setItems,
  ] = useState<
    Array<Client | ArchivedClient>
  >([]);

  const [
    selected,
    setSelected,
  ] = useState<
    Client | ArchivedClient | null
  >(null);

  const [
    clientVehicles,
    setClientVehicles,
  ] = useState<Vehicle[]>([]);

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    archived,
    setArchived,
  ] = useState(false);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  const [
    formOpen,
    setFormOpen,
  ] = useState(false);

  const [
    editing,
    setEditing,
  ] = useState<Client | null>(
    null,
  );

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    form,
    setForm,
  ] = useState<FormState>(
    emptyForm,
  );

  const [
    archiveOpen,
    setArchiveOpen,
  ] = useState(false);

  const [
    archiveReason,
    setArchiveReason,
  ] = useState<ArchiveReason>(
    "other",
  );

  const [
    archiveComment,
    setArchiveComment,
  ] = useState("");

  const [
    referralQuery,
    setReferralQuery,
  ] = useState("");

  const [
    referralOptions,
    setReferralOptions,
  ] = useState<Client[]>([]);

  const [
    referralLoading,
    setReferralLoading,
  ] = useState(false);

  const selectedClientNumber =
    selected?.client_number ??
    null;


  // ----------------------------------------------------------
  // Основной список клиентов
  // ----------------------------------------------------------

  useEffect(() => {
    let active = true;

    const timer =
      window.setTimeout(
        async () => {
          try {
            const response =
              archived
                ? await listArchivedClients(
                    search,
                  )
                : await listClients(
                    search,
                  );

            if (!active) {
              return;
            }

            setItems(
              response.items,
            );

            setError("");
            setLoading(false);
          } catch (loadError) {
            if (!active) {
              return;
            }

            setError(
              getError(loadError),
            );

            setLoading(false);
          }
        },
        200,
      );

    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [
    archived,
    search,
  ]);


  // ----------------------------------------------------------
  // Автомобили выбранного клиента
  // ----------------------------------------------------------

  useEffect(() => {
    if (
      selectedClientNumber ===
      null
    ) {
      return;
    }

    let active = true;

    listVehicles(
      "",
      100,
      selectedClientNumber,
    )
      .then((response) => {
        if (!active) {
          return;
        }

        setClientVehicles(
          response.items,
        );
      })
      .catch(() => {
        if (!active) {
          return;
        }

        setClientVehicles([]);
      });

    return () => {
      active = false;
    };
  }, [
    selectedClientNumber,
  ]);


  // ----------------------------------------------------------
  // Поиск клиента, который рекомендовал
  // ----------------------------------------------------------

  useEffect(() => {
    if (
      form.source !==
        "referral" ||
      referralQuery.trim()
        .length < 2 ||
      form
        .referred_by_client_number
    ) {
      return;
    }

    let active = true;

    const timer =
      window.setTimeout(
        async () => {
          setReferralLoading(
            true,
          );

          try {
            const response =
              await listClients(
                referralQuery.trim(),
                8,
              );

            if (!active) {
              return;
            }

            setReferralOptions(
              response.items.filter(
                (client) =>
                  client.client_number !==
                  editing
                    ?.client_number,
              ),
            );
          } catch {
            if (active) {
              setReferralOptions(
                [],
              );
            }
          } finally {
            if (active) {
              setReferralLoading(
                false,
              );
            }
          }
        },
        220,
      );

    return () => {
      active = false;
      window.clearTimeout(
        timer,
      );
    };
  }, [
    editing?.client_number,
    form
      .referred_by_client_number,
    form.source,
    referralQuery,
  ]);


  async function refresh() {
    const response =
      archived
        ? await listArchivedClients(
            search,
          )
        : await listClients(
            search,
          );

    setItems(
      response.items,
    );
  }


  function openCreate() {
    setEditing(null);
    setForm(emptyForm);

    setReferralQuery("");
    setReferralOptions([]);
    setReferralLoading(false);

    setFormOpen(true);
  }


  function openEdit(
    client: Client,
  ) {
    setEditing(client);

    setForm({
      full_name:
        client.full_name,

      phone_primary:
        client.phone_primary,

      phone_secondary:
        client.phone_secondary ??
        "",

      source:
        client.source,

      referred_by_client_number:
        client
          .referred_by_client_number
          ? String(
              client
                .referred_by_client_number,
            )
          : "",

      notes:
        client.notes ?? "",
    });

    setReferralQuery(
      client
        .referred_by_client_name ??
        "",
    );

    setReferralOptions([]);
    setReferralLoading(false);

    setFormOpen(true);
  }


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    setSaving(true);
    setError("");

    const referredNumber =
      form.source ===
        "referral" &&
      form
        .referred_by_client_number
        ? Number(
            form
              .referred_by_client_number,
          )
        : null;

    try {
      const result =
        editing
          ? await updateClient(
              editing.client_number,
              {
                full_name:
                  form.full_name
                    .trim(),

                phone_primary:
                  form.phone_primary
                    .trim(),

                phone_secondary:
                  form.phone_secondary
                    .trim() ||
                  null,

                source:
                  form.source,

                referred_by_client_number:
                  referredNumber,

                notes:
                  form.notes
                    .trim() ||
                  null,
              },
            )
          : await createClient(
              {
                full_name:
                  form.full_name
                    .trim(),

                phone_primary:
                  form.phone_primary
                    .trim(),

                phone_secondary:
                  form.phone_secondary
                    .trim() ||
                  null,

                source:
                  form.source,

                referred_by_client_number:
                  referredNumber,

                notes:
                  form.notes
                    .trim() ||
                  null,

                internal_mark:
                  false,
              },
            );

      setSelected(result);
      setClientVehicles([]);

      setFormOpen(false);

      await refresh();
    } catch (saveError) {
      setError(
        getError(saveError),
      );
    } finally {
      setSaving(false);
    }
  }


  async function toggleMark(
    client: Client,
  ) {
    try {
      const result =
        await setClientInternalMark(
          client.client_number,
          !client.internal_mark,
        );

      setSelected(result);

      await refresh();
    } catch (markError) {
      setError(
        getError(markError),
      );
    }
  }


  async function confirmArchive() {
    if (!selected) {
      return;
    }

    try {
      await archiveClient(
        selected.client_number,
        archiveReason,
        archiveComment.trim() ||
          null,
      );

      setArchiveOpen(false);
      setArchiveComment("");

      setSelected(null);
      setClientVehicles([]);

      await refresh();
    } catch (archiveError) {
      setError(
        getError(archiveError),
      );
    }
  }


  async function restore(
    client: ArchivedClient,
  ) {
    try {
      await restoreClient(
        client.client_number,
      );

      setSelected(null);
      setClientVehicles([]);

      await refresh();
    } catch (restoreError) {
      setError(
        getError(restoreError),
      );
    }
  }


  return (
    <section className="data-page">
      <div className="section-toolbar">
        <div className="search-field">
          <Search size={17} />

          <input
            placeholder=
              "Поиск по имени или телефону"
            value={search}
            onChange={(event) => {
              setSearch(
                event.target.value,
              );
            }}
          />
        </div>

        <div className="toolbar-actions">
          <button
            className=
              "secondary-button"
            onClick={() => {
              setArchived(
                (value) =>
                  !value,
              );

              setSelected(null);
              setClientVehicles([]);
            }}
            type="button"
          >
            {archived ? (
              <ArchiveRestore
                size={17}
              />
            ) : (
              <Archive
                size={17}
              />
            )}

            {archived
              ? "Активные"
              : "Архив"}
          </button>

          {!archived && (
            <button
              className=
                "primary-inline-button"
              onClick={
                openCreate
              }
              type="button"
            >
              <Plus size={17} />
              Новый клиент
            </button>
          )}
        </div>
      </div>


      {error && (
        <div className=
          "dashboard-error"
        >
          {error}
        </div>
      )}


      <div className="master-detail">
        <div className="data-card">
          <div className=
            "data-card-title"
          >
            <div>
              <span className=
                "card-kicker"
              >
                {archived
                  ? "Архив"
                  : "Клиентская база"}
              </span>

              <h2>
                {archived
                  ? "Архив клиентов"
                  : "Клиенты"}
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
              <UserRound
                size={28}
              />

              <div>
                <strong>
                  Ничего не найдено
                </strong>

                <p>
                  Измени поисковый
                  запрос.
                </p>
              </div>
            </div>
          ) : (
            <div className=
              "data-list"
            >
              {items.map(
                (client) => (
                  <button
                    className={
                      selected
                        ?.client_number ===
                      client
                        .client_number
                        ? "data-row data-row-active"
                        : "data-row"
                    }
                    key={
                      client
                        .client_number
                    }
                    onClick={() => {
                      setClientVehicles(
                        [],
                      );

                      setSelected(
                        client,
                      );
                    }}
                    type="button"
                  >
                    <span className=
                      "row-number"
                    >
                      №
                      {
                        client
                          .client_number
                      }
                    </span>

                    <span className=
                      "row-primary"
                    >
                      <strong>
                        {
                          client
                            .full_name
                        }

                        {client
                          .internal_mark && (
                          <span
                            aria-hidden=
                              "true"
                            className=
                              "internal-mark-symbol"
                          >
                            😈
                          </span>
                        )}
                      </strong>

                      <small>
                        {
                          client
                            .phone_primary
                        }
                      </small>
                    </span>

                    <span className=
                      "row-meta"
                    >
                      {sourceLabel(
                        client.source,
                      )}
                    </span>
                  </button>
                ),
              )}
            </div>
          )}
        </div>


        <div className="detail-card">
          {!selected ? (
            <div className=
              "detail-empty"
            >
              <UserRound
                size={34}
              />

              <strong>
                Выбери клиента
              </strong>

              <span>
                Здесь откроется его
                карточка.
              </span>
            </div>
          ) : (
            <>
              <div className=
                "detail-header"
              >
                <div>
                  <span className=
                    "card-kicker"
                  >
                    Клиент №
                    {
                      selected
                        .client_number
                    }
                  </span>

                  <h2>
                    {
                      selected
                        .full_name
                    }

                    {selected
                      .internal_mark && (
                      <span
                        aria-hidden=
                          "true"
                        className=
                          "internal-mark-symbol"
                      >
                        😈
                      </span>
                    )}
                  </h2>
                </div>

                {!archived && (
                  <button
                    className=
                      "icon-action"
                    onClick={() => {
                      openEdit(
                        selected as Client,
                      );
                    }}
                    title="Изменить"
                    type="button"
                  >
                    <Edit3
                      size={18}
                    />
                  </button>
                )}
              </div>


              <dl className=
                "detail-grid"
              >
                <div>
                  <dt>
                    Основной телефон
                  </dt>

                  <dd>
                    {
                      selected
                        .phone_primary
                    }
                  </dd>
                </div>

                <div>
                  <dt>
                    Второй телефон
                  </dt>

                  <dd>
                    {selected
                      .phone_secondary ||
                      "—"}
                  </dd>
                </div>

                <div>
                  <dt>
                    Источник
                  </dt>

                  <dd>
                    {sourceLabel(
                      selected.source,
                    )}
                  </dd>
                </div>

                <div>
                  <dt>
                    Рекомендовал
                  </dt>

                  <dd>
                    {selected
                      .referred_by_client_name ||
                      "—"}
                  </dd>
                </div>

                <div className=
                  "detail-wide"
                >
                  <dt>
                    Автомобили
                  </dt>

                  <dd className=
                    "client-vehicle-list"
                  >
                    {clientVehicles
                      .length > 0 ? (
                      clientVehicles.map(
                        (
                          vehicle,
                        ) => (
                          <span
                            key={
                              vehicle
                                .vehicle_number
                            }
                          >
                            {
                              vehicle
                                .brand
                            }{" "}
                            {
                              vehicle
                                .model
                            }
                          </span>
                        ),
                      )
                    ) : (
                      <span>
                        —
                      </span>
                    )}
                  </dd>
                </div>

                <div className=
                  "detail-wide"
                >
                  <dt>
                    Комментарий
                  </dt>

                  <dd>
                    {selected.notes ||
                      "—"}
                  </dd>
                </div>
              </dl>


              <div
                className=
                  "detail-actions detail-actions-stacked"
              >
                {archived ? (
                  <button
                    className=
                      "primary-inline-button"
                    onClick={() => {
                      void restore(
                        selected as ArchivedClient,
                      );
                    }}
                    type="button"
                  >
                    <ArchiveRestore
                      size={17}
                    />
                    Восстановить
                  </button>
                ) : (
                  <>
                    <button
                      className=
                        "danger-button"
                      onClick={() => {
                        setArchiveOpen(
                          true,
                        );
                      }}
                      type="button"
                    >
                      <Archive
                        size={17}
                      />
                      В архив
                    </button>

                    {currentUser
                      .role ===
                      "owner" && (
                      <button
                        className=
                          "internal-mark-action"
                        onClick={() => {
                          void toggleMark(
                            selected as Client,
                          );
                        }}
                        type="button"
                      >
                        {selected
                          .internal_mark
                          ? "Снять внутреннюю метку"
                          : "Поставить внутреннюю метку"}
                      </button>
                    )}
                  </>
                )}
              </div>
            </>
          )}
        </div>
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
                  ? `Клиент №${editing.client_number}`
                  : "Новая карточка"}
              </span>

              <h2>
                {editing
                  ? "Изменить клиента"
                  : "Новый клиент"}
              </h2>
            </div>


            <div className=
              "form-grid"
            >
              <label className=
                "form-wide"
              >
                <span>
                  Имя клиента *
                </span>

                <input
                  required
                  value={
                    form.full_name
                  }
                  onChange={(
                    event,
                  ) => {
                    setForm({
                      ...form,
                      full_name:
                        event.target
                          .value,
                    });
                  }}
                />
              </label>


              <label>
                <span>
                  Телефон *
                </span>

                <input
                  required
                  value={
                    form
                      .phone_primary
                  }
                  onChange={(
                    event,
                  ) => {
                    setForm({
                      ...form,
                      phone_primary:
                        event.target
                          .value,
                    });
                  }}
                />
              </label>


              <label>
                <span>
                  Второй телефон
                  {" "}
                  <small>
                    (необязательно)
                  </small>
                </span>

                <input
                  value={
                    form
                      .phone_secondary
                  }
                  onChange={(
                    event,
                  ) => {
                    setForm({
                      ...form,
                      phone_secondary:
                        event.target
                          .value,
                    });
                  }}
                />
              </label>


              <label>
                <span>
                  Источник *
                </span>

                <select
                  value={
                    form.source
                  }
                  onChange={(
                    event,
                  ) => {
                    const source =
                      event.target
                        .value as ClientSource;

                    setForm({
                      ...form,
                      source,
                      referred_by_client_number:
                        source ===
                        "referral"
                          ? form
                              .referred_by_client_number
                          : "",
                    });

                    if (
                      source !==
                      "referral"
                    ) {
                      setReferralQuery(
                        "",
                      );

                      setReferralOptions(
                        [],
                      );
                    }
                  }}
                >
                  <option value=
                    "avito"
                  >
                    Avito
                  </option>

                  <option value=
                    "referral"
                  >
                    По рекомендации
                  </option>

                  <option value=
                    "other"
                  >
                    Другое
                  </option>
                </select>
              </label>


              {form.source ===
                "referral" && (
                <label>
                  <span>
                    Кто рекомендовал
                    {" "}
                    <small>
                      (необязательно)
                    </small>
                  </span>

                  <div className=
                    "referral-picker"
                  >
                    <input
                      autoComplete="off"
                      placeholder=
                        "Имя или телефон"
                      value={
                        referralQuery
                      }
                      onChange={(
                        event,
                      ) => {
                        setReferralQuery(
                          event.target
                            .value,
                        );

                        setReferralOptions(
                          [],
                        );

                        setReferralLoading(
                          false,
                        );

                        setForm({
                          ...form,
                          referred_by_client_number:
                            "",
                        });
                      }}
                    />

                    {referralLoading && (
                      <div className=
                        "referral-hint"
                      >
                        Ищем клиента...
                      </div>
                    )}

                    {!referralLoading &&
                      referralOptions
                        .length >
                        0 && (
                        <div className=
                          "referral-options"
                        >
                          {referralOptions.map(
                            (
                              client,
                            ) => (
                              <button
                                key={
                                  client
                                    .client_number
                                }
                                onClick={() => {
                                  setForm({
                                    ...form,
                                    referred_by_client_number:
                                      String(
                                        client
                                          .client_number,
                                      ),
                                  });

                                  setReferralQuery(
                                    `${client.full_name} · ${client.phone_primary}`,
                                  );

                                  setReferralOptions(
                                    [],
                                  );
                                }}
                                type="button"
                              >
                                <strong>
                                  {
                                    client
                                      .full_name
                                  }
                                </strong>

                                <span>
                                  {
                                    client
                                      .phone_primary
                                  }
                                </span>
                              </button>
                            ),
                          )}
                        </div>
                      )}

                    {form
                      .referred_by_client_number && (
                      <div className=
                        "referral-selected"
                      >
                        Клиент выбран
                      </div>
                    )}
                  </div>
                </label>
              )}


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
                    form.notes
                  }
                  onChange={(
                    event,
                  ) => {
                    setForm({
                      ...form,
                      notes:
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
                onClick={() => {
                  setFormOpen(
                    false,
                  );
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


      {archiveOpen &&
        selected && (
          <div className=
            "modal-backdrop"
          >
            <div className=
              "modal-card modal-small"
            >
              <div className=
                "modal-header"
              >
                <span className=
                  "card-kicker"
                >
                  Клиент №
                  {
                    selected
                      .client_number
                  }
                </span>

                <h2>
                  Переместить в архив?
                </h2>
              </div>

              <div className=
                "form-grid"
              >
                <label className=
                  "form-wide"
                >
                  <span>
                    Причина
                  </span>

                  <select
                    value={
                      archiveReason
                    }
                    onChange={(
                      event,
                    ) => {
                      setArchiveReason(
                        event.target
                          .value as ArchiveReason,
                      );
                    }}
                  >
                    <option
                      value=
                        "no_longer_serviced"
                    >
                      Больше не обслуживается
                    </option>

                    <option
                      value=
                        "created_by_mistake"
                    >
                      Создан по ошибке
                    </option>

                    <option
                      value=
                        "owner_request"
                    >
                      По просьбе владельца
                    </option>

                    <option
                      value="other"
                    >
                      Другое
                    </option>
                  </select>
                </label>

                <label className=
                  "form-wide"
                >
                  <span>
                    Комментарий
                  </span>

                  <textarea
                    rows={3}
                    value={
                      archiveComment
                    }
                    onChange={(
                      event,
                    ) => {
                      setArchiveComment(
                        event.target
                          .value,
                      );
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
                  onClick={() => {
                    setArchiveOpen(
                      false,
                    );
                  }}
                  type="button"
                >
                  Отмена
                </button>

                <button
                  className=
                    "danger-button"
                  onClick={() => {
                    void confirmArchive();
                  }}
                  type="button"
                >
                  Подтвердить архив
                </button>
              </div>
            </div>
          </div>
        )}
    </section>
  );
}