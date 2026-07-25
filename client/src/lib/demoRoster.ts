import {
	DEMO_AGENTS,
	DEMO_QUEUES,
	type DemoAgent,
} from '@/lib/generated/demo-roster'

export { DEMO_AGENTS, DEMO_QUEUES, type DemoAgent }

export function formatAgentOption(agent: DemoAgent): string {
	return `${agent.agent_id} — ${agent.agent_name} (${agent.queue_ids.join(', ')})`
}
