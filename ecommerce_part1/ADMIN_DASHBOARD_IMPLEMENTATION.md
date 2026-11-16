# Admin Dashboard and CSS Generator — Implementation Guide

This guide extends the existing FORMA e-commerce website without replacing its Python/FastAPI backend or SQLite product database.

## Deliverables

### A. User analytics
- A development-only simulation endpoint that creates events using a fixed set of test IPs.
- A local IP-to-country fixture mapping for deterministic demonstrations.
- SQLite storage for IP, country, route, timestamp, user agent, and simulation flag.
- Admin APIs for summary, country counts, and recent events.
- An admin dashboard showing KPI cards, country table, and recent activity.

### B. CSS generator
- Controls for colours, font, font size, content width, page padding, section spacing, card gap, card radius, and button radius.
- Live preview.
- Generated CSS text preview.
- Reset to FORMA defaults.
- Download as `forma-custom-theme.css`.

## Important technical decisions

1. **Simulated IPs are application data, not spoofed network traffic.** Use the documentation-only IP ranges `192.0.2.0/24`, `198.51.100.0/24`, and `203.0.113.0/24`. Assign countries in a local fixture dictionary and mark records as simulated. Never imply those reserved addresses were actually geolocated.
2. **Real visitor GeoIP is a separate optional enhancement.** If added, use a maintained GeoIP database and return `Unknown` when lookup fails. Do not trust arbitrary `X-Forwarded-For` values.
3. **Protect admin routes.** Hiding an admin URL is not authentication. Use an environment-configured admin secret for a local demo and real authentication/authorization for deployment.
4. **Do not store secrets in JavaScript or commit them.**
5. **Treat IP addresses as potentially personal data.** Limit access and retention; consider masking or hashing in a real deployment.
6. **CSS generation must be allowlisted.** Generate a known set of CSS variables from validated colour, numeric, and font inputs. Do not inject arbitrary CSS text.

## Work order

1. Back up the current FORMA project and commit the baseline.
2. Add the analytics table and indexes to `sql/schema.sql`.
3. Implement fixture country mapping in `app/analytics.py`.
4. Add validated admin endpoints in `app/admin_routes.py`.
5. Test endpoints using FastAPI `/docs`.
6. Build `app/static/admin/index.html`, `admin.css`, and `analytics.js`.
7. Refactor selected storefront styles to CSS custom properties.
8. Build `css-generator.html`, `css-generator.css`, and `css-generator.js`.
9. Implement live preview, reset, validation, and CSS Blob download.
10. Run analytics tests, CSS generator tests, and existing storefront regression tests.
11. Update README and add screenshots.

See the root `README.md` for detailed SQL, endpoint, folder, testing, and run instructions.
