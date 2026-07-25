import { create } from 'zustand'

const STORAGE_KEY = 'assembled.username'
const MAX_LENGTH = 64

function readStoredUsername(): string {
	try {
		return localStorage.getItem(STORAGE_KEY) ?? ''
	} catch {
		return ''
	}
}

function normalizeUsername(value: string): string {
	return value.trim().slice(0, MAX_LENGTH)
}

interface UsernameState {
	username: string
	/** Bumps on each Login so hooks refetch even if the name is unchanged. */
	authEpoch: number
	login: (value: string) => void
}

export const useUsernameStore = create<UsernameState>(set => ({
	username: readStoredUsername(),
	authEpoch: 0,
	login: (value: string) => {
		const username = normalizeUsername(value)
		try {
			if (username) {
				localStorage.setItem(STORAGE_KEY, username)
			} else {
				localStorage.removeItem(STORAGE_KEY)
			}
		} catch {
			// Ignore storage failures; in-memory state still updates.
		}
		set(state => ({ username, authEpoch: state.authEpoch + 1 }))
	},
}))

export function getUsername(): string {
	return useUsernameStore.getState().username
}
