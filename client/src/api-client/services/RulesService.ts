/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RuleCreate } from '../models/RuleCreate';
import type { RuleRead } from '../models/RuleRead';
import type { RuleUpdate } from '../models/RuleUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RulesService {
  /**
   * List Rules
   * @returns RuleRead Successful Response
   * @throws ApiError
   */
  public static listRulesRulesGet({
    xUsername,
  }: {
    xUsername?: (string | null),
  }): CancelablePromise<Array<RuleRead>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/rules',
      headers: {
        'X-Username': xUsername,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Create Rule
   * @returns RuleRead Successful Response
   * @throws ApiError
   */
  public static createRuleRulesPost({
    requestBody,
    xUsername,
  }: {
    requestBody: RuleCreate,
    xUsername?: (string | null),
  }): CancelablePromise<RuleRead> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/rules',
      headers: {
        'X-Username': xUsername,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Get Rule
   * @returns RuleRead Successful Response
   * @throws ApiError
   */
  public static getRuleRulesRuleIdGet({
    ruleId,
    xUsername,
  }: {
    ruleId: string,
    xUsername?: (string | null),
  }): CancelablePromise<RuleRead> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/rules/{rule_id}',
      path: {
        'rule_id': ruleId,
      },
      headers: {
        'X-Username': xUsername,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Rule
   * @returns RuleRead Successful Response
   * @throws ApiError
   */
  public static updateRuleRulesRuleIdPatch({
    ruleId,
    requestBody,
    xUsername,
  }: {
    ruleId: string,
    requestBody: RuleUpdate,
    xUsername?: (string | null),
  }): CancelablePromise<RuleRead> {
    return __request(OpenAPI, {
      method: 'PATCH',
      url: '/rules/{rule_id}',
      path: {
        'rule_id': ruleId,
      },
      headers: {
        'X-Username': xUsername,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete Rule
   * @returns void
   * @throws ApiError
   */
  public static deleteRuleRulesRuleIdDelete({
    ruleId,
    xUsername,
  }: {
    ruleId: string,
    xUsername?: (string | null),
  }): CancelablePromise<void> {
    return __request(OpenAPI, {
      method: 'DELETE',
      url: '/rules/{rule_id}',
      path: {
        'rule_id': ruleId,
      },
      headers: {
        'X-Username': xUsername,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
