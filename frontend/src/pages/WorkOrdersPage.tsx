import { DisputePhotoGallery } from "../components/DisputePhotoGallery";
import { WorkOrderPrintPreview } from "../components/WorkOrderPrintPreview";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  ClipboardList,
  Edit3,
  FileWarning,
  Package,
  Plus,
  Printer,
  RefreshCw,
  RotateCcw,
  Save,
  Trash2,
  UserRound,
  Wrench,
  X,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import type {
  FormEvent,
} from "react";

import {
  createDispute,
  createPart,
  createPayment,
  createRecommendedWork,
  createWork,
  createWorkOrder,
  deleteDispute,
  deleteDisputePhoto,
  deletePart,
  deletePayment,
  deleteRecommendedWork,
  getPaymentSummary,
  getWorkOrder,
  listDisputePhotos,
  listDisputes,
  listEmployees,
  listParts,
  listRecommendedWorks,
  listWorkOrders,
  listWorks,
  listWorksFinancial,
  changeWorkOrderStatus,
  updateDispute,
  updatePart,
  updatePayment,
  updateRecommendedWork,
  updateWork,
  updateWorkOrder,
  uploadDisputePhoto,
} from "../api/workOrders";
import {
  listAppointments,
} from "../api/appointments";
import {
  ApiError,
} from "../api/client";
import {
  listClients,
} from "../api/clients";
import {
  listVehicles,
} from "../api/vehicles";
import type {
  Appointment,
} from "../types/appointment";
import type {
  CurrentUser,
} from "../types/auth";
import type {
  Client,
} from "../types/client";
import type {
  Vehicle,
} from "../types/vehicle";
import type {
  Dispute,
  DisputePhoto,
  EmployeePublic,
  Part,
  PartProvidedBy,
  Payment,
  PaymentMethod,
  PaymentSummary,
  RecommendedWork,
  WorkAssignmentInput,
  WorkItemFinancial,
  WorkItemPublic,
  WorkOrder,
  WorkOrderStatus,
} from "../types/workOrder";


type Props = {
  currentUser: CurrentUser;
};


type OrderFilter =
  | "all"
  | WorkOrderStatus;


type OrderTab =
  | "works"
  | "parts"
  | "recommended"
  | "disputes"
  | "payment";


type AssignmentForm = {
  employee_number: string;
  share_percent: string;
};


const statusLabels:
  Record<
    WorkOrderStatus,
    string
  > = {
    planned: "Запланирован",
    in_progress: "В работе",
    ready: "Готов",
    issued: "Выдан",
  };


const paymentLabels:
  Record<
    PaymentMethod,
    string
  > = {
    cash: "Наличные",
    card: "Карта",
    transfer: "Перевод",
  };


function errorText(
  error: unknown,
  fallback: string,
): string {
  if (
    error instanceof ApiError
  ) {
    return error.message;
  }

  return fallback;
}


function money(
  value:
    | string
    | number
    | null
    | undefined,
): string {
  const number =
    Number(value ?? 0);

  if (
    Number.isNaN(number)
  ) {
    return "0 ₽";
  }

  return new Intl.NumberFormat(
    "ru-RU",
    {
      style: "currency",
      currency: "RUB",
      maximumFractionDigits: 2,
    },
  ).format(number);
}


function dateTime(
  value:
    | string
    | null
    | undefined,
): string {
  if (!value) {
    return "—";
  }

  const parsed =
    new Date(value);

  if (
    Number.isNaN(
      parsed.getTime(),
    )
  ) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "ru-RU",
    {
      dateStyle: "short",
      timeStyle: "short",
    },
  ).format(parsed);
}


function isFinancialWork(
  item:
    | WorkItemPublic
    | WorkItemFinancial,
): item is WorkItemFinancial {
  return (
    "total_employee_earnings"
    in item
  );
}


function vehicleTitle(
  vehicle:
    Vehicle | undefined,
  plate: string,
): string {
  if (!vehicle) {
    return plate;
  }

  return (
    `${vehicle.brand} ` +
    `${vehicle.model} · ` +
    plate
  );
}


