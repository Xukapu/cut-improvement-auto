import { apiRequest } from "./client";
import type {
  ArchivedClient,
  ArchivedClientListResponse,
  ArchiveReason,
  Client,
  ClientCreate,
  ClientListResponse,
  ClientUpdate,
} from "../types/client";

export function listClients(
  search = "",
  limit = 100,
): Promise<ClientListResponse> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: "0",
  });

  if (search.trim()) {
    params.set("search", search.trim());
  }

  return apiRequest<ClientListResponse>(
    `/api/v1/clients?${params.toString()}`,
  );
}

export function listArchivedClients(
  search = "",
  limit = 100,
): Promise<ArchivedClientListResponse> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: "0",
  });

  if (search.trim()) {
    params.set("search", search.trim());
  }

  return apiRequest<ArchivedClientListResponse>(
    `/api/v1/clients/archive?${params.toString()}`,
  );
}

export function getClient(
  clientNumber: number,
): Promise<Client> {
  return apiRequest<Client>(
    `/api/v1/clients/${clientNumber}`,
  );
}

export function createClient(
  payload: ClientCreate,
): Promise<Client> {
  return apiRequest<Client>(
    "/api/v1/clients",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateClient(
  clientNumber: number,
  payload: ClientUpdate,
): Promise<Client> {
  return apiRequest<Client>(
    `/api/v1/clients/${clientNumber}`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
  );
}

export function setClientInternalMark(
  clientNumber: number,
  internalMark: boolean,
): Promise<Client> {
  return apiRequest<Client>(
    `/api/v1/clients/${clientNumber}/internal-mark`,
    {
      method: "PATCH",
      body: JSON.stringify({
        internal_mark: internalMark,
      }),
    },
  );
}

export function archiveClient(
  clientNumber: number,
  reason: ArchiveReason,
  comment: string | null,
): Promise<ArchivedClient> {
  return apiRequest<ArchivedClient>(
    `/api/v1/clients/${clientNumber}/archive`,
    {
      method: "POST",
      body: JSON.stringify({
        confirm: true,
        reason,
        comment,
      }),
    },
  );
}

export function restoreClient(
  clientNumber: number,
): Promise<Client> {
  return apiRequest<Client>(
    `/api/v1/clients/${clientNumber}/restore`,
    {
      method: "POST",
    },
  );
}
