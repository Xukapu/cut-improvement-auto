import {
  apiRequest,
} from "./client";

import type {
  Dispute,
  DisputeListResponse,
  DisputePayload,
  DisputePhoto,
  DisputePhotoListResponse,
  EmployeePublic,
  Part,
  PartListResponse,
  PartPayload,
  Payment,
  PaymentPayload,
  PaymentSummary,
  RecommendedWork,
  RecommendedWorkListResponse,
  RecommendedWorkPayload,
  WorkItemFinancial,
  WorkItemFinancialListResponse,
  WorkItemListResponse,
  WorkItemPayload,
  WorkOrder,
  WorkOrderCreatePayload,
  WorkOrderListResponse,
  WorkOrderStatus,
  WorkOrderUpdatePayload,
} from "../types/workOrder";


type ListWorkOrderOptions = {
  status?: WorkOrderStatus;
  clientNumber?: number;
  vehicleNumber?: number;
};


export function listWorkOrders(
  options:
    ListWorkOrderOptions = {},
): Promise<WorkOrderListResponse> {
  const params =
    new URLSearchParams({
      limit: "100",
      offset: "0",
    });

  if (options.status) {
    params.set(
      "status",
      options.status,
    );
  }

  if (
    options.clientNumber !==
    undefined
  ) {
    params.set(
      "client_number",
      String(
        options.clientNumber,
      ),
    );
  }

  if (
    options.vehicleNumber !==
    undefined
  ) {
    params.set(
      "vehicle_number",
      String(
        options.vehicleNumber,
      ),
    );
  }

  return apiRequest<
    WorkOrderListResponse
  >(
    `/api/v1/work-orders?${params.toString()}`,
  );
}


export function getWorkOrder(
  workOrderNumber: number,
): Promise<WorkOrder> {
  return apiRequest<WorkOrder>(
    `/api/v1/work-orders/${workOrderNumber}`,
  );
}


