import { useCallback, useEffect, useRef, useState } from 'react'
import { listRules, type RuleRead } from '@/lib/api'
import { getErrorMessage } from '@/lib/utils/errors'
import { useUsernameStore } from '@/stores/usernameStore'

export function useRules() {
	const username = useUsernameStore(state => state.username)
	const [rules, setRules] = useState<RuleRead[]>([])
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState<string | null>(null)
	const requestIdRef = useRef(0)

	const refetch = useCallback(async () => {
		const requestId = ++requestIdRef.current

		if (!username.trim()) {
			if (requestId !== requestIdRef.current) {
				return
			}
			setRules([])
			setError(null)
			setLoading(false)
			return
		}

		setLoading(true)
		try {
			const data = await listRules()
			if (requestId !== requestIdRef.current) {
				return
			}
			setRules(data)
			setError(null)
		} catch (err) {
			if (requestId !== requestIdRef.current) {
				return
			}
			setError(getErrorMessage(err))
		} finally {
			if (requestId === requestIdRef.current) {
				setLoading(false)
			}
		}
	}, [username])

	useEffect(() => {
		void refetch()
	}, [refetch])

	return {
		rules,
		loading,
		error,
		refetch,
	}
}
