import { useCallback } from 'react'
import type { RuleCreate } from '@/lib/api'

interface UseCreateRuleOptions {
	onSubmit: (body: RuleCreate) => Promise<boolean>
}

export function useCreateRule({ onSubmit }: UseCreateRuleOptions) {
	const submit = useCallback(
		async (body: RuleCreate) => onSubmit(body),
		[onSubmit]
	)

	return { submit }
}
