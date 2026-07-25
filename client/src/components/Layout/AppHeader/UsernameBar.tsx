import { useUsernameStore } from '@/stores/usernameStore'

export function UsernameBar() {
	const username = useUsernameStore(state => state.username)
	const setUsername = useUsernameStore(state => state.setUsername)

	return (
		<div className="username-bar">
			<label htmlFor="username-input">Username</label>
			<input
				id="username-input"
				type="text"
				value={username}
				maxLength={64}
				placeholder="your.name"
				onChange={event => setUsername(event.target.value)}
			/>
		</div>
	)
}
