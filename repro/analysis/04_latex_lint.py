#!/usr/bin/env python3
"""
04_latex_lint.py
=========================================================================
Static checks for manuscript/ that catch the errors a compiler would catch
first, so that an Overleaf round-trip is not the debugging loop.

Checks
  1. every \\input{...} target exists
  2. every \\ref / \\eqref has a matching \\label
  3. every \\cite key exists in refs.bib
  4. \\begin{X} / \\end{X} balance per file
  5. unresolved draft markers (\\tbd) counted per file
  6. duplicate \\label definitions

Usage
  python 04_latex_lint.py --dir <PAPER_INTAKE_20261104>/manuscript
Exit code 0 = clean, 1 = problems found.
"""
import argparse, os, re, sys, collections

INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|eqref)\{([^}]+)\}")
CITE_RE = re.compile(r"\\cite[a-zA-Z]*\{([^}]+)\}")
BEGIN_RE = re.compile(r"\\begin\{([^}]+)\}")
END_RE = re.compile(r"\\end\{([^}]+)\}")
BIB_RE = re.compile(r"@\w+\{([^,]+),")


def strip_comments(text):
    out = []
    for line in text.splitlines():
        i, cut = 0, len(line)
        while i < len(line):
            if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
                cut = i
                break
            i += 1
        out.append(line[:cut])
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    a = ap.parse_args()
    root = a.dir
    problems = []

    # ---- collect all tex files reachable from main.tex -------------------
    main_tex = os.path.join(root, "main.tex")
    if not os.path.exists(main_tex):
        sys.exit("missing main.tex in " + root)
    seen, queue = set(), [main_tex]
    texts = {}
    while queue:
        p = queue.pop()
        if p in seen:
            continue
        seen.add(p)
        if not os.path.exists(p):
            problems.append("MISSING INPUT: %s" % os.path.relpath(p, root))
            continue
        raw = open(p, encoding="utf-8").read()
        texts[p] = strip_comments(raw)
        for m in INPUT_RE.finditer(texts[p]):
            target = m.group(1).strip()
            cand = os.path.join(root, target)
            if not os.path.splitext(cand)[1]:
                cand += ".tex"
            queue.append(cand)

    # ---- 2..5 ------------------------------------------------------------
    labels = collections.Counter()
    refs = collections.defaultdict(list)
    tbd = collections.Counter()
    begin_end = []
    for p, t in texts.items():
        for m in LABEL_RE.finditer(t):
            labels[m.group(1)] += 1
        for m in REF_RE.finditer(t):
            refs[m.group(1)].append(os.path.basename(p))
        tbd[os.path.relpath(p, root)] = len(re.findall(r"\\tbd\{", t))
        stack = []
        for m in re.finditer(r"\\(begin|end)\{([^}]+)\}", t):
            kind, env = m.group(1), m.group(2)
            if kind == "begin":
                stack.append(env)
            else:
                if not stack:
                    begin_end.append("%s: \\end{%s} without begin" % (os.path.basename(p), env))
                elif stack[-1] != env:
                    begin_end.append("%s: \\end{%s} closes \\begin{%s}" % (os.path.basename(p), env, stack[-1]))
                    stack.pop()
                else:
                    stack.pop()
        for env in stack:
            begin_end.append("%s: unclosed \\begin{%s}" % (os.path.basename(p), env))

    for k, v in labels.items():
        if v > 1:
            problems.append("DUPLICATE LABEL: %s (%d)" % (k, v))
    for k, where in refs.items():
        if k not in labels:
            problems.append("UNDEFINED REF: %s  (in %s)" % (k, ",".join(sorted(set(where)))))
    problems.extend("ENV: " + b for b in begin_end)

    # ---- 3. citations ----------------------------------------------------
    bib_p = os.path.join(root, "refs.bib")
    bib_keys = set()
    if os.path.exists(bib_p):
        bib_keys = {m.group(1).strip() for m in BIB_RE.finditer(open(bib_p, encoding="utf-8").read())}
    cited = set()
    for t in texts.values():
        for m in CITE_RE.finditer(t):
            for k in m.group(1).split(","):
                cited.add(k.strip())
    for k in sorted(cited):
        if k not in bib_keys:
            problems.append("MISSING BIB ENTRY: %s" % k)
    unused = sorted(bib_keys - cited)

    # ---- report ----------------------------------------------------------
    print("files scanned : %d" % len(texts))
    print("labels        : %d" % len(labels))
    print("refs          : %d  (all resolved: %s)" % (len(refs), all(k in labels for k in refs)))
    print("citations     : %d  (bib entries: %d, missing: %d)"
          % (len(cited), len(bib_keys), len(cited - bib_keys)))
    if unused:
        print("unused bib    : %s" % ", ".join(unused))
    print("\\tbd markers  :", {k: v for k, v in tbd.items() if v})
    print()
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("OK - no structural problems found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
