import {
  apiRequest,
} from "./client";

import type {
  GlobalSearchResponse,
} from "../types/search";


export function globalSearch(
  query: string,
  limit = 20,
): Promise<GlobalSearchResponse> {
  const params =
    new URLSearchParams();

  params.set(
    "q",
    query.trim(),
  );

  params.set(
    "limit",
    String(limit),
  );

  return apiRequest<
    GlobalSearchResponse
  >(
    `/api/v1/search?${params.toString()}`,
  );
}