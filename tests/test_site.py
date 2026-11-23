"""Checks for the Sound Vibration Sanctuary site: the rebrand is complete, the facts match her own site, her flyer and
schedule, nothing is invented, every picture is there, the RSVP calendar's rules hold (group size, dogs, no online
payment), and the page opens and saves cleanly in TOB's website builder.

Run with TOB's Python (the builder checks need ``tob.sitebuilder``; they're skipped without it):

    C:\\Users\\ayala\\Projects\\TOB-OS\\.venv\\Scripts\\python.exe -m pytest tests -q
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1]
TOB = Path(r"C:\Users\ayala\Projects\TOB-OS")
PAGE = (SITE / "index.html").read_text(encoding="utf-8")
SCHEDULE = json.loads((SITE / "data" / "schedule.json").read_text(encoding="utf-8"))
CONFIG = json.loads((SITE / "data" / "config.json").read_text(encoding="utf-8"))   # where RSVPs go (Adrian fills it)
PHONE = "480-265-6136"   # her crystal shop's number, from her December flyer ("Text 480-265-6136 to RSVP")
FACEBOOK = "https://www.facebook.com/Soundvibrationsanctuary/"
INSTAGRAM = "https://www.instagram.com/soundvibrationsanctuary/"


class Tags(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict]] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def tags(name: str) -> list[dict]:
    p = Tags()
    p.feed(PAGE)
    return [a for t, a in p.tags if t == name]


def test_no_trace_of_the_old_store_is_left():
    old = ["Crystals & Crosses", "Crystals &amp; Crosses", "CrystalClearChoices", "crystalsandcrosses",
           "185 N Apache Trail", "320 W Superstition", "Marcellus", "Figtree", "#24152f",
           "tmpbizz.com/demo/crystalscrosses"]
    for f in ["index.html", "style.css", "script.js", "booking.js", "README.md"]:
        text = (SITE / f).read_text(encoding="utf-8")
        found = [w for w in old if w.lower() in text.lower()]
        assert not found, f"{f} still mentions {found}"


def test_her_real_details_are_on_the_page():
    assert "<title>Sound Vibration Sanctuary" in PAGE
    assert "Discover Inner Peace" in PAGE
    assert "212 W Superstition Blvd, Suite 103" in PAGE and "Apache Junction, AZ" in PAGE
    assert PHONE in PAGE and 'href="sms:+14802656136"' in PAGE and "texting is best" in PAGE
    assert "a peaceful environment where sound and vibration support relaxation, clarity, and well-being" in PAGE.lower()
    assert "Hibiscus Moon Academy" in PAGE
    assert PAGE.count(FACEBOOK) >= 2
    # her Instagram: linked in the header, the social area and the footer; its bio gives the shop and its hours
    assert PAGE.count(INSTAGRAM) >= 4
    assert re.search(r'class="nav-social".{0,400}' + re.escape(INSTAGRAM), PAGE, re.S)
    assert re.search(r'<footer.*' + re.escape(INSTAGRAM), PAGE, re.S)
    assert "Crystals, specimens, gifts &amp; jewelry" in PAGE and "Mon to Fri, 11 am to 2 pm" in PAGE
    # her own price list (soundvibrationsanctuary.com/list), nothing made up
    for name, price in [("Group sound meditation", "$20"), ("Private sound healing", "$80"),
                        ("Sound meditation with your dog", "$30"), ("On-body Tibetan bowl vibration", "$100"),
                        ("Chakra reading &amp; balancing", "$100"), ("Oracle card reading", "$35"),
                        ("Connecting with your crystal(s)", "$20"), ("Setting intentions with crystal grids", "$20")]:
        m = re.search(re.escape(name) + r".{0,120}?" + re.escape(price), PAGE, re.S)
        assert m, f"{name} should be listed at {price}"


def test_unknown_details_are_marked_placeholders_not_invented():
    assert len(re.findall(r'class="ph"', PAGE)) >= 5   # her name, gift cards, three reviews
    phones = set(re.findall(r"\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b", PAGE))
    assert phones == {PHONE}, f"only her own number: {phones}"
    # her email isn't known yet: one clearly marked, empty setting, and no address anywhere in the data
    assert CONFIG["rsvpEmail"] == "" and CONFIG["rsvpFormKey"] == "", "her email / form key are Adrian's to fill in"
    assert "email" not in SCHEDULE and "form" not in SCHEDULE, "only one place says where RSVPs go"
    for f in ["data/config.json", "data/schedule.json", "booking.js", "script.js"]:
        assert not re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", (SITE / f).read_text(encoding="utf-8")), f"no address in {f}"
    assert not re.search(r"[\w.+-]+@[\w-]+\.\w+", PAGE), "no email address until she gives one"
    readme = (SITE / "README.md").read_text(encoding="utf-8")
    assert "## Placeholders to fill in" in readme


def test_local_business_schema_is_valid_and_honest():
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', PAGE, re.S)
    data = json.loads(m.group(1))
    assert data["@type"] == "HealthAndBeautyBusiness" and data["name"] == "Sound Vibration Sanctuary"
    assert data["address"]["streetAddress"] == "212 W Superstition Blvd, Suite 103"
    assert data["telephone"] == "+1-480-265-6136"
    assert data["address"]["addressLocality"] == "Apache Junction" and data["address"]["addressRegion"] == "AZ"
    assert FACEBOOK in data["sameAs"] and INSTAGRAM in data["sameAs"]
    hours = data["openingHoursSpecification"][0]
    assert hours["dayOfWeek"] == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    assert (hours["opens"], hours["closes"]) == ("11:00", "14:00")
    assert "aggregateRating" not in data and "review" not in data
    assert "up to 10 participants" in json.dumps(data)
    assert len(data["hasOfferCatalog"]["itemListElement"]) == 8


def test_every_picture_is_there_with_alt_text_and_a_size():
    imgs = tags("img")
    assert len(imgs) >= 14
    for a in imgs:
        src = a["src"]
        assert (SITE / src).is_file(), f"missing {src}"
        assert a.get("alt"), f"{src} needs alt text"
        assert a.get("width") and a.get("height"), f"{src} needs width and height"
        assert "srcset" not in a, "srcset would stop the builder's Swap picture from showing"
    for f in ["favicon-32.png", "favicon-192.png", "apple-touch-icon.png", "og.jpg", "images/logo.png", "style.css",
              "script.js", "booking.js"]:
        assert (SITE / f).is_file()
    for ref in re.findall(r'(?:href|content)="(?:https://soundvibrationsanctuary\.com/)?([\w/-]+\.(?:png|jpg|webp|svg))"', PAGE):
        assert (SITE / ref).is_file(), f"missing {ref}"


def test_her_photos_are_used():
    imgs = tags("img")
    srcs = {a["src"] for a in imgs}
    # the logo in the header and the footer
    assert sum(1 for a in imgs if a["src"] == "images/logo.png") == 2
    # the crystals section: every stone she named, with its name shown
    for stone in ["Aquamarine", "Celestite", "Fluorite", "Garnet", "Herkimer Diamonds", "Quartz crystals", "Rhodochrosite"]:
        slug = stone.lower().replace(" ", "-")
        assert f"images/crystals/{slug}.webp" in srcs and f"<figcaption>{stone}</figcaption>" in PAGE
    # the shop shelves, the treatment room and the sound room
    for f in ["shop-shelves-1", "shop-shelves-2", "shop-shelves-3", "shop-shelves-4", "shop-shelves-5", "treatment-room",
              "crystal-layout-table", "sound-bath-room", "sound-room-bowls-gongs", "practitioner-gongs"]:
        assert f"images/{f}.webp" in srcs, f
    for a in imgs:
        assert max(int(a["width"]), int(a["height"])) <= 1600, f"{a['src']} should be 1600px or less"


# ------------------------------------------------------------------------------------- her December schedule & RSVPs
def test_december_schedule_matches_her_flyer():
    got = [(s["date"], s["start"], s["end"], s["price"], s["capacity"], s["dogs"], s.get("dogCapacity"))
           for s in SCHEDULE["sessions"]]
    assert got == [
        ("2026-12-04", "18:00", "19:00", 20, 10, False, None),
        ("2026-12-06", "12:30", "13:30", 30, 8, True, 4),
        ("2026-12-11", "18:00", "19:00", 20, 10, False, None),
        ("2026-12-13", "12:30", "13:30", 30, 8, True, 4),
        ("2026-12-18", "18:00", "19:00", 20, 10, False, None),
    ]
    assert SCHEDULE["phone"] == PHONE
    assert len({s["id"] for s in SCHEDULE["sessions"]}) == len(SCHEDULE["sessions"])
    assert "December Sound Meditation" in PAGE and "An hour with singing bowls and gongs" in PAGE
    assert "8 people &amp; 4 dogs max" in PAGE


def test_group_size_is_ten_everywhere():
    for f in ["index.html", "README.md", "booking.js", "data/schedule.json"]:
        text = (SITE / f).read_text(encoding="utf-8")
        assert not re.search(r"(up to|max(imum)?|most)\s+14\b|\b14 (guests|people|participants)", text, re.I), f
    assert "Up to 10 guests" in PAGE and "+$20 per additional person, up to 10" in PAGE
    assert all(s["capacity"] <= 10 for s in SCHEDULE["sessions"])


def test_rsvp_form_takes_no_payment_and_states_the_rules():
    form = re.search(r'<form class="form" id="rsvp-form".*?</form>', PAGE, re.S).group(0)
    for name in ["slot", "name", "email", "phone", "people", "dogs", "dog1", "dog2", "notes"]:
        assert f'name="{name}"' in form, name
    assert not re.search(r"cc-|card number|cvv|cvc|expir|stripe|paypal", PAGE, re.I), "no online payment"
    assert "pay in person" in PAGE.lower() and "Nothing is charged online" in PAGE
    assert "One dog of any size, or two dogs that weigh 30 lb or less together" in PAGE
    assert "Past Life Regression" in PAGE and "Coming soon" in PAGE
    assert "QHHT, the Quantum Healing Hypnosis Technique developed by Dolores Cannon" in PAGE
    assert "Linda practises it the proper, certified QHHT way" in PAGE
    # what visitors read: no claim that Dolores Cannon taught her personally, and no medical claims or promises
    shown = re.sub(r"<!--.*?-->", "", PAGE, flags=re.S)
    assert not re.search(r"(trained|taught|studied) (directly |personally )?(by|with|under) Dolores", shown, re.I)
    soon = re.search(r'<div class="soon">.*?</div>\s*<a', PAGE, re.S).group(0)
    assert not re.search(r"\b(cure|treat|diagnos|guarantee)", re.sub(r"<!--.*?-->", "", soon, flags=re.S), re.I)
    assert "<!-- ADRIAN: please confirm with Linda how she trained in QHHT" in soon   # the note for Adrian
    assert PAGE.index('src="script.js"') < PAGE.index('src="booking.js"')


NODE = shutil.which("node")


def booking(js: str):
    """Runs an expression against booking.js (its rules are plain functions) and returns the result."""
    if not NODE:
        pytest.skip("Node.js isn't on this PC")
    src = (SITE / "booking.js").as_posix()
    out = subprocess.run([NODE, "-e", f"const B = require({json.dumps(src)}); console.log(JSON.stringify({js}));"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_the_dog_rule():
    assert booking("B.dogRule(0, [])") == ""
    assert booking("B.dogRule(1, ['85'])") == "", "one dog of any weight"
    assert booking("B.dogRule(1, [])") == ""
    assert booking("B.dogRule(2, ['12', '18'])") == "", "two dogs at 30 lb together are fine"
    assert "30 lb" in booking("B.dogRule(2, ['12', '18.5'])")
    assert "weights" in booking("B.dogRule(2, ['12', ''])")
    assert booking("B.dogRule(3, ['5', '5'])")


def test_an_rsvp_is_checked_against_the_session():
    sunday = json.dumps(SCHEDULE["sessions"][1])
    friday = json.dumps(SCHEDULE["sessions"][0])
    now = "Date.UTC(2026, 10, 23)"
    ok = "{name: 'Ann', email: 'ann@example.com', phone: '480 555 0100', people: 2, dogs: 0, now: %s}" % now

    def fields(s, r):
        return [e["field"] for e in booking(f"B.check({s}, {r})")]

    assert fields(sunday, ok) == []
    assert fields(sunday, ok.replace("dogs: 0", "dogs: 2, dogWeights: ['10', '15']")) == []
    assert fields(sunday, ok.replace("dogs: 0", "dogs: 2, dogWeights: ['20', '15']")) == ["dogs"]
    assert fields(sunday, ok.replace("dogs: 0", "dogs: 1, dogWeights: ['90']")) == [], "one dog of any size"
    assert fields(friday, ok.replace("dogs: 0", "dogs: 1")) == ["dogs"], "Fridays are people only"
    assert fields(sunday, ok.replace("people: 2", "people: 9")) == ["people"], "Sundays: 8 people max"
    assert fields(friday, ok.replace("people: 2", "people: 11")) == ["people"], "10 people max"
    assert fields(friday, ok.replace("people: 2", "people: 10")) == []
    nearly = json.dumps({**SCHEDULE["sessions"][1], "booked": 7, "dogsBooked": 3})
    assert fields(nearly, ok.replace("people: 2", "people: 1").replace("dogs: 0", "dogs: 2, dogWeights: ['5', '5']")) == ["dogs"]
    assert fields(nearly, ok) == ["people"], "only 1 of 8 spots left"
    full = json.dumps({**SCHEDULE["sessions"][0], "booked": 10})
    assert fields(full, ok.replace("people: 2", "people: 1")) == ["slot"]
    assert fields(friday, ok.replace(now, "Date.UTC(2026, 11, 31)")) == ["slot"], "past sessions can't be booked"
    assert set(fields(friday, "{name: '', email: 'x', phone: '12', people: 1, dogs: 0, now: %s}" % now)) == {
        "name", "email", "phone"}
    assert booking("B.spotsLeft({capacity: 10, booked: 3})") == 7
    assert booking(f"B.total({sunday}, 3)") == 90


def test_rsvps_go_to_a_free_form_service_or_fall_back_to_a_text():
    assert booking("B.endpoint('')") is None
    assert booking("B.endpoint('abcd-1234')") == {"url": "https://api.web3forms.com/submit", "key": "abcd-1234"}
    assert booking("B.endpoint('https://formspree.io/f/xyz')") == {"url": "https://formspree.io/f/xyz", "key": None}
    assert booking("B.smsLink('480-265-6136', 'Hi there')") == "sms:+14802656136?&body=Hi%20there"


def test_rsvp_destination_comes_from_the_one_config_setting():
    assert booking("B.settings({}, {})") == {"email": "", "form": ""}
    assert booking("B.settings({}, {rsvpEmail: ' her@example.com '})") == {"email": "her@example.com", "form": ""}
    assert booking("B.settings({}, {rsvpFormKey: 'abc-123'})") == {"email": "", "form": "abc-123"}
    assert booking("B.settings({email: 'old@example.com', form: 'k'}, {rsvpEmail: '', rsvpFormKey: ''})") == {
        "email": "old@example.com", "form": "k"}, "an older schedule.json with email/form still works"
    assert booking("B.settings({email: 'old@example.com'}, {rsvpEmail: 'new@example.com'})")["email"] == "new@example.com"
    assert booking("B.settings({}, {rsvpEmail: 'PUT HER EMAIL HERE'})")["email"] == "", "a note is not an address"


def test_her_wellness_rates_flier():
    """Her flier "Wellness Rates & Offerings" (updated January 2026): services, prices, wording, rules, care note."""
    for name, price in [("Group sound meditation", "$20"), ("Private sound healing", "$80"),
                        ("Sound meditation with your dog", "$30"), ("On-body Tibetan bowl vibration", "$100"),
                        ("Chakra reading &amp; balancing", "$100"), ("Oracle card reading", "$35")]:
        assert re.search(re.escape(name) + r".{0,120}?" + re.escape(price), PAGE, re.S), name
    for words in ["tailored to your intentions", "Dogs must be leashed and non-reactive",
                  "Proceeds are donated to local animal rescues", "a sense of energetic alignment and inner harmony",
                  "Insightful oracle card readings offering guidance, reflection, and intuitive clarity",
                  "exploring crystal properties, energetic awareness, and intention setting. $20 per person",
                  "Rates subject to change", "not a substitute for medical or mental health care",
                  "Certified Crystal Practitioner and Sound Healing Practitioner, by appointment and in scheduled classes"]:
        assert words in PAGE, words
    assert "up to 14" not in PAGE, "her flier still says 14 for private groups; the owner has since made it 10"


def test_her_name_is_on_the_page():
    assert "With love, Linda Huss" in PAGE and "Facilitated by Linda Huss" in PAGE
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', PAGE, re.S)
    assert json.loads(m.group(1))["founder"]["name"] == "Linda Huss"


def test_page_basics_for_seo_and_accessibility():
    assert '<html lang="en">' in PAGE and 'name="viewport"' in PAGE and 'name="description"' in PAGE
    assert 'rel="canonical"' in PAGE and 'property="og:image"' in PAGE
    assert len(tags("h1")) == 1
    for a in tags("input") + tags("select") + tags("textarea"):
        assert re.search(rf'<label[^>]+for="{a["id"]}"', PAGE), f"#{a['id']} needs a label"
    for a in tags("a"):
        if a.get("target") == "_blank":
            assert "noopener" in a.get("rel", "")
    assert tags("iframe")[0].get("title")


# ------------------------------------------------------------------------------------------- TOB's website builder
@pytest.fixture
def builder(tmp_path, monkeypatch):
    if str(TOB) not in sys.path:
        sys.path.insert(0, str(TOB))
    try:
        from tob.sitebuilder.server import BuilderApi
    except Exception:   # noqa: BLE001
        pytest.skip("TOB's website builder isn't on this PC")
    monkeypatch.setenv("TOB_DATA_DIR", str(tmp_path / "data"))
    dev = tmp_path / "dev"
    site = dev / "soundvibrationsanctuary"
    shutil.copytree(SITE, site, ignore=shutil.ignore_patterns(".git", "tests", "__pycache__", ".pytest_cache"))
    return BuilderApi(dev), site


def test_it_opens_cleanly_in_the_website_builder(builder):
    from tob.sitebuilder import htmlmap

    api, site = builder
    info = api.call("GET", "info")
    card = [s for s in info["sites"] if s["name"] == site.name][0]
    assert card["title"].startswith("Sound Vibration Sanctuary") and card["thumb"].startswith("images/")
    s = api.call("POST", "open", {}, {"folder": str(site)})["site"]
    page = api.page(s["key"], "index.html")
    assert not page["notes"]
    pm = api.sessions[page["rev"]].pm
    body = [e for e in pm.els if e.tag == "body"][0]
    inside = [pm.els[i] for i in pm.inside(body.id)]
    unknown = [e.tag for e in inside if not e.known]
    assert not unknown, f"elements the builder can't edit on their own: {unknown}"
    assert htmlmap.strip_ids(page["html"]) == PAGE
    assert api.sites[s["key"]].images_dir == "images"


def test_a_live_edit_in_the_builder_lands_as_a_small_exact_change(builder):
    api, site = builder
    s = api.call("POST", "open", {}, {"folder": str(site)})["site"]
    page = api.page(s["key"], "index.html")
    pm = api.sessions[page["rev"]].pm
    h1 = [e for e in pm.els if e.tag == "h1"][0]
    name = [e for e in pm.els if e.tag == "span" and pm.inner(e.id) == "Gift card amounts and how to buy them"][0]
    res = api.save({"site": s["key"], "rev": page["rev"], "removed": [],
                    "patches": [[h1.id, f"\x01S{h1.id}\x02Find Your Calm</h1>"],
                                [name.id, f"\x01S{name.id}\x02$25 and $50, at the shop</span>"]]})
    assert res["ok"] and res["wrote"] == ["index.html"]
    text = (site / "index.html").read_text(encoding="utf-8")
    assert text == PAGE.replace(">Discover Inner Peace</h1>", ">Find Your Calm</h1>").replace(
        '<span class="ph">Gift card amounts and how to buy them</span>', '<span class="ph">$25 and $50, at the shop</span>')
