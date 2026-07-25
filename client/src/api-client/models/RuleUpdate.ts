/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AgentState } from './AgentState';
import type { ChannelType } from './ChannelType';
import type { RuleScope } from './RuleScope';
import type { Severity } from './Severity';
import type { TriggerType } from './TriggerType';
export type RuleUpdate = {
  name?: (string | null);
  enabled?: (boolean | null);
  owner_id?: (string | null);
  scope?: (RuleScope | null);
  trigger_type?: (TriggerType | null);
  threshold?: (number | null);
  target_state?: (AgentState | null);
  severity?: (Severity | null);
  channels?: (Array<ChannelType> | null);
};