export function WorkOrdersPage({
  currentUser,
}: Props) {
  const isOwner =
    currentUser.role === "owner";

  const canManageOrder =
    currentUser.role === "owner" ||
    currentUser.role ===
      "tech_admin";

  const canManageParts =
    canManageOrder;

  const canManagePayments =
    currentUser.role === "owner" ||
    currentUser.role ===
      "tech_admin" ||
    currentUser.role === "admin";


  const [
    filter,
    setFilter,
  ] = useState<OrderFilter>(
    "all",
  );

  const [
    orders,
    setOrders,
  ] = useState<WorkOrder[]>(
    [],
  );

  const [
    ordersLoading,
    setOrdersLoading,
  ] = useState(false);

  const [
    pageError,
    setPageError,
  ] = useState("");

  const [
    selectedNumber,
    setSelectedNumber,
  ] = useState<number | null>(
    null,
  );

  const [
    selectedOrder,
    setSelectedOrder,
  ] = useState<WorkOrder | null>(
    null,
  );

  const [
    detailLoading,
    setDetailLoading,
  ] = useState(false);

  const [
    tab,
    setTab,
  ] = useState<OrderTab>(
    "works",
  );

  const [
    vehicles,
    setVehicles,
  ] = useState<Vehicle[]>(
    [],
  );


  const [
    works,
    setWorks,
  ] = useState<
    Array<
      WorkItemPublic |
      WorkItemFinancial
    >
  >([]);

  const [
    parts,
    setParts,
  ] = useState<Part[]>(
    [],
  );

  const [
    partsTotal,
    setPartsTotal,
  ] = useState<
    string | number
  >("0");

  const [
    recommended,
    setRecommended,
  ] = useState<
    RecommendedWork[]
  >([]);

  const [
    disputes,
    setDisputes,
  ] = useState<Dispute[]>(
    [],
  );

  const [
    disputePhotos,
    setDisputePhotos,
  ] = useState<
    Record<
      number,
      DisputePhoto[]
    >
  >({});

  const [
    paymentSummary,
    setPaymentSummary,
  ] = useState<
    PaymentSummary | null
  >(null);


  const [
    employees,
    setEmployees,
  ] = useState<EmployeePublic[]>(
    [],
  );


  const [
    showPrintPreview,
    setShowPrintPreview,
  ] = useState(false);

  const [
    showCreate,
    setShowCreate,
  ] = useState(false);

  const [
    createClients,
    setCreateClients,
  ] = useState<Client[]>(
    [],
  );

  const [
    createVehicles,
    setCreateVehicles,
  ] = useState<Vehicle[]>(
    [],
  );

  const [
    createAppointments,
    setCreateAppointments,
  ] = useState<
    Appointment[]
  >([]);

  const [
    createClientNumber,
    setCreateClientNumber,
  ] = useState("");

  const [
    createVehicleNumber,
    setCreateVehicleNumber,
  ] = useState("");

  const [
    createAppointmentNumber,
    setCreateAppointmentNumber,
  ] = useState("");

  const [
    createReason,
    setCreateReason,
  ] = useState("");

  const [
    createMileage,
    setCreateMileage,
  ] = useState("");

  const [
    createSaving,
    setCreateSaving,
  ] = useState(false);


  const [
    editingOrder,
    setEditingOrder,
  ] = useState(false);

  const [
    orderReason,
    setOrderReason,
  ] = useState("");

  const [
    orderMileage,
    setOrderMileage,
  ] = useState("");

  const [
    orderSaving,
    setOrderSaving,
  ] = useState(false);


  const [
    showWorkForm,
    setShowWorkForm,
  ] = useState(false);

  const [
    editingWork,
    setEditingWork,
  ] = useState<
    WorkItemFinancial | null
  >(null);

  const [
    workName,
    setWorkName,
  ] = useState("");

  const [
    workPrice,
    setWorkPrice,
  ] = useState("");

  const [
    workAssignments,
    setWorkAssignments,
  ] = useState<
    AssignmentForm[]
  >([]);

  const [
    workSaving,
    setWorkSaving,
  ] = useState(false);


  const [
    showPartForm,
    setShowPartForm,
  ] = useState(false);

  const [
    editingPart,
    setEditingPart,
  ] = useState<Part | null>(
    null,
  );

  const [
    partName,
    setPartName,
  ] = useState("");

  const [
    partQuantity,
    setPartQuantity,
  ] = useState("1");

  const [
    partPrice,
    setPartPrice,
  ] = useState("");

  const [
    partSupplier,
    setPartSupplier,
  ] = useState("");

  const [
    partProvidedBy,
    setPartProvidedBy,
  ] = useState<PartProvidedBy>(
    "sto",
  );

  const [
    partSaving,
    setPartSaving,
  ] = useState(false);


  const [
    showRecommendedForm,
    setShowRecommendedForm,
  ] = useState(false);

  const [
    editingRecommended,
    setEditingRecommended,
  ] = useState<
    RecommendedWork | null
  >(null);

  const [
    recommendedName,
    setRecommendedName,
  ] = useState("");

  const [
    recommendedComment,
    setRecommendedComment,
  ] = useState("");

  const [
    recommendedSaving,
    setRecommendedSaving,
  ] = useState(false);


  const [
    showDisputeForm,
    setShowDisputeForm,
  ] = useState(false);

  const [
    editingDispute,
    setEditingDispute,
  ] = useState<
    Dispute | null
  >(null);

  const [
    disputeFound,
    setDisputeFound,
  ] = useState("");

  const [
    disputeRecommendation,
    setDisputeRecommendation,
  ] = useState("");

  const [
    disputeResponse,
    setDisputeResponse,
  ] = useState("");

  const [
    disputeSaving,
    setDisputeSaving,
  ] = useState(false);


  const [
    showPaymentForm,
    setShowPaymentForm,
  ] = useState(false);

  const [
    editingPayment,
    setEditingPayment,
  ] = useState<
    Payment | null
  >(null);

  const [
    paymentAmount,
    setPaymentAmount,
  ] = useState("");

  const [
    paymentMethod,
    setPaymentMethod,
  ] = useState<PaymentMethod>(
    "cash",
  );

  const [
    paymentComment,
    setPaymentComment,
  ] = useState("");

  const [
    paymentSaving,
    setPaymentSaving,
  ] = useState(false);


  const loadOrders =
    useCallback(async () => {
      setOrdersLoading(true);
      setPageError("");

      try {
        const result =
          await listWorkOrders(
            filter === "all"
              ? {}
              : {
                  status: filter,
                },
          );

        setOrders(
          result.items,
        );

        if (
          result.items.length === 0
        ) {
          setSelectedNumber(
            null,
          );
          setSelectedOrder(
            null,
          );
          return;
        }

        setSelectedNumber(
          (current) => {
            if (
              current !== null &&
              result.items.some(
                (item) =>
                  item
                    .work_order_number ===
                  current,
              )
            ) {
              return current;
            }

            return result
              .items[0]
              .work_order_number;
          },
        );
      } catch (error) {
        setPageError(
          errorText(
            error,
            "Не удалось загрузить заказ-наряды.",
          ),
        );
      } finally {
        setOrdersLoading(false);
      }
    }, [filter]);


  const loadDetails =
    useCallback(
      async (
        workOrderNumber: number,
      ) => {
        setDetailLoading(true);
        setPageError("");

        try {
          const [
            order,
            workResult,
            partResult,
            recommendedResult,
            disputeResult,
            paymentResult,
          ] = await Promise.all([
            getWorkOrder(
              workOrderNumber,
            ),

            isOwner
              ? listWorksFinancial(
                  workOrderNumber,
                )
              : listWorks(
                  workOrderNumber,
                ),

            listParts(
              workOrderNumber,
            ),

            listRecommendedWorks(
              workOrderNumber,
            ),

            listDisputes(
              workOrderNumber,
            ),

            getPaymentSummary(
              workOrderNumber,
            ),
          ]);

          setSelectedOrder(order);
          setOrderReason(
            order.reason,
          );
          setOrderMileage(
            order.mileage === null
              ? ""
              : String(
                  order.mileage,
                ),
          );

          setWorks(
            workResult.items,
          );

          setParts(
            partResult.items,
          );
          setPartsTotal(
            partResult.total_price,
          );

          setRecommended(
            recommendedResult.items,
          );

          setDisputes(
            disputeResult.items,
          );

          setPaymentSummary(
            paymentResult,
          );

          const photoEntries =
            await Promise.all(
              disputeResult.items.map(
                async (item) => {
                  const photos =
                    await listDisputePhotos(
                      workOrderNumber,
                      item.dispute_number,
                    );

                  return [
                    item.dispute_number,
                    photos.items,
                  ] as const;
                },
              ),
            );

          setDisputePhotos(
            Object.fromEntries(
              photoEntries,
            ),
          );
        } catch (error) {
          setPageError(
            errorText(
              error,
              "Не удалось загрузить заказ-наряд.",
            ),
          );
        } finally {
          setDetailLoading(false);
        }
      },
      [isOwner],
    );


  useEffect(() => {
    const timer =
      window.setTimeout(() => {
        void loadOrders();
      }, 0);

    return () => {
      window.clearTimeout(
        timer,
      );
    };
  }, [loadOrders]);


  useEffect(() => {
    if (
      selectedNumber === null
    ) {
      return;
    }

    const timer =
      window.setTimeout(() => {
        void loadDetails(
          selectedNumber,
        );
      }, 0);

    return () => {
      window.clearTimeout(
        timer,
      );
    };
  }, [
    selectedNumber,
    loadDetails,
  ]);


  useEffect(() => {
    let active = true;

    listVehicles(
      "",
      100,
    )
      .then((result) => {
        if (active) {
          setVehicles(
            result.items,
          );
        }
      })
      .catch(() => {
        if (active) {
          setVehicles([]);
        }
      });

    if (isOwner) {
      listEmployees()
        .then((result) => {
          if (active) {
            setEmployees(
              result.filter(
                (employee) =>
                  employee.is_active,
              ),
            );
          }
        })
        .catch(() => {
          if (active) {
            setEmployees([]);
          }
        });
    }

    return () => {
      active = false;
    };
  }, [isOwner]);


  const selectedVehicle =
    useMemo(
      () =>
        vehicles.find(
          (vehicle) =>
            vehicle
              .vehicle_number ===
            selectedOrder
              ?.vehicle_number,
        ),
      [
        vehicles,
        selectedOrder,
      ],
    );


  const workTotal =
    useMemo(
      () =>
        works.reduce(
          (
            total,
            work,
          ) =>
            total +
            Number(
              work.price,
            ),
          0,
        ),
      [works],
    );


  async function openCreateOrder() {
    setPageError("");
    setCreateSaving(false);

    setCreateClientNumber("");
    setCreateVehicleNumber("");
    setCreateAppointmentNumber("");
    setCreateReason("");
    setCreateMileage("");

    setCreateVehicles([]);
    setCreateAppointments([]);

    try {
      const result =
        await listClients(
          "",
          100,
        );

      setCreateClients(
        result.items,
      );

      setShowCreate(true);
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось загрузить клиентов.",
        ),
      );
    }
  }


  async function handleCreateClient(
    value: string,
  ) {
    setCreateClientNumber(
      value,
    );

    setCreateVehicleNumber("");
    setCreateAppointmentNumber("");
    setCreateAppointments([]);

    const number =
      Number(value);

    if (!number) {
      setCreateVehicles([]);
      return;
    }

    try {
      const result =
        await listVehicles(
          "",
          100,
          number,
        );

      setCreateVehicles(
        result.items,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось загрузить автомобили клиента.",
        ),
      );
    }
  }


  async function handleCreateVehicle(
    value: string,
  ) {
    setCreateVehicleNumber(
      value,
    );

    setCreateAppointmentNumber("");

    const clientNumber =
      Number(
        createClientNumber,
      );

    const vehicleNumber =
      Number(value);

    const vehicle =
      createVehicles.find(
        (item) =>
          item.vehicle_number ===
          vehicleNumber,
      );

    if (
      vehicle?.mileage !==
      null &&
      vehicle?.mileage !==
      undefined
    ) {
      setCreateMileage(
        String(
          vehicle.mileage,
        ),
      );
    }

    if (
      !clientNumber ||
      !vehicleNumber
    ) {
      setCreateAppointments([]);
      return;
    }

    try {
      const result =
        await listAppointments({
          clientNumber,
          vehicleNumber,
          status: "scheduled",
        });

      const usedAppointments =
        new Set(
          orders
            .map(
              (order) =>
                order
                  .appointment_number,
            )
            .filter(
              (
                value,
              ): value is number =>
                value !== null,
            ),
        );

      setCreateAppointments(
        result.items.filter(
          (appointment) =>
            !usedAppointments.has(
              appointment
                .appointment_number,
            ),
        ),
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось загрузить записи клиента.",
        ),
      );
    }
  }


  function handleCreateAppointment(
    value: string,
  ) {
    setCreateAppointmentNumber(
      value,
    );

    const appointment =
      createAppointments.find(
        (item) =>
          item
            .appointment_number ===
          Number(value),
      );

    if (appointment) {
      setCreateReason(
        appointment.reason,
      );
    }
  }


  async function handleCreateOrder(
    event: FormEvent,
  ) {
    event.preventDefault();

    const clientNumber =
      Number(
        createClientNumber,
      );

    const vehicleNumber =
      Number(
        createVehicleNumber,
      );

    const reason =
      createReason.trim();

    if (
      !clientNumber ||
      !vehicleNumber
    ) {
      setPageError(
        "Выберите клиента и автомобиль.",
      );
      return;
    }

    if (
      reason.length < 2
    ) {
      setPageError(
        "Укажите причину обращения.",
      );
      return;
    }

    setCreateSaving(true);
    setPageError("");

    try {
      const created =
        await createWorkOrder({
          client_number:
            clientNumber,

          vehicle_number:
            vehicleNumber,

          appointment_number:
            createAppointmentNumber
              ? Number(
                  createAppointmentNumber,
                )
              : null,

          reason,

          mileage:
            createMileage
              ? Number(
                  createMileage,
                )
              : null,
        });

      setShowCreate(false);

      await loadOrders();

      setSelectedNumber(
        created
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось создать заказ-наряд.",
        ),
      );
    } finally {
      setCreateSaving(false);
    }
  }


  async function saveOrder(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!selectedOrder) {
      return;
    }

    const reason =
      orderReason.trim();

    if (
      reason.length < 2
    ) {
      setPageError(
        "Укажите причину обращения.",
      );
      return;
    }

    setOrderSaving(true);
    setPageError("");

    try {
      await updateWorkOrder(
        selectedOrder
          .work_order_number,
        {
          reason,

          mileage:
            orderMileage
              ? Number(
                  orderMileage,
                )
              : null,
        },
      );

      setEditingOrder(false);

      await Promise.all([
        loadOrders(),
        loadDetails(
          selectedOrder
            .work_order_number,
        ),
      ]);
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось сохранить заказ-наряд.",
        ),
      );
    } finally {
      setOrderSaving(false);
    }
  }


  async function setStatus(
    status: WorkOrderStatus,
  ) {
    if (!selectedOrder) {
      return;
    }

    setPageError("");

    try {
      await changeWorkOrderStatus(
        selectedOrder
          .work_order_number,
        status,
      );

      await Promise.all([
        loadOrders(),
        loadDetails(
          selectedOrder
            .work_order_number,
        ),
      ]);
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось изменить статус.",
        ),
      );
    }
  }


  function resetWorkForm() {
    setShowWorkForm(false);
    setEditingWork(null);
    setWorkName("");
    setWorkPrice("");
    setWorkAssignments([]);
  }


  function openNewWork() {
    setEditingWork(null);
    setWorkName("");
    setWorkPrice("");

    setWorkAssignments([
      {
        employee_number:
          employees[0]
            ? String(
                employees[0]
                  .employee_number,
              )
            : "",
        share_percent: "100",
      },
    ]);

    setShowWorkForm(true);
  }


  function openWorkEditor(
    work: WorkItemFinancial,
  ) {
    setEditingWork(work);
    setWorkName(work.name);
    setWorkPrice(
      String(
        work.price,
      ),
    );

    setWorkAssignments(
      work.assignments.map(
        (assignment) => ({
          employee_number:
            String(
              assignment
                .employee_number,
            ),
          share_percent:
            String(
              assignment
                .share_percent,
            ),
        }),
      ),
    );

    setShowWorkForm(true);
  }


  function addAssignment() {
    setWorkAssignments(
      (current) => [
        ...current,
        {
          employee_number: "",
          share_percent: "",
        },
      ],
    );
  }


  function updateAssignment(
    index: number,
    field:
      | "employee_number"
      | "share_percent",
    value: string,
  ) {
    setWorkAssignments(
      (current) =>
        current.map(
          (
            item,
            itemIndex,
          ) =>
            itemIndex === index
              ? {
                  ...item,
                  [field]:
                    value,
                }
              : item,
        ),
    );
  }


  function removeAssignment(
    index: number,
  ) {
    setWorkAssignments(
      (current) =>
        current.filter(
          (
            _item,
            itemIndex,
          ) =>
            itemIndex !== index,
        ),
    );
  }


  async function saveWork(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!selectedOrder) {
      return;
    }

    const name =
      workName.trim();

    const price =
      Number(workPrice);

    const assignments:
      WorkAssignmentInput[] =
        workAssignments.map(
          (item) => ({
            employee_number:
              Number(
                item
                  .employee_number,
              ),

            share_percent:
              Number(
                item
                  .share_percent,
              ),
          }),
        );

    if (
      name.length < 2
    ) {
      setPageError(
        "Укажите название работы.",
      );
      return;
    }

    if (
      Number.isNaN(price) ||
      price < 0
    ) {
      setPageError(
        "Проверьте стоимость работы.",
      );
      return;
    }

    if (
      assignments.length === 0 ||
      assignments.some(
        (item) =>
          !item.employee_number ||
          !item.share_percent,
      )
    ) {
      setPageError(
        "Укажите исполнителей и их доли.",
      );
      return;
    }

    const uniqueEmployees =
      new Set(
        assignments.map(
          (item) =>
            item.employee_number,
        ),
      );

    if (
      uniqueEmployees.size !==
      assignments.length
    ) {
      setPageError(
        "Один сотрудник не может быть указан дважды.",
      );
      return;
    }

    const totalShare =
      assignments.reduce(
        (
          total,
          item,
        ) =>
          total +
          item.share_percent,
        0,
      );

    if (
      Math.abs(
        totalShare - 100,
      ) > 0.001
    ) {
      setPageError(
        "Сумма долей исполнителей должна быть ровно 100%.",
      );
      return;
    }

    setWorkSaving(true);
    setPageError("");

    try {
      if (editingWork) {
        await updateWork(
          selectedOrder
            .work_order_number,

          editingWork
            .work_item_number,

          {
            name,
            price,
            assignments,
          },
        );
      } else {
        await createWork(
          selectedOrder
            .work_order_number,
          {
            name,
            price,
            assignments,
          },
        );
      }

      resetWorkForm();

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось сохранить работу.",
        ),
      );
    } finally {
      setWorkSaving(false);
    }
  }


  function resetPartForm() {
    setShowPartForm(false);
    setEditingPart(null);
    setPartName("");
    setPartQuantity("1");
    setPartPrice("");
    setPartSupplier("");
    setPartProvidedBy("sto");
  }


  function openNewPart() {
    setEditingPart(null);
    setPartName("");
    setPartQuantity("1");
    setPartPrice("");
    setPartSupplier("");
    setPartProvidedBy("sto");
    setShowPartForm(true);
  }


  function openPartEditor(
    part: Part,
  ) {
    setEditingPart(part);
    setPartName(part.name);
    setPartQuantity(
      String(
        part.quantity,
      ),
    );
    setPartPrice(
      String(
        part.unit_price,
      ),
    );
    setPartSupplier(
      part.supplier ?? "",
    );
    setPartProvidedBy(
      part.provided_by,
    );
    setShowPartForm(true);
  }


  async function savePart(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!selectedOrder) {
      return;
    }

    const name =
      partName.trim();

    const quantity =
      Number(partQuantity);

    const price =
      Number(partPrice);

    if (
      name.length < 2
    ) {
      setPageError(
        "Укажите название запчасти.",
      );
      return;
    }

    if (
      !Number.isInteger(
        quantity,
      ) ||
      quantity < 1
    ) {
      setPageError(
        "Количество должно быть не меньше 1.",
      );
      return;
    }

    if (
      Number.isNaN(price) ||
      price < 0
    ) {
      setPageError(
        "Проверьте цену запчасти.",
      );
      return;
    }

    setPartSaving(true);
    setPageError("");

    const payload = {
      name,
      quantity,
      unit_price: price,
      supplier:
        partSupplier.trim() ||
        null,
      provided_by:
        partProvidedBy,
    };

    try {
      if (editingPart) {
        await updatePart(
          selectedOrder
            .work_order_number,

          editingPart
            .part_number,

          payload,
        );
      } else {
        await createPart(
          selectedOrder
            .work_order_number,
          payload,
        );
      }

      resetPartForm();

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось сохранить запчасть.",
        ),
      );
    } finally {
      setPartSaving(false);
    }
  }


  async function removePart(
    part: Part,
  ) {
    if (!selectedOrder) {
      return;
    }

    if (
      !window.confirm(
        `Удалить запчасть «${part.name}»?`,
      )
    ) {
      return;
    }

    try {
      await deletePart(
        selectedOrder
          .work_order_number,
        part.part_number,
      );

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось удалить запчасть.",
        ),
      );
    }
  }


  function resetRecommendedForm() {
    setShowRecommendedForm(
      false,
    );
    setEditingRecommended(
      null,
    );
    setRecommendedName("");
    setRecommendedComment("");
  }


  function openRecommendedEditor(
    item:
      RecommendedWork | null,
  ) {
    setEditingRecommended(
      item,
    );

    setRecommendedName(
      item?.name ?? "",
    );

    setRecommendedComment(
      item?.comment ?? "",
    );

    setShowRecommendedForm(
      true,
    );
  }


  async function saveRecommended(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!selectedOrder) {
      return;
    }

    const name =
      recommendedName.trim();

    if (
      name.length < 2
    ) {
      setPageError(
        "Укажите рекомендованную работу.",
      );
      return;
    }

    setRecommendedSaving(true);

    try {
      const payload = {
        name,
        comment:
          recommendedComment
            .trim() ||
          null,
      };

      if (
        editingRecommended
      ) {
        await updateRecommendedWork(
          selectedOrder
            .work_order_number,

          editingRecommended
            .recommended_work_number,

          payload,
        );
      } else {
        await createRecommendedWork(
          selectedOrder
            .work_order_number,
          payload,
        );
      }

      resetRecommendedForm();

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось сохранить рекомендацию.",
        ),
      );
    } finally {
      setRecommendedSaving(false);
    }
  }


  async function removeRecommended(
    item: RecommendedWork,
  ) {
    if (!selectedOrder) {
      return;
    }

    if (
      !window.confirm(
        `Удалить рекомендацию «${item.name}»?`,
      )
    ) {
      return;
    }

    try {
      await deleteRecommendedWork(
        selectedOrder
          .work_order_number,

        item
          .recommended_work_number,
      );

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось удалить рекомендацию.",
        ),
      );
    }
  }


  function resetDisputeForm() {
    setShowDisputeForm(false);
    setEditingDispute(null);
    setDisputeFound("");
    setDisputeRecommendation("");
    setDisputeResponse("");
  }


  function openDisputeEditor(
    dispute:
      Dispute | null,
  ) {
    setEditingDispute(
      dispute,
    );

    setDisputeFound(
      dispute
        ?.found_text ??
        "",
    );

    setDisputeRecommendation(
      dispute
        ?.master_recommendation ??
        "",
    );

    setDisputeResponse(
      dispute
        ?.client_response ??
        "",
    );

    setShowDisputeForm(true);
  }


  async function saveDispute(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!selectedOrder) {
      return;
    }

    const found =
      disputeFound.trim();

    if (
      found.length < 2
    ) {
      setPageError(
        "Опишите обнаруженную ситуацию.",
      );
      return;
    }

    setDisputeSaving(true);

    const payload = {
      found_text: found,

      master_recommendation:
        disputeRecommendation
          .trim() ||
        null,

      client_response:
        disputeResponse
          .trim() ||
        null,
    };

    try {
      if (editingDispute) {
        await updateDispute(
          selectedOrder
            .work_order_number,

          editingDispute
            .dispute_number,

          payload,
        );
      } else {
        await createDispute(
          selectedOrder
            .work_order_number,
          payload,
        );
      }

      resetDisputeForm();

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось сохранить спорную ситуацию.",
        ),
      );
    } finally {
      setDisputeSaving(false);
    }
  }


  async function removeDispute(
    dispute: Dispute,
  ) {
    if (!selectedOrder) {
      return;
    }

    if (
      !window.confirm(
        "Удалить спорную ситуацию из рабочего интерфейса?",
      )
    ) {
      return;
    }

    try {
      await deleteDispute(
        selectedOrder
          .work_order_number,

        dispute
          .dispute_number,
      );

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось удалить спорную ситуацию.",
        ),
      );
    }
  }


  async function uploadPhoto(
    dispute: Dispute,
    file: File,
  ) {
    if (!selectedOrder) {
      return;
    }

    try {
      await uploadDisputePhoto(
        selectedOrder
          .work_order_number,

        dispute
          .dispute_number,

        file,
      );

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось загрузить фотографию.",
        ),
      );
    }
  }


  async function removePhoto(
    dispute: Dispute,
    photo: DisputePhoto,
  ) {
    if (!selectedOrder) {
      return;
    }

    try {
      await deleteDisputePhoto(
        selectedOrder
          .work_order_number,

        dispute
          .dispute_number,

        photo.photo_number,
      );

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось удалить фотографию.",
        ),
      );
    }
  }


  function resetPaymentForm() {
    setShowPaymentForm(false);
    setEditingPayment(null);
    setPaymentAmount("");
    setPaymentMethod("cash");
    setPaymentComment("");
  }


  function openPaymentEditor(
    payment: Payment | null,
  ) {
    setEditingPayment(
      payment,
    );

    setPaymentAmount(
      payment
        ? String(
            payment.amount,
          )
        : String(
            paymentSummary
              ?.debt_amount ??
              "",
          ),
    );

    setPaymentMethod(
      payment
        ?.method ??
        "cash",
    );

    setPaymentComment(
      payment
        ?.comment ??
        "",
    );

    setShowPaymentForm(true);
  }


  async function savePayment(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (!selectedOrder) {
      return;
    }

    const amount =
      Number(
        paymentAmount,
      );

    if (
      Number.isNaN(amount) ||
      amount <= 0
    ) {
      setPageError(
        "Сумма оплаты должна быть больше нуля.",
      );
      return;
    }

    setPaymentSaving(true);

    const payload = {
      amount,
      method:
        paymentMethod,
      comment:
        paymentComment
          .trim() ||
        null,
    };

    try {
      if (editingPayment) {
        await updatePayment(
          selectedOrder
            .work_order_number,

          editingPayment
            .payment_number,

          payload,
        );
      } else {
        await createPayment(
          selectedOrder
            .work_order_number,
          payload,
        );
      }

      resetPaymentForm();

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось сохранить оплату.",
        ),
      );
    } finally {
      setPaymentSaving(false);
    }
  }


  async function removePayment(
    payment: Payment,
  ) {
    if (!selectedOrder) {
      return;
    }

    if (
      !window.confirm(
        `Удалить оплату ${money(payment.amount)}?`,
      )
    ) {
      return;
    }

    try {
      await deletePayment(
        selectedOrder
          .work_order_number,

        payment
          .payment_number,
      );

      await loadDetails(
        selectedOrder
          .work_order_number,
      );
    } catch (error) {
      setPageError(
        errorText(
          error,
          "Не удалось удалить оплату.",
        ),
      );
    }
  }


  function nextStatusActions() {
    if (
      !selectedOrder ||
      !canManageOrder
    ) {
      return null;
    }

    if (
      selectedOrder.status ===
      "planned"
    ) {
      return (
        <button
          className="wo-status-action"
          onClick={() => {
            void setStatus(
              "in_progress",
            );
          }}
          type="button"
        >
          <Wrench size={15} />
          Начать работу
        </button>
      );
    }

    if (
      selectedOrder.status ===
      "in_progress"
    ) {
      return (
        <button
          className="wo-status-action"
          onClick={() => {
            void setStatus(
              "ready",
            );
          }}
          type="button"
        >
          <CheckCircle2
            size={15}
          />
          Готов к выдаче
        </button>
      );
    }

    if (
      selectedOrder.status ===
      "ready"
    ) {
      return (
        <div className="wo-status-actions">
          <button
            className="wo-secondary-action"
            onClick={() => {
              void setStatus(
                "in_progress",
              );
            }}
            type="button"
          >
            <RotateCcw size={15} />
            Вернуть в работу
          </button>

          <button
            className="wo-status-action"
            onClick={() => {
              void setStatus(
                "issued",
              );
            }}
            type="button"
          >
            <CheckCircle2
              size={15}
            />
            Выдать автомобиль
          </button>
        </div>
      );
    }

    return null;
  }


  return (
    <section className="wo-page">
      <div className="wo-toolbar">
        <div className="wo-filters">
          {(
            [
              [
                "all",
                "Все",
              ],
              [
                "planned",
                "Запланированы",
              ],
              [
                "in_progress",
                "В работе",
              ],
              [
                "ready",
                "Готовы",
              ],
              [
                "issued",
                "Выданы",
              ],
            ] as Array<
              [
                OrderFilter,
                string,
              ]
            >
          ).map(
            ([
              value,
              label,
            ]) => (
              <button
                className={
                  filter === value
                    ? "wo-filter wo-filter-active"
                    : "wo-filter"
                }
                key={value}
                onClick={() => {
                  setFilter(value);
                }}
                type="button"
              >
                {label}
              </button>
            ),
          )}
        </div>

        <div className="wo-toolbar-actions">
          <button
            className="wo-refresh"
            disabled={
              ordersLoading
            }
            onClick={() => {
              void loadOrders();
            }}
            type="button"
          >
            <RefreshCw
              size={16}
            />
            Обновить
          </button>

          {canManageOrder && (
            <button
              className="primary-button wo-new-button"
              onClick={() => {
                void openCreateOrder();
              }}
              type="button"
            >
              <Plus size={16} />
              Новый заказ-наряд
            </button>
          )}
        </div>
      </div>


      {pageError && (
        <div className="wo-error">
          <AlertTriangle
            size={17}
          />
          {pageError}
        </div>
      )}


      <div className="wo-layout">
        <aside className="wo-list-panel">
          <div className="wo-list-heading">
            <span>
              Заказ-наряды
            </span>

            <strong>
              {orders.length}
            </strong>
          </div>

          {ordersLoading &&
          orders.length === 0 ? (
            <div className="wo-empty">
              Загружаем...
            </div>
          ) : orders.length === 0 ? (
            <div className="wo-empty">
              Заказ-нарядов пока нет.
            </div>
          ) : (
            <div className="wo-order-list">
              {orders.map(
                (order) => (
                  <button
                    className={
                      selectedNumber ===
                      order
                        .work_order_number
                        ? "wo-order-card wo-order-card-active"
                        : "wo-order-card"
                    }
                    key={
                      order
                        .work_order_number
                    }
                    onClick={() => {
                      setSelectedNumber(
                        order
                          .work_order_number,
                      );
                    }}
                    type="button"
                  >
                    <div className="wo-order-card-top">
                      <strong>
                        Заказ №
                        {
                          order
                            .work_order_number
                        }
                      </strong>

                      <span
                        className={
                          `wo-status wo-status-${order.status}`
                        }
                      >
                        {
                          statusLabels[
                            order.status
                          ]
                        }
                      </span>
                    </div>

                    <div className="wo-order-client">
                      {
                        order
                          .client_name
                      }
                    </div>

                    <div className="wo-order-vehicle">
                      {vehicleTitle(
                        vehicles.find(
                          (vehicle) =>
                            vehicle
                              .vehicle_number ===
                            order
                              .vehicle_number,
                        ),
                        order
                          .license_plate,
                      )}
                    </div>

                    <div className="wo-order-reason">
                      {
                        order.reason
                      }
                    </div>

                    <div className="wo-order-card-bottom">
                      <span>
                        {dateTime(
                          order
                            .created_at,
                        )}
                      </span>

                      <ChevronRight
                        size={15}
                      />
                    </div>
                  </button>
                ),
              )}
            </div>
          )}
        </aside>


        <main className="wo-detail-panel">
          {!selectedOrder ? (
            <div className="wo-detail-empty">
              <ClipboardList
                size={34}
              />

              <strong>
                Выберите заказ-наряд
              </strong>

              <span>
                Здесь откроется
                полная карточка ремонта.
              </span>
            </div>
          ) : (
            <>
              <div className="wo-detail-header">
                <div>
                  <div className="wo-detail-number">
                    Заказ-наряд №
                    {
                      selectedOrder
                        .work_order_number
                    }
                  </div>

                  <h2>
                    {
                      selectedOrder
                        .client_name
                    }
                  </h2>

                  <div className="wo-detail-car">
                    {vehicleTitle(
                      selectedVehicle,
                      selectedOrder
                        .license_plate,
                    )}
                  </div>
                </div>

                <div className="wo-detail-status-box">
                  <div className="wo-detail-top-actions">
                    <button
                      className="wo-print-button"
                      onClick={() => {
                        setShowPrintPreview(
                          true,
                        );
                      }}
                      type="button"
                    >
                      <Printer size={16} />
                      Печать
                    </button>

                    <span
                      className={
                        `wo-status wo-status-${selectedOrder.status}`
                      }
                    >
                      {
                        statusLabels[
                          selectedOrder
                            .status
                        ]
                      }
                    </span>
                  </div>

                  {nextStatusActions()}
                </div>
              </div>


              <div className="wo-overview">
                <div>
                  <span>
                    Причина обращения
                  </span>

                  <strong>
                    {
                      selectedOrder
                        .reason
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Пробег
                  </span>

                  <strong>
                    {selectedOrder
                      .mileage === null
                      ? "—"
                      : `${selectedOrder.mileage.toLocaleString("ru-RU")} км`}
                  </strong>
                </div>

                <div>
                  <span>
                    Запись
                  </span>

                  <strong>
                    {selectedOrder
                      .appointment_number ===
                    null
                      ? "Без записи"
                      : `№${selectedOrder.appointment_number}`}
                  </strong>
                </div>

                <div>
                  <span>
                    Создан
                  </span>

                  <strong>
                    {dateTime(
                      selectedOrder
                        .created_at,
                    )}
                  </strong>
                </div>
              </div>


              {canManageOrder &&
                selectedOrder.status !==
                  "issued" && (
                <div className="wo-order-edit-line">
                  <button
                    className="wo-link-button"
                    onClick={() => {
                      setEditingOrder(
                        (value) =>
                          !value,
                      );
                    }}
                    type="button"
                  >
                    <Edit3 size={14} />
                    Изменить данные
                  </button>
                </div>
              )}


              {editingOrder && (
                <form
                  className="wo-inline-form"
                  onSubmit={
                    saveOrder
                  }
                >
                  <label>
                    <span>
                      Причина обращения
                    </span>

                    <textarea
                      rows={3}
                      value={
                        orderReason
                      }
                      onChange={(event) => {
                        setOrderReason(
                          event.target
                            .value,
                        );
                      }}
                    />
                  </label>

                  <label>
                    <span>
                      Пробег
                    </span>

                    <input
                      min="0"
                      type="number"
                      value={
                        orderMileage
                      }
                      onChange={(event) => {
                        setOrderMileage(
                          event.target
                            .value,
                        );
                      }}
                    />
                  </label>

                  <div className="wo-form-actions">
                    <button
                      className="wo-secondary-action"
                      onClick={() => {
                        setEditingOrder(
                          false,
                        );
                      }}
                      type="button"
                    >
                      Отмена
                    </button>

                    <button
                      className="primary-button"
                      disabled={
                        orderSaving
                      }
                      type="submit"
                    >
                      <Save size={15} />
                      Сохранить
                    </button>
                  </div>
                </form>
              )}


              <div className="wo-summary-strip">
                <div>
                  <span>
                    Работы
                  </span>
                  <strong>
                    {money(
                      paymentSummary
                        ?.works_total ??
                        workTotal,
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    Запчасти СТО
                  </span>
                  <strong>
                    {money(
                      paymentSummary
                        ?.parts_total ??
                        partsTotal,
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    Всего
                  </span>
                  <strong>
                    {money(
                      paymentSummary
                        ?.repair_total,
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    Оплачено
                  </span>
                  <strong>
                    {money(
                      paymentSummary
                        ?.paid_amount,
                    )}
                  </strong>
                </div>

                <div
                  className={
                    Number(
                      paymentSummary
                        ?.debt_amount ??
                        0,
                    ) > 0
                      ? "wo-summary-debt"
                      : ""
                  }
                >
                  <span>
                    Остаток
                  </span>
                  <strong>
                    {money(
                      paymentSummary
                        ?.debt_amount,
                    )}
                  </strong>
                </div>
              </div>


              <div className="wo-tabs">
                <button
                  className={
                    tab === "works"
                      ? "wo-tab wo-tab-active"
                      : "wo-tab"
                  }
                  onClick={() => {
                    setTab("works");
                  }}
                  type="button"
                >
                  <Wrench size={15} />
                  Работы
                  <span>
                    {works.length}
                  </span>
                </button>

                <button
                  className={
                    tab === "parts"
                      ? "wo-tab wo-tab-active"
                      : "wo-tab"
                  }
                  onClick={() => {
                    setTab("parts");
                  }}
                  type="button"
                >
                  <Package size={15} />
                  Запчасти
                  <span>
                    {parts.length}
                  </span>
                </button>

                <button
                  className={
                    tab ===
                    "recommended"
                      ? "wo-tab wo-tab-active"
                      : "wo-tab"
                  }
                  onClick={() => {
                    setTab(
                      "recommended",
                    );
                  }}
                  type="button"
                >
                  <ClipboardList
                    size={15}
                  />
                  Рекомендации
                  <span>
                    {
                      recommended
                        .length
                    }
                  </span>
                </button>

                <button
                  className={
                    tab ===
                    "disputes"
                      ? "wo-tab wo-tab-active"
                      : "wo-tab"
                  }
                  onClick={() => {
                    setTab(
                      "disputes",
                    );
                  }}
                  type="button"
                >
                  <FileWarning
                    size={15}
                  />
                  Спорные ситуации
                  <span>
                    {disputes.length}
                  </span>
                </button>

                <button
                  className={
                    tab === "payment"
                      ? "wo-tab wo-tab-active"
                      : "wo-tab"
                  }
                  onClick={() => {
                    setTab(
                      "payment",
                    );
                  }}
                  type="button"
                >
                  <CircleDollarSign
                    size={15}
                  />
                  Оплата
                </button>
              </div>


              <div
                className={
                  detailLoading
                    ? "wo-tab-content wo-tab-loading"
                    : "wo-tab-content"
                }
              >
                {tab === "works" && (
                  <section className="wo-section">
                    <div className="wo-section-heading">
                      <div>
                        <span>
                          Выполненные работы
                        </span>

                        <h3>
                          Работы
                        </h3>
                      </div>

                      {isOwner &&
                        selectedOrder.status !==
                          "issued" && (
                        <button
                          className="wo-add-button"
                          onClick={
                            openNewWork
                          }
                          type="button"
                        >
                          <Plus size={15} />
                          Добавить работу
                        </button>
                      )}
                    </div>


                    {showWorkForm && (
                      <form
                        className="wo-editor"
                        onSubmit={
                          saveWork
                        }
                      >
                        <div className="wo-editor-heading">
                          <strong>
                            {editingWork
                              ? "Изменение работы"
                              : "Новая работа"}
                          </strong>

                          <button
                            className="wo-icon-button"
                            onClick={
                              resetWorkForm
                            }
                            type="button"
                          >
                            <X size={16} />
                          </button>
                        </div>

                        <div className="wo-form-grid">
                          <label className="wo-wide">
                            <span>
                              Название работы
                            </span>

                            <input
                              value={
                                workName
                              }
                              onChange={(event) => {
                                setWorkName(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>

                          <label>
                            <span>
                              Стоимость, ₽
                            </span>

                            <input
                              min="0"
                              step="0.01"
                              type="number"
                              value={
                                workPrice
                              }
                              onChange={(event) => {
                                setWorkPrice(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>
                        </div>

                        <div className="wo-assignment-block">
                          <div className="wo-assignment-title">
                            <strong>
                              Исполнители
                            </strong>

                            <span>
                              Сумма долей должна быть 100%
                            </span>
                          </div>

                          {workAssignments.map(
                            (
                              assignment,
                              index,
                            ) => (
                              <div
                                className="wo-assignment-row"
                                key={index}
                              >
                                <select
                                  value={
                                    assignment
                                      .employee_number
                                  }
                                  onChange={(event) => {
                                    updateAssignment(
                                      index,
                                      "employee_number",
                                      event
                                        .target
                                        .value,
                                    );
                                  }}
                                >
                                  <option value="">
                                    Выберите сотрудника
                                  </option>

                                  {employees.map(
                                    (employee) => (
                                      <option
                                        key={
                                          employee
                                            .employee_number
                                        }
                                        value={
                                          employee
                                            .employee_number
                                        }
                                      >
                                        {
                                          employee
                                            .full_name
                                        }
                                      </option>
                                    ),
                                  )}
                                </select>

                                <input
                                  max="100"
                                  min="0.01"
                                  placeholder="Доля %"
                                  step="0.01"
                                  type="number"
                                  value={
                                    assignment
                                      .share_percent
                                  }
                                  onChange={(event) => {
                                    updateAssignment(
                                      index,
                                      "share_percent",
                                      event
                                        .target
                                        .value,
                                    );
                                  }}
                                />

                                {workAssignments.length >
                                  1 && (
                                  <button
                                    className="wo-icon-button"
                                    onClick={() => {
                                      removeAssignment(
                                        index,
                                      );
                                    }}
                                    type="button"
                                  >
                                    <Trash2
                                      size={15}
                                    />
                                  </button>
                                )}
                              </div>
                            ),
                          )}

                          <button
                            className="wo-link-button"
                            onClick={
                              addAssignment
                            }
                            type="button"
                          >
                            <Plus size={14} />
                            Добавить исполнителя
                          </button>
                        </div>

                        <div className="wo-form-actions">
                          <button
                            className="wo-secondary-action"
                            onClick={
                              resetWorkForm
                            }
                            type="button"
                          >
                            Отмена
                          </button>

                          <button
                            className="primary-button"
                            disabled={
                              workSaving
                            }
                            type="submit"
                          >
                            <Save size={15} />
                            Сохранить
                          </button>
                        </div>
                      </form>
                    )}


                    {works.length ===
                    0 ? (
                      <div className="wo-section-empty">
                        Работы пока не добавлены.
                      </div>
                    ) : (
                      <div className="wo-item-list">
                        {works.map(
                          (work) => (
                            <article
                              className="wo-item-card"
                              key={
                                work
                                  .work_item_number
                              }
                            >
                              <div className="wo-item-main">
                                <div>
                                  <span>
                                    Работа №
                                    {
                                      work
                                        .work_item_number
                                    }
                                  </span>

                                  <strong>
                                    {
                                      work.name
                                    }
                                  </strong>
                                </div>

                                <strong className="wo-money">
                                  {money(
                                    work.price,
                                  )}
                                </strong>
                              </div>

                              <div className="wo-performers">
                                {work.assignments.map(
                                  (
                                    assignment,
                                  ) => (
                                    <div
                                      key={
                                        assignment
                                          .employee_number
                                      }
                                    >
                                      <UserRound
                                        size={13}
                                      />

                                      <span>
                                        {
                                          assignment
                                            .employee_name
                                        }
                                      </span>

                                      {isFinancialWork(
                                        work,
                                      ) &&
                                        "share_percent" in
                                          assignment && (
                                        <small>
                                          {
                                            assignment
                                              .share_percent
                                          }
                                          % · ставка{" "}
                                          {
                                            assignment
                                              .rate_percent_snapshot
                                          }
                                          % · начислено{" "}
                                          {money(
                                            assignment
                                              .earning_amount,
                                          )}
                                        </small>
                                      )}
                                    </div>
                                  ),
                                )}
                              </div>

                              {isFinancialWork(
                                work,
                              ) && (
                                <div className="wo-financial-line">
                                  <span>
                                    Начисления сотрудникам
                                  </span>

                                  <strong>
                                    {money(
                                      work
                                        .total_employee_earnings,
                                    )}
                                  </strong>
                                </div>
                              )}

                              {isOwner &&
                                isFinancialWork(
                                  work,
                                ) &&
                                selectedOrder.status !==
                                  "issued" && (
                                <div className="wo-item-actions">
                                  <button
                                    className="wo-link-button"
                                    onClick={() => {
                                      openWorkEditor(
                                        work,
                                      );
                                    }}
                                    type="button"
                                  >
                                    <Edit3
                                      size={14}
                                    />
                                    Изменить
                                  </button>
                                </div>
                              )}
                            </article>
                          ),
                        )}
                      </div>
                    )}
                  </section>
                )}


                {tab === "parts" && (
                  <section className="wo-section">
                    <div className="wo-section-heading">
                      <div>
                        <span>
                          Комплектующие
                        </span>

                        <h3>
                          Запчасти
                        </h3>
                      </div>

                      {canManageParts &&
                        selectedOrder.status !==
                          "issued" && (
                        <button
                          className="wo-add-button"
                          onClick={
                            openNewPart
                          }
                          type="button"
                        >
                          <Plus size={15} />
                          Добавить запчасть
                        </button>
                      )}
                    </div>


                    {showPartForm && (
                      <form
                        className="wo-editor"
                        onSubmit={
                          savePart
                        }
                      >
                        <div className="wo-editor-heading">
                          <strong>
                            {editingPart
                              ? "Изменение запчасти"
                              : "Новая запчасть"}
                          </strong>

                          <button
                            className="wo-icon-button"
                            onClick={
                              resetPartForm
                            }
                            type="button"
                          >
                            <X size={16} />
                          </button>
                        </div>

                        <div className="wo-form-grid">
                          <label className="wo-wide">
                            <span>
                              Название
                            </span>

                            <input
                              value={
                                partName
                              }
                              onChange={(event) => {
                                setPartName(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>

                          <label>
                            <span>
                              Количество
                            </span>

                            <input
                              min="1"
                              step="1"
                              type="number"
                              value={
                                partQuantity
                              }
                              onChange={(event) => {
                                setPartQuantity(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>

                          <label>
                            <span>
                              Цена за единицу
                            </span>

                            <input
                              min="0"
                              step="0.01"
                              type="number"
                              value={
                                partPrice
                              }
                              onChange={(event) => {
                                setPartPrice(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>

                          <label>
                            <span>
                              Кто предоставил
                            </span>

                            <select
                              value={
                                partProvidedBy
                              }
                              onChange={(event) => {
                                setPartProvidedBy(
                                  event
                                    .target
                                    .value as PartProvidedBy,
                                );
                              }}
                            >
                              <option value="sto">
                                СТО
                              </option>

                              <option value="client">
                                Клиент
                              </option>
                            </select>
                          </label>

                          <label>
                            <span>
                              Поставщик
                            </span>

                            <input
                              placeholder="Необязательно"
                              value={
                                partSupplier
                              }
                              onChange={(event) => {
                                setPartSupplier(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>
                        </div>

                        <div className="wo-form-actions">
                          <button
                            className="wo-secondary-action"
                            onClick={
                              resetPartForm
                            }
                            type="button"
                          >
                            Отмена
                          </button>

                          <button
                            className="primary-button"
                            disabled={
                              partSaving
                            }
                            type="submit"
                          >
                            <Save size={15} />
                            Сохранить
                          </button>
                        </div>
                      </form>
                    )}


                    {parts.length ===
                    0 ? (
                      <div className="wo-section-empty">
                        Запчасти пока не добавлены.
                      </div>
                    ) : (
                      <div className="wo-item-list">
                        {parts.map(
                          (part) => (
                            <article
                              className="wo-item-card"
                              key={
                                part
                                  .part_number
                              }
                            >
                              <div className="wo-item-main">
                                <div>
                                  <span>
                                    Запчасть №
                                    {
                                      part
                                        .part_number
                                    }
                                  </span>

                                  <strong>
                                    {
                                      part.name
                                    }
                                  </strong>
                                </div>

                                <strong className="wo-money">
                                  {money(
                                    part
                                      .total_price,
                                  )}
                                </strong>
                              </div>

                              <div className="wo-part-meta">
                                <span>
                                  {
                                    part.quantity
                                  }{" "}
                                  ×{" "}
                                  {money(
                                    part
                                      .unit_price,
                                  )}
                                </span>

                                <span>
                                  {part.provided_by ===
                                  "sto"
                                    ? "Запчасть СТО"
                                    : "Запчасть клиента — в сумму ремонта не входит"}
                                </span>

                                {part.supplier && (
                                  <span>
                                    Поставщик:{" "}
                                    {
                                      part
                                        .supplier
                                    }
                                  </span>
                                )}
                              </div>

                              {canManageParts &&
                                selectedOrder.status !==
                                  "issued" && (
                                <div className="wo-item-actions">
                                  <button
                                    className="wo-link-button"
                                    onClick={() => {
                                      openPartEditor(
                                        part,
                                      );
                                    }}
                                    type="button"
                                  >
                                    <Edit3
                                      size={14}
                                    />
                                    Изменить
                                  </button>

                                  <button
                                    className="wo-danger-link"
                                    onClick={() => {
                                      void removePart(
                                        part,
                                      );
                                    }}
                                    type="button"
                                  >
                                    <Trash2
                                      size={14}
                                    />
                                    Удалить
                                  </button>
                                </div>
                              )}
                            </article>
                          ),
                        )}
                      </div>
                    )}
                  </section>
                )}


                {tab ===
                  "recommended" && (
                  <section className="wo-section">
                    <div className="wo-section-heading">
                      <div>
                        <span>
                          Не выполнено сейчас
                        </span>

                        <h3>
                          Рекомендованные работы
                        </h3>
                      </div>

                      {selectedOrder.status !==
                        "issued" && (
                        <button
                          className="wo-add-button"
                          onClick={() => {
                            openRecommendedEditor(
                              null,
                            );
                          }}
                          type="button"
                        >
                          <Plus size={15} />
                          Добавить
                        </button>
                      )}
                    </div>


                    {showRecommendedForm && (
                      <form
                        className="wo-editor"
                        onSubmit={
                          saveRecommended
                        }
                      >
                        <div className="wo-editor-heading">
                          <strong>
                            {editingRecommended
                              ? "Изменение рекомендации"
                              : "Новая рекомендация"}
                          </strong>

                          <button
                            className="wo-icon-button"
                            onClick={
                              resetRecommendedForm
                            }
                            type="button"
                          >
                            <X size={16} />
                          </button>
                        </div>

                        <div className="wo-form-grid">
                          <label className="wo-wide">
                            <span>
                              Работа
                            </span>

                            <input
                              value={
                                recommendedName
                              }
                              onChange={(event) => {
                                setRecommendedName(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>

                          <label className="wo-wide">
                            <span>
                              Комментарий
                            </span>

                            <textarea
                              rows={3}
                              value={
                                recommendedComment
                              }
                              onChange={(event) => {
                                setRecommendedComment(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>
                        </div>

                        <div className="wo-form-actions">
                          <button
                            className="wo-secondary-action"
                            onClick={
                              resetRecommendedForm
                            }
                            type="button"
                          >
                            Отмена
                          </button>

                          <button
                            className="primary-button"
                            disabled={
                              recommendedSaving
                            }
                            type="submit"
                          >
                            <Save size={15} />
                            Сохранить
                          </button>
                        </div>
                      </form>
                    )}


                    {recommended.length ===
                    0 ? (
                      <div className="wo-section-empty">
                        Рекомендаций пока нет.
                      </div>
                    ) : (
                      <div className="wo-item-list">
                        {recommended.map(
                          (item) => (
                            <article
                              className="wo-item-card"
                              key={
                                item
                                  .recommended_work_number
                              }
                            >
                              <div className="wo-item-main">
                                <div>
                                  <span>
                                    Рекомендация №
                                    {
                                      item
                                        .recommended_work_number
                                    }
                                  </span>

                                  <strong>
                                    {
                                      item.name
                                    }
                                  </strong>
                                </div>
                              </div>

                              {item.comment && (
                                <p className="wo-item-text">
                                  {
                                    item
                                      .comment
                                  }
                                </p>
                              )}

                              {selectedOrder.status !==
                                "issued" && (
                                <div className="wo-item-actions">
                                  <button
                                    className="wo-link-button"
                                    onClick={() => {
                                      openRecommendedEditor(
                                        item,
                                      );
                                    }}
                                    type="button"
                                  >
                                    <Edit3
                                      size={14}
                                    />
                                    Изменить
                                  </button>

                                  <button
                                    className="wo-danger-link"
                                    onClick={() => {
                                      void removeRecommended(
                                        item,
                                      );
                                    }}
                                    type="button"
                                  >
                                    <Trash2
                                      size={14}
                                    />
                                    Удалить
                                  </button>
                                </div>
                              )}
                            </article>
                          ),
                        )}
                      </div>
                    )}
                  </section>
                )}


                {tab ===
                  "disputes" && (
                  <section className="wo-section">
                    <div className="wo-section-heading">
                      <div>
                        <span>
                          Фиксация состояния
                        </span>

                        <h3>
                          Спорные ситуации и фото
                        </h3>
                      </div>

                      {selectedOrder.status !==
                        "issued" && (
                        <button
                          className="wo-add-button"
                          onClick={() => {
                            openDisputeEditor(
                              null,
                            );
                          }}
                          type="button"
                        >
                          <Plus size={15} />
                          Добавить ситуацию
                        </button>
                      )}
                    </div>


                    {showDisputeForm && (
                      <form
                        className="wo-editor"
                        onSubmit={
                          saveDispute
                        }
                      >
                        <div className="wo-editor-heading">
                          <strong>
                            {editingDispute
                              ? "Изменение ситуации"
                              : "Новая спорная ситуация"}
                          </strong>

                          <button
                            className="wo-icon-button"
                            onClick={
                              resetDisputeForm
                            }
                            type="button"
                          >
                            <X size={16} />
                          </button>
                        </div>


                        <div className="wo-form-grid">
                          <label className="wo-wide">
                            <span>
                              Что обнаружено
                            </span>

                            <textarea
                              rows={3}
                              value={
                                disputeFound
                              }
                              onChange={(event) => {
                                setDisputeFound(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>


                          <label className="wo-wide">
                            <span>
                              Рекомендация мастера
                            </span>

                            <textarea
                              rows={3}
                              value={
                                disputeRecommendation
                              }
                              onChange={(event) => {
                                setDisputeRecommendation(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>


                          <label className="wo-wide">
                            <span>
                              Ответ клиента
                            </span>

                            <textarea
                              rows={3}
                              value={
                                disputeResponse
                              }
                              onChange={(event) => {
                                setDisputeResponse(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>
                        </div>


                        <div className="wo-form-actions">
                          <button
                            className="wo-secondary-action"
                            onClick={
                              resetDisputeForm
                            }
                            type="button"
                          >
                            Отмена
                          </button>

                          <button
                            className="primary-button"
                            disabled={
                              disputeSaving
                            }
                            type="submit"
                          >
                            <Save size={15} />
                            Сохранить
                          </button>
                        </div>
                      </form>
                    )}


                    {disputes.length ===
                    0 ? (
                      <div className="wo-section-empty">
                        Спорных ситуаций нет.
                      </div>
                    ) : (
                      <div className="wo-item-list">
                        {disputes.map(
                          (dispute) => (
                            <article
                              className="wo-dispute-card"
                              key={
                                dispute
                                  .dispute_number
                              }
                            >
                              <div className="wo-dispute-heading">
                                <div>
                                  <span>
                                    Ситуация №
                                    {
                                      dispute
                                        .dispute_number
                                    }{" "}
                                    ·{" "}
                                    {dateTime(
                                      dispute
                                        .recorded_at,
                                    )}
                                  </span>

                                  <strong>
                                    Что обнаружено
                                  </strong>

                                  <p>
                                    {
                                      dispute
                                        .found_text
                                    }
                                  </p>
                                </div>
                              </div>


                              {dispute.master_recommendation && (
                                <div className="wo-dispute-note">
                                  <span>
                                    Рекомендация мастера
                                  </span>

                                  <p>
                                    {
                                      dispute
                                        .master_recommendation
                                    }
                                  </p>
                                </div>
                              )}


                              {dispute.client_response && (
                                <div className="wo-dispute-note">
                                  <span>
                                    Ответ клиента
                                  </span>

                                  <p>
                                    {
                                      dispute
                                        .client_response
                                    }
                                  </p>
                                </div>
                              )}


                              <DisputePhotoGallery
                                canEdit={
                                  selectedOrder.status !==
                                  "issued"
                                }
                                disputeNumber={
                                  dispute
                                    .dispute_number
                                }
                                photos={
                                  disputePhotos[
                                    dispute
                                      .dispute_number
                                  ] ?? []
                                }
                                workOrderNumber={
                                  selectedOrder
                                    .work_order_number
                                }
                                onDelete={(photo) =>
                                  removePhoto(
                                    dispute,
                                    photo,
                                  )
                                }
                                onUpload={(file) =>
                                  uploadPhoto(
                                    dispute,
                                    file,
                                  )
                                }
                              />


                              {selectedOrder.status !==
                                "issued" && (
                                <div className="wo-item-actions">
                                  <button
                                    className="wo-link-button"
                                    onClick={() => {
                                      openDisputeEditor(
                                        dispute,
                                      );
                                    }}
                                    type="button"
                                  >
                                    <Edit3
                                      size={14}
                                    />
                                    Изменить
                                  </button>

                                  <button
                                    className="wo-danger-link"
                                    onClick={() => {
                                      void removeDispute(
                                        dispute,
                                      );
                                    }}
                                    type="button"
                                  >
                                    <Trash2
                                      size={14}
                                    />
                                    Удалить
                                  </button>
                                </div>
                              )}
                            </article>
                          ),
                        )}
                      </div>
                    )}
                  </section>
                )}

                {tab === "payment" && (
                  <section className="wo-section">
                    <div className="wo-section-heading">
                      <div>
                        <span>
                          Учёт оплаты и задолженности
                        </span>

                        <h3>
                          Оплата
                        </h3>
                      </div>

                      {canManagePayments &&
                        Number(
                          paymentSummary
                            ?.debt_amount ??
                            0,
                        ) > 0 && (
                        <button
                          className="wo-add-button"
                          onClick={() => {
                            openPaymentEditor(
                              null,
                            );
                          }}
                          type="button"
                        >
                          <Plus size={15} />
                          Добавить оплату
                        </button>
                      )}
                    </div>


                    <div className="wo-payment-summary">
                      <div>
                        <span>
                          Работы
                        </span>

                        <strong>
                          {money(
                            paymentSummary
                              ?.works_total,
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Запчасти СТО
                        </span>

                        <strong>
                          {money(
                            paymentSummary
                              ?.parts_total,
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Итого ремонт
                        </span>

                        <strong>
                          {money(
                            paymentSummary
                              ?.repair_total,
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Оплачено
                        </span>

                        <strong>
                          {money(
                            paymentSummary
                              ?.paid_amount,
                          )}
                        </strong>
                      </div>

                      <div className="wo-payment-debt">
                        <span>
                          Осталось оплатить
                        </span>

                        <strong>
                          {money(
                            paymentSummary
                              ?.debt_amount,
                          )}
                        </strong>
                      </div>
                    </div>


                    {showPaymentForm && (
                      <form
                        className="wo-editor"
                        onSubmit={
                          savePayment
                        }
                      >
                        <div className="wo-editor-heading">
                          <strong>
                            {editingPayment
                              ? "Изменение оплаты"
                              : "Новая оплата"}
                          </strong>

                          <button
                            className="wo-icon-button"
                            onClick={
                              resetPaymentForm
                            }
                            type="button"
                          >
                            <X size={16} />
                          </button>
                        </div>

                        <div className="wo-form-grid">
                          <label>
                            <span>
                              Сумма
                            </span>

                            <input
                              min="0.01"
                              step="0.01"
                              type="number"
                              value={
                                paymentAmount
                              }
                              onChange={(event) => {
                                setPaymentAmount(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>

                          <label>
                            <span>
                              Способ оплаты
                            </span>

                            <select
                              value={
                                paymentMethod
                              }
                              onChange={(event) => {
                                setPaymentMethod(
                                  event
                                    .target
                                    .value as PaymentMethod,
                                );
                              }}
                            >
                              <option value="cash">
                                Наличные
                              </option>

                              <option value="card">
                                Карта
                              </option>

                              <option value="transfer">
                                Перевод
                              </option>
                            </select>
                          </label>

                          <label className="wo-wide">
                            <span>
                              Комментарий
                            </span>

                            <input
                              placeholder="Необязательно"
                              value={
                                paymentComment
                              }
                              onChange={(event) => {
                                setPaymentComment(
                                  event
                                    .target
                                    .value,
                                );
                              }}
                            />
                          </label>
                        </div>

                        <div className="wo-form-actions">
                          <button
                            className="wo-secondary-action"
                            onClick={
                              resetPaymentForm
                            }
                            type="button"
                          >
                            Отмена
                          </button>

                          <button
                            className="primary-button"
                            disabled={
                              paymentSaving
                            }
                            type="submit"
                          >
                            <Save size={15} />
                            Сохранить
                          </button>
                        </div>
                      </form>
                    )}


                    {paymentSummary
                      ?.payments.length ===
                    0 ? (
                      <div className="wo-section-empty">
                        Оплат пока нет.
                      </div>
                    ) : (
                      <div className="wo-item-list">
                        {paymentSummary
                          ?.payments.map(
                            (payment) => (
                              <article
                                className="wo-payment-row"
                                key={
                                  payment
                                    .payment_number
                                }
                              >
                                <div>
                                  <span>
                                    Оплата №
                                    {
                                      payment
                                        .payment_number
                                    }{" "}
                                    ·{" "}
                                    {dateTime(
                                      payment
                                        .paid_at,
                                    )}
                                  </span>

                                  <strong>
                                    {
                                      paymentLabels[
                                        payment
                                          .method
                                      ]
                                    }
                                  </strong>

                                  {payment.comment && (
                                    <p>
                                      {
                                        payment
                                          .comment
                                      }
                                    </p>
                                  )}
                                </div>

                                <strong className="wo-money">
                                  {money(
                                    payment
                                      .amount,
                                  )}
                                </strong>

                                {canManagePayments && (
                                  <div className="wo-payment-actions">
                                    <button
                                      className="wo-link-button"
                                      onClick={() => {
                                        openPaymentEditor(
                                          payment,
                                        );
                                      }}
                                      type="button"
                                    >
                                      <Edit3
                                        size={14}
                                      />
                                      Изменить
                                    </button>

                                    <button
                                      className="wo-danger-link"
                                      onClick={() => {
                                        void removePayment(
                                          payment,
                                        );
                                      }}
                                      type="button"
                                    >
                                      <Trash2
                                        size={14}
                                      />
                                      Удалить
                                    </button>
                                  </div>
                                )}
                              </article>
                            ),
                          )}
                      </div>
                    )}
                  </section>
                )}
              </div>
            </>
          )}
        </main>
      </div>


      {showPrintPreview &&
        selectedOrder && (
        <WorkOrderPrintPreview
          order={
            selectedOrder
          }
          parts={parts}
          paymentSummary={
            paymentSummary
          }
          recommended={
            recommended
          }
          vehicle={
            selectedVehicle
          }
          works={works}
          onClose={() => {
            setShowPrintPreview(
              false,
            );
          }}
        />
      )}

      {showCreate && (
        <div className="wo-modal-backdrop">
          <form
            className="wo-modal"
            onSubmit={
              handleCreateOrder
            }
          >
            <div className="wo-modal-heading">
              <div>
                <span>
                  Новый ремонт
                </span>

                <h2>
                  Новый заказ-наряд
                </h2>
              </div>

              <button
                className="wo-icon-button"
                onClick={() => {
                  setShowCreate(false);
                }}
                type="button"
              >
                <X size={18} />
              </button>
            </div>

            <div className="wo-form-grid">
              <label className="wo-wide">
                <span>
                  Клиент *
                </span>

                <select
                  required
                  value={
                    createClientNumber
                  }
                  onChange={(event) => {
                    void handleCreateClient(
                      event.target
                        .value,
                    );
                  }}
                >
                  <option value="">
                    Выберите клиента
                  </option>

                  {createClients.map(
                    (client) => (
                      <option
                        key={
                          client
                            .client_number
                        }
                        value={
                          client
                            .client_number
                        }
                      >
                        {
                          client
                            .full_name
                        }{" "}
                        ·{" "}
                        {
                          client
                            .phone_primary
                        }
                      </option>
                    ),
                  )}
                </select>
              </label>

              <label className="wo-wide">
                <span>
                  Автомобиль *
                </span>

                <select
                  disabled={
                    !createClientNumber
                  }
                  required
                  value={
                    createVehicleNumber
                  }
                  onChange={(event) => {
                    void handleCreateVehicle(
                      event.target
                        .value,
                    );
                  }}
                >
                  <option value="">
                    Выберите автомобиль
                  </option>

                  {createVehicles.map(
                    (vehicle) => (
                      <option
                        key={
                          vehicle
                            .vehicle_number
                        }
                        value={
                          vehicle
                            .vehicle_number
                        }
                      >
                        {
                          vehicle.brand
                        }{" "}
                        {
                          vehicle.model
                        }{" "}
                        ·{" "}
                        {
                          vehicle
                            .license_plate
                        }
                      </option>
                    ),
                  )}
                </select>
              </label>

              <label className="wo-wide">
                <span>
                  Запись клиента
                </span>

                <select
                  disabled={
                    !createVehicleNumber
                  }
                  value={
                    createAppointmentNumber
                  }
                  onChange={(event) => {
                    handleCreateAppointment(
                      event.target
                        .value,
                    );
                  }}
                >
                  <option value="">
                    Без привязки к записи
                  </option>

                  {createAppointments.map(
                    (appointment) => (
                      <option
                        key={
                          appointment
                            .appointment_number
                        }
                        value={
                          appointment
                            .appointment_number
                        }
                      >
                        №
                        {
                          appointment
                            .appointment_number
                        }{" "}
                        ·{" "}
                        {
                          appointment
                            .appointment_date
                        }{" "}
                        {
                          appointment
                            .appointment_time
                        }{" "}
                        ·{" "}
                        {
                          appointment
                            .reason
                        }
                      </option>
                    ),
                  )}
                </select>
              </label>

              <label className="wo-wide">
                <span>
                  Причина обращения *
                </span>

                <textarea
                  required
                  rows={4}
                  value={
                    createReason
                  }
                  onChange={(event) => {
                    setCreateReason(
                      event.target
                        .value,
                    );
                  }}
                />
              </label>

              <label>
                <span>
                  Пробег
                </span>

                <input
                  min="0"
                  type="number"
                  value={
                    createMileage
                  }
                  onChange={(event) => {
                    setCreateMileage(
                      event.target
                        .value,
                    );
                  }}
                />
              </label>
            </div>

            <div className="wo-form-actions">
              <button
                className="wo-secondary-action"
                onClick={() => {
                  setShowCreate(false);
                }}
                type="button"
              >
                Отмена
              </button>

              <button
                className="primary-button"
                disabled={
                  createSaving
                }
                type="submit"
              >
                <Save size={15} />

                {createSaving
                  ? "Создаём..."
                  : "Создать заказ-наряд"}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}