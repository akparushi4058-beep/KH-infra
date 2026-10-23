# KH Infra Equipment website

Static site for [khgroupindia.com](https://www.khgroupindia.com), deployed by Vercel on every push to `main`.

## Editing products

All products, photos, specs, search aliases and categories live in `catalog.json`. After editing it, regenerate the pages:

```bash
python3 build.py
```

This rewrites the generated sections of `index.html` and writes one page per product (`/<product-slug>/`), one page per category, `sitemap.xml`, `robots.txt` and `llms.txt`. Commit the generated files along with `catalog.json`.

## Files

- `index.html` – homepage. The header and footer between the `BUILD:HEADER` / `BUILD:FOOTER` markers are copied into every generated page.
- `styles.css` – shared styles. `app.js` – homepage catalogue, filters and product sheet.
- `img/`, `products/` – product photos.
