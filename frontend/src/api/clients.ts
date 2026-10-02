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
  ArchivedClient,
  ArchivedClientListResponse,
  ArchiveReason,
  Client,
  ClientCreate,
  ClientListResponse,
  ClientSource,
  ClientUpdate,
} from "../types/client";

import type {
  SyncQueuedOperation,
} from "../types/sync";


function pendingClientFromOperation(
  operation:
    SyncQueuedOperation,
  knownClients:
    Client[],
): Client {
  const payload =
    operation.payload;

  const referrerId =
    typeof payload
      .referred_by_client_id ===
      "string"
      ? payload
          .referred_by_client_id
      : null;

  const referrer =
    referrerId
      ? knownClients.find(
          (client) =>
            client.id ===
            referrerId,
        )
      : undefined;

  const timestamp =
    new Date(
      operation.created_at,
    ).toISOString();

  return {
    id:
      operation.entity_id,

    client_number: 0,

    full_name:
      String(
        payload.full_name ??
        "",
      ),

    phone_primary:
      String(
        payload.phone_primary ??
        "",
      ),

    phone_secondary:
      typeof payload
        .phone_secondary ===
        "string"
        ? payload
            .phone_secondary
        : null,

    source:
      String(
        payload.source ??
        "other",
      ) as ClientSource,

    referred_by_client_number:
      referrer
        ?.client_number ??
      null,

    referred_by_client_name:
      referrer
        ?.full_name ??
      null,

    internal_mark:
      payload.internal_mark ===
      true,

    notes:
      typeof payload.notes ===
        "string"
        ? payload.notes
        : null,

    created_at:
      timestamp,

    updated_at:
      timestamp,

    sync_pending:
      true,
  };
}


function matchesSearch(
  client: Client,
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
    client.full_name,
    client.phone_primary,
    client.phone_secondary ?? "",
  ].some(
    (item) =>
      item
        .toLocaleLowerCase()
        .includes(value),
  );
}


export async function listClients(
  search = "",
  limit = 100,
): Promise<ClientListResponse> {
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

  const response =
    await apiRequest<ClientListResponse>(
      `/api/v1/clients?${params.toString()}`,
    );

  const operations =
    await listPendingSyncOperations();

  const pendingOperations =
    operations.filter(
      (operation) =>
        operation.kind ===
        "client.create",
    );

  if (
    pendingOperations.length ===
    0
  ) {
    return response;
  }

  const knownIds =
    new Set(
      response.items.map(
        (client) =>
          client.id,
      ),
    );

  const pendingClients =
    pendingOperations
      .filter(
        (operation) =>
          !knownIds.has(
            operation.entity_id,
          ),
      )
      .map(
        (operation) =>
          pendingClientFromOperation(
            operation,
            response.items,
          ),
      )
      .filter(
        (client) =>
          matchesSearch(
            client,
            search,
          ),
      );

  return {
    ...response,

    items: [
      ...pendingClients,
      ...response.items,
    ],

    total:
      response.total +
      pendingClients.length,
  };
}


export function listArchivedClients(
  search = "",
  limit = 100,
): Promise<ArchivedClientListResponse> {
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


export async function createClient(
  payload:
    ClientCreate,
): Promise<Client> {
  try {
    return await apiRequest<Client>(
      "/api/v1/clients",
      {
        method: "POST",

        body: JSON.stringify(
          payload,
        ),
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


    let referrer:
      Client | undefined;


    if (
      payload
        .referred_by_client_number !==
      null
    ) {
      const cached =
        await listClients(
          "",
          100,
        );

      referrer =
        cached.items.find(
          (client) =>
            !client.sync_pending &&
            client.client_number ===
              payload
                .referred_by_client_number,
        );

      if (!referrer) {
        throw new ApiError(
          0,
          "Не удалось найти клиента, который дал рекомендацию, в локальных данных.",
        );
      }
    }


    const entityId =
      createSyncUuid();

    const operation =
      await queueSyncOperation(
        "client.create",

        entityId,

        {
          full_name:
            payload.full_name,

          phone_primary:
            payload.phone_primary,

          phone_secondary:
            payload.phone_secondary,

          source:
            payload.source,

          referred_by_client_id:
            referrer
              ?.id ??
            null,

          notes:
            payload.notes,

          internal_mark:
            payload.internal_mark ??
            false,
        },
      );


    return pendingClientFromOperation(
      operation,
      referrer
        ? [referrer]
        : [],
    );
  }
}


export function updateClient(
  clientNumber: number,
  payload:
    ClientUpdate,
): Promise<Client> {
  return apiRequest<Client>(
    `/api/v1/clients/${clientNumber}`,
    {
      method: "PUT",

      body: JSON.stringify(
        payload,
      ),
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
        internal_mark:
          internalMark,
      }),
    },
  );
}


export function archiveClient(
  clientNumber: number,
  reason:
    ArchiveReason,
  comment:
    string | null,
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