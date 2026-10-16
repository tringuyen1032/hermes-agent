// Flatten an English catalog export into a JSON inventory of leaves.
// Usage: npx tsx --tsconfig <tsconfig> dump.mts <module.ts> <export.path> <out.json>
//   e.g. dump.mts apps/desktop/src/i18n/en.ts en desktop-en.json
//        dump.mts apps/desktop/src/plugins/kanban/i18n.ts KANBAN_LOCALES.en kanban-en.json
// Each leaf: { segs: string[], kind: 'string'|'function'|'array'|..., value?, arity?, source? }.
// `segs` keeps real key segments, so flat records with dotted keys ('display.personality') survive.
import { writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const [modulePath, exportPath, out] = process.argv.slice(2)

const mod = await import(pathToFileURL(resolve(modulePath)).href)
const root = exportPath.split('.').reduce((value: any, key) => value?.[key], mod)

if (!root || typeof root !== 'object') {
  throw new Error(`export ${exportPath} not found in ${modulePath}`)
}

type Leaf = { segs: string[]; kind: string; value?: unknown; arity?: number; source?: string }
const leaves: Leaf[] = []

function walk(value: unknown, segs: string[]) {
  if (typeof value === 'function') {
    leaves.push({ segs, kind: 'function', arity: value.length, source: value.toString() })
  } else if (Array.isArray(value)) {
    leaves.push({ segs, kind: 'array', value })
  } else if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) walk(child, [...segs, key])
  } else {
    leaves.push({ segs, kind: typeof value, value })
  }
}

walk(root, [])
writeFileSync(out, JSON.stringify(leaves, null, 1))

const counts: Record<string, number> = {}
for (const leaf of leaves) counts[leaf.kind] = (counts[leaf.kind] ?? 0) + 1
console.log(`${exportPath}: ${leaves.length} leaves`, counts)
