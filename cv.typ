#let data = yaml("main.yml")
#let pubs = yaml("publications.yml")

// --- Page setup ---

#set page(
  paper: "us-letter",
  margin: (x: 0.5in, y: 0.5in),
  footer: context {
    set text(size: 8pt, fill: luma(128), style: "italic")
    let total = counter(page).final().first()
    align(center)[
      #if total > 1 [Page #counter(page).display() of #total. ]
      Compiled #datetime.today().display("[month repr:long] [day], [year]").
    ]
  },
)

#set text(size: 10.5pt)
#set par(justify: false, leading: 0.45em)
#set list(marker: box(width: 0.45em, height: 0.45em, fill: black))

// --- Show rules ---

// Bold the CV author's name wherever it appears (e.g. in publication author lists)
#show "Alistair Pattison": strong

#show heading.where(level: 1): it => {
  v(0.8em, weak: true)
  block(text(size: 13pt, weight: "regular", smallcaps(it.body)))
  v(0.35em, weak: true)
}

// --- Helper functions ---

#let fmt-authors(authors) = {
  if type(authors) == str { return authors }
  let n = authors.len()
  if n == 0 { return "" }
  if n == 1 { return authors.at(0) }
  if n == 2 { return authors.at(0) + " and " + authors.at(1) }
  authors.slice(0, n - 1).join(", ") + ", and " + authors.at(n - 1)
}

#let render-pub(pub) = {
  let author-str = fmt-authors(pub.at("author", default: ""))
  let title = pub.at("title", default: "")
  let note = pub.at("note", default: "")
  let date = pub.at("date", default: "")
  let url = pub.at("url", default: "")

  [#author-str. ]
  emph(title)
  if note != "" { [. #note] }
  if date != "" { [ (#date)] }
  if url != "" { [. #link(url)[(link)]] }
  [.]
}

#let render-item(item) = {
  let title = item.at("title", default: "")
  let subtitle = item.at("subtitle", default: "")
  let dates-raw = item.at("dates", default: "")
  let dates = if type(dates-raw) == int { str(dates-raw) } else { dates-raw }
  let advisor = item.at("with", default: "")
  let details = item.at("details", default: "")
  let bullets = item.at("bullets", default: ())
  let citation = item.at("citation", default: "")

  if citation != "" {
    render-pub(pubs.at(citation))
    return
  }

  // Build left-column content: title, subtitle, details, advisor
  let left-col = {
    if title != "" { strong(title) }
    if subtitle != "" {
      [, ]
      eval(subtitle, mode: "markup")
    }
    if details != "" {
      [ --- ]
      details
    }
    if advisor != "" {
      linebreak()
      h(1em)
      emph([with #advisor])
    }
  }

  // Lay out title row with right-aligned dates
  if dates != "" {
    grid(
      columns: (1fr, auto),
      align: (left + top, right + top),
      column-gutter: 0.5em,
      left-col, emph(dates),
    )
  } else if title != "" or details != "" {
    left-col
  }

  if bullets.len() > 0 {
    list(..bullets.map(b => [#b]))
  }
}

#let render-section(section) = {
  heading(level: 1, section.title)

  for item in section.at("items", default: ()) {
    v(0.6em, weak: true)
    pad(left: 1em, render-item(item))
  }
}

#let render-header(about) = {
  let contact = ()

  if about.at("email", default: "") != "" {
    contact.push(about.email)
  }
  if about.at("phone", default: "") != "" {
    contact.push(about.phone)
  }
  if about.at("website", default: "") != "" {
    contact.push(link("https://" + about.website, about.website)
  }

  align(center)[
    #text(size: 20pt, smallcaps(strong(about.name)))
    #if contact.len() > 0 {
      v(0.25em, weak: true)
      emph(contact.join([ #h(1em) | #h(1em) ]))
    }
  ]
}

// --- Main body ---

#render-header(data.about)

#for section in data.sections {
  render-section(section)
}
