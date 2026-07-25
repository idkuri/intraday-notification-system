import { FormEvent, useEffect, useState } from 'react'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Checkbox from '@mui/material/Checkbox'
import CircularProgress from '@mui/material/CircularProgress'
import FormControlLabel from '@mui/material/FormControlLabel'
import FormGroup from '@mui/material/FormGroup'
import MenuItem from '@mui/material/MenuItem'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import {
	AgentState,
	Severity,
	TriggerType,
	type RuleCreate,
	type RuleRead,
	type RuleUpdate,
} from '@/api-client'
import { useDemoRoster } from '@/hooks/useDemoRoster'
import { formatAgentOption } from '@/lib/demoRoster'
import { getUsername } from '@/stores/usernameStore'
import {
	DEFAULT_CHANNELS,
	DEFAULT_SEVERITY,
	TRIGGER_FIELD_CONFIG,
	TRIGGER_LABELS,
	parseCommaSeparatedIds,
} from '../triggerFormConfig'
import { parseRuleForm } from './parseRuleForm'

interface RuleFormProps {
	disabled: boolean
	submitting: boolean
	editingRule: RuleRead | null
	onCreate: (body: RuleCreate) => Promise<boolean>
	onUpdate: (ruleId: string, body: RuleUpdate) => Promise<boolean>
	onClose: () => void
}

function emptyFormState() {
	return {
		name: '',
		triggerType: TriggerType.QUEUE_SLA_BREACHED,
		agentId: '',
		queueIdsText: '',
		threshold: '',
		targetState: AgentState.AVAILABLE,
		severity: DEFAULT_SEVERITY,
	}
}

function formStateFromRule(rule: RuleRead) {
	return {
		name: rule.name,
		triggerType: rule.trigger_type,
		agentId: rule.scope.agent_id ?? '',
		queueIdsText: rule.scope.queue_ids?.join(', ') ?? '',
		threshold: rule.threshold != null ? String(rule.threshold) : '',
		targetState: rule.target_state ?? AgentState.AVAILABLE,
		severity: rule.severity ?? DEFAULT_SEVERITY,
	}
}

