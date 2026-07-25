import { OpenAPI } from '@/api-client'
import { getUsername } from '@/stores/usernameStore'

/** Call once at app boot. Username is also passed per-call (codegen always sets the header key). */
export function configureApiClient(): void {
	OpenAPI.BASE =
		import.meta.env.VITE_API_BASE_URL?.trim() || 'http://127.0.0.1:8000'
	OpenAPI.HEADERS = async (): Promise<Record<string, string>> => {
		const username = getUsername().trim()
		if (!username) {
			return {}
		}
		return { 'X-Username': username }
	}
}

/** Header args for generated *Service methods that take `xUsername`. */
export function usernameHeader(): { xUsername: string | null } {
	const username = getUsername().trim()
	return { xUsername: username || null }
}
