import {
  ApiError,
  apiRequest,
} from "./client";

import {
  listClients,
} from "./clients";

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
  Client,
} from "../types/client";

import type {
  SyncQueuedOperation,
} from "../types/sync";

import type {
  Vehicle,
  VehicleCreate,
  VehicleListResponse,
  VehicleUpdate,
} from "../types/vehicle";


function pendingVehicleFromOperation(
  operation: SyncQueuedOperation,
  clients: Client[],
): Vehicle {
  const payload =
    operation.payload;

  const ownerId =
    typeof payload.owner_client_id ===
      "string"
      ? payload.owner_client_id
      : "";

  const owner =
    clients.find(
      (client) =>
        client.id === ownerId,
    );

  return {
    id:
      operation.entity_id,

    license_plate:
      String(
        payload.license_plate ??
        "",
      ),

    vin:
      typeof payload.vin ===
        "string"
        ? payload.vin
        : null,

    brand:
      String(
        payload.brand ??
        "",
      ),

    model:
      String(
        payload.model ??
        "",
      ),

    year:
      typeof payload.year ===
        "number"
        ? payload.year
        : null,

    mileage:
      typeof payload.mileage ===
        "number"
        ? payload.mileage
        : null,

    vehicle_number: 0,

    current_owner_client_number:
      owner?.client_number ??
      0,

    current_owner_name:
      owner?.full_name ??
      String(
        payload.owner_client_name ??
        "Владелец",
      ),

    sync_pending: true,
  };
}


function matchesSearch(
  vehicle: Vehicle,
  search: string,
): boolean {
  const value =
    search
      .trim()
      .toLocaleLowerCase();

  if (!value) {
    return true;
  }

  return [
    vehicle.license_plate,
    vehicle.vin ?? "",
    vehicle.brand,
    vehicle.model,
  ].some(
    (item) =>
      item
        .toLocaleLowerCase()
        .includes(value),
  );
}


export async function listVehicles(
  search = "",
  limit = 100,
  clientNumber?: number,
): Promise<VehicleListResponse> {
  const params =
    new URLSearchParams({
      limit: String(limit),
      offset: "0",
    });

  if (search.trim()) {
    params.set(
      "search",
      search.trim(),
    );
  }

  if (
    clientNumber !== undefined
  ) {
    params.set(
      "client_number",
      String(clientNumber),
    );
  }


  const response =
    await apiRequest<VehicleListResponse>(
      `/api/v1/vehicles?${params.toString()}`,
    );


  const operations =
    await listPendingSyncOperations();

  const pendingOperations =
    operations.filter(
      (operation) =>
        operation.kind ===
        "vehicle.create",
    );


  if (
    pendingOperations.length === 0
  ) {
    return response;
  }


  const clientData =
    await listClients(
      "",
      100,
    );


  const knownIds =
    new Set(
      response.items.map(
        (vehicle) =>
          vehicle.id,
      ),
    );


  const pendingVehicles =
    pendingOperations
      .filter(
        (operation) =>
          !knownIds.has(
            operation.entity_id,
          ),
      )
      .map(
        (operation) =>
          pendingVehicleFromOperation(
            operation,
            clientData.items,
          ),
      )
      .filter(
        (vehicle) =>
          matchesSearch(
            vehicle,
            search,
          ),
      )
      .filter(
        (vehicle) =>
          clientNumber ===
            undefined ||
          vehicle
            .current_owner_client_number ===
            clientNumber,
      );


  return {
    ...response,

    items: [
      ...pendingVehicles,
      ...response.items,
    ],

    total:
      response.total +
      pendingVehicles.length,
  };
}


export function getVehicle(
  vehicleNumber: number,
): Promise<Vehicle> {
  return apiRequest<Vehicle>(
    `/api/v1/vehicles/${vehicleNumber}`,
  );
}


export async function createVehicle(
  payload: VehicleCreate,
): Promise<Vehicle> {
  const canUseNormalApi =
    payload.owner_client_number !==
      null &&
    payload.owner_client_number > 0;


  if (canUseNormalApi) {
    try {
      return await apiRequest<Vehicle>(
        "/api/v1/vehicles",
        {
          method: "POST",

          body: JSON.stringify({
            license_plate:
              payload.license_plate,

            vin:
              payload.vin,

            brand:
              payload.brand,

            model:
              payload.model,

            year:
              payload.year,

            mileage:
              payload.mileage,

            owner_client_number:
              payload.owner_client_number,
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
      "vehicle.create",

      entityId,

      {
        license_plate:
          payload.license_plate,

        vin:
          payload.vin,

        brand:
          payload.brand,

        model:
          payload.model,

        year:
          payload.year,

        mileage:
          payload.mileage,

        owner_client_id:
          payload.owner_client_id,

        owner_client_name:
          payload.owner_client_name,
      },
    );


  return pendingVehicleFromOperation(
    operation,
    [
      {
        id:
          payload.owner_client_id,

        client_number:
          payload
            .owner_client_number ??
          0,

        full_name:
          payload.owner_client_name,

        phone_primary: "",
        phone_secondary: null,

        source: "other",

        referred_by_client_number:
          null,

        referred_by_client_name:
          null,

        internal_mark: false,

        notes: null,

        created_at:
          new Date().toISOString(),

        updated_at:
          new Date().toISOString(),

        sync_pending:
          payload
            .owner_client_number ===
          null,
      },
    ],
  );
}


export function updateVehicle(
  vehicleNumber: number,
  payload: VehicleUpdate,
): Promise<Vehicle> {
  return apiRequest<Vehicle>(
    `/api/v1/vehicles/${vehicleNumber}`,
    {
      method: "PUT",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function transferVehicle(
  vehicleNumber: number,
  newOwnerClientNumber: number,
): Promise<Vehicle> {
  return apiRequest<Vehicle>(
    `/api/v1/vehicles/${vehicleNumber}/transfer`,
    {
      method: "POST",

      body: JSON.stringify({
        new_owner_client_number:
          newOwnerClientNumber,
      }),
    },
  );
}