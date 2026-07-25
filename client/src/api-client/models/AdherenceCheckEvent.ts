/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AdherenceCheckEvent = {
  event_id: string;
  ts: string;
  type: string;
  agent_id: string;
  queue_ids?: (Array<string> | null);
  scheduled_state: string;
  actual_state: string;
  in_violation: boolean;
  violation_started_at?: (string | null);
};

