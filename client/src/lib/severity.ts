import type { ChipProps } from '@mui/material/Chip'
import type { Severity } from '@/api-client'

/** MUI Chip color for each API severity. */
export const SEVERITY_CHIP_COLOR: Record<
	Severity,
	NonNullable<ChipProps['color']>
> = {
	info: 'info',
	warning: 'warning',
	critical: 'error',
}
