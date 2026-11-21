# Sound Vibration Sanctuary: website

One-page site for Sound Vibration Sanctuary, sound healing and crystal work at 212 W Superstition Blvd,
Apache Junction, AZ. It replaces her GoDaddy site (soundvibrationsanctuary.com), and the share tags and
canonical link already point at that address. (The folder keeps its old name so TOB's jobs and links still find it.)

Plain HTML, CSS and JavaScript with no build step: `index.html`, `style.css` (colours at the top as named
variables), `script.js` (menu, forms, the singing bowl tone). Fonts load from Google Fonts: Cormorant Garamond for
headings and Quicksand for the text (Quicksand is the font her current site uses). Both are SIL Open Font License.

## Where the content came from
- **Her website** (home page and `/list`, fetched 2026-11-21): the name, the address, the tagline "Discover Inner
  Peace", the "Our Story" text (used word for word), the mailing list line, and the full menu and price list with her
  descriptions: group sound meditation $20, private session (1 to 4 people) $80 plus $20 per extra guest up to 14,
  sound meditation with your dog $30, on-body Tibetan bowl vibration $100, chakra reading and balancing $100, oracle
  card reading (Kyle Gray decks) $35, and two crystal classes at $20. It also gave her credentials (Sound Healing
  Practitioner, Certified Crystal Practitioner from Hibiscus Moon Academy) and her brand lavender `#8577b8`.
- **Instagram** (instagram.com/soundvibrationsanctuary, read 2026-11-21): her bio gave the shop ("Crystals •
  Specimens • Gifts • Jewelry"), the **shop hours, Mon-Fri 11-2**, and "Sound healing & chakra balancing by
  appointment". Those are on the page (Shop section, Hours, and `openingHoursSpecification` in the schema). The rest
  of the bio was cut off ("... more") and post captions weren't readable, so nothing else came from there. It's
  linked in the header (icon), the mobile menu, the reviews note, the shop, the contact area and the footer.
- **Facebook** (facebook.com/Soundvibrationsanctuary): Facebook only let us see the page name and town, so no posts,
  photos, hours or phone number came from there. It's linked next to Instagram everywhere.
- **Photos**: all made on this PC with TOB's image generator (`python -m tob.creator.imagegen`, Z-Image Turbo).
  They are not stock and have no words in them. They are in `images/` as WebP. `og.png` is the link preview and
  `favicon.svg` / `apple-touch-icon.png` are the icons (sound ripples on deep plum).

## On the page
Header with a Book button, a hero with "Hear a singing bowl" (a soft bowl tone made in the browser, only when
clicked), a welcome quote and three pillars, sessions and prices (each "Book this" picks that session in the form),
crystal classes and upcoming events, the shop (crystals, specimens, gifts, jewelry) with its hours, what to expect, her story with her credentials, a gallery, gift cards, a reviews
area, hours and location with a map and directions, a booking form, a mailing list signup, Instagram and Facebook links, and a
footer with the TMP credit. It has LocalBusiness schema (HealthAndBeautyBusiness, with her real prices as offers),
share tags, labelled forms, a skip link, visible focus, support for reduced motion, and it is mobile-first.

## Placeholders to fill in
These are shown with a dotted lavender underline (class `ph`) so they're easy to spot and click in the builder.
They aren't on her site or Facebook, so nothing was made up:
1. **Her name** under the story ("With love, your name").
2. **Phone number** (Visit section). Once she gives it, also add `"telephone"` to the schema in `<head>`.
3. **Class days and times**: the group sound meditation and crystal class rows in Hours.
4. **Upcoming events**: three dates and times (group sound meditation, with your dog, crystal grids).
5. **Gift cards**: the amounts and how to buy them.
6. **Reviews**: three quotes and guest names (real ones from Facebook or clients, with their OK).
7. **Email for the forms**: the booking and mailing list forms send nothing yet. Put her email in `data-email=""` on
   `<form id="book-form">` and `<form id="news-form">` and they'll open an email to her with everything filled in.
   Until then they thank the visitor and point them to Facebook. A form service (like Formspree) or her mailing list
   tool can replace this later.
8. **Photos of the real space**: the generated photos stand in until she has her own. Use Swap picture in the
   builder.

Also to confirm with her: the shop hours (Mon to Fri, 11 am to 2 pm, from her Instagram bio) are still right,
whether she'd like the shop to list products or prices, and whether she wants her name shown.

## Editing it live in TOB's website builder
Open TOB › Create › Website builder. The site is listed as "Sound Vibration Sanctuary" (folder
`C:\Dev\crystalscrosses-redesign`). Click any words to change them, use Swap picture or Create one on any photo, and
change colours in Design (Lavender, Violet, Plum, Sand and the others are the named site colours). The builder saves
into these same files (its own styles go in `builder.css`). Nothing goes online until Publish is clicked.

## Tests
`tests/test_site.py`: the rebrand is complete, her real facts and prices are on the page, unknowns are placeholders,
the schema is valid, every picture is there with alt text and a size, and the page opens and saves cleanly in the
website builder. Run it with TOB's Python:

    C:\Users\ayala\Projects\TOB-OS\.venv\Scripts\python.exe -m pytest tests -q
