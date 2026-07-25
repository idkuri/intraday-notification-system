import { useState } from 'react'
import { useNotifications } from '@/hooks/useNotifications'
import { getErrorMessage } from '@/lib/utils/errors'

function severityClass(severity: string): string {
	switch (severity) {
		case 'critical':
			return 'badge badge-critical'
		case 'warning':
			return 'badge badge-warning'
		default:
			return 'badge badge-info'
	}
}

export function NotificationsPage() {
	const { notifications, loading, error, clearInbox } = useNotifications()
	const [clearing, setClearing] = useState(false)
	const [clearError, setClearError] = useState<string | null>(null)

	const handleClearInbox = async () => {
		setClearing(true)
		setClearError(null)
		try {
			await clearInbox()
		} catch (err) {
			setClearError(getErrorMessage(err))
		} finally {
			setClearing(false)
		}
	}

	return (
		<section>
			<div className="page-header">
				<h2>Notifications</h2>
				<button
					type="button"
					className="btn btn-danger"
					disabled={loading || clearing || notifications.length === 0}
					onClick={() => void handleClearInbox()}
				>
					{clearing ? 'Clearing…' : 'Clear inbox'}
				</button>
			</div>

			{error && <div className="alert alert-error">{error}</div>}
			{clearError && <div className="alert alert-error">{clearError}</div>}

			{loading && notifications.length === 0 ? (
				<div className="empty-state">Loading notifications…</div>
			) : notifications.length === 0 ? (
				<div className="empty-state">No notifications yet.</div>
			) : (
				<div className="panel">
					<table className="data-table">
						<thead>
							<tr>
								<th>ID</th>
								<th>Severity</th>
								<th>Title</th>
								<th>Body</th>
								<th>Recipient</th>
								<th>Rule ID</th>
								<th>Timestamp</th>
							</tr>
						</thead>
						<tbody>
							{notifications.map(notification => (
								<tr key={notification.id}>
									<td className="mono">{notification.id}</td>
									<td>
										<span className={severityClass(notification.severity)}>
											{notification.severity}
										</span>
									</td>
									<td>{notification.title}</td>
									<td>{notification.body}</td>
									<td className="mono">{notification.recipient_id}</td>
									<td className="mono">{notification.rule_id}</td>
									<td>{new Date(notification.ts).toLocaleString()}</td>
								</tr>
							))}
						</tbody>
					</table>
				</div>
			)}
		</section>
	)
}
