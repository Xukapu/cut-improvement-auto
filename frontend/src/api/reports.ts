import {
  apiRequest,
} from "./client";

import type {
  ClientReport,
  EmployeeAccrualReport,
  FinanceReport,
  WorkReport,
} from "../types/report";


type ReportPeriod = {
  dateFrom: string;
  dateTo: string;
};


function reportQuery(
  period: ReportPeriod,
): string {
  const params =
    new URLSearchParams();

  params.set(
    "date_from",
    period.dateFrom,
  );

  params.set(
    "date_to",
    period.dateTo,
  );

  return params.toString();
}


export function getClientReport(
  period: ReportPeriod,
): Promise<ClientReport> {
  return apiRequest<ClientReport>(
    `/api/v1/reports/clients?${reportQuery(period)}`,
  );
}


export function getFinanceReport(
  period: ReportPeriod,
): Promise<FinanceReport> {
  return apiRequest<FinanceReport>(
    `/api/v1/reports/finance?${reportQuery(period)}`,
  );
}


export function getWorkReport(
  period: ReportPeriod,
): Promise<WorkReport> {
  return apiRequest<WorkReport>(
    `/api/v1/reports/works?${reportQuery(period)}`,
  );
}


export function getEmployeeAccrualReport(
  period: ReportPeriod,
): Promise<EmployeeAccrualReport> {
  return apiRequest<EmployeeAccrualReport>(
    `/api/v1/reports/employee-accruals?${reportQuery(period)}`,
  );
}