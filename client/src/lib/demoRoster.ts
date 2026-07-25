import type { DemoAgentRead } from '@/api-client'

export function formatAgentOption(agent: DemoAgentRead): string {
	return `${agent.agent_id} — ${agent.agent_name} (${agent.queue_ids.join(', ')})`
}
