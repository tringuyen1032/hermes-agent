// Validate translated catalog functions against their English originals.
// Usage: node validate-fns.mjs <repo> <in.json> <out.json>
//   in:  [{ id, en, vi, identifierArgs?: number[] }]   (en: JS source, vi: TS arrow function source)
//   out: [{ id, problem: string|null, fixed: string }]
// Mirrors catalog-completeness.test.ts: same arity, every interpolated argument English renders must
// still render, same return shape; plus: must not throw on numeric/string arguments, must not be untranslated.
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import vm from 'node:vm'

const [repo, input, output] = process.argv.slice(2)
const { transformSync } = await import(pathToFileURL(resolve(repo, 'node_modules/esbuild/lib/main.js')).href)

const VI = /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i

function compile(source, loader) {
  const code = transformSync(`(${source.trim().replace(/;\s*$/, '')})`, { loader, format: 'esm' }).code
  return vm.runInNewContext(code.trim().replace(/;\s*$/, ''), Object.create(null), { timeout: 200 })
}

const shape = value => (Array.isArray(value) ? `array(${value.length})` : value && typeof value === 'object'
  ? `object(${Object.keys(value).sort().join(',')})` : typeof value)

function call(fn, args) {
  try {
    return { ok: true, value: fn(...args) }
  } catch (error) {
    return { ok: false, error: String(error).slice(0, 160) }
  }
}

function check({ en, vi, identifierArgs = [] }) {
  if (typeof vi !== 'string' || !vi.includes('=>')) {
    return 'must be an arrow function'
  }

  let enFn
  let viFn

  try {
    enFn = compile(en, 'js')
  } catch {
    return null // cannot evaluate English: leave it to the type checker
  }

  try {
    viFn = compile(vi, 'ts')
  } catch (error) {
    return `does not parse: ${String(error).split('\n')[0].slice(0, 200)}`
  }

  if (typeof viFn !== 'function') {
    return 'must evaluate to a function'
  }

  if (viFn.length !== enFn.length) {
    return `takes ${viFn.length} parameter(s); English takes ${enFn.length} — keep the same parameter list`
  }

  const probes = Array.from({ length: enFn.length }, (_, index) => `⟦${index}⟧`)
  const enOut = call(enFn, probes)

  if (enOut.ok) {
    const viOut = call(viFn, probes)

    if (!viOut.ok) {
      return `throws when called with text arguments: ${viOut.error}`
    }

    if (shape(viOut.value) !== shape(enOut.value)) {
      return `returns ${shape(viOut.value)}; English returns ${shape(enOut.value)}`
    }

    const enText = JSON.stringify(enOut.value)
    const viText = JSON.stringify(viOut.value)

    for (const [index, probe] of probes.entries()) {
      if (enText.includes(probe) && !identifierArgs.includes(index) && !viText.includes(probe)) {
        return `drops argument #${index + 1} (${probe}) that English shows — keep every interpolation`
      }
    }

    // Plain words of running text: commands, ids and placeholders do not count.
    const words = enText
      .replace(/⟦\d⟧|\$\{[^}]*\}|`[^`]*`/g, ' ')
      .split(/\s+/)
      .filter(token => /^[A-Za-z]+[,.!?:;]?$/.test(token))

    if (words.length >= 3 && viText === enText) {
      return 'output is identical to English — translate the text'
    }

    if (words.length >= 6 && !VI.test(viText)) {
      return 'output still looks English — translate the human-readable text into Vietnamese'
    }
  }

  const lost = logicAtoms(en).filter(atom => !logicAtoms(vi).includes(atom))

  if (lost.length) {
    return `drops English logic: ${lost.map(atom => `\`${atom}\``).join(', ')} — keep every condition and array method except plural tests like \`n===1\``
  }

  return behaviour(enFn, viFn, en)
}

