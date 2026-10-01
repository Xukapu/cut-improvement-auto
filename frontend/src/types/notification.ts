export type NotificationChannel =
  | "sms"
  | "max";


export type NotificationKind =
  | "appointment_confirmation"
  | "appointment_reminder"
  | "service_reminder";


export type NotificationStatus =
  | "prepared"
  | "sent"
  | "failed"
  | "cancelled";


export type ServiceReminderStatus =
  | "planned"
  | "completed"
  | "cancelled";


export type NotificationPreference = {
  client_id: string;
  client_number: number;
  client_name: string;
  phone_primary: string;

  sms_enabled: boolean;
  max_enabled: boolean;
  max_connected: boolean;

  appointment_confirmation_enabled:
    boolean;

  appointment_reminder_enabled:
    boolean;

  service_reminder_enabled:
    boolean;
};


export type NotificationPreferenceUpdate = {
  sms_enabled: boolean;
  max_enabled: boolean;

  appointment_confirmation_enabled:
    boolean;

  appointment_reminder_enabled:
    boolean;

  service_reminder_enabled:
    boolean;
};


export type CustomerNotification = {
  id: string;

  client_number:
    | number
    | null;

  client_name:
    | string
    | null;

  vehicle_number:
    | number
    | null;

  appointment_number:
    | number
    | null;

  channel: NotificationChannel;
  kind: NotificationKind;
  status: NotificationStatus;

  message_text: string;

  scheduled_for: string;

  sent_at:
    | string
    | null;

  error_message:
    | string
    | null;

  created_at: string;
};


export type ServiceReminder = {
  id: string;

  client_number: number;
  client_name: string;

  vehicle_number: number;
  vehicle_name: string;

  work_name: string;

  due_date:
    | string
    | null;

  due_mileage:
    | number
    | null;

  message_text: string;

  status:
    ServiceReminderStatus;

  completed_at:
    | string
    | null;

  created_at: string;
  updated_at: string;
};


export type ServiceReminderCreate = {
  client_number: number;
  vehicle_number: number;

  work_name: string;

  due_date:
    | string
    | null;

  due_mileage:
    | number
    | null;

  message_text: string;
};


export type PrepareDueResponse = {
  prepared_count: number;
};

export type CustomerNotificationUpdate = {
  message_text: string;
  scheduled_for: string;
};