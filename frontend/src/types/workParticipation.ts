export type WorkParticipation = {
  enabled: boolean;

  employee_number:
    | number
    | null;

  employee_name: string;

  rate_percent:
    | string
    | number
    | null;
};


export type WorkParticipationUpdate = {
  enabled: boolean;

  rate_percent:
    | number
    | null;
};