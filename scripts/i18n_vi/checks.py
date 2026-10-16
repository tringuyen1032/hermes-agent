"""Mechanical checks for a translated UI string. Return (fixed_text, problem|None)."""

from __future__ import annotations

import re

PLACEHOLDER_RES = [
    re.compile(r"\{\{[^{}]*\}\}"),                 # {{literal}}
    re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}"),     # {name}
    re.compile(r"\{\d+\}"),                        # {0}
    re.compile(r"\$\{[^{}]+\}"),                   # ${expr}
    re.compile(r"%\([A-Za-z_]+\)[sdif]"),           # %(name)s
    re.compile(r"(?<!%)%[sdif]"),                   # %s
]
BACKTICK = re.compile(r"`[^`\n]+`")
URL = re.compile(r"https?://[^\s)\"'`>\]]+")
# A slash command starts the text or follows whitespace, a quote, "(" or "[" ("file(s)/section(s)" is prose).
SLASH = re.compile(r"(?<![^\s\"'“‘(\[])/[a-z][a-z0-9_-]*(?![\w/.])")
OPTION_LETTER = re.compile(r"\[[A-Za-z](?:/[A-Za-z])*\]")
ENV_VAR = re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b")
VI_LETTERS = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.IGNORECASE)


def placeholders(text: str) -> set[str]:
    found: set[str] = set()
    for rx in PLACEHOLDER_RES:
        found.update(rx.findall(text))
    return found


KEEP_CASE = {"Hermes", "Nous", "OpenRouter", "OpenAI", "Anthropic", "Claude", "Codex", "Gemini", "GitHub",
             "Git", "Docker", "Telegram", "Discord", "Slack", "WhatsApp", "Signal", "Matrix", "Stripe", "Kanban",
             "Python", "Electron", "Ollama", "Windows", "Linux", "Markdown", "Enter", "Esc", "Tab", "Shift",
             "Ctrl", "Space", "Backspace", "Email", "Google", "Microsoft", "Apple", "Chrome", "Chromium"}


def fix_case(en: str, vi: str) -> str:
    """Mirror the source's initial capitalization: a lowercase English fragment is often spliced
    mid-sentence, while a capitalized one is a sentence/label (Vietnamese uses sentence case)."""
    m_en = re.match(r"^(\s*)([A-Za-z])", en)
    m_vi = re.match(r"^(\s*)(\w+)", vi)
    if not m_en or not m_vi:
        return vi
    first_word = m_vi.group(2)
    if first_word in KEEP_CASE or (len(first_word) > 1 and first_word.isupper()) or not first_word[0].isalpha():
        return vi
    pos = m_vi.start(2)
    ch = vi[pos]
    want = ch.lower() if m_en.group(2).islower() else ch.upper()
    return vi[:pos] + want + vi[pos + 1:]


def _missing(source_tokens, target: str) -> list[str]:
    return sorted({tok for tok in source_tokens if tok not in target})


def check_text(en: str, vi: str, *, allow_same: bool = False) -> tuple[str, str | None]:
    if not isinstance(vi, str):
        return "", "translation must be a string"
    # Re-impose the source's outer whitespace: CLI output aligns on it.
    lead = re.match(r"^\s*", en).group(0)
    trail = re.search(r"\s*$", en).group(0)
    core = vi.strip()
    fixed = lead + core + trail if en.strip() else en

    problems: list[str] = []
    src_ph, dst_ph = placeholders(en), placeholders(fixed)
    if src_ph != dst_ph:
        lost, extra = sorted(src_ph - dst_ph), sorted(dst_ph - src_ph)
        if lost:
            problems.append(f"placeholders lost: {' '.join(lost)} (copy them verbatim)")
        if extra:
            problems.append(f"placeholders not in the source: {' '.join(extra)}")
    for label, rx in (("code span", BACKTICK), ("URL", URL), ("slash command", SLASH),
                      ("option letter", OPTION_LETTER), ("environment variable", ENV_VAR)):
        lost = _missing(rx.findall(en), fixed)
        if lost:
            problems.append(f"{label} changed or missing: {' '.join(lost)} (copy verbatim)")
    if en.count("\n") != fixed.count("\n"):
        problems.append(f"keep exactly {en.count(chr(10))} line break(s) like the source")
    if "\\n" in fixed and "\\n" not in en:
        problems.append("use real line breaks, not a literal backslash-n")

    if not allow_same and looks_untranslated(en, fixed):
        problems.append("this looks untranslated — translate the human-readable text into Vietnamese")
    return fixed, ("; ".join(problems) or None)


def prose_words(text: str) -> list[str]:
    """Plain words of running text; commands, paths, ids and placeholders do not count."""
    stripped = re.sub(r"`[^`]*`|\{[^}]*\}|https?://\S+", " ", text)
    return [tok for tok in stripped.split() if re.fullmatch(r"[A-Za-z]+[,.!?:;]?", tok)]


def looks_untranslated(en: str, vi: str) -> bool:
    """An echo of English prose, or long prose with no Vietnamese letter at all. Short labels may
    legitimately carry no diacritics ("Token bot Slack"), and code-like text stays as is."""
    words = prose_words(en)
    if len(words) < 3:
        return False
    if vi.strip().casefold() == en.strip().casefold():
        return True
    return len(words) >= 6 and not VI_LETTERS.search(vi)
