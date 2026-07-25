import Box from '@mui/material/Box'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppHeader } from '@/components/Layout/AppHeader'
import { AppNav } from '@/components/Layout/AppNav'
import { NotificationsPage } from '@/routes/notifications'
import { RulesPage } from '@/routes/rules'

export function App() {
	return (
		<Box
			sx={{
				minHeight: '100vh',
				display: 'flex',
				flexDirection: 'column',
			}}
		>
			<AppHeader />
			<AppNav />
			<Box
				component="main"
				sx={{
					flex: 1,
					width: '100%',
					maxWidth: 1100,
					mx: 'auto',
					px: 2.5,
					py: 2.5,
				}}
			>
				<Routes>
					<Route path="/" element={<NotificationsPage />} />
					<Route path="/rules" element={<RulesPage />} />
					<Route path="*" element={<Navigate to="/" replace />} />
				</Routes>
			</Box>
		</Box>
	)
}
