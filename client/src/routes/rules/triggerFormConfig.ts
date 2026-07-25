import { ChannelType, Severity, type TriggerType } from '@/api-client'

export type { TriggerFieldConfig } from './triggerFormConfig.generated'
export { TRIGGER_FIELD_CONFIG } from './triggerFormConfig.generated'

export const TRIGGER_LABELS: Record<TriggerType, string> = {
	queue_sla_breached: 'Queue SLA breached',
	queue_tickets_waiting: 'Queue tickets waiting',
	queue_forecast_over_volume: 'Queue forecast over recent volume',
	adherence_violation_duration: 'Adherence violation duration',
	agent_state_duration: 'Agent state duration',
}

export const DEFAULT_SEVERITY = Severity.WARNING
export const DEFAULT_CHANNELS = Object.values(ChannelType)

export function parseCommaSeparatedIds(value: string): string[] {
	return value
		.split(',')
		.map(item => item.trim())
		.filter(Boolean)
}
