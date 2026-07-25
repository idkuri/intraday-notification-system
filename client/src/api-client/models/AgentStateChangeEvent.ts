/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AgentStateChangeEvent = {
  event_id: string;
  ts: string;
  type: string;
  agent_id: string;
  queue_ids?: (Array<string> | null);
  previous_state?: (string | null);
  previous_state_duration_sec?: (number | null);
  new_state: string;
};