export function RuleCreateForm({
	disabled,
	submitting,
	editingRule,
	onCreate,
	onUpdate,
	onClose,
}: RuleFormProps) {
	const isEditing = editingRule != null
	const [name, setName] = useState('')
	const [triggerType, setTriggerType] = useState<TriggerType>(
		TriggerType.QUEUE_SLA_BREACHED
	)
	const [agentId, setAgentId] = useState('')
	const [queueIdsText, setQueueIdsText] = useState('')
	const [threshold, setThreshold] = useState('')
	const [targetState, setTargetState] = useState<AgentState>(
		AgentState.AVAILABLE
	)
	const [severity, setSeverity] = useState<Severity>(DEFAULT_SEVERITY)
	const [formError, setFormError] = useState<string | null>(null)
	const {
		agents,
		queues,
		loading: rosterLoading,
		error: rosterError,
	} = useDemoRoster()

	useEffect(() => {
		const next = editingRule ? formStateFromRule(editingRule) : emptyFormState()
		setName(next.name)
		setTriggerType(next.triggerType)
		setAgentId(next.agentId)
		setQueueIdsText(next.queueIdsText)
		setThreshold(next.threshold)
		setTargetState(next.targetState)
		setSeverity(next.severity)
		setFormError(null)
	}, [editingRule])

	const fieldConfig = TRIGGER_FIELD_CONFIG[triggerType]

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault()
		setFormError(null)

		const parsed = parseRuleForm({
			name,
			ownerId: getUsername(),
			triggerType,
			agentId,
			queueIds: parseCommaSeparatedIds(queueIdsText),
			thresholdText: threshold,
			targetState,
		})
		if ('error' in parsed) {
			setFormError(parsed.error)
			return
		}

		const { fields } = parsed
		const channels = [...DEFAULT_CHANNELS]

		if (isEditing && editingRule) {
			const body: RuleUpdate = {
				name: fields.name,
				enabled: editingRule.enabled ?? true,
				trigger_type: triggerType,
				severity,
				channels,
				scope: fields.scope,
				threshold: fields.threshold,
				target_state: fields.targetState,
			}
			const success = await onUpdate(editingRule.id, body)
			if (success) {
				onClose()
			}
			return
		}

		const body: RuleCreate = {
			name: fields.name,
			enabled: true,
			owner_id: fields.ownerId,
			trigger_type: triggerType,
			severity,
			channels,
			scope: fields.scope,
			threshold: fields.threshold,
			target_state: fields.targetState,
		}

		const success = await onCreate(body)
		if (success) {
			onClose()
		}
	}

	const fieldsDisabled = disabled || submitting || rosterLoading

	return (
		<Box
			component="form"
			id="rule-form"
			onSubmit={event => void handleSubmit(event)}
		>
			<Stack spacing={2}>
				{formError && <Alert severity="error">{formError}</Alert>}
				{rosterError && (
					<Alert severity="error">
						Could not load demo roster: {rosterError}
					</Alert>
				)}
				{rosterLoading && (
					<Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
						<CircularProgress size={16} />
						<Typography variant="body2" color="text.secondary">
							Loading agents and queues…
						</Typography>
					</Stack>
				)}

				<Box
					sx={{
						display: 'grid',
						gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
						gap: 2,
					}}
				>
					<TextField
						id="rule-name"
						label="Name"
						value={name}
						onChange={event => setName(event.target.value)}
						disabled={fieldsDisabled}
						size="small"
						fullWidth
					/>

					<TextField
						id="rule-trigger-type"
						label="Trigger type"
						select
						value={triggerType}
						onChange={event =>
							setTriggerType(event.target.value as TriggerType)
						}
						disabled={fieldsDisabled}
						size="small"
						fullWidth
					>
						{Object.values(TriggerType).map(type => (
							<MenuItem key={type} value={type}>
								{TRIGGER_LABELS[type]}
							</MenuItem>
						))}
					</TextField>

					{fieldConfig.showAgentId && (
						<TextField
							id="rule-agent-id"
							label={`Scope agent${fieldConfig.agentIdRequired ? ' *' : ' (optional)'}`}
							select
							value={agentId}
							onChange={event => setAgentId(event.target.value)}
							disabled={fieldsDisabled}
							size="small"
							fullWidth
						>
							<MenuItem value="">
								{fieldConfig.agentIdRequired
									? 'Select agent…'
									: 'Any matching agent'}
							</MenuItem>
							{agents.map(agent => (
								<MenuItem key={agent.agent_id} value={agent.agent_id}>
									{formatAgentOption(agent)}
								</MenuItem>
							))}
						</TextField>
					)}

					{fieldConfig.showThreshold && (
						<TextField
							id="rule-threshold"
							label={
								triggerType === TriggerType.QUEUE_TICKETS_WAITING
									? 'Threshold (tickets) *'
									: triggerType === TriggerType.QUEUE_FORECAST_OVER_VOLUME
										? 'Threshold (% of recent volume) *'
										: 'Threshold (seconds) *'
							}
							type="number"
							slotProps={{ htmlInput: { min: 0 } }}
							value={threshold}
							onChange={event => setThreshold(event.target.value)}
							disabled={fieldsDisabled}
							size="small"
							fullWidth
						/>
					)}

					{fieldConfig.showTargetState && (
						<TextField
							id="rule-target-state"
							label="Target state"
							select
							value={targetState}
							onChange={event =>
								setTargetState(event.target.value as AgentState)
							}
							disabled={fieldsDisabled}
							size="small"
							fullWidth
						>
							{Object.values(AgentState).map(state => (
								<MenuItem key={state} value={state}>
									{state}
								</MenuItem>
							))}
						</TextField>
					)}

					<TextField
						id="rule-severity"
						label="Severity"
						select
						value={severity}
						onChange={event => setSeverity(event.target.value as Severity)}
						disabled={fieldsDisabled}
						size="small"
						fullWidth
					>
						{Object.values(Severity).map(level => (
							<MenuItem key={level} value={level}>
								{level}
							</MenuItem>
						))}
					</TextField>

					{fieldConfig.showQueueIds && (
						<Box sx={{ gridColumn: '1 / -1' }}>
							<Typography variant="body2" sx={{ mb: 0.5, fontWeight: 600 }}>
								Scope queues
								{fieldConfig.queueIdsRequired ? ' *' : ' (optional)'}
							</Typography>
							<FormGroup row>
								{queues.map(queueId => {
									const selected =
										parseCommaSeparatedIds(queueIdsText).includes(queueId)
									return (
										<FormControlLabel
											key={queueId}
											control={
												<Checkbox
													checked={selected}
													onChange={() => {
														const current = parseCommaSeparatedIds(queueIdsText)
														const next = selected
															? current.filter(id => id !== queueId)
															: [...current, queueId]
														setQueueIdsText(next.join(', '))
													}}
													disabled={fieldsDisabled}
													size="small"
												/>
											}
											label={queueId}
										/>
									)
								})}
							</FormGroup>
						</Box>
					)}
				</Box>
			</Stack>
		</Box>
	)
}

export function ruleFormSubmitLabel(
	isEditing: boolean,
	submitting: boolean
): string {
	if (submitting) {
		return isEditing ? 'Saving…' : 'Creating…'
	}
	return isEditing ? 'Save changes' : 'Create rule'
}
