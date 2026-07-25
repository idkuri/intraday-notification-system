import { useCallback, useState } from 'react'
import { RulesService, type RuleCreate, type RuleUpdate } from '@/api-client'
import { usernameHeader } from '@/lib/configureApiClient'
import { getErrorMessage } from '@/lib/utils/errors'
import { useUsernameStore } from '@/stores/usernameStore'

interface UseRuleActionsOptions {
	refetch: () => Promise<void>
}

export function useRuleActions({ refetch }: UseRuleActionsOptions) {
	const username = useUsernameStore(state => state.username)
	const [actionError, setActionError] = useState<string | null>(null)
	const [busyRuleId, setBusyRuleId] = useState<string | null>(null)
	const [creating, setCreating] = useState(false)

	const requireUsername = useCallback(() => {
		if (!username.trim()) {
			setActionError('Set a username in the header before mutating rules.')
			return false
		}
		return true
	}, [username])

	const create = useCallback(
		async (body: RuleCreate) => {
			if (!requireUsername()) {
				return false
			}

			setCreating(true)
			setActionError(null)
			try {
				await RulesService.createRuleRulesPost({
					requestBody: body,
					...usernameHeader(),
				})
				await refetch()
				return true
			} catch (err) {
				setActionError(getErrorMessage(err))
				return false
			} finally {
				setCreating(false)
			}
		},
		[refetch, requireUsername]
	)

	const toggleEnabled = useCallback(
		async (ruleId: string, enabled: boolean) => {
			if (!requireUsername()) {
				return
			}

			setBusyRuleId(ruleId)
			setActionError(null)
			try {
				await RulesService.updateRuleRulesRuleIdPatch({
					ruleId,
					requestBody: { enabled: !enabled },
					...usernameHeader(),
				})
				await refetch()
			} catch (err) {
				setActionError(getErrorMessage(err))
			} finally {
				setBusyRuleId(null)
			}
		},
		[refetch, requireUsername]
	)

	const remove = useCallback(
		async (ruleId: string) => {
			if (!requireUsername()) {
				return
			}

			setBusyRuleId(ruleId)
			setActionError(null)
			try {
				await RulesService.deleteRuleRulesRuleIdDelete({
					ruleId,
					...usernameHeader(),
				})
				await refetch()
			} catch (err) {
				setActionError(getErrorMessage(err))
			} finally {
				setBusyRuleId(null)
			}
		},
		[refetch, requireUsername]
	)

	const patch = useCallback(
		async (ruleId: string, body: RuleUpdate) => {
			if (!requireUsername()) {
				return false
			}

			setBusyRuleId(ruleId)
			setActionError(null)
			try {
				await RulesService.updateRuleRulesRuleIdPatch({
					ruleId,
					requestBody: body,
					...usernameHeader(),
				})
				await refetch()
				return true
			} catch (err) {
				setActionError(getErrorMessage(err))
				return false
			} finally {
				setBusyRuleId(null)
			}
		},
		[refetch, requireUsername]
	)

	return {
		username,
		actionError,
		busyRuleId,
		creating,
		create,
		toggleEnabled,
		remove,
		patch,
		canMutate: Boolean(username.trim()),
	}
}
