// Bundle a catalog module with esbuild (Vite-style env + asset stubs), then flatten one export.
// Usage: node bundle-dump.mjs <repo> <tsconfig> <module.ts> <export.path> <out.json>
import { mkdirSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const [repo, tsconfig, modulePath, exportPath, out] = process.argv.slice(2)
const { build } = await import(pathToFileURL(resolve(repo, 'node_modules/esbuild/lib/main.js')).href)
// Inside the repo so the bundle's bare imports (react, …) resolve from its node_modules.
const cacheDir = resolve(repo, process.env.VI_I18N_BUNDLE_DIR || 'node_modules/.cache/vi-i18n')
mkdirSync(cacheDir, { recursive: true })
const outfile = join(cacheDir, `${exportPath.replace(/\W+/g, '_')}-${process.pid}.mjs`)
const empty = ['.css', '.scss', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.woff', '.woff2', '.ttf', '.mp3', '.wav']

await build({
  entryPoints: [resolve(repo, modulePath)],
  bundle: true,
  format: 'esm',
  platform: 'node',
  outfile,
  logLevel: 'error',
  tsconfig: resolve(repo, tsconfig),
  jsx: 'automatic',
  define: { 'import.meta.env': JSON.stringify({ DEV: false, PROD: true, MODE: 'production', SSR: false }) },
  loader: { ...Object.fromEntries(empty.map(ext => [ext, 'empty'])), '.jsonl': 'text', '.md': 'text' },
  packages: 'external'
})

const mod = await import(pathToFileURL(outfile).href)
const root = exportPath.split('.').reduce((value, key) => value?.[key], mod)

if (!root || typeof root !== 'object') {
  throw new Error(`export ${exportPath} not found in ${modulePath}`)
}

const leaves = []

function walk(value, segs) {
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
const counts = {}
for (const leaf of leaves) counts[leaf.kind] = (counts[leaf.kind] ?? 0) + 1
console.log(`${exportPath}: ${leaves.length} leaves`, counts)

// Catalog modules can leave timers/sockets behind at import; the dump is done.
process.exit(0)
