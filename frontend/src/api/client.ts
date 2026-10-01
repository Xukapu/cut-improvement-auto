import {
  cacheApiResponse,
  emitServerState,
  getCachedApiResponse,
} from "../offline/offlineStore";


export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(
    status: number,
    message: string,
    detail?: unknown,
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}


type ApiOptions =
  RequestInit & {
    skipJson?: boolean;
    offlineCache?: boolean;
  };


type ValidationIssue = {
  loc?: unknown[];
  msg?: string;
  type?: string;

  ctx?:
    Record<
      string,
      unknown
    >;
};


const fieldLabels:
  Record<
    string,
    string
  > = {
    full_name:
      "Имя клиента",

    phone_primary:
      "Основной телефон",

    phone_secondary:
      "Второй телефон",

    source:
      "Источник",

    referred_by_client_number:
      "Клиент, который рекомендовал",

    notes:
      "Комментарий",

    license_plate:
      "Госномер",

    vin:
      "VIN",

    brand:
      "Марка",

    model:
      "Модель",

    year:
      "Год",

    mileage:
      "Пробег",

    owner_client_number:
      "Владелец",

    client_number:
      "Клиент",

    vehicle_number:
      "Автомобиль",

    appointment_date:
      "Дата записи",

    appointment_time:
      "Время записи",

    reason:
      "Причина обращения",

    comment:
      "Комментарий",

    status:
      "Статус",
  };


function fieldName(
  issue:
    ValidationIssue,
): string {
  const location =
    issue.loc ?? [];

  for (
    let index =
      location.length - 1;
    index >= 0;
    index -= 1
  ) {
    const item =
      location[index];

    if (
      typeof item ===
        "string" &&
      item !== "body" &&
      item !== "query" &&
      item !== "path"
    ) {
      return (
        fieldLabels[item] ??
        item
      );
    }
  }

  return "Поле";
}


function validationMessage(
  issue:
    ValidationIssue,
): string {
  const field =
    fieldName(issue);

  const type =
    issue.type ?? "";

  const raw =
    issue.msg ?? "";

  const context =
    issue.ctx ?? {};


  if (
    type === "missing" ||
    type.endsWith(
      "_missing",
    ) ||
    raw.includes(
      "Field required",
    )
  ) {
    return (
      `Поле «${field}» ` +
      "обязательно для заполнения."
    );
  }


  if (
    type ===
    "string_too_short"
  ) {
    const minimum =
      context.min_length;

    return minimum !== undefined
      ? `Поле «${field}» слишком короткое. Минимум ${minimum} символов.`
      : `Поле «${field}» слишком короткое.`;
  }


  if (
    type ===
    "string_too_long"
  ) {
    const maximum =
      context.max_length;

    return maximum !== undefined
      ? `Поле «${field}» слишком длинное. Максимум ${maximum} символов.`
      : `Поле «${field}» слишком длинное.`;
  }


  if (
    type === "int_parsing" ||
    type === "int_type"
  ) {
    return (
      `Поле «${field}» ` +
      "должно содержать целое число."
    );
  }


  if (
    type ===
      "date_parsing" ||
    type ===
      "date_from_datetime_parsing"
  ) {
    return (
      `В поле «${field}» ` +
      "указана неправильная дата."
    );
  }


  if (
    type ===
    "time_parsing"
  ) {
    return (
      `В поле «${field}» ` +
      "указано неправильное время."
    );
  }


  if (
    type === "enum" ||
    type ===
      "literal_error"
  ) {
    return (
      `В поле «${field}» ` +
      "выбрано недопустимое значение."
    );
  }


  if (
    type ===
    "greater_than_equal"
  ) {
    return (
      `Значение поля «${field}» ` +
      "слишком маленькое."
    );
  }


  if (
    type ===
    "less_than_equal"
  ) {
    return (
      `Значение поля «${field}» ` +
      "слишком большое."
    );
  }


  if (raw) {
    return (
      `Поле «${field}»: ` +
      raw
    );
  }


  return (
    "Проверьте поле " +
    `«${field}».`
  );
}


