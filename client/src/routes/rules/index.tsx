import { useState } from 'react'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import IconButton from '@mui/material/IconButton'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Tooltip from '@mui/material/Tooltip'
import Typography from '@mui/material/Typography'
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import PauseCircleOutlinedIcon from '@mui/icons-material/PauseCircleOutlined'
import PlayCircleOutlinedIcon from '@mui/icons-material/PlayCircleOutlined'
import type { RuleRead } from '@/api-client'
import { useRules } from '@/hooks/useRules'
import { useRuleActions } from '@/hooks/useRuleActions'
import { SEVERITY_CHIP_COLOR } from '@/lib/severity'
import {
	RuleCreateForm,
	ruleFormSubmitLabel,
} from './components/RuleCreateForm'
import { formatThresholdLabel } from './components/parseRuleForm'

function scopeLabel(rule: RuleRead): string {
	const parts: string[] = []
	if (rule.scope.agent_id) {
		parts.push(`agent: ${rule.scope.agent_id}`)
	}
	if (rule.scope.queue_ids?.length) {
		parts.push(`queues: ${rule.scope.queue_ids.join(', ')}`)
	}
	if (rule.threshold != null) {
		parts.push(formatThresholdLabel(rule.trigger_type, rule.threshold))
	}
	if (rule.target_state) {
		parts.push(`state: ${rule.target_state}`)
	}
	return parts.join(' · ') || '—'
}

export function RulesPage() {
	const { rules, loading, error, refetch } = useRules()
	const {
		actionError,
		busyRuleId,
		creating,
		create,
		toggleEnabled,
		remove,
		patch,
		canMutate,
	} = useRuleActions({ refetch })
	const [formOpen, setFormOpen] = useState(false)
	const [editingRule, setEditingRule] = useState<RuleRead | null>(null)
	const isEditing = editingRule != null
	const formSubmitting =
		creating || (isEditing && busyRuleId === editingRule.id)

	const closeForm = () => {
		if (formSubmitting) {
			return
		}
		setFormOpen(false)
		setEditingRule(null)
	}

	const openCreate = () => {
		setEditingRule(null)
		setFormOpen(true)
	}

	const openEdit = (rule: RuleRead) => {
		setEditingRule(rule)
		setFormOpen(true)
	}

	return (
		<Box component="section">
			<Stack
				direction="row"
				spacing={2}
				sx={{
					mb: 2,
					alignItems: 'center',
					justifyContent: 'space-between',
				}}
			>
				<Typography variant="h5" component="h2">
					Rules
				</Typography>
				<Button variant="contained" disabled={!canMutate} onClick={openCreate}>
					Create rule
				</Button>
			</Stack>

			{!canMutate && (
				<Alert severity="info" sx={{ mb: 2 }}>
					Set a username in the header to view and manage your rules. Demo
					personas: a_19, a_42, lead_billing.
				</Alert>
			)}

			{(error || actionError) && (
				<Alert severity="error" sx={{ mb: 2 }}>
					{error ?? actionError}
				</Alert>
			)}

			<Dialog
				open={formOpen}
				onClose={closeForm}
				fullWidth
				maxWidth="md"
				aria-labelledby="rule-form-title"
			>
				<DialogTitle id="rule-form-title">
					{isEditing ? 'Edit rule' : 'Create rule'}
				</DialogTitle>
				<DialogContent dividers>
					{formOpen && (
						<RuleCreateForm
							key={editingRule?.id ?? 'create'}
							disabled={!canMutate}
							submitting={formSubmitting}
							editingRule={editingRule}
							onCreate={create}
							onUpdate={patch}
							onClose={closeForm}
						/>
					)}
				</DialogContent>
				<DialogActions>
					<Button onClick={closeForm} disabled={formSubmitting}>
						Cancel
					</Button>
					<Button
						type="submit"
						form="rule-form"
						variant="contained"
						disabled={!canMutate || formSubmitting}
					>
						{ruleFormSubmitLabel(isEditing, formSubmitting)}
					</Button>
				</DialogActions>
			</Dialog>

			{loading && rules.length === 0 ? (
				<Typography color="text.secondary">Loading rules…</Typography>
			) : rules.length === 0 ? (
				<Typography color="text.secondary">No rules configured yet.</Typography>
			) : (
				<TableContainer component={Paper} variant="outlined">
					<Table size="small">
						<TableHead>
							<TableRow>
								<TableCell>Name</TableCell>
								<TableCell>Trigger</TableCell>
								<TableCell>Severity</TableCell>
								<TableCell>Status</TableCell>
								<TableCell>Scope</TableCell>
								<TableCell align="right">Actions</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{rules.map(rule => {
								const rowBusy = !canMutate || busyRuleId === rule.id

								return (
									<TableRow key={rule.id} hover>
										<TableCell>{rule.name}</TableCell>
										<TableCell>
											<Typography
												component="span"
												variant="body2"
												sx={{
													fontFamily:
														'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
												}}
											>
												{rule.trigger_type}
											</Typography>
										</TableCell>
										<TableCell>
											<Chip
												size="small"
												label={rule.severity ?? 'warning'}
												color={SEVERITY_CHIP_COLOR[rule.severity ?? 'warning']}
											/>
										</TableCell>
										<TableCell>
											<Chip
												size="small"
												label={rule.enabled !== false ? 'enabled' : 'disabled'}
												color={rule.enabled !== false ? 'success' : 'error'}
											/>
										</TableCell>
										<TableCell>{scopeLabel(rule)}</TableCell>
										<TableCell align="right">
											<Tooltip title="Edit">
												<span>
													<IconButton
														aria-label="Edit rule"
														size="small"
														disabled={rowBusy}
														onClick={() => openEdit(rule)}
													>
														<EditOutlinedIcon fontSize="small" />
													</IconButton>
												</span>
											</Tooltip>
											<Tooltip
												title={rule.enabled !== false ? 'Disable' : 'Enable'}
											>
												<span>
													<IconButton
														aria-label={
															rule.enabled !== false
																? 'Disable rule'
																: 'Enable rule'
														}
														size="small"
														color={rule.enabled !== false ? 'success' : 'error'}
														disabled={rowBusy}
														onClick={() =>
															void toggleEnabled(
																rule.id,
																rule.enabled !== false
															)
														}
													>
														{rule.enabled !== false ? (
															<PauseCircleOutlinedIcon fontSize="small" />
														) : (
															<PlayCircleOutlinedIcon fontSize="small" />
														)}
													</IconButton>
												</span>
											</Tooltip>
											<Tooltip title="Delete">
												<span>
													<IconButton
														aria-label="Delete rule"
														size="small"
														color="error"
														disabled={rowBusy}
														onClick={() => {
															if (editingRule?.id === rule.id) {
																setFormOpen(false)
																setEditingRule(null)
															}
															void remove(rule.id)
														}}
													>
														<DeleteOutlinedIcon fontSize="small" />
													</IconButton>
												</span>
											</Tooltip>
										</TableCell>
									</TableRow>
								)
							})}
						</TableBody>
					</Table>
				</TableContainer>
			)}
		</Box>
	)
}
