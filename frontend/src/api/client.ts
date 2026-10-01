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

type ApiOptions = RequestInit & {
  skipJson?: boolean;
};

export async function apiRequest<T>(
  path: string,
  options: ApiOptions = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  const response = await fetch(path, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    let detail: unknown = null;

    try {
      detail = await response.json();
    } catch {
      detail = await response.text();
    }

    let message =
      `Ошибка HTTP ${response.status}`;

    if (
      detail &&
      typeof detail === "object" &&
      "detail" in detail
    ) {
      const apiDetail = (
        detail as {
          detail?: unknown;
        }
      ).detail;

      if (typeof apiDetail === "string") {
        message = apiDetail;
      }
    }

    throw new ApiError(
      response.status,
      message,
      detail,
    );
  }

  if (
    options.skipJson ||
    response.status === 204
  ) {
    return undefined as T;
  }

  return (await response.json()) as T;
}