import { createApiClient } from '@/lib/api-client/client'
import type { components } from '@/lib/api-client/schema'
import { parseApiError } from '@/lib/utils/errors'
import { getUsername } from '@/stores/usernameStore'

export type RuleRead = components['schemas']['RuleRead']
export type RuleCreate = components['schemas']['RuleCreate']
export type RuleUpdate = components['schemas']['RuleUpdate']
export type NotificationRead = components['schemas']['NotificationRead']

const baseUrl =
	import.meta.env.VITE_API_BASE_URL?.trim() || 'http://127.0.0.1:8000'

const client = createApiClient(baseUrl)

client.use({
	onRequest({ request }) {
		const username = getUsername()
		if (username) {
			request.headers.set('X-Username', username)
		}
		return request
	},
})

async function unwrap<T>(result: {
	data?: T
	error?: unknown
	response: Response
}): Promise<T> {
	const { data, error, response } = result
	if (error || !response.ok) {
		throw parseApiError(error, response.status)
	}
	return data as T
}

export async function listRules(): Promise<RuleRead[]> {
	const result = await client.GET('/rules', {
		params: {
			header: {
				'X-Username': getUsername() || null,
			},
		},
	})
	return unwrap(result)
}

export async function createRule(body: RuleCreate): Promise<RuleRead> {
	const result = await client.POST('/rules', {
		body,
		params: {
			header: {
				'X-Username': getUsername() || null,
			},
		},
	})
	return unwrap(result)
}

export async function patchRule(
	ruleId: string,
	body: RuleUpdate
): Promise<RuleRead> {
	const result = await client.PATCH('/rules/{rule_id}', {
		params: {
			path: { rule_id: ruleId },
			header: {
				'X-Username': getUsername() || null,
			},
		},
		body,
	})
	return unwrap(result)
}

export async function deleteRule(ruleId: string): Promise<void> {
	const result = await client.DELETE('/rules/{rule_id}', {
		params: {
			path: { rule_id: ruleId },
			header: {
				'X-Username': getUsername() || null,
			},
		},
	})
	await unwrap(result)
}

export async function listNotifications(): Promise<NotificationRead[]> {
	const result = await client.GET('/notifications')
	return unwrap(result)
}

export async function clearNotifications(): Promise<void> {
	const result = await client.DELETE('/notifications')
	await unwrap(result)
}
