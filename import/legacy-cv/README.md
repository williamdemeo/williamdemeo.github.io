# The CV copies this repository did not already hold

Four copies of the CV existed when #16 was written (ADR-003). Two of them live
outside this repository, so they are snapshotted here: a check that reads its
sources over the network is not a check `nix flake check` can run, and ADR-004
gives CI no network by design.

These files are **provenance, not content**. Nothing renders them, and nothing
should be corrected in them — their disagreements are the point, and
`scripts/python/check_cv_sources.py` reads them to prove that every entry in
every copy reached `cv.yml` or was declared an omission there.

| file | copy | as of |
| --- | --- | --- |
| `cv-repo-README.md` | `github.com/williamdemeo/cv`, `README.md` | January 2025 |
| `demeo_cv-2022.txt` | `gitlab.com/williamdemeo/job-app`, `cv/demeo_cv.pdf` | June 2022 |

The other two copies were already in this repository and are read in place:
`import/zola-content/cv/index.md` (December 2021) and `docs/cv.md`.

## `cv-repo-README.md`

Fetched from `raw.githubusercontent.com/williamdemeo/cv/main/README.md`.

    sha256  7060955340c8e03906643f62058ae5a9abd5b2b06ba2d641a289a4c62e9cdeea

Verbatim, including the two headings that are artifacts of the page break in
whatever produced it (`# Talks (cont.)`) rather than sections of their own.

## `demeo_cv-2022.txt`

`cv/demeo_cv.pdf` in the GitLab repository is byte-identical to
`demeo_cv-2022.pdf` at that repository's root — same blob,
`1a764ced1cc3eac208f7ad1e39fdbf879edfd199` — so the PDF the Zola about page
linked to is the 2022 CV.

    demeo_cv.pdf  sha256  9e561012b499e5d49e5a36de01fb913a30c0de0a5918fded517d77e01089ca1b
    extracted     sha256  8ed62199afc2c5d0cc1c74d0fafdf53fd968048f9e7040a5a528f73cc5b38cc6

**The text, not the LaTeX.** That repository also carries `cv/demeo_cv-2021.tex`
and its `cv/aux/*.tex` includes, which are easier to parse — but they are not
what the PDF was built from. The commit that produced this PDF
(`273045d8`, 17 June 2022, *"update cv and add LOI"*) changed three PDFs and no
`.tex` at all, so the 2022 source was never committed. The 2021 LaTeX is missing
five things the PDF has: the NJIT appointment, two NJIT courses, the Sheffield
2021 summer school, and the two 2021 SUNY Buffalo certificates. Parsing it would
have silently lost all five, which is the failure this whole exercise exists to
prevent.

`pdf_text.py` produced this file, by hand, once:

    python3 import/legacy-cv/pdf_text.py demeo_cv.pdf > demeo_cv-2022.txt

It is provenance tooling and no build target runs it. It inflates the content
streams, reads the text-showing operators, and treats a large negative kern
inside a `TJ` array as an inter-word space, which is the only reason the output
has spaces in it at all. Word spacing is the only thing it reconstructs:
hyperlink targets are not in the text layer, so **every URL in this snapshot's
entries is lost**. Where an entry needed one, it came from another copy.
