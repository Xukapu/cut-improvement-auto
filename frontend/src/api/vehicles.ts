import { apiRequest } from "./client";
import type {
  Vehicle,
  VehicleCreate,
  VehicleListResponse,
  VehicleUpdate,
} from "../types/vehicle";

export function listVehicles(
  search = "",
  limit = 100,
  clientNumber?: number,
): Promise<VehicleListResponse> {
  const params = new URLSearchParams({
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

  return apiRequest<VehicleListResponse>(
    `/api/v1/vehicles?${params.toString()}`,
  );
}

export function getVehicle(
  vehicleNumber: number,
): Promise<Vehicle> {
  return apiRequest<Vehicle>(
    `/api/v1/vehicles/${vehicleNumber}`,
  );
}

export function createVehicle(
  payload: VehicleCreate,
): Promise<Vehicle> {
  return apiRequest<Vehicle>(
    "/api/v1/vehicles",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
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
      body: JSON.stringify(payload),
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