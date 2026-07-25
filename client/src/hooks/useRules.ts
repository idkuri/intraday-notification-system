import { useCallback, useEffect, useRef, useState } from 'react'
import { RulesService, type RuleRead } from '@/api-client'
import { usernameHeader } from '@/lib/configureApiClient'
import { getErrorMessage } from '@/lib/utils/errors'
import { useUsernameStore } from '@/stores/usernameStore'

export function useRules() {
	const username = useUsernameStore(state => state.username)
	const authEpoch = useUsernameStore(state => state.authEpoch)
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
			const data = await RulesService.listRulesRulesGet(usernameHeader())
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
		// authEpoch: re-run on Login even when the username string is unchanged.
	}, [refetch, authEpoch])

	return {
		rules,
		loading,
		error,
		refetch,
	}
}
