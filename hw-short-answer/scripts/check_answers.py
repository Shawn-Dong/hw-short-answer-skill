#!/usr/bin/env python3
"""Check homework answer prose for the user's style rules and common AI tells.

Usage:
    python3 check_answers.py FILE [FILE ...] [--all]

FILE can be:
    .tex    Text after each \\answer is checked, split by \\item into sub-answers.
            With --all, every \\clearpage page of the document body is checked instead.
    .ipynb  Markdown cells that hold an answer ("Answer:", "Response here:") are checked.
            Cells that still hold only the placeholder are skipped.
    .md/.txt  Each "## " section is one answer. A file with no "## " is one answer.

ERROR lines must be fixed. WARN lines need a judgment call (see SKILL.md section 4).
Exit code is 1 if any ERROR was found.

Prose rules are adapted from a blog lint script that follows humanizer
(https://github.com/blader/humanizer) and stop-slop (https://github.com/hardikpandya/stop-slop),
both MIT. Standard library only, Python 3.8+.
"""
import json
import re
import sys

# ---------------------------------------------------------------- word lists
BANNED = [
    "i hope this helps", "great question", "certainly!", "let me know if",
    "let's dive in", "let's dive into", "let's explore", "let's break this down", "without further ado",
    "here's the thing", "here's what you need to know", "in today's fast-paced", "in today's digital",
    "in the ever-evolving", "ever-changing landscape", "evolving landscape", "stands as a testament",
    "a testament to", "rich tapestry", "delve", "delves", "delving", "game-changer", "game changer",
    "unlock the power", "unleash the power", "let that sink in", "the future looks bright",
    "exciting times ahead", "at the end of the day", "it's worth noting that", "it is worth noting that",
    "up to my last training", "as of my last", "in this answer", "in this report we", "as mentioned above",
]
AI_WORDS = [
    "additionally", "align with", "bolstered", "crucial", "enduring", "enhance", "garner", "interplay",
    "intricate", "landscape", "meticulous", "meticulously", "pivotal", "robust", "seamless", "seamlessly",
    "showcase", "showcasing", "underscore", "underscores", "underscoring", "highlighting", "vibrant",
    "leverage", "leveraging", "empower", "empowering", "holistic", "cutting-edge", "transformative",
    "navigate", "navigating", "realm", "paradigm", "foster", "fostering", "streamline", "notably",
    "furthermore", "moreover", "significantly", "comprehensive", "nuanced", "key insight",
]
SUMMARY_OPENERS = re.compile(
    r"^(overall|in conclusion|in summary|to summarize|to sum up|in short|all in all|ultimately|"
    r"taken together|in essence)\b", re.I)
SIGNPOSTS = re.compile(r"\b(this|which|that) (shows|suggests|demonstrates|highlights|indicates|illustrates) that\b", re.I)
HEDGE_STACK = re.compile(r"\b(may|might|could|can)\s+(potentially|possibly|perhaps|arguably)\b", re.I)
CONTRAST = [
    re.compile(r"\bnot (?:just|only|merely|simply|necessarily)\b", re.I),
    re.compile(r"\brather than\b", re.I),
    re.compile(r"\binstead of\b", re.I),
    re.compile(r", not (?:a |an |the |just )?\w", re.I),
    re.compile(r"\b(?:it|this|that)(?:'s| is) not\b", re.I),
    re.compile(r"\b(?:isn't|is not|aren't|are not|doesn't|does not|don't|do not)\b[^.]{0,80}\. "
               r"(?:It|They|This|That)(?:'s| is| are)\b", re.I),
]
ITEM = r"(?:[^\s,;:()]+ ){0,4}[^\s,;:()]+"
CLAUSE = r"(?!(?:including|such as|like|which|who|where|when|while|with|then|from|after|before|because|so|but)\b)"
TRIAD = re.compile(rf"{ITEM}, {CLAUSE}{ITEM},? (?:and|or) {ITEM}", re.I)
ABBREV = re.compile(r"\b(?:e\.g|i\.e|vs|etc|Fig|Eq|approx|al|cf|resp|No)\.$", re.I)
LONG = 30


