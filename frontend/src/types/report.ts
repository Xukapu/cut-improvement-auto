export type NewClientReportItem = {
  client_number: number;
  full_name: string;
  source: string;
  created_at: string;
};


export type RegularClientReportItem = {
  client_number: number;
  full_name: string;
  visits: number;
};


export type ClientSourceReportItem = {
  source: string;
  count: number;
};


export type ReferralReportItem = {
  client_number: number;
  client_name: string;

  referred_by_client_number: number;
  referred_by_name: string;
};


export type ClientReport = {
  date_from: string;
  date_to: string;

  new_clients_count: number;
  regular_clients_count: number;

  new_clients:
    NewClientReportItem[];

  regular_clients:
    RegularClientReportItem[];

  sources:
    ClientSourceReportItem[];

  referrals:
    ReferralReportItem[];
};


export type FinanceReport = {
  date_from: string;
  date_to: string;

  payments_received: string;

  cash_received: string;
  card_received: string;
  transfer_received: string;

  works_total: string;
  sto_parts_total: string;
  repair_total: string;

  current_debt: string;
};


export type WorkReportItem = {
  work_order_number: number;
  work_item_number: number;

  name: string;
  price: string;

  recorded_at: string;
};


export type WorkReport = {
  date_from: string;
  date_to: string;

  total: number;
  total_amount: string;

  items: WorkReportItem[];
};


export type EmployeeWorkAccrual = {
  work_order_number: number;
  work_item_number: number;
  work_name: string;

  work_price: string;

  share_percent: string;
  share_base: string;

  rate_percent_snapshot: string;
  earning_amount: string;

  recorded_at: string;
};


export type EmployeeAccrualItem = {
  employee_number: number;
  employee_name: string;

  works:
    EmployeeWorkAccrual[];

  total_share_base: string;
  total_earnings: string;
};


export type EmployeeAccrualReport = {
  date_from: string;
  date_to: string;

  employees:
    EmployeeAccrualItem[];

  grand_total: string;
};