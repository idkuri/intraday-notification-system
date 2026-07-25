import type { AgentState, TriggerType } from '@/api-client'
import { TRIGGER_FIELD_CONFIG } from '../triggerFormConfig'

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
	targetState: AgentState
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
			threshold: config.showThreshold ? parsedThreshold : null,
			targetState: config.showTargetState ? input.targetState : null,
		},
	}
}
