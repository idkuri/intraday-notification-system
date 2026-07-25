import type { components } from '@/lib/api-client/schema'

type HTTPValidationError = components['schemas']['HTTPValidationError']

export class ApiError extends Error {
	readonly status: number
	readonly details: string[]

	constructor(message: string, status: number, details: string[] = []) {
		super(message)
		this.name = 'ApiError'
		this.status = status
		this.details = details
	}
}

function isValidationError(body: unknown): body is HTTPValidationError {
	return (
		typeof body === 'object' &&
		body !== null &&
		'detail' in body &&
		Array.isArray((body as HTTPValidationError).detail)
	)
}

export function parseApiError(error: unknown, status: number): ApiError {
	if (isValidationError(error)) {
		const details = (error.detail ?? []).map(
			item => `${item.loc.join('.')}: ${item.msg}`
		)
		return new ApiError('Validation failed', status, details)
	}

	if (typeof error === 'object' && error !== null && 'detail' in error) {
		const detail = (error as { detail: unknown }).detail
		if (typeof detail === 'string') {
			return new ApiError(detail, status)
		}
	}

	return new ApiError(`Request failed (${status})`, status)
}

export function getErrorMessage(err: unknown): string {
	if (err instanceof ApiError) {
		if (err.details.length > 0) {
			return `${err.message}: ${err.details.join('; ')}`
		}
		return err.message
	}
	if (err instanceof Error) {
		return err.message
	}
	return 'An unexpected error occurred'
}
