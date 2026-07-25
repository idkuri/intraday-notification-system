/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChannelType } from './ChannelType';
import type { Severity } from './Severity';
/**
 * Persisted inbox notification.
 */
export type NotificationRead = {
  id: string;
  rule_id: string;
  recipient_id: string;
  title: string;
  body: string;
  severity: Severity;
  entity_key: string;
  triggering_event_id: string;
  ts: string;
  delivered_channels: Array<ChannelType>;
};

