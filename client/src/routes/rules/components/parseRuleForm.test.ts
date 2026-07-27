import { describe, expect, it } from 'vitest'
import { AgentState, TriggerType } from '@/api-client'
import {
	formatThresholdLabel,
	parseRuleForm,
	splitThresholdSeconds,
	type ThresholdUnit,
} from './parseRuleForm'

const base = {
	name: 'Test rule',
	ownerId: 'lead_billing',
	agentId: '',
	queueIds: [] as string[],
	thresholdText: '',
	thresholdUnit: 'min' as ThresholdUnit,
	targetState: AgentState.ON_CALL,
}

describe('splitThresholdSeconds', () => {
	it('picks hours when evenly divisible', () => {
		expect(splitThresholdSeconds(7200)).toEqual({ value: '2', unit: 'hr' })
	})

	it('picks minutes when evenly divisible by 60 but not 3600', () => {
		expect(splitThresholdSeconds(2700)).toEqual({ value: '45', unit: 'min' })
	})

	it('picks seconds otherwise', () => {
		expect(splitThresholdSeconds(30)).toEqual({ value: '30', unit: 'sec' })
	})
})

describe('formatThresholdLabel', () => {
	it('formats duration thresholds with unit suffix', () => {
		expect(formatThresholdLabel(TriggerType.AGENT_STATE_DURATION, 2700)).toBe(
			'threshold: 45m'
		)
		expect(
			formatThresholdLabel(TriggerType.ADHERENCE_VIOLATION_DURATION, 7200)
		).toBe('threshold: 2h')
		expect(formatThresholdLabel(TriggerType.AGENT_STATE_DURATION, 30)).toBe(
			'threshold: 30s'
		)
	})

	it('formats non-duration thresholds as raw numbers', () => {
		expect(formatThresholdLabel(TriggerType.QUEUE_TICKETS_WAITING, 20)).toBe(
			'threshold: 20'
		)
	})
})

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

	it('parses an adherence rule in minutes', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.ADHERENCE_VIOLATION_DURATION,
			agentId: 'a_19',
			thresholdText: '10',
			thresholdUnit: 'min',
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

	it('parses adherence with queues only', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.ADHERENCE_VIOLATION_DURATION,
			queueIds: ['billing', 'tier_2'],
			thresholdText: '10',
			thresholdUnit: 'min',
		})
		expect(result).toEqual({
			fields: {
				name: 'Test rule',
				ownerId: 'lead_billing',
				scope: { agent_id: null, queue_ids: ['billing', 'tier_2'] },
				threshold: 600,
				targetState: null,
			},
		})
	})

	it('parses agent_state_duration with minutes', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.AGENT_STATE_DURATION,
			agentId: 'a_42',
			thresholdText: '45',
			thresholdUnit: 'min',
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

	it('parses agent_state_duration with seconds', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.AGENT_STATE_DURATION,
			queueIds: ['billing'],
			thresholdText: '30',
			thresholdUnit: 'sec',
		})
		expect(result).toEqual({
			fields: {
				name: 'Test rule',
				ownerId: 'lead_billing',
				scope: { agent_id: null, queue_ids: ['billing'] },
				threshold: 30,
				targetState: AgentState.ON_CALL,
			},
		})
	})

	it('parses agent_state_duration with hours', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.AGENT_STATE_DURATION,
			queueIds: ['billing', 'vip'],
			thresholdText: '2',
			thresholdUnit: 'hr',
		})
		expect(result).toEqual({
			fields: {
				name: 'Test rule',
				ownerId: 'lead_billing',
				scope: { agent_id: null, queue_ids: ['billing', 'vip'] },
				threshold: 7200,
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

	it('requires agent or queues for adherence', () => {
		const result = parseRuleForm({
			...base,
			triggerType: TriggerType.ADHERENCE_VIOLATION_DURATION,
			thresholdText: '10',
		})
		expect(result).toEqual({
			error: 'Provide an agent ID and/or queue IDs for this trigger.',
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
			thresholdText: '45',
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
