import { useCallback, useEffect, useRef, useState } from 'react'
import { NotificationsService, type NotificationRead } from '@/api-client'
import { usernameHeader } from '@/lib/configureApiClient'
import { getErrorMessage } from '@/lib/utils/errors'
import { useUsernameStore } from '@/stores/usernameStore'

const POLL_INTERVAL_MS = 3000

export function useNotifications() {
	const username = useUsernameStore(state => state.username)
	const authEpoch = useUsernameStore(state => state.authEpoch)
	const [notifications, setNotifications] = useState<NotificationRead[]>([])
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState<string | null>(null)
	const requestIdRef = useRef(0)

	const refetch = useCallback(async () => {
		const requestId = ++requestIdRef.current

		if (!username.trim()) {
			if (requestId !== requestIdRef.current) {
				return
			}
			setNotifications([])
			setError(null)
			setLoading(false)
			return
		}

		try {
			const data =
				await NotificationsService.listNotificationsNotificationsGet(
					usernameHeader()
				)
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
	}, [username])

	useEffect(() => {
		void refetch()
		const intervalId = window.setInterval(() => {
			void refetch()
		}, POLL_INTERVAL_MS)

		return () => {
			requestIdRef.current += 1
			window.clearInterval(intervalId)
		}
		// authEpoch: re-run on Login even when the username string is unchanged.
	}, [refetch, authEpoch])

	const clearInbox = useCallback(async () => {
		await NotificationsService.clearInboxNotificationsDelete(usernameHeader())
		await refetch()
	}, [refetch])

	return {
		notifications,
		loading,
		error,
		clearInbox,
		refetch,
		canView: Boolean(username.trim()),
	}
}
