import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import { UsernameBar } from './UsernameBar'

export function AppHeader() {
	return (
		<AppBar
			position="static"
			elevation={0}
			sx={{
				bgcolor: '#1a2332',
				color: '#f8fafc',
				borderBottom: '1px solid #2d3a4f',
			}}
		>
			<Toolbar
				sx={{
					gap: 2,
					justifyContent: 'space-between',
					minHeight: 56,
					px: { xs: 2, sm: 2.5 },
				}}
			>
				<Typography
					variant="h6"
					component="h1"
					sx={{
						fontSize: '1.125rem',
						fontWeight: 600,
						letterSpacing: '0.01em',
					}}
				>
					Assembled Intraday Notification
				</Typography>
				<UsernameBar />
			</Toolbar>
		</AppBar>
	)
}
