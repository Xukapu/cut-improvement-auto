import {
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  UserX,
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
  loading: boolean;
  onRefresh: () => void;
};


export function DashboardAttentionCard({
  dashboard,
  loading,
  onRefresh,
}: Props) {
  const noShow =
    dashboard?.no_show_count ?? 0;

  const ready =
    dashboard?.ready_count ?? 0;

  const debt =
    Number(
      dashboard?.debt_total ?? 0,
    );

  const hasAttention =
    noShow > 0 ||
    ready > 0 ||
    debt > 0;


  return (
    <section className="attention-panel">
      <div className="attention-header">
        <div>
          <span className="card-kicker">
            Рабочая смена
          </span>

          <h2>
            Требует внимания
          </h2>
        </div>

        <button
          className="refresh-button"
          disabled={loading}
          onClick={onRefresh}
          type="button"
        >
          <RefreshCw
            className={
              loading
                ? "spin"
                : ""
            }
            size={17}
          />

          Обновить
        </button>
      </div>


      {loading && !dashboard ? (
        <div className="attention-calm">
          Обновляем данные...
        </div>
      ) : !hasAttention ? (
        <div className="attention-calm">
          <CheckCircle2
            size={19}
          />

          <div>
            <strong>
              На сегодня всё спокойно
            </strong>

            <span>
              Нет событий, требующих
              отдельного внимания.
            </span>
          </div>
        </div>
      ) : (
        <div className="attention-list">

          {noShow > 0 && (
            <div className="attention-item">
              <UserX size={18} />

              <div>
                <strong>
                  Не приехали на запись
                </strong>

                <span>
                  Количество: {noShow}
                </span>
              </div>
            </div>
          )}


          {ready > 0 && (
            <div className="attention-item">
              <Wrench size={18} />

              <div>
                <strong>
                  Есть автомобили,
                  готовые к выдаче
                </strong>

                <span>
                  Количество: {ready}
                </span>
              </div>
            </div>
          )}


          {debt > 0 && (
            <div className="attention-item attention-item-warning">
              <WalletCards
                size={18}
              />

              <div>
                <strong>
                  Есть задолженность
                </strong>

                <span>
                  {formatMoney(
                    dashboard
                      ?.debt_total ??
                      "0",
                  )}
                </span>
              </div>
            </div>
          )}


          {!noShow &&
            !ready &&
            debt <= 0 && (
              <div className="attention-item">
                <AlertTriangle
                  size={18}
                />

                <span>
                  Проверьте текущую
                  рабочую смену.
                </span>
              </div>
            )}
        </div>
      )}
    </section>
  );
}