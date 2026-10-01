export type ClientSource =
  | "avito"
  | "referral"
  | "other";

export type ArchiveReason =
  | "no_longer_serviced"
  | "created_by_mistake"
  | "owner_request"
  | "other";

export type Client = {
  client_number: number;
  full_name: string;
  phone_primary: string;
  phone_secondary: string | null;
  source: ClientSource;
  referred_by_client_number: number | null;
  referred_by_client_name: string | null;
  internal_mark: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ArchivedClient = Client & {
  archived_at: string;
  archive_reason: ArchiveReason;
  archive_comment: string | null;
};

export type ClientListResponse = {
  items: Client[];
  total: number;
  limit: number;
  offset: number;
};

export type ArchivedClientListResponse = {
  items: ArchivedClient[];
  total: number;
  limit: number;
  offset: number;
};

export type ClientCreate = {
  full_name: string;
  phone_primary: string;
  phone_secondary: string | null;
  source: ClientSource;
  referred_by_client_number: number | null;
  notes: string | null;
  internal_mark?: boolean;
};

export type ClientUpdate = {
  full_name: string;
  phone_primary: string;
  phone_secondary: string | null;
  source: ClientSource;
  referred_by_client_number: number | null;
  notes: string | null;
};
