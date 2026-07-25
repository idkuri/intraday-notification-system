import Tab from '@mui/material/Tab'
import Tabs from '@mui/material/Tabs'
import { Link, useLocation } from 'react-router-dom'

export function AppNav() {
	const location = useLocation()
	const value = location.pathname.startsWith('/rules') ? '/rules' : '/'

	return (
		<Tabs
			value={value}
			sx={{
				px: { xs: 1, sm: 1.5 },
				bgcolor: '#fff',
				borderBottom: '1px solid #d8dee8',
				minHeight: 44,
				'& .MuiTabs-indicator': { height: 3 },
			}}
		>
			<Tab
				label="Notifications"
				value="/"
				component={Link}
				to="/"
				sx={{ textTransform: 'none', minHeight: 44 }}
			/>
			<Tab
				label="Rules"
				value="/rules"
				component={Link}
				to="/rules"
				sx={{ textTransform: 'none', minHeight: 44 }}
			/>
		</Tabs>
	)
}
