export type AppointmentStatus =
  | "scheduled"
  | "no_show";


export type Appointment = {
  id: string;

  appointment_number: number;

  client_number: number;
  client_name: string;

  vehicle_number: number;
  license_plate: string;

  appointment_date: string;
  appointment_time: string;

  reason: string;

  comment:
    | string
    | null;

  status: AppointmentStatus;

  sync_pending?: boolean;
};


export type AppointmentListResponse = {
  items: Appointment[];

  total: number;
  limit: number;
  offset: number;
};


export type AppointmentInput = {
  client_number: number;
  vehicle_number: number;

  appointment_date: string;
  appointment_time: string;

  reason: string;

  comment:
    | string
    | null;

  status: AppointmentStatus;
};


export type AppointmentCreateInput = {
  client_id: string;

  client_number:
    | number
    | null;

  client_name: string;

  vehicle_id: string;

  vehicle_number:
    | number
    | null;

  license_plate: string;

  appointment_date: string;
  appointment_time: string;

  reason: string;

  comment:
    | string
    | null;

  status: AppointmentStatus;
};