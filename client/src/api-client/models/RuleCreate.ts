/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AgentState } from './AgentState';
import type { ChannelType } from './ChannelType';
import type { RuleScope } from './RuleScope';
import type { Severity } from './Severity';
import type { TriggerType } from './TriggerType';
export type RuleCreate = {
  name: string;
  enabled?: boolean;
  owner_id: string;
  scope: RuleScope;
  trigger_type: TriggerType;
  threshold?: (number | null);
  target_state?: (AgentState | null);
  severity?: Severity;
  channels?: Array<ChannelType>;
};

