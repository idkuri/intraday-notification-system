import { useState } from 'react'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Typography from '@mui/material/Typography'
import { useNotifications } from '@/hooks/useNotifications'
import { SEVERITY_CHIP_COLOR } from '@/lib/severity'
import { getErrorMessage } from '@/lib/utils/errors'

const monoSx = {
	fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
} as const

export function NotificationsPage() {
	const { notifications, loading, error, clearInbox, canView } =
		useNotifications()
	const [clearing, setClearing] = useState(false)
	const [clearError, setClearError] = useState<string | null>(null)

	const handleClearInbox = async () => {
		setClearing(true)
		setClearError(null)
		try {
			await clearInbox()
		} catch (err) {
			setClearError(getErrorMessage(err))
		} finally {
			setClearing(false)
		}
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
					Notifications
				</Typography>
				<Button
					variant="outlined"
					color="error"
					disabled={
						!canView || loading || clearing || notifications.length === 0
					}
					onClick={() => void handleClearInbox()}
				>
					{clearing ? 'Clearing…' : 'Clear inbox'}
				</Button>
			</Stack>

			{!canView && (
				<Alert severity="info" sx={{ mb: 2 }}>
					Login with a username to view your inbox. Seed recipients: a_19, a_42,
					lead_billing.
				</Alert>
			)}

			{(error || clearError) && (
				<Alert severity="error" sx={{ mb: 2 }}>
					{error ?? clearError}
				</Alert>
			)}

			{!canView ? (
				<Typography color="text.secondary">No username set.</Typography>
			) : loading && notifications.length === 0 ? (
				<Typography color="text.secondary">Loading notifications…</Typography>
			) : notifications.length === 0 ? (
				<Typography color="text.secondary">
					No notifications for this recipient yet.
				</Typography>
			) : (
				<TableContainer component={Paper} variant="outlined">
					<Table size="small">
						<TableHead>
							<TableRow>
								<TableCell>ID</TableCell>
								<TableCell>Severity</TableCell>
								<TableCell>Title</TableCell>
								<TableCell>Body</TableCell>
								<TableCell>Recipient</TableCell>
								<TableCell>Rule ID</TableCell>
								<TableCell>Timestamp</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{notifications.map(notification => (
								<TableRow key={notification.id} hover>
									<TableCell>
										<Typography component="span" variant="body2" sx={monoSx}>
											{notification.id}
										</Typography>
									</TableCell>
									<TableCell>
										<Chip
											size="small"
											label={notification.severity}
											color={SEVERITY_CHIP_COLOR[notification.severity]}
										/>
									</TableCell>
									<TableCell>{notification.title}</TableCell>
									<TableCell>{notification.body}</TableCell>
									<TableCell>
										<Typography component="span" variant="body2" sx={monoSx}>
											{notification.recipient_id}
										</Typography>
									</TableCell>
									<TableCell>
										<Typography component="span" variant="body2" sx={monoSx}>
											{notification.rule_id}
										</Typography>
									</TableCell>
									<TableCell>
										{new Date(notification.ts).toLocaleString()}
									</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>
			)}
		</Box>
	)
}
