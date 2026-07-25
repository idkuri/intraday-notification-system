/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdherenceCheckEvent } from '../models/AdherenceCheckEvent';
import type { AgentStateChangeEvent } from '../models/AgentStateChangeEvent';
import type { IngestEventResponse } from '../models/IngestEventResponse';
import type { QueueSnapshotEvent } from '../models/QueueSnapshotEvent';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EventsService {
  /**
   * Ingest Event
   * Ingest a single domain event and return emitted notification IDs.
   * @returns IngestEventResponse Successful Response
   * @throws ApiError
   */
  public static ingestEventEventsPost({
    requestBody,
  }: {
    requestBody: (QueueSnapshotEvent | AgentStateChangeEvent | AdherenceCheckEvent),
  }): CancelablePromise<IngestEventResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/events',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
