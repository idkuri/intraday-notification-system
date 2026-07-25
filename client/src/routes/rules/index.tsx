import { useRules } from '@/hooks/useRules'
import { useRuleActions } from '@/hooks/useRuleActions'
import { RuleCreateForm } from './components/RuleCreateForm'

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

export function RulesPage() {
	const { rules, loading, error, refetch } = useRules()
	const {
		actionError,
		busyRuleId,
		creating,
		create,
		toggleEnabled,
		remove,
		canMutate,
	} = useRuleActions({ refetch })

	return (
		<section>
			<div className="page-header">
				<h2>Rules</h2>
			</div>

			{!canMutate && (
				<div className="alert alert-info">
					Set a username in the header to view and manage your rules. Demo
					personas: a_19, a_42, lead_billing.
				</div>
			)}

			{(error || actionError) && (
				<div className="alert alert-error">{error ?? actionError}</div>
			)}

			<RuleCreateForm
				disabled={!canMutate || creating}
				submitting={creating}
				onSubmit={create}
			/>

			{loading && rules.length === 0 ? (
				<div className="empty-state">Loading rules…</div>
			) : rules.length === 0 ? (
				<div className="empty-state">No rules configured yet.</div>
			) : (
				<div className="panel">
					<table className="data-table">
						<thead>
							<tr>
								<th>Name</th>
								<th>Trigger</th>
								<th>Audience</th>
								<th>Severity</th>
								<th>Status</th>
								<th>Owner</th>
								<th>Scope</th>
								<th>Actions</th>
							</tr>
						</thead>
						<tbody>
							{rules.map(rule => {
								const scopeParts: string[] = []
								if (rule.scope.agent_id) {
									scopeParts.push(`agent: ${rule.scope.agent_id}`)
								}
								if (rule.scope.queue_ids?.length) {
									scopeParts.push(`queues: ${rule.scope.queue_ids.join(', ')}`)
								}
								if (rule.threshold != null) {
									scopeParts.push(`threshold: ${rule.threshold}`)
								}
								if (rule.target_state) {
									scopeParts.push(`state: ${rule.target_state}`)
								}

								return (
									<tr key={rule.id}>
										<td>{rule.name}</td>
										<td className="mono">{rule.trigger_type}</td>
										<td>{rule.audience}</td>
										<td>
											<span className={severityClass(rule.severity)}>
												{rule.severity}
											</span>
										</td>
										<td>
											<span
												className={
													rule.enabled
														? 'badge badge-enabled'
														: 'badge badge-disabled'
												}
											>
												{rule.enabled ? 'enabled' : 'disabled'}
											</span>
										</td>
										<td className="mono">{rule.owner_id}</td>
										<td>{scopeParts.join(' · ') || '—'}</td>
										<td>
											<div className="actions-cell">
												<button
													type="button"
													className="btn btn-sm"
													disabled={!canMutate || busyRuleId === rule.id}
													onClick={() =>
														void toggleEnabled(rule.id, rule.enabled)
													}
												>
													{rule.enabled ? 'Disable' : 'Enable'}
												</button>
												<button
													type="button"
													className="btn btn-sm btn-danger"
													disabled={!canMutate || busyRuleId === rule.id}
													onClick={() => void remove(rule.id)}
												>
													Delete
												</button>
											</div>
										</td>
									</tr>
								)
							})}
						</tbody>
					</table>
				</div>
			)}
		</section>
	)
}
