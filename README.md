# Sound Vibration Sanctuary: website

One-page site for Sound Vibration Sanctuary, sound healing and crystal work at 212 W Superstition Blvd,
Suite 103, Apache Junction, AZ. It replaces her GoDaddy site (soundvibrationsanctuary.com), and the share tags and
canonical link already point at that address. (The folder keeps its old name so TOB's jobs and links still find it.)

Plain HTML, CSS and JavaScript with no build step: `index.html`, `style.css` (colours at the top as named
variables), `script.js` (menu, forms, the singing bowl tone), `booking.js` (the RSVP calendar) and
`data/schedule.json` (the dates, times, prices and spots the calendar shows) and `data/config.json` (where RSVPs and
messages are sent). Fonts load from Google Fonts: Cormorant Garamond for
headings and Quicksand for the text (Quicksand is the font her current site uses). Both are SIL Open Font License.

## Where the content came from
- **Her website** (home page and `/list`, fetched 2026-11-21): the name, the address, the tagline "Discover Inner
  Peace", the "Our Story" text (used word for word), the mailing list line, and the full menu and price list with her
  descriptions: group sound meditation $20, private session (1 to 4 people) $80 plus $20 per extra guest (her site said fourteen;
  she has since lowered every group to **10**),
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
- **Her own photos and notes** (`OneDrive\Pictures\SVS`, 2026-11-23; the originals are untouched, copies were
  resized to 1600px at most and saved as WebP):
  - `logo.jpg`, her tree-of-life logo: `images/logo.png` (header and footer), `favicon-32.png`, `favicon-192.png`,
    `apple-touch-icon.png`.
  - The seven stones named by file (Aquamarine, Celestite, Fluorite, Garnet, Herkimer Diamonds, Quartz crystals,
    Rhodochrosite): `images/crystals/`, shown in the "Crystals in the shop" section.
  - IMG_3255 to IMG_3492 and IMG_3521/3522: the sound room, the treatment room, the crystal layout table, her with
    the bowls and gongs, and the shop shelves (`images/shop-shelves-1..5.webp`, `treatment-room.webp` and the others).
    `og.jpg` (the link preview) is cut from the sound room photo. IMG_3486 is her Spiritual Wellness 101 Series
    poster (Wednesdays 6:30 to 8 pm, Nov 4 to Dec 30): shown as a picture, and its remaining dates are listed.
  - IMG_3539 (her December schedule) and IMG_3547 (her flyer "December Sound Meditation: An hour with singing bowls
    and gongs"): Group Sound Meditation on Fridays Dec 4, 11 and 18, 6 to 7 pm, $20, no dogs; Group Sound
    Meditation with Your Dog on Sundays Dec 6 and 13, 12:30 to 1:30 pm, $30 per person, 8 people and 4 dogs max;
    "212 W Superstition Blvd, #103" and "Text 480-265-6136 to RSVP". These are in `data/schedule.json` and on the page.
  - From the owner via Adrian: groups are 10 people at most; dogs come free, one dog of any size or two dogs that
    weigh 30 lb or less together; no online payment, guests pay in person and no-shows are fine; 480-265-6136 is the
    crystal shop's phone and texting is preferred; Past Life Regressions are coming soon, done the certified QHHT
    (Quantum Healing Hypnosis Technique) way. The owner and practitioner is **Linda Huss** (her name is in the
    signature, the about section, the photo descriptions and the schema's `founder`; the fliers themselves don't
    print it).
  - `Flier.jpg`, her "Wellness Rates & Offerings" flier (updated January 2026), used as the reference for the
    sessions: the same prices; her wording for each service; "Dogs must be leashed and non-reactive"; "Proceeds are
    donated to local animal rescues"; crystal classes $20 per person; "Facilitated by a Certified Crystal
    Practitioner and Sound Healing Practitioner by Appointment and Scheduled Classes"; "Rates subject to change"; and
    her note that the services "are not a substitute for medical or mental health care" (under the sessions and in
    the footer). Its dotted price leaders are echoed on the session cards and classes. It still lists private groups
    of fourteen; the owner has since made every group 10, so the site says 10.
- **Made on this PC**: the dog and oracle card photos are still stand-ins from TOB's image generator (she had no
  photos of those yet). Swap them in the builder when she has her own.

## On the page
Header with her logo and an RSVP button, a hero with "Hear a singing bowl" (a soft bowl tone made in the browser, only when
clicked), a welcome quote and three pillars, sessions and prices (each "Book this" picks that session in the form),
a "coming soon" note for Past Life Regression (QHHT), the December calendar and RSVP form, crystal classes and
the Spiritual Wellness 101 dates, the crystals in the shop, the shop (crystals, specimens, gifts, jewelry) with its hours, what to expect, her story with her credentials, a gallery, gift cards, a reviews
area, hours, phone and location with a map and directions, a message form, a mailing list signup, Instagram and Facebook links, and a
footer with the TMP credit. It has LocalBusiness schema (HealthAndBeautyBusiness, with her real prices as offers),
share tags, labelled forms, a skip link, visible focus, support for reduced motion, and it is mobile-first.

## The RSVP calendar (December sound meditations)
Visitors see the month, the sessions on each day, and the spots left out of the capacity (and the dog spots on
Sundays). They pick a session and RSVP with their name, email, phone, number of people, dogs (none, 1 or 2, with
weights) and notes. The form checks the group size, the spots left and the dog rule before sending. Nothing is paid
online: the form shows the total to pay in person.

**The dates are in `data/schedule.json`.** Edit it in Notepad or on GitHub and the site updates after the push:
- one line per session: `date`, `start`/`end` (24-hour Arizona time), `title`, `price` per person, `capacity`,
  `booked`, and for dog sessions `dogs: true`, `dogCapacity` and `dogsBooked`;
- as RSVPs come in, raise `booked` (and `dogsBooked`) so the site shows the right number of spots left. A static
  site can't count them by itself. Setting `booked` to `capacity` closes a session; past sessions hide themselves;

**Where RSVPs go is set in one place: `data/config.json`** (both values are empty until Adrian has them; never put
a made-up address there):
- `rsvpEmail`: Linda's email address. The RSVP form opens the visitor's email app addressed to her with the RSVP
  filled in (mailto). The "Get in touch" and mailing list forms use it too (a `data-email` on those forms, as
  before, still takes priority);
- `rsvpFormKey` (optional): a free **Web3Forms access key** (web3forms.com: enter her email, the key arrives by
  email) or a **Formspree form link** (`https://formspree.io/f/...`). RSVPs then go straight to her inbox, and
  `rsvpEmail` is the backup if the service doesn't answer;
- with neither set (as now), the RSVP form still works: it offers a ready-made text message to 480-265-6136 with
  everything filled in, matching her flyer ("Text 480-265-6136 to RSVP"). The other forms ask visitors to text.

## Placeholders to fill in
These are shown with a dotted lavender underline (class `ph`) so they're easy to spot and click in the builder.
They aren't on her site or Facebook, so nothing was made up:
1. **Gift cards**: the amounts and how to buy them.
2. **Reviews**: three quotes and guest names (real ones from Facebook or clients, with their OK).
3. **Her email / form key** in `data/config.json` (see above). Until then the forms point visitors to her phone.
4. **Prices of the Spiritual Wellness 101 classes** and the days of the two $20 crystal classes: not on her poster
   or price list, so they aren't on the page.

Also to confirm with her: the shop hours (Mon to Fri, 11 am to 2 pm, from her Instagram bio) are still right,
and whether she'd like the shop to list products or prices.

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
