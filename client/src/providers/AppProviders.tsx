import CssBaseline from '@mui/material/CssBaseline'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import type { ReactNode } from 'react'

const theme = createTheme({
	palette: {
		background: {
			default: '#f4f6f9',
		},
		text: {
			primary: '#1a1f2e',
		},
	},
	typography: {
		fontFamily: ['Segoe UI', 'system-ui', '-apple-system', 'sans-serif'].join(
			','
		),
	},
	components: {
		MuiButton: {
			styleOverrides: {
				root: {
					textTransform: 'none',
				},
			},
		},
		MuiCssBaseline: {
			styleOverrides: {
				body: {
					minHeight: '100vh',
				},
				'#root': {
					minHeight: '100vh',
				},
			},
		},
	},
})

interface AppProvidersProps {
	children: ReactNode
}

export function AppProviders({ children }: AppProvidersProps) {
	return (
		<ThemeProvider theme={theme}>
			<CssBaseline />
			{children}
		</ThemeProvider>
	)
}
