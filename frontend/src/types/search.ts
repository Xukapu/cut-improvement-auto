export type SearchClientResult = {
  client_number: number;
  full_name: string;

  phone_primary: string;
  phone_secondary: string | null;

  source: string;
  internal_mark: boolean;
};


export type SearchVehicleResult = {
  vehicle_number: number;

  license_plate: string;
  vin: string | null;

  brand: string;
  model: string;

  year: number | null;
  mileage: number | null;

  current_owner_client_number: number;
  current_owner_name: string;
};


export type GlobalSearchResponse = {
  query: string;

  clients: SearchClientResult[];
  vehicles: SearchVehicleResult[];

  total_clients: number;
  total_vehicles: number;
  total: number;
};