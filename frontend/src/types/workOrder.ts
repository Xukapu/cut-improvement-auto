export type WorkOrderStatus =
  | "planned"
  | "in_progress"
  | "ready"
  | "issued";


export type WorkOrder = {
  work_order_number: number;

  client_number: number;
  client_name: string;

  vehicle_number: number;
  license_plate: string;

  appointment_number: number | null;

  status: WorkOrderStatus;

  reason: string;
  mileage: number | null;

  created_at: string;
  started_at: string | null;
  ready_at: string | null;
  issued_at: string | null;
};


export type WorkOrderListResponse = {
  items: WorkOrder[];
  total: number;
  limit: number;
  offset: number;
};


export type WorkOrderCreatePayload = {
  client_number: number;
  vehicle_number: number;
  appointment_number: number | null;
  reason: string;
  mileage: number | null;
};


export type WorkOrderUpdatePayload = {
  reason: string;
  mileage: number | null;
};


export type EmployeePublic = {
  employee_number: number;
  full_name: string;
  is_active: boolean;
};


export type WorkAssignmentInput = {
  employee_number: number;
  share_percent: number;
};


export type WorkAssignmentPublic = {
  employee_number: number;
  employee_name: string;
};


export type WorkAssignmentFinancial =
  WorkAssignmentPublic & {
    share_percent:
      | string
      | number;

    rate_percent_snapshot:
      | string
      | number;

    earning_amount:
      | string
      | number;
  };


export type WorkItemPublic = {
  work_item_number: number;

  name: string;

  price:
    | string
    | number;

  assignments:
    WorkAssignmentPublic[];
};


export type WorkItemFinancial = {
  work_item_number: number;

  name: string;

  price:
    | string
    | number;

  assignments:
    WorkAssignmentFinancial[];

  total_employee_earnings:
    | string
    | number;
};


export type WorkItemListResponse = {
  items: WorkItemPublic[];
  total: number;
};


export type WorkItemFinancialListResponse = {
  items: WorkItemFinancial[];
  total: number;
};


export type WorkItemPayload = {
  name: string;

  price:
    | string
    | number;

  assignments:
    WorkAssignmentInput[];
};


export type PartProvidedBy =
  | "sto"
  | "client";


export type Part = {
  part_number: number;

  name: string;

  quantity: number;

  unit_price:
    | string
    | number;

  total_price:
    | string
    | number;

  supplier: string | null;

  provided_by:
    PartProvidedBy;
};


export type PartListResponse = {
  items: Part[];
  total: number;

  total_price:
    | string
    | number;
};


export type PartPayload = {
  name: string;
  quantity: number;

  unit_price:
    | string
    | number;

  supplier: string | null;

  provided_by:
    PartProvidedBy;
};


export type RecommendedWork = {
  recommended_work_number: number;
  name: string;
  comment: string | null;
};


export type RecommendedWorkListResponse = {
  items: RecommendedWork[];
  total: number;
};


export type RecommendedWorkPayload = {
  name: string;
  comment: string | null;
};


export type Dispute = {
  dispute_number: number;

  found_text: string;

  master_recommendation:
    string | null;

  client_response:
    string | null;

  recorded_at: string;
};


export type DisputeListResponse = {
  items: Dispute[];
  total: number;
};


export type DisputePayload = {
  found_text: string;

  master_recommendation:
    string | null;

  client_response:
    string | null;
};


export type DisputePhoto = {
  photo_number: number;

  original_filename: string;

  content_type:
    string | null;

  size_bytes: number;
};


export type DisputePhotoListResponse = {
  items: DisputePhoto[];
  total: number;
};


export type PaymentMethod =
  | "cash"
  | "card"
  | "transfer";


export type Payment = {
  payment_number: number;

  amount:
    | string
    | number;

  method: PaymentMethod;

  comment: string | null;

  paid_at: string;
};


export type PaymentSummary = {
  work_order_number: number;

  works_total:
    | string
    | number;

  parts_total:
    | string
    | number;

  repair_total:
    | string
    | number;

  paid_amount:
    | string
    | number;

  debt_amount:
    | string
    | number;

  payments: Payment[];
};


export type PaymentPayload = {
  amount:
    | string
    | number;

  method: PaymentMethod;

  comment: string | null;
};