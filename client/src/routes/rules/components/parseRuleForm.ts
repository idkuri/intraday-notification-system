import { TriggerType, type AgentState } from '@/api-client'
import { TRIGGER_FIELD_CONFIG } from '../triggerFormConfig'

export type ThresholdUnit = 'hr' | 'min' | 'sec'

export const THRESHOLD_UNITS: ThresholdUnit[] = ['hr', 'min', 'sec']
export const THRESHOLD_UNIT_LABELS: Record<ThresholdUnit, string> = {
	hr: 'hour(s)',
	min: 'minute(s)',
	sec: 'second(s)',
}
export const DEFAULT_THRESHOLD_UNIT: ThresholdUnit = 'min'

export interface RuleFormFields {
	name: string
	ownerId: string
	scope: {
		agent_id: string | null
		queue_ids: string[] | null
	}
	threshold: number | null
	targetState: AgentState | null
}

interface RuleFormInput {
	name: string
	ownerId: string
	triggerType: TriggerType
	agentId: string
	queueIds: string[]
	thresholdText: string
	thresholdUnit: ThresholdUnit
	targetState: AgentState
}

const DURATION_TRIGGER_TYPES = new Set<TriggerType>([
	TriggerType.ADHERENCE_VIOLATION_DURATION,
	TriggerType.AGENT_STATE_DURATION,
])

const UNIT_TO_SECONDS: Record<ThresholdUnit, number> = {
	hr: 3600,
	min: 60,
	sec: 1,
}

/** Duration triggers store threshold in seconds; the form edits value + unit. */
export function isDurationThresholdTrigger(triggerType: TriggerType): boolean {
	return DURATION_TRIGGER_TYPES.has(triggerType)
}

/** Form value (+ unit for duration) → API threshold. */
export function thresholdForApi(
	triggerType: TriggerType,
	parsedThreshold: number,
	unit: ThresholdUnit
): number {
	if (!isDurationThresholdTrigger(triggerType)) {
		return parsedThreshold
	}
	return parsedThreshold * UNIT_TO_SECONDS[unit]
}

/** API seconds → form value + unit (largest whole unit that divides evenly). */
export function splitThresholdSeconds(seconds: number): {
	value: string
	unit: ThresholdUnit
} {
	if (seconds % 3600 === 0) {
		return { value: String(seconds / 3600), unit: 'hr' }
	}
	if (seconds % 60 === 0) {
		return { value: String(seconds / 60), unit: 'min' }
	}
	return { value: String(seconds), unit: 'sec' }
}

/** API threshold → form value string (duration uses split; others pass through). */
export function thresholdFormValue(
	triggerType: TriggerType,
	thresholdSeconds: number | null | undefined
): string {
	if (thresholdSeconds == null) {
		return ''
	}
	if (isDurationThresholdTrigger(triggerType)) {
		return splitThresholdSeconds(thresholdSeconds).value
	}
	return String(thresholdSeconds)
}

/** API threshold → form unit (duration only; default min when empty). */
export function thresholdFormUnit(
	triggerType: TriggerType,
	thresholdSeconds: number | null | undefined
): ThresholdUnit {
	if (thresholdSeconds == null || !isDurationThresholdTrigger(triggerType)) {
		return DEFAULT_THRESHOLD_UNIT
	}
	return splitThresholdSeconds(thresholdSeconds).unit
}

/** List/summary display for a rule threshold. */
export function formatThresholdLabel(
	triggerType: TriggerType,
	threshold: number
): string {
	if (isDurationThresholdTrigger(triggerType)) {
		const { value, unit } = splitThresholdSeconds(threshold)
		const suffix = unit === 'hr' ? 'h' : unit === 'min' ? 'm' : 's'
		return `threshold: ${value}${suffix}`
	}
	return `threshold: ${threshold}`
}

function firstError(checks: Array<string | false>): string | undefined {
	return checks.find((check): check is string => typeof check === 'string')
}

/** Returns the first validation error, or parsed fields ready for create/update. */
export function parseRuleForm(
	input: RuleFormInput
): { error: string } | { fields: RuleFormFields } {
	const config = TRIGGER_FIELD_CONFIG[input.triggerType]
	const name = input.name.trim()
	const ownerId = input.ownerId.trim()
	const agentId = input.agentId.trim()
	const thresholdText = input.thresholdText.trim()
	const parsedThreshold = config.showThreshold ? Number(thresholdText) : null

	const error = firstError([
		!name && 'Name is required.',
		!ownerId && 'Login with a username before creating rules.',
		config.agentIdRequired &&
			!agentId &&
			'Agent ID is required for this trigger.',
		config.queueIdsRequired &&
			input.queueIds.length === 0 &&
			'At least one queue ID is required for this trigger.',
		config.requireAgentOrQueues &&
			!agentId &&
			input.queueIds.length === 0 &&
			'Provide an agent ID and/or queue IDs for this trigger.',
		config.showThreshold &&
			!thresholdText &&
			'Threshold is required for this trigger.',
		config.showThreshold &&
			(parsedThreshold == null || Number.isNaN(parsedThreshold)) &&
			'Threshold must be a valid number.',
		config.showThreshold &&
			parsedThreshold != null &&
			!Number.isNaN(parsedThreshold) &&
			parsedThreshold <= 0 &&
			'Threshold must be greater than 0.',
	])

	if (error) {
		return { error }
	}

	return {
		fields: {
			name,
			ownerId,
			scope: {
				agent_id: config.showAgentId && agentId ? agentId : null,
				queue_ids:
					config.showQueueIds && input.queueIds.length > 0
						? input.queueIds
						: null,
			},
			threshold:
				config.showThreshold && parsedThreshold != null
					? thresholdForApi(
							input.triggerType,
							parsedThreshold,
							input.thresholdUnit
						)
					: null,
			targetState: config.showTargetState ? input.targetState : null,
		},
	}
}
