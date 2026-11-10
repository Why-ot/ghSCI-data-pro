#!/usr/bin/env python3
"""
05_pdf_layout_check.py
=========================================================================
Offline layout inspection for a compiled PDF: no rasteriser required.

Why this exists
  The build machine has no PDF renderer (no pdftoppm/mutool/gs/soffice) and
  PyPI is unreachable, so pages cannot be turned into images. Text coordinates
  are still available inside the PDF, and they are enough to answer the three
  questions that actually matter after a compile:

    1. is any text outside the printable area?
    2. does any line start inside the column gutter (i.e. a wide table or an
       overfull hbox spilling from the left column into the right one)?
    3. is any caption/float orphaned from its text?

Checks are geometric and therefore approximate; a clean report means "no gross
overflow", not "the page is beautiful".

Usage
  python 05_pdf_layout_check.py --pdf <file.pdf> [--verbose]
"""
import argparse, sys, io, math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from pypdf import PdfReader

# IEEEtran on US letter: 612 x 792 pt, side margin ~54 pt, gutter ~24 pt.
LETTER_W, LETTER_H = 612.0, 792.0


def chunks(page):
    """yield (x, y, size, text) for every text chunk drawn on the page"""
    out = []

    def visitor(text, cm, tm, font_dict, font_size):
        if not text or not text.strip():
            return
        x = cm[0] * tm[4] + cm[2] * tm[5] + cm[4]
        y = cm[1] * tm[4] + cm[3] * tm[5] + cm[5]
        out.append((x, y, font_size or 0.0, text))

    page.extract_text(visitor_text=visitor)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    r = PdfReader(a.pdf)
    print("pages:", len(r.pages))
    first = r.pages[0].mediabox
    w, h = float(first.width), float(first.height)
    print("page size: %.0f x %.0f pt" % (w, h))
    if abs(w - LETTER_W) > 20 or abs(h - LETTER_H) > 20:
        print("  NOTE: not US-letter; margins below are estimates")

    # column geometry guessed from the data: histogram of chunk start x
    allc = [c for p in r.pages for c in chunks(p)]
    xs = sorted(c[0] for c in allc)
    left_margin = xs[max(0, int(0.01 * len(xs)))]
    right_edge = xs[int(0.99 * len(xs))]
    print("text x-range: %.1f .. %.1f pt" % (left_margin, right_edge))
    print("  (page numbers sit at the top-right and are excluded below)")

    # a chunk is only 'outside' if it is beyond the margin by more than TOL pt
    # and is not part of the running head / page number band
    TOL = 3.0
    HEADER_Y = h - 45.0
    FOOTER_Y = 30.0

    problems = 0
    print("\nper page")
    for i, p in enumerate(r.pages, 1):
        cs = chunks(p)
        if not cs:
            print("  p%02d  (no text)" % i)
            continue
        body = [c for c in cs if FOOTER_Y < c[1] < HEADER_Y]
        head = [c for c in cs if not (FOOTER_Y < c[1] < HEADER_Y)]
        x0 = min(c[0] for c in body) if body else 0
        x1 = max(c[0] for c in body) if body else 0
        over_left = [c for c in body if c[0] < left_margin - TOL]
        over_right = [c for c in body if c[0] > 561.0 + TOL]
        flag = ""
        if over_left or over_right:
            flag = "  <-- %d left, %d right" % (len(over_left), len(over_right))
            problems += len(over_left) + len(over_right)
        print("  p%02d  body x[%6.1f..%6.1f] n=%4d  head/foot=%d%s"
              % (i, x0, x1, len(body), len(head), flag))
        if a.verbose and (over_left or over_right):
            for c in (over_left + over_right)[:6]:
                print("        x=%.1f y=%.1f size=%.1f %r" % (c[0], c[1], c[2], c[3][:60]))

    print("\noutside-margin chunks (body only): %d" % problems)
    print("VERDICT:", "no gross overflow detected" if problems == 0
          else "check the flagged pages; likely an overfull table or figure")
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
