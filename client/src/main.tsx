import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { configureApiClient } from '@/lib/configureApiClient'
import { AppProviders } from '@/providers/AppProviders'
import { App } from '@/App'
import '@/styles/global.css'

configureApiClient()

createRoot(document.getElementById('root')!).render(
	<StrictMode>
		<BrowserRouter>
			<AppProviders>
				<App />
			</AppProviders>
		</BrowserRouter>
	</StrictMode>
)
