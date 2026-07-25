import { useState, type FormEvent } from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useUsernameStore } from '@/stores/usernameStore'

const darkFieldSx = {
	minWidth: 180,
	'& .MuiOutlinedInput-root': {
		color: '#f8fafc',
		bgcolor: '#0f172a',
		'& fieldset': { borderColor: '#475569' },
		'&:hover fieldset': { borderColor: '#94a3b8' },
		'&.Mui-focused fieldset': { borderColor: '#93c5fd' },
	},
	'& .MuiInputLabel-root': { color: '#cbd5e1' },
	'& .MuiInputLabel-root.Mui-focused': { color: '#93c5fd' },
	'& .MuiOutlinedInput-input::placeholder': {
		color: '#94a3b8',
		opacity: 1,
	},
} as const

export function UsernameBar() {
	const username = useUsernameStore(state => state.username)
	const login = useUsernameStore(state => state.login)
	const [draft, setDraft] = useState('')

	function onSubmit(event: FormEvent) {
		event.preventDefault()
		login(draft)
	}

	function onSwitchUser() {
		setDraft(username)
		login('')
	}

	if (username) {
		return (
			<Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
				<Typography variant="body2" sx={{ color: '#e2e8f0' }}>
					Logged in as{' '}
					<Box component="strong" sx={{ color: '#f8fafc', fontWeight: 600 }}>
						{username}
					</Box>
				</Typography>
				<Button
					type="button"
					size="small"
					variant="outlined"
					onClick={onSwitchUser}
					sx={{
						color: '#f8fafc',
						borderColor: '#64748b',
						'&:hover': {
							borderColor: '#94a3b8',
							bgcolor: 'rgba(248, 250, 252, 0.08)',
						},
					}}
				>
					Switch user
				</Button>
			</Stack>
		)
	}

	return (
		<Box
			component="form"
			onSubmit={onSubmit}
			sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
		>
			<TextField
				id="username-input"
				label="Username"
				size="small"
				value={draft}
				slotProps={{ htmlInput: { maxLength: 64 } }}
				placeholder="your.name"
				autoComplete="username"
				onChange={event => setDraft(event.target.value)}
				sx={darkFieldSx}
			/>
			<Button type="submit" size="small" variant="contained">
				Login
			</Button>
		</Box>
	)
}
