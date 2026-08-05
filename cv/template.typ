// The CV's layout, for the PDF.  See ADR-010.
//
// Written by hand; the two files beside it are generated.  cv.typ carries the
// CV as data and publications.typ the publication list, and neither carries a
// word about how a page looks -- so the page and the PDF cannot disagree about
// what the CV says, and this is the only place that decides how the paper one
// reads.
//
// It takes no font from the system: Libertinus Serif and New Computer Modern
// are compiled into the Typst binary, and `--ignore-system-fonts` at the
// compile makes that a guarantee rather than a hope.  That is what lets
// `gen_cv.py --check --pdf` recompile and compare bytes -- a template that
// resolved a font by name would produce a different file on a machine with a
// different font installed, and the check would fail for a reason that has
// nothing to do with the CV.
//
// A run is `(text, emphasis)` with an optional third element, the link target:
// emphasis is "strong", "em" or none.  Both generators emit them and `rich` is
// the only thing that renders one.

#let accent = rgb("#1f3864")
#let rule-colour = rgb("#c9ccd4")
#let muted = rgb("#4a4f5a")

// A link is underlined rather than only coloured: this document gets printed,
// and colour alone does not survive a monochrome printer -- the same reason
// the site's own link styling gives (ADR-005).  The offset and the thin stroke
// are because a CV is a page of institutions, and every one of them is a link.
//
// The pieces are pulled out by index rather than destructured.  `let (text,
// ..) = run` binds over the builtin `text` for the rest of the block, and the
// error that follows -- "expected function, found string" -- names neither the
// shadowing nor the line that wanted the builtin.
#let rich(runs) = {
  for run in runs {
    // Two generators emit runs.  gen_cv.py's carry a link target and
    // gen_publications.py's do not, because nothing in a citation links from
    // the middle of a line -- so the third element is optional rather than the
    // two files being made to agree about a field neither of them needs.
    let body = run.at(0)
    let emphasis = run.at(1, default: none)
    let url = run.at(2, default: none)
    if emphasis == "strong" { body = strong(body) }
    if emphasis == "em" { body = emph(body) }
    if url == none { body } else { link(url, text(fill: accent, underline(offset: 1.6pt, stroke: 0.4pt, body))) }
  }
}

// `sticky` keeps the heading with the block after it.  Without it, REFERENCES
// set alone at the foot of page 5 with its seven names on page 6 -- which is
// the sort of thing that only shows up by looking at the compiled document.
#let section-heading(title) = {
  block(above: 1.15em, below: 0.55em, breakable: false, sticky: true, {
    text(size: 9.5pt, weight: "semibold", tracking: 0.09em, upper(title))
    v(-0.55em)
    line(length: 100%, stroke: 0.5pt + rule-colour)
  })
}

// The date gutter.  `grid` rather than `table` so there is no cell padding to
// fight, and `breakable: false` so a two-line entry never leaves its date
// stranded at the foot of a page.
#let dated-entry(term, body) = block(breakable: false, below: 0.5em, grid(
  columns: (4.2em, 1fr),
  gutter: 0.9em,
  align(right, text(size: 9pt, fill: muted, term)),
  body,
))

// The bullet is set at the body size, not smaller.  Grid rows align on the top
// of the cell rather than on a shared baseline, so a 7pt bullet beside 10.5pt
// text sits visibly above the line it belongs to.
#let bullet-entry(body) = block(breakable: false, below: 0.45em, grid(
  columns: (0.7em, 1fr),
  column-gutter: 0.4em,
  align(right, text(fill: muted, sym.bullet)),
  body,
))

#let entry-body(entry) = {
  if "head" in entry { rich(entry.head) }
  for line in entry.at("body", default: ()) {
    linebreak()
    text(size: 9.5pt, fill: muted, rich(line))
  }
}

#let publication-entry(index, pub) = block(breakable: false, below: 0.5em, grid(
  columns: (1.6em, 1fr),
  column-gutter: 0.55em,
  align(right, text(size: 9pt, fill: muted, [#index.])),
  {
    strong(pub.title)
    if pub.editor { [ ]; emph("(editor)") }
    linebreak()
    text(size: 9.5pt, fill: muted, rich(pub.byline))
    linebreak()
    text(size: 9.5pt, fill: muted, rich(pub.imprint))
    if pub.links.len() > 0 {
      linebreak()
      text(size: 9.5pt, {
        for (i, entry) in pub.links.enumerate() {
          if i > 0 { text(fill: muted)[ · ] }
          link(entry.at(1), text(fill: accent, underline(offset: 1.6pt, stroke: 0.4pt, entry.at(0))))
        }
      })
    }
  },
))

#let render-sections(sections) = {
  for section in sections {
    section-heading(section.title)

    if section.kind == "timeline" {
      for entry in section.entries {
        dated-entry(entry.at("term", default: ""), entry-body(entry))
      }
    } else if section.kind == "publications" {
      for (i, pub) in section.publications.enumerate() {
        publication-entry(i + 1, pub)
      }
    } else if section.kind == "prose" {
      for entry in section.entries {
        for line in entry.at("body", default: ()) {
          block(below: 0.5em, rich(line))
        }
      }
    } else if section.kind == "groups" {
      for entry in section.entries {
        block(breakable: false, below: 0.35em, above: 0.7em, rich(entry.head))
        for item in entry.at("items", default: ()) {
          bullet-entry(rich(item.head))
        }
      }
    } else {
      // "list" and "talks": the same shape, and the difference between them is
      // the site's, not the page's.
      for entry in section.entries {
        bullet-entry(entry-body(entry))
        for item in entry.at("items", default: ()) {
          pad(left: 1.6em, bullet-entry(text(size: 9.5pt, fill: muted, rich(item.head))))
        }
      }
    }

    if "note" in section {
      block(above: 0.6em, below: 0.4em, text(size: 9pt, fill: muted, rich(section.note)))
    }
  }
}

#let cv-document(name: "", title: "", email: "", url: "", built: none, body) = {
  set document(title: name + " " + title, author: name, date: built)

  set page(
    paper: "us-letter",
    margin: (x: 0.95in, y: 0.85in),
    footer: context {
      set text(size: 8pt, fill: muted)
      grid(
        columns: (1fr, auto, 1fr),
        align(left, link(url, url.replace("https://", ""))),
        align(center, [Generated #built.display("[day padding:none] [month repr:long] [year]")]),
        align(right, [Page #counter(page).display() of #counter(page).final().first()]),
      )
    },
  )

  set text(font: "Libertinus Serif", size: 10.5pt, lang: "en", hyphenate: true)
  set par(justify: true, leading: 0.55em, spacing: 0.55em)
  show link: it => it

  // The title block.  Once, at the top, not repeated per page: the running
  // footer already says whose CV this is.
  block(below: 0.4em, text(size: 20pt, weight: "semibold", tracking: 0.02em, name))
  block(below: 0.9em, text(size: 9.5pt, fill: muted, {
    link("mailto:" + email, text(fill: accent, underline(offset: 1.6pt, stroke: 0.4pt, email)))
    [ · ]
    link(url, text(fill: accent, underline(offset: 1.6pt, stroke: 0.4pt, url.replace("https://", ""))))
  }))

  body
}
