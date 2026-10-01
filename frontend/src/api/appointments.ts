import {
  apiRequest,
} from "./client";

import type {
  Appointment,
  AppointmentInput,
  AppointmentListResponse,
  AppointmentStatus,
} from "../types/appointment";

type ListOptions = {
  date?: string;
  status?: AppointmentStatus;
  clientNumber?: number;
  vehicleNumber?: number;
};

export function listAppointments(
  options: ListOptions = {},
): Promise<AppointmentListResponse> {
  const params =
    new URLSearchParams({
      limit: "100",
      offset: "0",
    });

  if (options.date) {
    params.set(
      "appointment_date",
      options.date,
    );
  }

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

  return apiRequest<AppointmentListResponse>(
    `/api/v1/appointments?${params.toString()}`,
  );
}

export function createAppointment(
  payload: AppointmentInput,
): Promise<Appointment> {
  return apiRequest<Appointment>(
    "/api/v1/appointments",
    {
      method: "POST",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}

export function updateAppointment(
  appointmentNumber: number,
  payload: AppointmentInput,
): Promise<Appointment> {
  return apiRequest<Appointment>(
    `/api/v1/appointments/${appointmentNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(
        payload,
      ),
    },
  );
}