/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DemoRosterResponse } from '../models/DemoRosterResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DemoService {
  /**
   * Get Demo Roster
   * Return the static demo agents and queues for UI pickers.
   * @returns DemoRosterResponse Successful Response
   * @throws ApiError
   */
  public static getDemoRosterDemoRosterGet(): CancelablePromise<DemoRosterResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/demo/roster',
    });
  }
}