export function createWorkOrder(
  payload:
    WorkOrderCreatePayload,
): Promise<WorkOrder> {
  return apiRequest<WorkOrder>(
    "/api/v1/work-orders",
    {
      method: "POST",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updateWorkOrder(
  workOrderNumber: number,
  payload:
    WorkOrderUpdatePayload,
): Promise<WorkOrder> {
  return apiRequest<WorkOrder>(
    `/api/v1/work-orders/${workOrderNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function changeWorkOrderStatus(
  workOrderNumber: number,
  status: WorkOrderStatus,
): Promise<WorkOrder> {
  return apiRequest<WorkOrder>(
    `/api/v1/work-orders/${workOrderNumber}/status`,
    {
      method: "PATCH",
      body: JSON.stringify({
        status,
      }),
    },
  );
}


export function listEmployees():
  Promise<EmployeePublic[]> {
  return apiRequest<
    EmployeePublic[]
  >(
    "/api/v1/employees?include_inactive=false",
  );
}


export function listWorks(
  workOrderNumber: number,
): Promise<WorkItemListResponse> {
  return apiRequest<
    WorkItemListResponse
  >(
    `/api/v1/work-orders/${workOrderNumber}/works`,
  );
}


export function listWorksFinancial(
  workOrderNumber: number,
): Promise<WorkItemFinancialListResponse> {
  return apiRequest<
    WorkItemFinancialListResponse
  >(
    `/api/v1/work-orders/${workOrderNumber}/works/financial`,
  );
}


export function createWork(
  workOrderNumber: number,
  payload: WorkItemPayload,
): Promise<WorkItemFinancial> {
  return apiRequest<
    WorkItemFinancial
  >(
    `/api/v1/work-orders/${workOrderNumber}/works`,
    {
      method: "POST",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updateWork(
  workOrderNumber: number,
  workItemNumber: number,
  payload: WorkItemPayload,
): Promise<WorkItemFinancial> {
  return apiRequest<
    WorkItemFinancial
  >(
    `/api/v1/work-orders/${workOrderNumber}/works/${workItemNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function listParts(
  workOrderNumber: number,
): Promise<PartListResponse> {
  return apiRequest<
    PartListResponse
  >(
    `/api/v1/work-orders/${workOrderNumber}/parts`,
  );
}


export function createPart(
  workOrderNumber: number,
  payload: PartPayload,
): Promise<Part> {
  return apiRequest<Part>(
    `/api/v1/work-orders/${workOrderNumber}/parts`,
    {
      method: "POST",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updatePart(
  workOrderNumber: number,
  partNumber: number,
  payload: PartPayload,
): Promise<Part> {
  return apiRequest<Part>(
    `/api/v1/work-orders/${workOrderNumber}/parts/${partNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export async function deletePart(
  workOrderNumber: number,
  partNumber: number,
): Promise<void> {
  await apiRequest<void>(
    `/api/v1/work-orders/${workOrderNumber}/parts/${partNumber}`,
    {
      method: "DELETE",
      skipJson: true,
    },
  );
}


export function listRecommendedWorks(
  workOrderNumber: number,
): Promise<RecommendedWorkListResponse> {
  return apiRequest<
    RecommendedWorkListResponse
  >(
    `/api/v1/work-orders/${workOrderNumber}/recommended-works`,
  );
}


export function createRecommendedWork(
  workOrderNumber: number,
  payload:
    RecommendedWorkPayload,
): Promise<RecommendedWork> {
  return apiRequest<
    RecommendedWork
  >(
    `/api/v1/work-orders/${workOrderNumber}/recommended-works`,
    {
      method: "POST",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updateRecommendedWork(
  workOrderNumber: number,
  recommendedWorkNumber: number,
  payload:
    RecommendedWorkPayload,
): Promise<RecommendedWork> {
  return apiRequest<
    RecommendedWork
  >(
    `/api/v1/work-orders/${workOrderNumber}/recommended-works/${recommendedWorkNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export async function deleteRecommendedWork(
  workOrderNumber: number,
  recommendedWorkNumber: number,
): Promise<void> {
  await apiRequest<void>(
    `/api/v1/work-orders/${workOrderNumber}/recommended-works/${recommendedWorkNumber}`,
    {
      method: "DELETE",
      skipJson: true,
    },
  );
}


export function listDisputes(
  workOrderNumber: number,
): Promise<DisputeListResponse> {
  return apiRequest<
    DisputeListResponse
  >(
    `/api/v1/work-orders/${workOrderNumber}/disputes`,
  );
}


export function createDispute(
  workOrderNumber: number,
  payload: DisputePayload,
): Promise<Dispute> {
  return apiRequest<Dispute>(
    `/api/v1/work-orders/${workOrderNumber}/disputes`,
    {
      method: "POST",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updateDispute(
  workOrderNumber: number,
  disputeNumber: number,
  payload: DisputePayload,
): Promise<Dispute> {
  return apiRequest<Dispute>(
    `/api/v1/work-orders/${workOrderNumber}/disputes/${disputeNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export async function deleteDispute(
  workOrderNumber: number,
  disputeNumber: number,
): Promise<void> {
  await apiRequest<void>(
    `/api/v1/work-orders/${workOrderNumber}/disputes/${disputeNumber}`,
    {
      method: "DELETE",
      skipJson: true,
    },
  );
}


export function listDisputePhotos(
  workOrderNumber: number,
  disputeNumber: number,
): Promise<DisputePhotoListResponse> {
  return apiRequest<
    DisputePhotoListResponse
  >(
    `/api/v1/work-orders/${workOrderNumber}/disputes/${disputeNumber}/photos`,
  );
}


export function uploadDisputePhoto(
  workOrderNumber: number,
  disputeNumber: number,
  file: File,
): Promise<DisputePhoto> {
  const formData =
    new FormData();

  formData.append(
    "file",
    file,
  );

  return apiRequest<
    DisputePhoto
  >(
    `/api/v1/work-orders/${workOrderNumber}/disputes/${disputeNumber}/photos`,
    {
      method: "POST",
      body: formData,
    },
  );
}


export async function deleteDisputePhoto(
  workOrderNumber: number,
  disputeNumber: number,
  photoNumber: number,
): Promise<void> {
  await apiRequest<void>(
    `/api/v1/work-orders/${workOrderNumber}/disputes/${disputeNumber}/photos/${photoNumber}`,
    {
      method: "DELETE",
      skipJson: true,
    },
  );
}


export function disputePhotoUrl(
  workOrderNumber: number,
  disputeNumber: number,
  photoNumber: number,
): string {
  return (
    `/api/v1/work-orders/${workOrderNumber}` +
    `/disputes/${disputeNumber}` +
    `/photos/${photoNumber}/file`
  );
}


export function getPaymentSummary(
  workOrderNumber: number,
): Promise<PaymentSummary> {
  return apiRequest<
    PaymentSummary
  >(
    `/api/v1/work-orders/${workOrderNumber}/payment`,
  );
}


export function createPayment(
  workOrderNumber: number,
  payload: PaymentPayload,
): Promise<Payment> {
  return apiRequest<Payment>(
    `/api/v1/work-orders/${workOrderNumber}/payments`,
    {
      method: "POST",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updatePayment(
  workOrderNumber: number,
  paymentNumber: number,
  payload: PaymentPayload,
): Promise<Payment> {
  return apiRequest<Payment>(
    `/api/v1/work-orders/${workOrderNumber}/payments/${paymentNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export async function deletePayment(
  workOrderNumber: number,
  paymentNumber: number,
): Promise<void> {
  await apiRequest<void>(
    `/api/v1/work-orders/${workOrderNumber}/payments/${paymentNumber}`,
    {
      method: "DELETE",
      skipJson: true,
    },
  );
}