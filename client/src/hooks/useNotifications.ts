import { useCallback, useEffect, useRef, useState } from 'react'
import {
	clearNotifications,
	listNotifications,
	type NotificationRead,
} from '@/lib/api'
import { getErrorMessage } from '@/lib/utils/errors'

const POLL_INTERVAL_MS = 3000

export function useNotifications() {
	const [notifications, setNotifications] = useState<NotificationRead[]>([])
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState<string | null>(null)
	const requestIdRef = useRef(0)

	const refetch = useCallback(async () => {
		const requestId = ++requestIdRef.current

		try {
			const data = await listNotifications()
			if (requestId !== requestIdRef.current) {
				return
			}
			setNotifications(data)
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
	}, [])

	useEffect(() => {
		void refetch()
		const intervalId = window.setInterval(() => {
			void refetch()
		}, POLL_INTERVAL_MS)

		return () => {
			requestIdRef.current += 1
			window.clearInterval(intervalId)
		}
	}, [refetch])

	const clearInbox = useCallback(async () => {
		await clearNotifications()
		await refetch()
	}, [refetch])

	return {
		notifications,
		loading,
		error,
		clearInbox,
		refetch,
	}
}
