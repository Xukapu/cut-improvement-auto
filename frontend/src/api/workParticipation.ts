import {
  apiRequest,
} from "./client";

import type {
  WorkParticipation,
  WorkParticipationUpdate,
} from "../types/workParticipation";


export function getWorkParticipation():
  Promise<WorkParticipation> {
  return apiRequest<
    WorkParticipation
  >(
    "/api/v1/account/work-participation",
  );
}


export function updateWorkParticipation(
  payload:
    WorkParticipationUpdate,
): Promise<WorkParticipation> {
  return apiRequest<
    WorkParticipation
  >(
    "/api/v1/account/work-participation",
    {
      method: "PUT",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}