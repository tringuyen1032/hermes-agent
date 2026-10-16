// Flatten the TUI English catalog: path, kind, arity, function source and a positional probe template.
// Usage: npx tsx dump-tui.mts <repo> <out.json>
import { writeFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'

const [repo, out] = process.argv.slice(2)

const { en } = await import(pathToFileURL(`${repo}/ui-tui/src/i18n/en.ts`).href)

type Leaf = { path: string; kind: string; arity?: number; value?: unknown; source?: string; template?: string; probeError?: string }
const leaves: Leaf[] = []

function walk(value: unknown, path: string) {
  if (typeof value === 'function') {
    const leaf: Leaf = { path, kind: 'function', arity: value.length, source: value.toString() }

    try {
      const probes = Array.from({ length: value.length }, (_, index) => `{${index}}`)
      const rendered = value(...probes)
      leaf.template = typeof rendered === 'string' ? rendered : JSON.stringify(rendered)
    } catch (error) {
      leaf.probeError = String(error)
    }

    leaves.push(leaf)
  } else if (Array.isArray(value)) {
    leaves.push({ path, kind: 'array', value })
  } else if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) walk(child, path ? `${path}.${key}` : key)
  } else {
    leaves.push({ path, kind: typeof value, value })
  }
}

walk(en, '')
writeFileSync(out, JSON.stringify(leaves, null, 1))

const counts: Record<string, number> = {}
for (const leaf of leaves) counts[leaf.kind] = (counts[leaf.kind] ?? 0) + 1
console.log('leaves:', leaves.length, counts, 'probe errors:', leaves.filter(l => l.probeError).length)
