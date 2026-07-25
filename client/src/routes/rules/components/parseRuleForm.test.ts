import { describe, expect, it } from 'vitest'
import { AgentState, TriggerType } from '@/api-client'
import { parseRuleForm } from './parseRuleForm'

const base = {
	name: 'Test rule',
	ownerId: 'lead_billing',
	agentId: '',
	queueIds: [] as string[],
	thresholdText: '',
	targetState: AgentState.ON_CALL,
}

describe('parseRuleForm', () => {
	it('parses a queue SLA rule', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.QUEUE_SLA_BREACHED,
			queueIds: ['billing'],
		})
		expect(result).toEqual({
			fields: {
				name: 'Test rule',
				ownerId: 'lead_billing',
				scope: { agent_id: null, queue_ids: ['billing'] },
				threshold: null,
				targetState: null,
			},
		})
	})

	it('parses a tickets-waiting rule with threshold', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.QUEUE_TICKETS_WAITING,
			queueIds: ['billing'],
			thresholdText: '20',
		})
		expect(result).toEqual({
			fields: {
				name: 'Test rule',
				ownerId: 'lead_billing',
				scope: { agent_id: null, queue_ids: ['billing'] },
				threshold: 20,
				targetState: null,
			},
		})
	})

	it('parses an adherence rule', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.ADHERENCE_VIOLATION_DURATION,
			agentId: 'a_19',
			thresholdText: '600',
		})
		expect(result).toEqual({
			fields: {
				name: 'Test rule',
				ownerId: 'lead_billing',
				scope: { agent_id: 'a_19', queue_ids: null },
				threshold: 600,
				targetState: null,
			},
		})
	})

	it('parses agent_state_duration with agent only', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.AGENT_STATE_DURATION,
			agentId: 'a_42',
			thresholdText: '2700',
		})
		expect(result).toEqual({
			fields: {
				name: 'Test rule',
				ownerId: 'lead_billing',
				scope: { agent_id: 'a_42', queue_ids: null },
				threshold: 2700,
				targetState: AgentState.ON_CALL,
			},
		})
	})

	it('parses agent_state_duration with queues only', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.AGENT_STATE_DURATION,
			queueIds: ['billing', 'vip'],
			thresholdText: '2700',
		})
		expect(result).toEqual({
			fields: {
				name: 'Test rule',
				ownerId: 'lead_billing',
				scope: { agent_id: null, queue_ids: ['billing', 'vip'] },
				threshold: 2700,
				targetState: AgentState.ON_CALL,
			},
		})
	})

	it('requires a name', () => {
		const result = parseRuleForm({
			...base,
			name: '   ',
			triggerType: TriggerType.QUEUE_SLA_BREACHED,
			queueIds: ['billing'],
		})
		expect(result).toEqual({ error: 'Name is required.' })
	})

	it('requires a username', () => {
		const result = parseRuleForm({
			...base,
			ownerId: '',
			triggerType: TriggerType.QUEUE_SLA_BREACHED,
			queueIds: ['billing'],
		})
		expect(result).toEqual({
			error: 'Login with a username before creating rules.',
		})
	})

	it('requires agent id for adherence', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.ADHERENCE_VIOLATION_DURATION,
			thresholdText: '600',
		})
		expect(result).toEqual({
			error: 'Agent ID is required for this trigger.',
		})
	})

	it('requires queue ids for queue SLA', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.QUEUE_SLA_BREACHED,
		})
		expect(result).toEqual({
			error: 'At least one queue ID is required for this trigger.',
		})
	})

	it('requires agent or queues for agent_state_duration', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.AGENT_STATE_DURATION,
			thresholdText: '2700',
		})
		expect(result).toEqual({
			error: 'Provide an agent ID and/or queue IDs for this trigger.',
		})
	})

	it('rejects a non-numeric threshold', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.QUEUE_TICKETS_WAITING,
			queueIds: ['billing'],
			thresholdText: 'abc',
		})
		expect(result).toEqual({ error: 'Threshold must be a valid number.' })
	})

	it('rejects a non-positive threshold', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.QUEUE_TICKETS_WAITING,
			queueIds: ['billing'],
			thresholdText: '0',
		})
		expect(result).toEqual({ error: 'Threshold must be greater than 0.' })
	})
})
