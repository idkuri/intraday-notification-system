import type { components } from '@/lib/api-client/schema'

export type TriggerType = components['schemas']['TriggerType']
export type Audience = components['schemas']['Audience']
export type AgentState = components['schemas']['AgentState']
export type Severity = components['schemas']['Severity']
export type ChannelType = components['schemas']['ChannelType']

export const TRIGGER_TYPES: TriggerType[] = [
	'queue_sla_breached',
	'queue_tickets_waiting',
	'adherence_violation_duration',
	'agent_state_duration',
]

export const TRIGGER_LABELS: Record<TriggerType, string> = {
	queue_sla_breached: 'Queue SLA breached',
	queue_tickets_waiting: 'Queue tickets waiting',
	adherence_violation_duration: 'Adherence violation duration',
	agent_state_duration: 'Agent state duration',
}

export const AGENT_STATES: AgentState[] = [
	'available',
	'on_call',
	'on_break',
	'in_meeting',
	'offline',
]

export const SEVERITIES: Severity[] = ['info', 'warning', 'critical']

export const CHANNELS: ChannelType[] = ['console', 'inbox']

export interface TriggerFieldConfig {
	showAgentId: boolean
	showQueueIds: boolean
	showThreshold: boolean
	showTargetState: boolean
	agentIdRequired: boolean
	queueIdsRequired: boolean
	defaultAudience: Audience
}

export const TRIGGER_FIELD_CONFIG: Record<TriggerType, TriggerFieldConfig> = {
	queue_sla_breached: {
		showAgentId: false,
		showQueueIds: true,
		showThreshold: false,
		showTargetState: false,
		agentIdRequired: false,
		queueIdsRequired: true,
		defaultAudience: 'team_lead',
	},
	queue_tickets_waiting: {
		showAgentId: false,
		showQueueIds: true,
		showThreshold: true,
		showTargetState: false,
		agentIdRequired: false,
		queueIdsRequired: true,
		defaultAudience: 'team_lead',
	},
	adherence_violation_duration: {
		showAgentId: true,
		showQueueIds: false,
		showThreshold: true,
		showTargetState: false,
		agentIdRequired: true,
		queueIdsRequired: false,
		defaultAudience: 'agent',
	},
	agent_state_duration: {
		showAgentId: true,
		showQueueIds: true,
		showThreshold: true,
		showTargetState: true,
		agentIdRequired: false,
		queueIdsRequired: false,
		defaultAudience: 'agent',
	},
}

export const DEFAULT_SEVERITY: Severity = 'warning'
export const DEFAULT_CHANNELS: ChannelType[] = ['console', 'inbox']

export function defaultAudienceForTrigger(triggerType: TriggerType): Audience {
	return TRIGGER_FIELD_CONFIG[triggerType].defaultAudience
}

export function parseCommaSeparatedIds(value: string): string[] {
	return value
		.split(',')
		.map(item => item.trim())
		.filter(Boolean)
}
