export function todayIso(): string {
  const now = new Date();

  const year = now.getFullYear();

  const month = String(
    now.getMonth() + 1,
  ).padStart(2, "0");

  const day = String(
    now.getDate(),
  ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

export function formatDate(
  value: string,
): string {
  const [year, month, day] =
    value.split("-");

  if (!year || !month || !day) {
    return value;
  }

  return `${day}.${month}.${year}`;
}

export function formatTime(
  value: string,
): string {
  return value.slice(0, 5);
}

export function formatMoney(
  value: string | number,
): string {
  const amount = Number(value);

  if (Number.isNaN(amount)) {
    return String(value);
  }

  return new Intl.NumberFormat(
    "ru-RU",
    {
      style: "currency",
      currency: "RUB",
      minimumFractionDigits: 2,
    },
  ).format(amount);
}

export function roleLabel(
  role: string,
): string {
  const labels: Record<string, string> = {
    owner: "Владелец",
    admin: "Администратор",
    mechanic: "Механик",
    tech_admin: "Технический администратор",
  };

  return labels[role] ?? role;
}

export function userInitials(
  login: string,
): string {
  if (login.toLowerCase() === "andrey") {
    return "АК";
  }

  return login
    .slice(0, 2)
    .toUpperCase();
}