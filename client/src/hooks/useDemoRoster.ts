import { useEffect, useState } from 'react'
import { DemoService, type DemoAgentRead } from '@/api-client'
import { getErrorMessage } from '@/lib/utils/errors'

export function useDemoRoster() {
	const [agents, setAgents] = useState<DemoAgentRead[]>([])
	const [queues, setQueues] = useState<string[]>([])
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState<string | null>(null)

	useEffect(() => {
		let cancelled = false

		void (async () => {
			setLoading(true)
			try {
				const roster = await DemoService.getDemoRosterDemoRosterGet()
				if (cancelled) {
					return
				}
				setAgents(roster.agents)
				setQueues(roster.queues)
				setError(null)
			} catch (err) {
				if (cancelled) {
					return
				}
				setAgents([])
				setQueues([])
				setError(getErrorMessage(err))
			} finally {
				if (!cancelled) {
					setLoading(false)
				}
			}
		})()

		return () => {
			cancelled = true
		}
	}, [])

	return { agents, queues, loading, error }
}
