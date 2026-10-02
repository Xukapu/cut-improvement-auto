export type Vehicle = {
  id: string;

  license_plate: string;
  vin: string | null;
  brand: string;
  model: string;

  year: number | null;
  mileage: number | null;

  vehicle_number: number;

  current_owner_client_number: number;
  current_owner_name: string;

  sync_pending?: boolean;
};


export type VehicleListResponse = {
  items: Vehicle[];

  total: number;
  limit: number;
  offset: number;
};


export type VehicleCreate = {
  license_plate: string;
  vin: string | null;
  brand: string;
  model: string;

  year: number | null;
  mileage: number | null;

  owner_client_id: string;

  owner_client_number:
    | number
    | null;

  owner_client_name: string;
};


export type VehicleUpdate = {
  license_plate: string;
  vin: string | null;
  brand: string;
  model: string;

  year: number | null;
  mileage: number | null;
};