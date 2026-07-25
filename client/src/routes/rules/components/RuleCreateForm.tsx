import { FormEvent, useState } from 'react'
import type { RuleCreate } from '@/lib/api'
import type {
	AgentState,
	Audience,
	ChannelType,
	Severity,
	TriggerType,
} from '@/lib/consts/triggers'
import {
	AGENT_STATES,
	CHANNELS,
	DEFAULT_CHANNELS,
	DEFAULT_SEVERITY,
	SEVERITIES,
	TRIGGER_FIELD_CONFIG,
	TRIGGER_LABELS,
	TRIGGER_TYPES,
	defaultAudienceForTrigger,
	parseCommaSeparatedIds,
} from '@/lib/consts/triggers'
import { DEMO_AGENTS, DEMO_QUEUES, formatAgentOption } from '@/lib/demoRoster'
import { useCreateRule } from '../hooks/useCreateRule'

interface RuleCreateFormProps {
	disabled: boolean
	submitting: boolean
	onSubmit: (body: RuleCreate) => Promise<boolean>
}

export function RuleCreateForm({
	disabled,
	submitting,
	onSubmit,
}: RuleCreateFormProps) {
	const { submit } = useCreateRule({ onSubmit })
	const [name, setName] = useState('')
	const [ownerId, setOwnerId] = useState('')
	const [triggerType, setTriggerType] =
		useState<TriggerType>('queue_sla_breached')
	const [audience, setAudience] = useState<Audience>(
		defaultAudienceForTrigger('queue_sla_breached')
	)
	const [audienceOverridden, setAudienceOverridden] = useState(false)
	const [agentId, setAgentId] = useState('')
	const [queueIdsText, setQueueIdsText] = useState('')
	const [threshold, setThreshold] = useState('')
	const [targetState, setTargetState] = useState<AgentState>('available')
	const [severity, setSeverity] = useState<Severity>(DEFAULT_SEVERITY)
	const [channels, setChannels] = useState<ChannelType[]>([...DEFAULT_CHANNELS])
	const [enabled, setEnabled] = useState(true)
	const [formError, setFormError] = useState<string | null>(null)

	const fieldConfig = TRIGGER_FIELD_CONFIG[triggerType]

	const toggleChannel = (channel: ChannelType) => {
		setChannels(current =>
			current.includes(channel)
				? current.filter(item => item !== channel)
				: [...current, channel]
		)
	}

	const resetForm = () => {
		setName('')
		setOwnerId('')
		setTriggerType('queue_sla_breached')
		setAudience(defaultAudienceForTrigger('queue_sla_breached'))
		setAudienceOverridden(false)
		setAgentId('')
		setQueueIdsText('')
		setThreshold('')
		setTargetState('available')
		setSeverity(DEFAULT_SEVERITY)
		setChannels([...DEFAULT_CHANNELS])
		setEnabled(true)
		setFormError(null)
	}

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault()
		setFormError(null)

		const trimmedName = name.trim()
		const trimmedOwnerId = ownerId.trim()
		const queueIds = parseCommaSeparatedIds(queueIdsText)

		if (!trimmedName) {
			setFormError('Name is required.')
			return
		}
		if (!trimmedOwnerId) {
			setFormError('Owner ID is required.')
			return
		}
		if (fieldConfig.agentIdRequired && !agentId.trim()) {
			setFormError('Agent ID is required for this trigger.')
			return
		}
		if (fieldConfig.queueIdsRequired && queueIds.length === 0) {
			setFormError('At least one queue ID is required for this trigger.')
			return
		}
		if (
			triggerType === 'agent_state_duration' &&
			!agentId.trim() &&
			queueIds.length === 0
		) {
			setFormError('Provide an agent ID and/or queue IDs for this trigger.')
			return
		}
		if (fieldConfig.showThreshold && !threshold.trim()) {
			setFormError('Threshold is required for this trigger.')
			return
		}
		if (channels.length === 0) {
			setFormError('Select at least one delivery channel.')
			return
		}

		const parsedThreshold =
			fieldConfig.showThreshold && threshold.trim() ? Number(threshold) : null

		if (
			fieldConfig.showThreshold &&
			(parsedThreshold == null || Number.isNaN(parsedThreshold))
		) {
			setFormError('Threshold must be a valid number.')
			return
		}

		const body: RuleCreate = {
			name: trimmedName,
			enabled,
			audience,
			owner_id: trimmedOwnerId,
			trigger_type: triggerType,
			severity,
			channels,
			scope: {
				agent_id:
					fieldConfig.showAgentId && agentId.trim() ? agentId.trim() : null,
				queue_ids:
					fieldConfig.showQueueIds && queueIds.length > 0 ? queueIds : null,
			},
			threshold: fieldConfig.showThreshold ? parsedThreshold : null,
			target_state: fieldConfig.showTargetState ? targetState : null,
		}

		const success = await submit(body)
		if (success) {
			resetForm()
		}
	}

	return (
		<div className="panel">
			<h3>Create rule</h3>

			{formError && <div className="alert alert-error">{formError}</div>}

			<form onSubmit={event => void handleSubmit(event)}>
				<div className="form-grid">
					<div className="form-field">
						<label htmlFor="rule-name">Name</label>
						<input
							id="rule-name"
							value={name}
							onChange={event => setName(event.target.value)}
							disabled={disabled || submitting}
						/>
					</div>

					<div className="form-field">
						<label htmlFor="rule-owner-id">
							Owner (notification recipient)
						</label>
						{audience === 'agent' ? (
							<select
								id="rule-owner-id"
								value={ownerId}
								onChange={event => {
									const next = event.target.value
									setOwnerId(next)
									if (fieldConfig.showAgentId && !agentId) {
										setAgentId(next)
									}
								}}
								disabled={disabled || submitting}
								required
							>
								<option value="">Select agent…</option>
								{DEMO_AGENTS.map(agent => (
									<option key={agent.agent_id} value={agent.agent_id}>
										{formatAgentOption(agent)}
									</option>
								))}
							</select>
						) : (
							<input
								id="rule-owner-id"
								value={ownerId}
								onChange={event => setOwnerId(event.target.value)}
								placeholder="e.g. lead_billing"
								disabled={disabled || submitting}
								required
							/>
						)}
					</div>

					<div className="form-field">
						<label htmlFor="rule-trigger-type">Trigger type</label>
						<select
							id="rule-trigger-type"
							value={triggerType}
							onChange={event => {
								const next = event.target.value as TriggerType
								setTriggerType(next)
								if (!audienceOverridden) {
									setAudience(defaultAudienceForTrigger(next))
								}
							}}
							disabled={disabled || submitting}
						>
							{TRIGGER_TYPES.map(type => (
								<option key={type} value={type}>
									{TRIGGER_LABELS[type]}
								</option>
							))}
						</select>
					</div>

					<div className="form-field">
						<label htmlFor="rule-audience">Audience</label>
						<select
							id="rule-audience"
							value={audience}
							onChange={event => {
								setAudience(event.target.value as Audience)
								setAudienceOverridden(true)
							}}
							disabled={disabled || submitting}
						>
							<option value="agent">agent</option>
							<option value="team_lead">team_lead</option>
						</select>
					</div>

					{fieldConfig.showAgentId && (
						<div className="form-field">
							<label htmlFor="rule-agent-id">
								Scope agent{fieldConfig.agentIdRequired ? ' *' : ' (optional)'}
							</label>
							<select
								id="rule-agent-id"
								value={agentId}
								onChange={event => {
									const next = event.target.value
									setAgentId(next)
									if (audience === 'agent' && next) {
										setOwnerId(next)
									}
								}}
								disabled={disabled || submitting}
							>
								<option value="">
									{fieldConfig.agentIdRequired
										? 'Select agent…'
										: 'Any matching agent'}
								</option>
								{DEMO_AGENTS.map(agent => (
									<option key={agent.agent_id} value={agent.agent_id}>
										{formatAgentOption(agent)}
									</option>
								))}
							</select>
						</div>
					)}

					{fieldConfig.showQueueIds && (
						<div className="form-field form-field--full">
							<span>
								Scope queues
								{fieldConfig.queueIdsRequired ? ' *' : ' (optional)'}
							</span>
							<div className="checkbox-row">
								{DEMO_QUEUES.map(queueId => {
									const selected =
										parseCommaSeparatedIds(queueIdsText).includes(queueId)
									return (
										<label key={queueId}>
											<input
												type="checkbox"
												checked={selected}
												onChange={() => {
													const current = parseCommaSeparatedIds(queueIdsText)
													const next = selected
														? current.filter(id => id !== queueId)
														: [...current, queueId]
													setQueueIdsText(next.join(', '))
												}}
												disabled={disabled || submitting}
											/>
											{queueId}
										</label>
									)
								})}
							</div>
						</div>
					)}

					{fieldConfig.showThreshold && (
						<div className="form-field">
							<label htmlFor="rule-threshold">Threshold (seconds) *</label>
							<input
								id="rule-threshold"
								type="number"
								min="0"
								value={threshold}
								onChange={event => setThreshold(event.target.value)}
								disabled={disabled || submitting}
							/>
						</div>
					)}

					{fieldConfig.showTargetState && (
						<div className="form-field">
							<label htmlFor="rule-target-state">Target state</label>
							<select
								id="rule-target-state"
								value={targetState}
								onChange={event =>
									setTargetState(event.target.value as AgentState)
								}
								disabled={disabled || submitting}
							>
								{AGENT_STATES.map(state => (
									<option key={state} value={state}>
										{state}
									</option>
								))}
							</select>
						</div>
					)}

					<div className="form-field">
						<label htmlFor="rule-severity">Severity</label>
						<select
							id="rule-severity"
							value={severity}
							onChange={event => setSeverity(event.target.value as Severity)}
							disabled={disabled || submitting}
						>
							{SEVERITIES.map(level => (
								<option key={level} value={level}>
									{level}
								</option>
							))}
						</select>
					</div>

					<div className="form-field form-field--full">
						<span>Channels</span>
						<div className="checkbox-row">
							{CHANNELS.map(channel => (
								<label key={channel}>
									<input
										type="checkbox"
										checked={channels.includes(channel)}
										onChange={() => toggleChannel(channel)}
										disabled={disabled || submitting}
									/>
									{channel}
								</label>
							))}
						</div>
					</div>

					<div className="form-field form-field--full">
						<label>
							<input
								type="checkbox"
								checked={enabled}
								onChange={event => setEnabled(event.target.checked)}
								disabled={disabled || submitting}
							/>{' '}
							Enabled
						</label>
					</div>
				</div>

				{disabled && (
					<p className="helper-text">
						Enter a username in the header to create rules.
					</p>
				)}

				<div style={{ marginTop: '0.75rem' }}>
					<button
						type="submit"
						className="btn btn-primary"
						disabled={disabled || submitting}
					>
						{submitting ? 'Creating…' : 'Create rule'}
					</button>
				</div>
			</form>
		</div>
	)
}
