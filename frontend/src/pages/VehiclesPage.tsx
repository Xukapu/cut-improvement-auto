import {
  Car,
  Edit3,
  Plus,
  Search,
  UserRoundCog,
} from "lucide-react";
import {
  useEffect,
  useState,
} from "react";
import type { FormEvent } from "react";

import { ApiError } from "../api/client";
import {
  listClients,
} from "../api/clients";
import {
  createVehicle,
  listVehicles,
  transferVehicle,
  updateVehicle,
} from "../api/vehicles";
import type {
  Client,
} from "../types/client";
import type {
  Vehicle,
} from "../types/vehicle";

type FormState = {
  license_plate: string;
  vin: string;
  brand: string;
  model: string;
  year: string;
  mileage: string;
  owner_client_number: string;
};

const emptyForm: FormState = {
  license_plate: "",
  vin: "",
  brand: "",
  model: "",
  year: "",
  mileage: "",
  owner_client_number: "",
};

function getError(
  error: unknown,
): string {
  return error instanceof ApiError
    ? error.message
    : "Произошла ошибка.";
}

export function VehiclesPage() {
  const [
    items,
    setItems,
  ] = useState<Vehicle[]>([]);

  const [
    clients,
    setClients,
  ] = useState<Client[]>([]);

  const [
    selected,
    setSelected,
  ] = useState<Vehicle | null>(null);

  const [search, setSearch] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [formOpen, setFormOpen] =
    useState(false);

  const [editing, setEditing] =
    useState<Vehicle | null>(null);

  const [saving, setSaving] =
    useState(false);

  const [form, setForm] =
    useState<FormState>(emptyForm);

  const [
    transferOpen,
    setTransferOpen,
  ] = useState(false);

  const [
    newOwnerNumber,
    setNewOwnerNumber,
  ] = useState("");

  async function refresh() {
    const [vehicleData, clientData] =
      await Promise.all([
        listVehicles(search),
        listClients("", 100),
      ]);

    setItems(vehicleData.items);
    setClients(clientData.items);
  }

  useEffect(() => {
    let active = true;

    const timer =
      window.setTimeout(
        async () => {
          try {
            const [
              vehicleData,
              clientData,
            ] = await Promise.all([
              listVehicles(search),
              listClients("", 100),
            ]);

            if (!active) {
              return;
            }

            setItems(
              vehicleData.items,
            );

            setClients(
              clientData.items,
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
  }, [search]);

  function openCreate() {
    setEditing(null);

    setForm({
      ...emptyForm,
      owner_client_number:
        clients[0]
          ? String(
              clients[0]
                .client_number,
            )
          : "",
    });

    setFormOpen(true);
  }

  function openEdit(
    vehicle: Vehicle,
  ) {
    setEditing(vehicle);

    setForm({
      license_plate:
        vehicle.license_plate,
      vin:
        vehicle.vin ?? "",
      brand:
        vehicle.brand,
      model:
        vehicle.model,
      year:
        vehicle.year !== null
          ? String(vehicle.year)
          : "",
      mileage:
        vehicle.mileage !== null
          ? String(
              vehicle.mileage,
            )
          : "",
      owner_client_number:
        String(
          vehicle
            .current_owner_client_number,
        ),
    });

    setFormOpen(true);
  }

  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    setSaving(true);
    setError("");

    const base = {
      license_plate:
        form.license_plate.trim(),
      vin:
        form.vin.trim() ||
        null,
      brand:
        form.brand.trim(),
      model:
        form.model.trim(),
      year:
        form.year
          ? Number(form.year)
          : null,
      mileage:
        form.mileage
          ? Number(form.mileage)
          : null,
    };

    try {
      const result = editing
        ? await updateVehicle(
            editing.vehicle_number,
            base,
          )
        : await createVehicle({
            ...base,
            owner_client_number:
              Number(
                form
                  .owner_client_number,
              ),
          });

      setSelected(result);
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

  async function doTransfer() {
    if (
      !selected ||
      !newOwnerNumber
    ) {
      return;
    }

    try {
      const result =
        await transferVehicle(
          selected.vehicle_number,
          Number(newOwnerNumber),
        );

      setSelected(result);
      setTransferOpen(false);
      setNewOwnerNumber("");

      await refresh();
    } catch (transferError) {
      setError(
        getError(transferError),
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
              "Госномер, VIN, марка или модель"
            value={search}
            onChange={(event) => {
              setSearch(
                event.target.value,
              );
            }}
          />
        </div>

        <button
          className=
            "primary-inline-button"
          disabled={
            clients.length === 0
          }
          onClick={openCreate}
          type="button"
        >
          <Plus size={17} />
          Новый автомобиль
        </button>
      </div>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      <div className="master-detail">
        <div className="data-card">
          <div className="data-card-title">
            <div>
              <span className="card-kicker">
                Автопарк
              </span>

              <h2>
                Автомобили
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
          ) : items.length === 0 ? (
            <div className="empty-state">
              <Car size={28} />

              <div>
                <strong>
                  Автомобили
                  не найдены
                </strong>
              </div>
            </div>
          ) : (
            <div className="data-list">
              {items.map(
                (vehicle) => (
                  <button
                    className={
                      selected
                        ?.vehicle_number ===
                      vehicle.vehicle_number
                        ? "data-row data-row-active"
                        : "data-row"
                    }
                    key={
                      vehicle
                        .vehicle_number
                    }
                    onClick={() => {
                      setSelected(vehicle);
                    }}
                    type="button"
                  >
                    <span className="row-number">
                      №
                      {
                        vehicle
                          .vehicle_number
                      }
                    </span>

                    <span className="row-primary">
                      <strong>
                        {vehicle.brand}{" "}
                        {vehicle.model}
                      </strong>

                      <small>
                        {
                          vehicle
                            .license_plate
                        }
                      </small>
                    </span>

                    <span className="row-meta">
                      {vehicle.mileage !==
                      null
                        ? `${vehicle.mileage.toLocaleString(
                            "ru-RU",
                          )} км`
                        : "—"}
                    </span>
                  </button>
                ),
              )}
            </div>
          )}
        </div>

        <div className="detail-card">
          {!selected ? (
            <div className="detail-empty">
              <Car size={34} />

              <strong>
                Выбери автомобиль
              </strong>

              <span>
                Здесь откроется его
                карточка.
              </span>
            </div>
          ) : (
            <>
              <div className="detail-header">
                <div>
                  <span className="card-kicker">
                    Автомобиль №
                    {
                      selected
                        .vehicle_number
                    }
                  </span>

                  <h2>
                    {selected.brand}{" "}
                    {selected.model}
                  </h2>
                </div>

                <button
                  className=
                    "icon-action"
                  onClick={() => {
                    openEdit(selected);
                  }}
                  title="Изменить"
                  type="button"
                >
                  <Edit3 size={18} />
                </button>
              </div>

              <dl className="detail-grid">
                <div>
                  <dt>
                    Госномер *
                  </dt>

                  <dd>
                    {
                      selected
                        .license_plate
                    }
                  </dd>
                </div>

                <div>
                  <dt>
                    VIN (необязательно)
                  </dt>

                  <dd>
                    {selected.vin ||
                      "—"}
                  </dd>
                </div>

                <div>
                  <dt>
                    Год (необязательно)
                  </dt>

                  <dd>
                    {selected.year ??
                      "—"}
                  </dd>
                </div>

                <div>
                  <dt>
                    Пробег (необязательно)
                  </dt>

                  <dd>
                    {selected.mileage !==
                    null
                      ? `${selected.mileage.toLocaleString(
                          "ru-RU",
                        )} км`
                      : "—"}
                  </dd>
                </div>

                <div className="detail-wide">
                  <dt>
                    Текущий владелец
                  </dt>

                  <dd>
                    {
                      selected
                        .current_owner_name
                    }{" "}
                    · Клиент №
                    {
                      selected
                        .current_owner_client_number
                    }
                  </dd>
                </div>
              </dl>

              <div className="detail-actions">
                <button
                  className=
                    "secondary-button"
                  onClick={() => {
                    setNewOwnerNumber(
                      String(
                        selected
                          .current_owner_client_number,
                      ),
                    );

                    setTransferOpen(
                      true,
                    );
                  }}
                  type="button"
                >
                  <UserRoundCog
                    size={17}
                  />
                  Сменить владельца
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {formOpen && (
        <div className="modal-backdrop">
          <form
            className="modal-card"
            onSubmit={submit}
          >
            <div className="modal-header">
              <span className="card-kicker">
                {editing
                  ? `Автомобиль №${editing.vehicle_number}`
                  : "Новая карточка"}
              </span>

              <h2>
                {editing
                  ? "Изменить автомобиль"
                  : "Новый автомобиль"}
              </h2>
            </div>

            <div className="form-grid">
              <label>
                <span>
                  Марка *
                </span>

                <input
                  required
                  value={form.brand}
                  onChange={(event) => {
                    setForm({
                      ...form,
                      brand:
                        event.target.value,
                    });
                  }}
                />
              </label>

              <label>
                <span>
                  Модель *
                </span>

                <input
                  required
                  value={form.model}
                  onChange={(event) => {
                    setForm({
                      ...form,
                      model:
                        event.target.value,
                    });
                  }}
                />
              </label>

              <label>
                <span>
                  Госномер *
                </span>

                <input
                  required
                  value={
                    form.license_plate
                  }
                  onChange={(event) => {
                    setForm({
                      ...form,
                      license_plate:
                        event.target.value,
                    });
                  }}
                />
              </label>

              <label>
                <span>
                  VIN (необязательно)
                </span>

                <input
                  value={form.vin}
                  onChange={(event) => {
                    setForm({
                      ...form,
                      vin:
                        event.target.value,
                    });
                  }}
                />
              </label>

              <label>
                <span>
                  Год (необязательно)
                </span>

                <input
                  min="1900"
                  max="2100"
                  type="number"
                  value={form.year}
                  onChange={(event) => {
                    setForm({
                      ...form,
                      year:
                        event.target.value,
                    });
                  }}
                />
              </label>

              <label>
                <span>
                  Пробег (необязательно)
                </span>

                <input
                  min="0"
                  type="number"
                  value={form.mileage}
                  onChange={(event) => {
                    setForm({
                      ...form,
                      mileage:
                        event.target.value,
                    });
                  }}
                />
              </label>

              {!editing && (
                <label className="form-wide">
                  <span>
                    Владелец *
                  </span>

                  <select
                    required
                    value={
                      form
                        .owner_client_number
                    }
                    onChange={(event) => {
                      setForm({
                        ...form,
                        owner_client_number:
                          event.target
                            .value,
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
              )}
            </div>

            <div className="modal-actions">
              <button
                className=
                  "secondary-button"
                onClick={() => {
                  setFormOpen(false);
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

      {transferOpen &&
        selected && (
          <div className="modal-backdrop">
            <div className=
              "modal-card modal-small"
            >
              <div className="modal-header">
                <span className="card-kicker">
                  {
                    selected
                      .license_plate
                  }
                </span>

                <h2>
                  Смена владельца
                </h2>
              </div>

              <label className="single-field">
                <span>
                  Новый владелец
                </span>

                <select
                  value={
                    newOwnerNumber
                  }
                  onChange={(event) => {
                    setNewOwnerNumber(
                      event.target.value,
                    );
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
                          client.full_name
                        }
                      </option>
                    ),
                  )}
                </select>
              </label>

              <div className="modal-actions">
                <button
                  className=
                    "secondary-button"
                  onClick={() => {
                    setTransferOpen(
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
                  onClick={() => {
                    void doTransfer();
                  }}
                  type="button"
                >
                  Сменить владельца
                </button>
              </div>
            </div>
          </div>
        )}
    </section>
  );
}