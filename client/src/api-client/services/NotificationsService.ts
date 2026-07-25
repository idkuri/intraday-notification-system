/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NotificationRead } from '../models/NotificationRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class NotificationsService {
  /**
   * List Notifications
   * @returns NotificationRead Successful Response
   * @throws ApiError
   */
  public static listNotificationsNotificationsGet({
    xUsername,
  }: {
    xUsername?: (string | null),
  }): CancelablePromise<Array<NotificationRead>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/notifications',
      headers: {
        'X-Username': xUsername,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Clear Inbox
   * @returns void
   * @throws ApiError
   */
  public static clearInboxNotificationsDelete({
    xUsername,
  }: {
    xUsername?: (string | null),
  }): CancelablePromise<void> {
    return __request(OpenAPI, {
      method: 'DELETE',
      url: '/notifications',
      headers: {
        'X-Username': xUsername,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
