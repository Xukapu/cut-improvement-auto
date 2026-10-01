import {
  Download,
  ExternalLink,
  FileText,
  X,
} from "lucide-react";
import {
  useState,
} from "react";

import type {
  Vehicle,
} from "../types/vehicle";
import type {
  Part,
  PaymentSummary,
  RecommendedWork,
  WorkItemFinancial,
  WorkItemPublic,
  WorkOrder,
} from "../types/workOrder";


type DocumentType =
  | "order"
  | "act";


type Props = {
  order: WorkOrder;

  vehicle:
    | Vehicle
    | undefined;

  works: Array<
    WorkItemPublic |
    WorkItemFinancial
  >;

  parts: Part[];

  recommended:
    RecommendedWork[];

  paymentSummary:
    | PaymentSummary
    | null;

  onClose: () => void;
};


function workOrderPdfUrl(
  workOrderNumber: number,
): string {
  return (
    `/api/v1/work-orders/` +
    `${workOrderNumber}` +
    `/documents/work-order.pdf`
  );
}


function completionActPdfUrl(
  workOrderNumber: number,
): string {
  return (
    `/api/v1/work-orders/` +
    `${workOrderNumber}` +
    `/documents/completion-act.pdf`
  );
}


export function WorkOrderPrintPreview({
  order,
  vehicle,
  works,
  parts,
  recommended,
  paymentSummary,
  onClose,
}: Props) {
  void vehicle;
  void works;
  void parts;
  void recommended;
  void paymentSummary;

  const actAvailable =
    order.status === "ready" ||
    order.status === "issued";

  const [
    documentType,
    setDocumentType,
  ] = useState<DocumentType>(
    "order",
  );

  const pdfUrl =
    documentType === "order"
      ? workOrderPdfUrl(
          order.work_order_number,
        )
      : completionActPdfUrl(
          order.work_order_number,
        );

  const documentName =
    documentType === "order"
      ? `Заказ-наряд №${order.work_order_number}`
      : `Акт выполненных работ №${order.work_order_number}`;


  return (
    <div
      aria-modal="true"
      className="wo-pdf-overlay"
      role="dialog"
    >
      <div className="wo-pdf-window">
        <header className="wo-pdf-toolbar">
          <div className="wo-pdf-toolbar-left">
            <FileText size={20} />

            <div>
              <strong>
                Печатные документы
              </strong>

              <span>
                {documentName}
              </span>
            </div>
          </div>


          <div className="wo-pdf-toolbar-right">
            <a
              className="wo-pdf-action"
              href={pdfUrl}
              rel="noreferrer"
              target="_blank"
            >
              <ExternalLink
                size={15}
              />
              Открыть отдельно
            </a>

            <a
              className="wo-pdf-action"
              download
              href={pdfUrl}
            >
              <Download
                size={15}
              />
              Скачать PDF
            </a>

            <button
              aria-label="Закрыть"
              className="wo-pdf-close"
              onClick={onClose}
              type="button"
            >
              <X size={19} />
            </button>
          </div>
        </header>


        <div className="wo-pdf-switcher">
          <button
            className={
              documentType === "order"
                ? "wo-pdf-type wo-pdf-type-active"
                : "wo-pdf-type"
            }
            onClick={() => {
              setDocumentType(
                "order",
              );
            }}
            type="button"
          >
            Заказ-наряд
          </button>

          <button
            className={
              documentType === "act"
                ? "wo-pdf-type wo-pdf-type-active"
                : "wo-pdf-type"
            }
            disabled={
              !actAvailable
            }
            onClick={() => {
              if (
                actAvailable
              ) {
                setDocumentType(
                  "act",
                );
              }
            }}
            title={
              actAvailable
                ? "Акт выполненных работ"
                : "Акт станет доступен, когда ремонт будет готов или выдан"
            }
            type="button"
          >
            Акт выполненных работ
          </button>

          {!actAvailable && (
            <span className="wo-pdf-act-note">
              Акт доступен после завершения ремонта
            </span>
          )}
        </div>


        <div className="wo-pdf-viewer">
          <iframe
            key={pdfUrl}
            src={pdfUrl}
            title={documentName}
          />
        </div>
      </div>
    </div>
  );
}