/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DemoAgentRead } from './DemoAgentRead';
/**
 * Agents and queues used by the sample feed and rule UI pickers.
 */
export type DemoRosterResponse = {
  agents: Array<DemoAgentRead>;
  /**
   * Queue IDs present in the demo feed
   */
  queues: Array<string>;
};

