import type { MenuItemConstructorOptions } from 'electron'
import { describe, expect, it } from 'vitest'

import { localizeMenuTemplate } from './native-menu-i18n'

const template: MenuItemConstructorOptions[] = [
  {
    label: 'Hermes',
    submenu: [{ label: 'About Hermes' }, { label: 'Check for Updates…' }, { role: 'hide' }, { role: 'quit' }]
  },
  { label: 'Edit', submenu: [{ role: 'undo' }, { role: 'copy' }, { type: 'separator' }, { role: 'selectAll' }] },
  { label: 'Window', role: 'windowMenu', submenu: [{ role: 'minimize' }, { role: 'zoom' }] },
  { label: 'Help', role: 'help', submenu: [{ label: 'Check for Updates…' }] }
]

const labels = (items: MenuItemConstructorOptions[]): unknown[] =>
  items.map(item => (Array.isArray(item.submenu) ? [item.label, labels(item.submenu)] : (item.label ?? item.type)))

describe('localizeMenuTemplate', () => {
  it('relabels authored labels, app-name labels and role defaults for Vietnamese', () => {
    expect(labels(localizeMenuTemplate(template, 'vi', 'Hermes'))).toEqual([
      ['Hermes', ['Giới thiệu về Hermes', 'Kiểm tra bản cập nhật…', 'Ẩn Hermes', 'Thoát Hermes']],
      ['Sửa', ['Hoàn tác', 'Sao chép', 'separator', 'Chọn tất cả']],
      ['Cửa sổ', ['Thu nhỏ', 'Thu phóng']],
      ['Trợ giúp', ['Kiểm tra bản cập nhật…']]
    ])
  })

  it('keeps roles, accelerators and handlers while relabelling', () => {
    const click = () => {}

    const [item] = localizeMenuTemplate(
      [{ label: 'Zoom In', accelerator: 'CommandOrControl+Plus', click }],
      'vi-VN',
      'X'
    )

    expect(item).toEqual({ label: 'Phóng to', accelerator: 'CommandOrControl+Plus', click })
    expect(localizeMenuTemplate(template, 'vi', 'Hermes')[2].role).toBe('windowMenu')
  })

  it('leaves the English template untouched for languages without native-menu copy', () => {
    expect(localizeMenuTemplate(template, 'en', 'Hermes')).toBe(template)
    expect(localizeMenuTemplate(template, 'ja', 'Hermes')).toBe(template)
  })
})
