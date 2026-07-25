import { NavLink } from 'react-router-dom'

export function AppNav() {
	return (
		<nav className="app-nav">
			<NavLink
				to="/"
				end
				className={({ isActive }) =>
					`app-nav__link${isActive ? ' app-nav__link--active' : ''}`
				}
			>
				Notifications
			</NavLink>
			<NavLink
				to="/rules"
				className={({ isActive }) =>
					`app-nav__link${isActive ? ' app-nav__link--active' : ''}`
				}
			>
				Rules
			</NavLink>
		</nav>
	)
}
