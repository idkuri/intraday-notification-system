/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Result of evaluating and delivering notifications for one ingested event.
 *
 * Attributes:
 * notifications_emitted: Number of notifications created for this event.
 * notification_ids: Primary keys of those notification rows, in creation order.
 */
export type IngestEventResponse = {
  /**
   * Count of notifications created
   */
  notifications_emitted: number;
  /**
   * IDs of created notification rows
   */
  notification_ids: Array<string>;
};

