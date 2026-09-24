#!/usr/bin/env python3
"""Builds dict-app's system-search word list from the bundles the dictionary site already ships.

WHY THIS EXISTS: Android's search framework shows suggestions from a ContentProvider, and that
provider needs the words ON THE DEVICE — a Trusted Web Activity renders the site in Chrome, so the
dictionary's own word list is not reachable from the app at suggestion time. The list is therefore
extracted here, committed as assets, and read by DgDictSuggestProvider.

WHICH WORDS, AND WHY THESE: the site's offline engine (ddg-ui public/static/offline-dpd.js) looks a
query up by EXACT key —
    heads = (dpd_i2h[key] || []) + (dpd_ebts[key] ? [key] : dpd_ebts[key + ' 1'] ? [key + ' 1'] : [])
— so a suggestion is only honest if the site can resolve it as typed. Two files come out of that:

  dpd_headwords.txt  what a reader would call the word: every plain headword of dpd_ebts, plus the
                     bare form of a numbered homograph ("akaṅkha 1.1" -> "akaṅkha") when that bare
                     form is itself resolvable. Numbered keys are otherwise DROPPED: the engine
                     matches "akaṅkha" against dpd_ebts["akaṅkha 1"] only, so for the ~8k entries
                     that have no " 1" variant the numbered key is the only form that resolves —
                     offering "akaṅkha 1.1" in a search box would be nonsense, so those words are
                     simply not suggested (they are unfindable on the site today either way).

  dpd_forms.txt      the inflected forms (dpd_i2h keys) that are not already headwords — a Pali
                     reader usually meets "gacchati", not "gam", and every one of these resolves.

Ranking is the reason for two files rather than one list with a flag: the provider scans
dpd_headwords.txt first, so a headword outranks an inflected form for the same prefix.

USAGE:
    python3 scripts/build-dict-headwords.py            # writes both assets
    python3 scripts/build-dict-headwords.py --check    # exits 1 if a committed asset is stale
"""

import argparse
import os
import re
import sys

SOURCE_DIR = "/var/www/dictPlugin/assets/standalone-dpd"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                      "dict-app", "src", "main", "assets")

# Both bundles are `var name = { "key": "value", ... }` — one entry per line, and a value may
# itself contain quotes, so match the key at the start of the line only.
KEY = re.compile(r'^  "((?:[^"\\]|\\.)*)": ')
NUMBERED = re.compile(r"^.* \d+(\.\d+)*$")


def keys(path):
    out = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            found = KEY.match(line)
            if found:
                word = found.group(1).replace('\\"', '"').replace("\\\\", "\\").strip()
                if word:
                    out.append(word)
    return out


def build():
    ebts = keys(os.path.join(SOURCE_DIR, "dpd_ebts.js"))
    i2h = keys(os.path.join(SOURCE_DIR, "dpd_i2h.js"))
    resolvable = set(ebts) | set(i2h)

    def bare(word):
        return re.sub(r" \d+(\.\d+)*$", "", word)

    headwords = set()
    for word in ebts:
        if NUMBERED.match(word):
            base = bare(word)
            if base in resolvable:
                headwords.add(base)
        else:
            headwords.add(word)

    forms = {word for word in i2h if word not in headwords}
    return sorted(headwords), sorted(forms)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="fail if a committed asset differs from what this script would write")
    args = parser.parse_args()

    if not os.path.isdir(SOURCE_DIR):
        print("source bundles not found: %s" % SOURCE_DIR, file=sys.stderr)
        return 1

    headwords, forms = build()
    wanted = {
        os.path.join(ASSETS, "dpd_headwords.txt"): "\n".join(headwords) + "\n",
        os.path.join(ASSETS, "dpd_forms.txt"): "\n".join(forms) + "\n",
    }

    if args.check:
        stale = False
        for path, body in wanted.items():
            current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            if current != body:
                print("stale: %s (run without --check)" % path, file=sys.stderr)
                stale = True
        if stale:
            return 1
        print("up to date: %d headwords, %d forms" % (len(headwords), len(forms)))
        return 0

    os.makedirs(ASSETS, exist_ok=True)
    for path, body in wanted.items():
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(body)
        print("wrote %s: %d words, %.2f MB"
              % (path, body.count("\n"), len(body.encode("utf-8")) / 1048576))
    return 0


if __name__ == "__main__":
    sys.exit(main())
