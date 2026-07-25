import { ApiError } from '@/api-client'

function validationDetails(body: unknown): string[] {
	if (
		typeof body !== 'object' ||
		body === null ||
		!('detail' in body) ||
		!Array.isArray((body as { detail: unknown }).detail)
	) {
		return []
	}

	return (
		body as { detail: Array<{ loc: unknown[]; msg: string }> }
	).detail.map(item => `${item.loc.join('.')}: ${item.msg}`)
}

function detailMessage(body: unknown): string | null {
	if (typeof body !== 'object' || body === null || !('detail' in body)) {
		return null
	}
	const detail = (body as { detail: unknown }).detail
	return typeof detail === 'string' ? detail : null
}

export function getErrorMessage(err: unknown): string {
	if (err instanceof ApiError) {
		const details = validationDetails(err.body)
		if (details.length > 0) {
			return `Validation failed: ${details.join('; ')}`
		}
		const detail = detailMessage(err.body)
		if (detail) {
			return detail
		}
		return err.message || `Request failed (${err.status})`
	}
	if (err instanceof Error) {
		return err.message
	}
	return 'An unexpected error occurred'
}
