/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type QueueSnapshotEvent = {
  event_id: string;
  ts: string;
  type: string;
  queue_id: string;
  tickets_waiting: number;
  longest_wait_sec: number;
  sla_target_sec: number;
  agents_available: number;
  agents_on_call: number;
  volume_last_15m: number;
  volume_forecast_next_15m?: (number | null);
};

