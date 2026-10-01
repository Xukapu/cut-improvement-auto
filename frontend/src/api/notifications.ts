import {
  apiRequest,
} from "./client";

import type {
  CustomerNotification,
  CustomerNotificationUpdate,
  NotificationKind,
  NotificationPreference,
  NotificationPreferenceUpdate,
  NotificationStatus,
  PrepareDueResponse,
  ServiceReminder,
  ServiceReminderCreate,
  ServiceReminderStatus,
} from "../types/notification";


type NotificationFilters = {
  clientNumber?: number;
  status?: NotificationStatus;
  kind?: NotificationKind;
};


export function listCustomerNotifications(
  filters:
    NotificationFilters = {},
): Promise<CustomerNotification[]> {
  const params =
    new URLSearchParams();

  params.set(
    "limit",
    "200",
  );

  if (
    filters.clientNumber !==
    undefined
  ) {
    params.set(
      "client_number",
      String(
        filters.clientNumber,
      ),
    );
  }

  if (filters.status) {
    params.set(
      "notification_status",
      filters.status,
    );
  }

  if (filters.kind) {
    params.set(
      "kind",
      filters.kind,
    );
  }

  return apiRequest<
    CustomerNotification[]
  >(
    `/api/v1/notifications?${params.toString()}`,
  );
}


export function getNotificationPreferences(
  clientNumber: number,
): Promise<NotificationPreference> {
  return apiRequest<
    NotificationPreference
  >(
    `/api/v1/notifications/clients/${clientNumber}/preferences`,
  );
}


export function updateNotificationPreferences(
  clientNumber: number,
  payload:
    NotificationPreferenceUpdate,
): Promise<NotificationPreference> {
  return apiRequest<
    NotificationPreference
  >(
    `/api/v1/notifications/clients/${clientNumber}/preferences`,
    {
      method: "PUT",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function listServiceReminders(
  options: {
    clientNumber?: number;
    status?:
      ServiceReminderStatus;
  } = {},
): Promise<ServiceReminder[]> {
  const params =
    new URLSearchParams();

  if (
    options.clientNumber !==
    undefined
  ) {
    params.set(
      "client_number",
      String(
        options.clientNumber,
      ),
    );
  }

  if (options.status) {
    params.set(
      "reminder_status",
      options.status,
    );
  }

  const query =
    params.toString();

  return apiRequest<
    ServiceReminder[]
  >(
    query
      ? `/api/v1/notifications/service-reminders?${query}`
      : "/api/v1/notifications/service-reminders",
  );
}


export function createServiceReminder(
  payload:
    ServiceReminderCreate,
): Promise<ServiceReminder> {
  return apiRequest<
    ServiceReminder
  >(
    "/api/v1/notifications/service-reminders",
    {
      method: "POST",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function cancelServiceReminder(
  reminderId: string,
): Promise<ServiceReminder> {
  return apiRequest<
    ServiceReminder
  >(
    `/api/v1/notifications/service-reminders/${reminderId}/cancel`,
    {
      method: "POST",
    },
  );
}


export function prepareDueNotifications():
  Promise<PrepareDueResponse> {
  return apiRequest<
    PrepareDueResponse
  >(
    "/api/v1/notifications/service-reminders/prepare-due",
    {
      method: "POST",
    },
  );
}

export function updateCustomerNotification(
  notificationId: string,
  payload:
    CustomerNotificationUpdate,
): Promise<CustomerNotification> {
  return apiRequest<
    CustomerNotification
  >(
    `/api/v1/notifications/${notificationId}`,
    {
      method: "PUT",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export async function deleteCustomerNotification(
  notificationId: string,
): Promise<void> {
  await apiRequest<void>(
    `/api/v1/notifications/${notificationId}`,
    {
      method: "DELETE",
      skipJson: true,
    },
  );
}