// Code that decides WHAT is shown: comparisons, truthiness tests and array methods. Plural tests
// (`=== 1`, `!== 1`, `> 1`) may go — Vietnamese does not inflect — everything else must survive.
function logicAtoms(source) {
  const code = codeOnly(source).replace(/\s+/g, '')
  const atoms = new Set()

  for (const [, left, op, right] of code.matchAll(/([A-Za-z_$][\w$.]*)(===|!==|==|!=|<=|>=|<|>)([\w$.]+|"")/g)) {
    if (!(['1'].includes(right) && ['===', '!==', '==', '!=', '>'].includes(op))) {
      atoms.add(`${left}${op.replace(/^([=!])==$/, '$1=')}${right}`)
    }
  }

  for (const [, ident] of code.matchAll(/(?<![=!<>]=?)\b([A-Za-z_$][\w$.]*)\?(?![.?])/g)) atoms.add(`${ident}?`)
  for (const [, method] of code.matchAll(/\.(filter|map|join|slice|some|every|find|reduce|flatMap)\(/g)) atoms.add(`.${method}(`)

  return [...atoms]
}

// Behavioural diff over an input grid: the translation must keep English's logic (conditions,
// filters, joins), so it may not render empty where English does not (or vice versa), throw where
// English does not, or show artifacts English never shows — dangling separators from an unfiltered
// empty piece, "null"/"undefined" leaking from a dropped condition, doubled spaces.
// Realistic values by default; the edge values join only when English's own source branches on them,
// so a plain `${name}` template is never blamed for rendering an empty name.
function poolFor(source) {
  const code = codeOnly(source)
  const pool = [0, 1, 2, 7, 'abc', 'Xyz', true, false, ['x'], ['x', 'y']]

  if (/\bnull\b|\?\?/.test(code)) pool.push(null)
  if (/\bundefined\b|\?\?/.test(code)) pool.push(undefined)
  if (/\.length\b/.test(code)) pool.push([], '')
  // A bare truthiness test (`sha ? … : …`, `!name`), not a comparison like `count === 1 ? …`.
  if (/(?<![=!<>]=?\s*)\b[A-Za-z_$][\w$]*\s*\?(?![.?])|![A-Za-z_$]/.test(code)) pool.push('')

  return pool
}

/** The source with string and template text blanked out (template `${…}` code kept). */
function codeOnly(source) {
  let out = ''
  let i = 0

  const skipQuoted = quote => {
    i += 1
    while (i < source.length && source[i] !== quote) i += source[i] === '\\' ? 2 : 1
    i += 1
    out += ' "" '
  }

  const template = () => {
    i += 1
    while (i < source.length && source[i] !== '`') {
      if (source[i] === '\\') {
        i += 2
      } else if (source[i] === '$' && source[i + 1] === '{') {
        i += 2
        out += ' ( '
        code('}')
        out += ' ) '
        i += 1
      } else {
        i += 1
      }
    }
    i += 1
  }

  const code = closer => {
    let depth = 0
    while (i < source.length) {
      const ch = source[i]
      if (ch === closer && depth === 0) return
      if (ch === '"' || ch === "'") skipQuoted(ch)
      else if (ch === '`') template()
      else {
        if (ch === '{') depth += 1
        if (ch === '}') depth -= 1
        out += ch
        i += 1
      }
    }
  }

  code(null)

  return out
}

// [pattern, label, category]: a category is only judged when English is clean in it for that input.
const ARTIFACTS = [
  [/^\s|\s$/, 'leading/trailing whitespace', 'space'],
  [/\S {2,}\S/, 'doubled spaces', 'space'],
  [/\s[,.;:!?](?![\d.])/, 'a separator after a space', 'punct'],
  [/,\s*,|;\s*;/, 'a doubled separator', 'punct'],
  [/\(\s*\)|\[\s*\]/, 'empty brackets', 'punct'],
  [/^\s*[,.;:]|[,;:]\s*$/, 'a dangling separator at the edge', 'punct'],
  [/\b(null|undefined|NaN)\b|\[object /, 'null/undefined/NaN', 'nullish']
]

function grid(arity, pool) {
  const vectors = []
  const total = pool.length ** arity

  for (let index = 0; index < Math.min(total, 400); index += 1) {
    const pick = Math.floor((index * total) / Math.min(total, 400))
    vectors.push(Array.from({ length: arity }, (_, slot) => pool[Math.floor(pick / pool.length ** slot) % pool.length]))
  }

  return vectors
}

const show = args => args.map(arg => JSON.stringify(arg) ?? 'undefined').join(', ')

function behaviour(enFn, viFn, source) {
  for (const args of grid(enFn.length, poolFor(source))) {
    const enOut = call(enFn, args)

    if (!enOut.ok) {
      continue
    }

    const viOut = call(viFn, args)

    if (!viOut.ok) {
      return `throws for arguments (${show(args)}) where English does not: ${viOut.error} — keep English's logic`
    }

    const enText = typeof enOut.value === 'string' ? enOut.value : JSON.stringify(enOut.value) ?? ''
    const viText = typeof viOut.value === 'string' ? viOut.value : JSON.stringify(viOut.value) ?? ''

    if ((enText.trim() === '') !== (viText.trim() === '')) {
      return `for arguments (${show(args)}) English renders ${JSON.stringify(enText)} but yours renders ${JSON.stringify(viText)} — keep English's conditions`
    }

    const dirty = new Set(ARTIFACTS.filter(([pattern]) => pattern.test(enText)).map(([, , category]) => category))

    for (const [pattern, label, category] of ARTIFACTS) {
      if (!dirty.has(category) && pattern.test(viText)) {
        return `for arguments (${show(args)}) yours renders ${JSON.stringify(viText)} (${label}); English renders ${JSON.stringify(enText)} — keep English's filtering/conditions so empty pieces never show`
      }
    }
  }

  return null
}

const items = JSON.parse(readFileSync(input, 'utf8'))
const results = items.map(item => ({ id: item.id, fixed: String(item.vi ?? '').trim(), problem: check(item) }))
writeFileSync(output, JSON.stringify(results))
