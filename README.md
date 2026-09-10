# alandefreitas.github.io

Alan de Freitas's personal site, served by GitHub Pages from the `main` branch at https://alandefreitas.github.io/. Jekyll, with the layouts and includes of the 2022 "academic" theme kept in the repo and restyled. The reasoning behind the design and the content lives outside this repo, in `~/Documents/Professional/Resume/Strategy/website/README.md` (design decisions) and `Strategy/brand/criteria.md` (palette, type and layout rules every change must follow).

## Layout of the repo

| Path | What it is |
| --- | --- |
| `index.md` | Home: video cover, bio (opening paragraph, then Engineering and Academia and industry side by side with one image each), repositories, selected publications. |
| `resume.md`, `repositories.md`, `publications.md`, `contact.md` | One page each; the content comes from `_data/` and the layouts. `cv.html` is only a redirect from the old `/cv` address to `/resume`. |
| `_layouts/` | `default` (page frame), `home`, `cv` (the resume: label column and entries), `contact`, `page`, `repositories`, `publications` (grouped by year). |
| `_includes/` | `head`, `header`, `footer` (social links, click-to-play video script, external links in new tabs), `repositories`, `publications` (takes an optional `items` list), `contact`, `toc` (table of contents built from the page's headings: floating in the left margin on wide screens, one line of links under the title elsewhere; a layout wraps its content in `.toc-layout` and includes it with `root`, `levels` and optionally `inline=false`; the inline rendering keeps the deepest levels that fit in about 200 characters, one line per top-level heading when there are two; used by the resume and the publications page). |
| `_sass/main.scss` | The whole stylesheet: palette tokens as CSS custom properties (light scheme, and a dark scheme that follows the system preference), type, layout, components. Compiled through `assets/css/main.scss`. |
| `_data/` | `settings.yml` (menu, social links, contact card), `repositories.yml`, `publications.yml`, `cv/*.yml`. |
| `assets/img/` | `testimonial-cover.jpg` (video cover), `bio-engineering.jpg` and `bio-academia.jpg` (the two bio images), `qr-site.svg` (charcoal on sand, readable in both colour schemes), `email.png` (the address as an image so harvesters do not get plain text; charcoal on transparent, inverted by CSS in dark mode). |
| `local/` | Ignored scratch folder (video source, drafts); excluded from the build. |

`courses.md`, `people.md` and their layouts are theme leftovers with empty sample data and no menu entry.

## Working on the site

```
export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
bundle install
bundle exec jekyll serve --config _config.yml,_config_dev.yml
```

Then open http://127.0.0.1:4000/. Changes to `_config.yml` need a restart; everything else regenerates on save. `_config_dev.yml` is ignored by git; if missing, create it with `url: "http://localhost:4000"`, `baseurl: ""`, and the site title and description. GitHub Pages builds with its own Jekyll and ignores the Gemfile.

- Printing any page (or "Save as PDF" on the resume) uses the print rules at the end of `_sass/main.scss`: light colours, no navigation, no breaks inside entries. To check them without a browser dialog:

  ```
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=/tmp/resume.pdf http://127.0.0.1:4000/resume/
  ```

- `?theme=dark` or `?theme=light` on any URL forces a colour scheme for the browser session; `?theme=auto` clears it. There is no toggle on the page by design.
- To change the video cover frame, see the recipe in the Strategy website README.
- To regenerate the email image (Baskerville, since Garamond is not installed locally) or the QR code:

  ```
  magick -background none -fill '#232323' -font /System/Library/Fonts/Supplemental/Baskerville.ttc -pointsize 64 label:'alandefreitas@gmail.com' -trim +repage -bordercolor none -border 6 assets/img/email.png
  python3 -c "import segno; segno.make('https://alandefreitas.github.io/', error='m').save('assets/img/qr-site.svg', scale=10, border=2, dark='#232323', light='#CDC6B4', xmldecl=False, svgclass=None, lineclass=None)"
  ```

- Commit on top of the pushed history; never amend or rewrite commits that are already on GitHub. Pushing `main` publishes the site, so it is Alan's step.