# ---------------------------------------------------------------- extraction
def strip_tex(text):
    """Turn LaTeX answer source into plain prose a reader would read."""
    t = re.sub(r"(?<!\\)%.*", "", text)                       # comments
    t = t.replace("\\$", "USD").replace("\\%", "%").replace("\\&", "and").replace("{,}", ",")
    t = re.sub(r"\\\[.*?\\\]", " MATH. ", t, flags=re.S)       # display math
    t = re.sub(r"\$\$.*?\$\$", " MATH. ", t, flags=re.S)
    t = re.sub(r"\\begin\{(align|equation|gather|multline)\*?\}.*?\\end\{\1\*?\}", " MATH. ", t, flags=re.S)
    t = re.sub(r"\\begin\{(figure|table|tabular|center)\*?\}.*?\\end\{\1\*?\}", " ", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", "MATH", t)                         # inline math
    t = re.sub(r"\\item\b(\[[^\]]*\])?", "\n\n", t)
    t = re.sub(r"\\(?:texttt|verb)\{[^{}]*\}", "CODE", t)
    for cmd in ("textit", "textbf", "emph", "text", "underline", "textsc"):
        t = re.sub(rf"\\{cmd}\{{([^{{}}]*)\}}", r"\1", t)
    t = re.sub(r"\\(?:begin|end)\{[^}]*\}(\[[^\]]*\])?", " ", t)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", t)
    t = t.replace("``", '"').replace("''", '"').replace("~", " ").replace("\\\\", " ")
    t = t.replace("{", "").replace("}", "")
    return t


def strip_md(text):
    text = "\n".join(l for l in text.split("\n") if not re.match(r"^\s*(?:#|\|)", l))  # headings and tables are not prose
    t = re.sub(r"\$\$.*?\$\$", " MATH. ", text, flags=re.S)
    t = re.sub(r"\$[^$\n]*\$", "MATH", t)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"`[^`]*`", "CODE", t)
    t = re.sub(r"\]\([^)]*\)", "]", t)
    t = re.sub(r"^\s*(?:\*\*)?(?:answer|response(?: here)?)\s*:?\s*(?:\*\*)?\s*:?", "", t, flags=re.I)
    return t.replace("**", "").replace("__", "")


def blocks_from_tex(src, all_pages=False):
    src = re.sub(r"(?<!\\)%.*", "", src)
    body = src.split("\\begin{document}", 1)[-1]
    if all_pages:
        return [(f"page {i + 1}", "tex", p) for i, p in enumerate(re.split(r"\\clearpage|\\newpage", body))]
    out = []
    header_re = re.compile(r"\\textbf\{(Problem[^}]*)\}|\\pensive(?:item|first)\{([^}]*)\}|\\(?:sub)*section\*?\{([^}]*)\}")
    stop_re = re.compile(r"\\clearpage|\\newpage|\\pensiveitem|\\pensivefirst|\\(?:sub)*section\*?\{|"
                         r"\\noindent\\textbf\{Problem|\\end\{document\}")
    for m in re.finditer(r"\\answer\b", body):
        start = m.end()
        stop = stop_re.search(body, start)
        chunk = body[start: stop.start() if stop else len(body)]
        headers = list(header_re.finditer(body, 0, m.start()))
        label = next((g for g in headers[-1].groups() if g), "answer") if headers else "answer"
        label = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", label).replace("\\_", "_")
        lm = re.search(r"\\begin\{(enumerate|itemize)\}(.*)\\end\{\1\}", chunk, flags=re.S)
        if not lm:
            out.append((label, "tex", chunk))
            continue
        pre, post = chunk[:lm.start()], chunk[lm.end():]
        if strip_tex(pre).strip():
            out.append((f"{label} intro", "tex", pre))
        items = re.split(r"\\item\b(?:\[[^\]]*\])?", lm.group(2))[1:]
        for k, it in enumerate(items):
            tag = f"{chr(97 + k)}." if lm.group(1) == "enumerate" else f"bullet {k + 1}"
            out.append((f"{label} {tag}", "tex", it))
        if strip_tex(post).strip():
            out.append((f"{label} after list", "tex", post))
    return out


def blocks_from_ipynb(src):
    nb = json.loads(src)
    out = []
    for i, c in enumerate(nb.get("cells", [])):
        if c.get("cell_type") != "markdown":
            continue
        text = "".join(c.get("source", []))
        if not re.search(r"(?im)^\s*(?:\*\*)?(answer|response)\b", text) and "Answer:" not in text:
            continue
        rest = strip_md(text).strip()
        if not rest or re.fullmatch(r"(?i)(response here:?|answer:?\s*response here)\.?", rest):
            continue
        out.append((f"cell {i}", "md", text))
    return out


def blocks_from_md(src):
    parts = re.split(r"(?m)^## ", src)
    if len(parts) == 1:
        return [("text", "md", src)]
    out = []
    for p in parts[1:]:
        title, _, body = p.partition("\n")
        if re.search(r"(?i)\bnotes?\b", title):
            continue
        out.append((title.strip()[:60], "md", body))
    return out


# ---------------------------------------------------------------- checks
def sentences(text):
    text = re.sub(r"(?m)^\s*(?:[-*+]|\d+\.)\s+", "\n\n", text)
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    out = []
    for para in paras:
        pieces = re.split(r"(?<=[.!?])[\"')\]]?\s+", re.sub(r"\s+", " ", para).strip())
        merged = []
        for p in pieces:
            if merged and ABBREV.search(merged[-1]):
                merged[-1] += " " + p
            else:
                merged.append(p)
        out += [s.strip() for s in merged if len(s.split()) >= 3]
    return out


def count(text, phrase):
    return len(re.findall(rf"(?<![\w-]){re.escape(phrase)}(?![\w-])", text, re.I))


