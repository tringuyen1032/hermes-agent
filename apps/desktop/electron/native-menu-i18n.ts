import type { MenuItemConstructorOptions } from 'electron'

// The native menus (macOS menu bar, tray) are the only UI main draws itself, so they follow the
// renderer's language — reported over `hermes:menu-locale` — rather than the renderer catalog.
// Templates stay authored in English; a language listed here relabels them as a last step, and any
// other language keeps the English labels and Electron's role defaults untouched.

type Role = NonNullable<MenuItemConstructorOptions['role']>

interface NativeMenuCopy {
  /** Labels for role items that carry no label of their own (Electron's defaults are English). */
  roles: Partial<Record<Role, (appName: string) => string>>
  /** Authored English label → translation. */
  labels: Record<string, string>
  /** Authored labels that embed the app name (`About Hermes`). */
  patterns: ReadonlyArray<readonly [RegExp, (name: string) => string]>
}

const VI: NativeMenuCopy = {
  roles: {
    services: () => 'Dịch vụ',
    hide: appName => `Ẩn ${appName}`,
    hideOthers: () => 'Ẩn các ứng dụng khác',
    unhide: () => 'Hiện tất cả',
    quit: appName => `Thoát ${appName}`,
    undo: () => 'Hoàn tác',
    redo: () => 'Làm lại',
    cut: () => 'Cắt',
    copy: () => 'Sao chép',
    paste: () => 'Dán',
    pasteAndMatchStyle: () => 'Dán và khớp kiểu',
    delete: () => 'Xóa',
    selectAll: () => 'Chọn tất cả',
    showSubstitutions: () => 'Hiện bảng thay thế',
    toggleTextReplacement: () => 'Thay thế văn bản',
    forceReload: () => 'Buộc tải lại',
    togglefullscreen: () => 'Bật/tắt toàn màn hình',
    minimize: () => 'Thu nhỏ',
    zoom: () => 'Thu phóng',
    front: () => 'Đưa tất cả lên trước',
    close: () => 'Đóng'
  },
  labels: {
    'Check for Updates…': 'Kiểm tra bản cập nhật…',
    File: 'Tệp',
    'New Window': 'Cửa sổ mới',
    'Open Folder…': 'Mở thư mục…',
    Close: 'Đóng',
    Edit: 'Sửa',
    Substitutions: 'Thay thế',
    View: 'Xem',
    Reload: 'Tải lại',
    'Toggle Developer Tools': 'Bật/tắt công cụ nhà phát triển',
    'Actual Size': 'Kích thước thực',
    'Zoom In': 'Phóng to',
    'Zoom Out': 'Thu nhỏ',
    Window: 'Cửa sổ',
    Help: 'Trợ giúp'
  },
  patterns: [
    [/^About (.+)$/, name => `Giới thiệu về ${name}`],
    [/^Show (.+)$/, name => `Hiện ${name}`],
    [/^Quit (.+)$/, name => `Thoát ${name}`]
  ]
}

const COPY: Record<string, NativeMenuCopy> = { vi: VI }

/** Copy for a renderer locale id (`vi`, `vi-VN`), or null to keep the English template. */
function copyFor(locale: string): NativeMenuCopy | null {
  const id = locale.trim().toLowerCase().replace(/_/g, '-')

  return COPY[id] ?? COPY[id.split('-')[0]] ?? null
}

function relabel(label: string, copy: NativeMenuCopy): string {
  if (Object.hasOwn(copy.labels, label)) {
    return copy.labels[label]
  }

  for (const [pattern, render] of copy.patterns) {
    const match = label.match(pattern)

    if (match) {
      return render(match[1])
    }
  }

  return label
}

function localizeItem(item: MenuItemConstructorOptions, copy: NativeMenuCopy, appName: string) {
  const next: MenuItemConstructorOptions = { ...item }

  if (typeof item.label === 'string') {
    next.label = relabel(item.label, copy)
  } else if (item.role && copy.roles[item.role]) {
    next.label = copy.roles[item.role]!(appName)
  }

  if (Array.isArray(item.submenu)) {
    next.submenu = item.submenu.map(child => localizeItem(child, copy, appName))
  }

  return next
}

/** Relabel a menu template for the renderer's language; returns it untouched when there is no copy. */
export function localizeMenuTemplate(
  template: MenuItemConstructorOptions[],
  locale: string,
  appName: string
): MenuItemConstructorOptions[] {
  const copy = copyFor(locale)

  return copy ? template.map(item => localizeItem(item, copy, appName)) : template
}
