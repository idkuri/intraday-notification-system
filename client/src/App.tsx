import { Navigate, Route, Routes } from 'react-router-dom'
import { AppHeader } from '@/components/Layout/AppHeader'
import { AppNav } from '@/components/Layout/AppNav'
import { NotificationsPage } from '@/routes/notifications'
import { RulesPage } from '@/routes/rules'

export function App() {
	return (
		<div className="app-shell">
			<AppHeader />
			<AppNav />
			<main className="app-main">
				<Routes>
					<Route path="/" element={<NotificationsPage />} />
					<Route path="/rules" element={<RulesPage />} />
					<Route path="*" element={<Navigate to="/" replace />} />
				</Routes>
			</main>
		</div>
	)
}