def check(label, kind, raw):
    findings = []
    err = lambda rule, msg, items=(): findings.append(("ERROR", rule, msg, items))
    warn = lambda rule, msg, items=(): findings.append(("WARN ", rule, msg, items))

    if kind == "tex":
        dashes_src = len(re.findall(r"(?<![-\w])---?(?!-)", re.sub(r"\$[^$]*\$", "", raw)))
        if re.search(r"\\tfrac", re.sub(r"\\\[.*?\\\]", "", raw, flags=re.S)):
            warn("inline-tfrac", "\\tfrac in running text; write 1/5 or a display fraction")
        text = strip_tex(raw)
    else:
        dashes_src = 0
        text = strip_md(raw)
    lower = text.lower()
    sents = sentences(text)
    if not sents:
        return findings, 0, 0.0

    dashes = dashes_src + len(re.findall(r"[—–]| -- ", text))
    if dashes:
        err("dashes", f"{dashes} dash(es) in prose; use a comma, colon or period")
    semis = text.count(";")
    if semis:
        err("semicolons", f"{semis} semicolon(s); split the sentence or join with a conjunction")
    label_ref = re.compile(r"\((?:[a-z]|[ivx]{1,4}|\d{1,2})\)")  # "model (b)", "part (ii)" refer to sub-question labels
    paren = [s for s in sents if re.search(r"(?:^|\s)\(", label_ref.sub("", s))]
    if paren:
        err("parentheses", "parenthetical aside in prose; fold it into the sentence or make it its own sentence"
            " (math like f(x) or P(A) is fine)", paren)
    for p in BANNED:
        n = count(lower, p)
        if n:
            err("banned-phrase", f'"{p}" x{n}')
    if SUMMARY_OPENERS.search(sents[-1]):
        err("summary-closer", "last sentence is a summary closer; end on the last concrete fact", [sents[-1]])
    hits = [(w, count(lower, w)) for w in AI_WORDS if count(lower, w)]
    if hits:
        warn("ai-words", ", ".join(f"{w} x{n}" if n > 1 else w for w, n in hits))
    sign = [s for s in sents if SIGNPOSTS.search(s)]
    if len(sign) > 1:
        warn("signposts", f'{len(sign)} "this shows/suggests that" sentences; state the claim directly', sign)
    hedges = [s for s in sents if HEDGE_STACK.search(s)]
    if hedges:
        warn("stacked-hedge", "two hedges in a row; keep one", hedges)
    con = [s for s in sents if any(r.search(s) for r in CONTRAST)]
    if len(con) > 2:
        err("contrast", f"{len(con)} contrast frames; keep at most 2, each answering a real question", con)
    elif con:
        warn("contrast", "keep only if the negative half answers something the question asked", con)
    tri = [s for s in sents if TRIAD.search(s)]
    if tri:
        warn("triads", "keep if it is a real list of names, data or facts", tri)
    lengths = [len(s.split()) for s in sents]
    avg = sum(lengths) / len(lengths)
    long = [s for s in sents if len(s.split()) > LONG]
    if avg > 20 or len(long) > max(1, int(len(sents) * 0.08)):
        err("long-sentences", f"average {avg:.1f} words (keep at or under 20), {len(long)} over {LONG}", long)
    elif long:
        warn("long-sentences", f"{len(long)} sentence(s) over {LONG} words", long)
    openers = [s.split()[0].lower().strip('"') for s in sents]
    runs = sorted({openers[i] for i in range(len(openers) - 2) if openers[i] == openers[i + 1] == openers[i + 2]})
    if runs:
        warn("same-opener", f"three sentences in a row start with {runs}")
    if re.search(r"[“”‘’]", text):
        warn("curly-quotes", "use straight quotes")
    return findings, len(sents), avg


def main(argv):
    all_pages = "--all" in argv
    files = [a for a in argv if a != "--all"]
    if not files:
        print(__doc__)
        return 2
    any_error = False
    for path in files:
        src = open(path, encoding="utf-8").read()
        if path.endswith(".tex"):
            blocks = blocks_from_tex(src, all_pages)
        elif path.endswith(".ipynb"):
            blocks = blocks_from_ipynb(src)
        else:
            blocks = blocks_from_md(src)
        print(f"\n### {path}  ({len(blocks)} answer block(s))")
        if not blocks:
            print("  no answers found (tex needs \\answer, notebooks need an Answer/Response cell)")
        for label, kind, raw in blocks:
            findings, n, avg = check(label, kind, raw)
            if n == 0:
                continue
            errors = [f for f in findings if f[0] == "ERROR"]
            any_error |= bool(errors)
            mark = "x" if errors else ("~" if findings else "ok")
            print(f"\n  [{mark}] {label}  ({n} sentences, average {avg:.1f} words)")
            for level, rule, msg, items in findings:
                print(f"      {level} {rule}: {msg}")
                for it in items:
                    print(f"          - {it[:120]}")
    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
