/* generated using export_trigger_field_config.py — do not edit */
import type { TriggerType } from '@/api-client'

/** Which create/edit fields a trigger type shows or requires. */
export interface TriggerFieldConfig {
	showAgentId: boolean
	showQueueIds: boolean
	showThreshold: boolean
	showTargetState: boolean
	agentIdRequired: boolean
	queueIdsRequired: boolean
	requireAgentOrQueues: boolean
}

export const TRIGGER_FIELD_CONFIG: Record<TriggerType, TriggerFieldConfig> = {
	queue_sla_breached: {
		showAgentId: false,
		showQueueIds: true,
		showThreshold: false,
		showTargetState: false,
		agentIdRequired: false,
		queueIdsRequired: true,
		requireAgentOrQueues: false,
	},
	queue_tickets_waiting: {
		showAgentId: false,
		showQueueIds: true,
		showThreshold: true,
		showTargetState: false,
		agentIdRequired: false,
		queueIdsRequired: true,
		requireAgentOrQueues: false,
	},
	queue_forecast_over_volume: {
		showAgentId: false,
		showQueueIds: true,
		showThreshold: true,
		showTargetState: false,
		agentIdRequired: false,
		queueIdsRequired: true,
		requireAgentOrQueues: false,
	},
	adherence_violation_duration: {
		showAgentId: true,
		showQueueIds: true,
		showThreshold: true,
		showTargetState: false,
		agentIdRequired: false,
		queueIdsRequired: false,
		requireAgentOrQueues: true,
	},
	agent_state_duration: {
		showAgentId: true,
		showQueueIds: true,
		showThreshold: true,
		showTargetState: true,
		agentIdRequired: false,
		queueIdsRequired: false,
		requireAgentOrQueues: true,
	},
}
