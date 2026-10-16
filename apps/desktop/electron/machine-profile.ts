import * as fs from 'node:fs'
import * as os from 'node:os'

import { app, ipcMain } from 'electron'

import { DEFAULT_UI_LOCALE } from './default-ui-locale'

export interface MachineProfile {
  ageDays: number | null
  arch: string
  /** The build's first-run UI language (see default-ui-locale.ts); absent on builds that follow the OS. */
  defaultUiLocale?: string
  locale: string
  platform: NodeJS.Platform
  release: string
  username: string
}

export function registerMachineProfile(): void {
  ipcMain.handle('hermes:machine:profile', readMachineProfile)
}

function readMachineProfile(): MachineProfile {
  let ageDays: number | null = null
  let username = ''

  // Home birthtime approximates account age. Unsupported filesystems leave it unknown.
  try {
    const { birthtimeMs } = fs.statSync(os.homedir())

    if (birthtimeMs > 0) {
      ageDays = Math.max(0, Math.floor((Date.now() - birthtimeMs) / 86_400_000))
    }
  } catch {
    // Unknown age must not make a daily-use machine look newly set up.
  }

  try {
    username = os.userInfo().username
  } catch {
    // The guide can ask for a name without suggesting an OS login.
  }

  return {
    ageDays,
    arch: process.arch,
    defaultUiLocale: DEFAULT_UI_LOCALE,
    locale: app.getLocale() || '',
    platform: process.platform,
    release: os.release(),
    username
  }
}
