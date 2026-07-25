import { UsernameBar } from './UsernameBar'

export function AppHeader() {
	return (
		<header className="app-header">
			<h1 className="app-header__brand">Assembled Intraday</h1>
			<UsernameBar />
		</header>
	)
}
