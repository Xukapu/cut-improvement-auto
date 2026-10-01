import { apiRequest } from "./client";
import type { DashboardResponse } from "../types/dashboard";

export function getDashboard(
  reportDate: string,
): Promise<DashboardResponse> {
  const params = new URLSearchParams({
    report_date: reportDate,
  });

  return apiRequest<DashboardResponse>(
    `/api/v1/dashboard?${params.toString()}`,
  );
}