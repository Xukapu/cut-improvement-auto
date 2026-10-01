import {
  Car,
  CheckCircle2,
  WalletCards,
  Wrench,
} from "lucide-react";

import type {
  DashboardResponse,
} from "../types/dashboard";

import {
  formatMoney,
} from "../utils/format";


type Props = {
  dashboard: DashboardResponse | null;
};


export function DashboardVehicleStateCard({
  dashboard,
}: Props) {
  const inProgress =
    dashboard?.in_progress ?? [];

  const ready =
    dashboard?.ready ?? [];

  const debts =
    dashboard?.debts ?? [];

  const empty =
    inProgress.length === 0 &&
    ready.length === 0 &&
    debts.length === 0;


  return (
    <article className="workspace-card vehicle-now-card">
      <div className="card-header">
        <div>
          <span className="card-kicker">
            Текущее состояние
          </span>

          <h3>
            Автомобили сейчас
          </h3>
        </div>

        <Car size={21} />
      </div>


      {empty ? (
        <div className="vehicle-now-empty">
          <CheckCircle2
            size={23}
          />

          <div>
            <strong>
              Активных ремонтов нет
            </strong>

            <span>
              Сейчас нет машин
              в работе, готовых к выдаче
              или с задолженностью.
            </span>
          </div>
        </div>
      ) : (
        <div className="vehicle-now-groups">

          {inProgress.length > 0 && (
            <section className="vehicle-now-group">
              <div className="vehicle-now-heading">
                <Wrench size={15} />

                <strong>
                  В работе
                </strong>

                <span>
                  {inProgress.length}
                </span>
              </div>

              <div className="vehicle-now-list">
                {inProgress.map(
                  (order) => (
                    <div
                      className="vehicle-now-row"
                      key={
                        order
                          .work_order_number
                      }
                    >
                      <div>
                        <strong>
                          {
                            order
                              .vehicle_name
                          }
                        </strong>

                        <span>
                          {
                            order
                              .license_plate
                          }
                        </span>
                      </div>

                      <small>
                        Заказ №
                        {
                          order
                            .work_order_number
                        }
                      </small>
                    </div>
                  ),
                )}
              </div>
            </section>
          )}


          {ready.length > 0 && (
            <section className="vehicle-now-group">
              <div className="vehicle-now-heading">
                <CheckCircle2
                  size={15}
                />

                <strong>
                  Готовы к выдаче
                </strong>

                <span>
                  {ready.length}
                </span>
              </div>

              <div className="vehicle-now-list">
                {ready.map(
                  (order) => (
                    <div
                      className="vehicle-now-row"
                      key={
                        order
                          .work_order_number
                      }
                    >
                      <div>
                        <strong>
                          {
                            order
                              .vehicle_name
                          }
                        </strong>

                        <span>
                          {
                            order
                              .license_plate
                          }
                        </span>
                      </div>

                      <small>
                        Заказ №
                        {
                          order
                            .work_order_number
                        }
                      </small>
                    </div>
                  ),
                )}
              </div>
            </section>
          )}


          {debts.length > 0 && (
            <section className="vehicle-now-group">
              <div className="vehicle-now-heading">
                <WalletCards
                  size={15}
                />

                <strong>
                  Задолженность
                </strong>

                <span>
                  {debts.length}
                </span>
              </div>

              <div className="vehicle-now-list">
                {debts.map(
                  (debt) => (
                    <div
                      className="vehicle-now-row"
                      key={
                        debt
                          .work_order_number
                      }
                    >
                      <div>
                        <strong>
                          {
                            debt
                              .client_name
                          }
                        </strong>

                        <span>
                          Заказ №
                          {
                            debt
                              .work_order_number
                          }
                        </span>
                      </div>

                      <small className="vehicle-now-debt">
                        {formatMoney(
                          debt.debt,
                        )}
                      </small>
                    </div>
                  ),
                )}
              </div>
            </section>
          )}
        </div>
      )}
    </article>
  );
}