function extractErrorMessage(
  status: number,
  payload: unknown,
): string {
  if (
    payload &&
    typeof payload ===
      "object" &&
    "detail" in payload
  ) {
    const detail =
      (
        payload as {
          detail?: unknown;
        }
      ).detail;

    if (
      typeof detail ===
      "string"
    ) {
      return detail;
    }

    if (
      Array.isArray(
        detail,
      )
    ) {
      const messages =
        detail
          .filter(
            (
              item,
            ): item is ValidationIssue =>
              Boolean(
                item &&
                typeof item ===
                  "object",
              ),
          )
          .map(
            validationMessage,
          );

      if (
        messages.length > 0
      ) {
        return messages.join(
          " ",
        );
      }
    }
  }


  if (
    typeof payload ===
      "string" &&
    payload.trim()
  ) {
    return payload.trim();
  }


  if (status === 422) {
    return (
      "Сервер не принял данные формы. " +
      "Проверьте обязательные поля."
    );
  }


  if (status === 400) {
    return (
      "Сервер отклонил запрос. " +
      "Проверьте введённые данные."
    );
  }


  if (status === 401) {
    return (
      "Сессия завершена. " +
      "Войдите в систему снова."
    );
  }


  if (status === 403) {
    return (
      "Недостаточно прав " +
      "для этого действия."
    );
  }


  if (status === 404) {
    return (
      "Запись не найдена."
    );
  }


  if (status === 409) {
    return (
      "Операцию нельзя выполнить " +
      "в текущем состоянии."
    );
  }


  if (status >= 500) {
    return (
      "Ошибка сервера. " +
      "Повторите попытку."
    );
  }


  return (
    `Ошибка HTTP ${status}`
  );
}


function isGetRequest(
  method:
    string | undefined,
): boolean {
  return (
    (
      method ??
      "GET"
    ).toUpperCase() ===
    "GET"
  );
}


async function cachedFallback<T>(
  path: string,
): Promise<
  | {
      found: true;
      value: T;
    }
  | {
      found: false;
    }
> {
  const cached =
    await getCachedApiResponse<T>(
      path,
    );

  if (!cached.found) {
    return {
      found: false,
    };
  }

  return {
    found: true,
    value: cached.payload,
  };
}


export async function apiRequest<T>(
  path: string,
  options:
    ApiOptions = {},
): Promise<T> {
  const {
    skipJson = false,
    offlineCache = true,
    ...requestOptions
  } = options;

  const method =
    requestOptions.method ??
    "GET";

  const allowCache =
    offlineCache &&
    isGetRequest(method) &&
    path.startsWith(
      "/api/v1/",
    );


  const headers =
    new Headers(
      requestOptions.headers,
    );


  if (
    requestOptions.body &&
    !(
      requestOptions.body
        instanceof FormData
    ) &&
    !headers.has(
      "Content-Type",
    )
  ) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }


  let response:
    Response;


  try {
    response = await fetch(
      path,
      {
        ...requestOptions,
        headers,

        credentials:
          "include",
      },
    );

    emitServerState(
      true,
    );
  } catch {
    emitServerState(
      false,
    );

    if (allowCache) {
      const cached =
        await cachedFallback<T>(
          path,
        );

      if (cached.found) {
        return cached.value;
      }
    }

    throw new ApiError(
      0,
      "Нет связи с сервером.",
    );
  }


  const raw =
    await response.text();


  let payload:
    unknown = null;


  if (raw) {
    try {
      payload =
        JSON.parse(raw);
    } catch {
      payload = raw;
    }
  }


  if (!response.ok) {
    if (
      allowCache &&
      response.status >= 500
    ) {
      const cached =
        await cachedFallback<T>(
          path,
        );

      if (cached.found) {
        emitServerState(
          false,
        );

        return cached.value;
      }
    }

    throw new ApiError(
      response.status,

      extractErrorMessage(
        response.status,
        payload,
      ),

      payload,
    );
  }


  if (
    skipJson ||
    response.status === 204
  ) {
    return undefined as T;
  }


  if (allowCache) {
    await cacheApiResponse(
      path,
      payload,
    );
  }


  return payload as T;
}