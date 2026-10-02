import {
  ApiError,
  apiRequest,
} from "./client";

import {
  createSyncUuid,
} from "./sync";

import {
  listPendingSyncOperations,
} from "../offline/offlineStore";

import {
  queueSyncOperation,
} from "../sync/syncQueue";

import type {
  Appointment,
  AppointmentCreateInput,
  AppointmentInput,
  AppointmentListResponse,
  AppointmentStatus,
} from "../types/appointment";

import type {
  SyncQueuedOperation,
} from "../types/sync";


type ListOptions = {
  date?: string;

  status?:
    AppointmentStatus;

  clientNumber?: number;
  vehicleNumber?: number;
};


function pendingAppointmentFromOperation(
  operation:
    SyncQueuedOperation,
): Appointment {
  const payload =
    operation.payload;

  return {
    id:
      operation.entity_id,

    appointment_number: 0,

    client_number:
      typeof payload
        .client_number ===
        "number"
        ? payload.client_number
        : 0,

    client_name:
      String(
        payload.client_name ??
        "Клиент",
      ),

    vehicle_number:
      typeof payload
        .vehicle_number ===
        "number"
        ? payload.vehicle_number
        : 0,

    license_plate:
      String(
        payload.license_plate ??
        "",
      ),

    appointment_date:
      String(
        payload.appointment_date ??
        "",
      ),

    appointment_time:
      String(
        payload.appointment_time ??
        "",
      ),

    reason:
      String(
        payload.reason ??
        "",
      ),

    comment:
      typeof payload.comment ===
        "string"
        ? payload.comment
        : null,

    status:
      String(
        payload.status ??
        "scheduled",
      ) as AppointmentStatus,

    sync_pending: true,
  };
}


function matchesOptions(
  appointment: Appointment,
  options: ListOptions,
): boolean {
  if (
    options.date &&
    appointment
      .appointment_date !==
      options.date
  ) {
    return false;
  }

  if (
    options.status &&
    appointment.status !==
      options.status
  ) {
    return false;
  }

  if (
    options.clientNumber !==
      undefined &&
    appointment.client_number !==
      options.clientNumber
  ) {
    return false;
  }

  if (
    options.vehicleNumber !==
      undefined &&
    appointment.vehicle_number !==
      options.vehicleNumber
  ) {
    return false;
  }

  return true;
}


export async function listAppointments(
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


  let response:
    AppointmentListResponse;


  try {
    response =
      await apiRequest<AppointmentListResponse>(
        `/api/v1/appointments?${params.toString()}`,
      );
  } catch (error) {
    const offline =
      error instanceof
        ApiError &&
      (
        error.status === 0 ||
        error.status >= 500
      );

    if (!offline) {
      throw error;
    }

    response = {
      items: [],
      total: 0,
      limit: 100,
      offset: 0,
    };
  }


  const operations =
    await listPendingSyncOperations();

  const knownIds =
    new Set(
      response.items.map(
        (appointment) =>
          appointment.id,
      ),
    );


  const pending =
    operations
      .filter(
        (operation) =>
          operation.kind ===
          "appointment.create",
      )
      .filter(
        (operation) =>
          !knownIds.has(
            operation.entity_id,
          ),
      )
      .map(
        pendingAppointmentFromOperation,
      )
      .filter(
        (appointment) =>
          matchesOptions(
            appointment,
            options,
          ),
      );


  const items = [
    ...pending,
    ...response.items,
  ].sort(
    (
      left,
      right,
    ) =>
      left.appointment_time
        .localeCompare(
          right.appointment_time,
        ),
  );


  return {
    ...response,

    items,

    total:
      response.total +
      pending.length,
  };
}


export async function createAppointment(
  payload:
    AppointmentCreateInput,
): Promise<Appointment> {
  const canUseNormalApi =
    payload.client_number !==
      null &&
    payload.client_number > 0 &&
    payload.vehicle_number !==
      null &&
    payload.vehicle_number > 0;


  if (canUseNormalApi) {
    try {
      return await apiRequest<Appointment>(
        "/api/v1/appointments",
        {
          method: "POST",

          body: JSON.stringify({
            client_number:
              payload.client_number,

            vehicle_number:
              payload.vehicle_number,

            appointment_date:
              payload.appointment_date,

            appointment_time:
              payload.appointment_time,

            reason:
              payload.reason,

            comment:
              payload.comment,

            status:
              payload.status,
          }),
        },
      );
    } catch (error) {
      const offline =
        error instanceof
          ApiError &&
        (
          error.status === 0 ||
          error.status >= 500
        );

      if (!offline) {
        throw error;
      }
    }
  }


  const entityId =
    createSyncUuid();


  const operation =
    await queueSyncOperation(
      "appointment.create",

      entityId,

      {
        client_id:
          payload.client_id,

        client_number:
          payload.client_number,

        client_name:
          payload.client_name,

        vehicle_id:
          payload.vehicle_id,

        vehicle_number:
          payload.vehicle_number,

        license_plate:
          payload.license_plate,

        appointment_date:
          payload.appointment_date,

        appointment_time:
          payload.appointment_time,

        reason:
          payload.reason,

        comment:
          payload.comment,

        status:
          payload.status,
      },
    );


  return pendingAppointmentFromOperation(
    operation,
  );
}


export function updateAppointment(
  appointmentNumber: number,
  payload:
    AppointmentInput,
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