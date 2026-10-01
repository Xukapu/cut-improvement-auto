export type DashboardAppointment = {
  appointment_number: number;
  appointment_time: string;

  client_number: number;
  client_name: string;

  vehicle_number: number;
  vehicle_name: string;
  license_plate: string | null;

  reason: string;
  status: "scheduled" | "no_show";
};

export type DashboardWorkOrder = {
  work_order_number: number;

  client_number: number;
  client_name: string;

  vehicle_number: number;
  vehicle_name: string;
  license_plate: string | null;

  status:
    | "planned"
    | "in_progress"
    | "ready"
    | "issued";

  reason: string;
};

export type DashboardDebt = {
  work_order_number: number;

  client_number: number;
  client_name: string;

  repair_total: string;
  paid: string;
  debt: string;
};

export type DashboardResponse = {
  report_date: string;

  appointments_today: DashboardAppointment[];
  in_progress: DashboardWorkOrder[];
  ready: DashboardWorkOrder[];
  debts: DashboardDebt[];

  scheduled_count: number;
  no_show_count: number;
  in_progress_count: number;
  ready_count: number;

  debt_total: string;
};