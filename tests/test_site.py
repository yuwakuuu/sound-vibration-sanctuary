"""Checks for the Sound Vibration Sanctuary site: the rebrand is complete, the facts match her own site, nothing is
invented, every picture is there, and the page opens and saves cleanly in TOB's website builder.

Run with TOB's Python (the builder checks need ``tob.sitebuilder``; they're skipped without it):

    C:\\Users\\ayala\\Projects\\TOB-OS\\.venv\\Scripts\\python.exe -m pytest tests -q
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1]
TOB = Path(r"C:\Users\ayala\Projects\TOB-OS")
PAGE = (SITE / "index.html").read_text(encoding="utf-8")
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
    old = ["Crystals & Crosses", "Crystals &amp; Crosses", "Linda", "Huss", "CrystalClearChoices", "crystalsandcrosses",
           "185 N Apache Trail", "320 W Superstition", "480-265-6136", "Marcellus", "Figtree", "#24152f",
           "tmpbizz.com/demo/crystalscrosses"]
    for f in ["index.html", "style.css", "script.js", "favicon.svg", "README.md"]:
        text = (SITE / f).read_text(encoding="utf-8")
        found = [w for w in old if w.lower() in text.lower()]
        assert not found, f"{f} still mentions {found}"


def test_her_real_details_are_on_the_page():
    assert "<title>Sound Vibration Sanctuary" in PAGE
    assert "Discover Inner Peace" in PAGE
    assert "212 W Superstition Blvd" in PAGE and "Apache Junction, AZ" in PAGE
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
    assert len(re.findall(r'class="ph"', PAGE)) >= 10
    assert not re.search(r"\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b", PAGE), "no phone number until she gives one"
    assert not re.search(r"[\w.+-]+@[\w-]+\.\w+", PAGE), "no email address until she gives one"
    readme = (SITE / "README.md").read_text(encoding="utf-8")
    assert "## Placeholders to fill in" in readme


def test_local_business_schema_is_valid_and_honest():
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', PAGE, re.S)
    data = json.loads(m.group(1))
    assert data["@type"] == "HealthAndBeautyBusiness" and data["name"] == "Sound Vibration Sanctuary"
    assert data["address"]["streetAddress"] == "212 W Superstition Blvd"
    assert data["address"]["addressLocality"] == "Apache Junction" and data["address"]["addressRegion"] == "AZ"
    assert FACEBOOK in data["sameAs"] and INSTAGRAM in data["sameAs"]
    hours = data["openingHoursSpecification"][0]
    assert hours["dayOfWeek"] == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    assert (hours["opens"], hours["closes"]) == ("11:00", "14:00")
    assert "telephone" not in data and "aggregateRating" not in data and "review" not in data
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
    for f in ["favicon.svg", "apple-touch-icon.png", "og.png", "style.css", "script.js"]:
        assert (SITE / f).is_file()


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
    phone = [e for e in pm.els if e.tag == "span" and pm.inner(e.id) == "Phone number"][0]
    res = api.save({"site": s["key"], "rev": page["rev"], "removed": [],
                    "patches": [[h1.id, f"\x01S{h1.id}\x02Find Your Calm</h1>"],
                                [phone.id, f"\x01S{phone.id}\x02(480) 555-0100</span>"]]})
    assert res["ok"] and res["wrote"] == ["index.html"]
    text = (site / "index.html").read_text(encoding="utf-8")
    assert text == PAGE.replace(">Discover Inner Peace</h1>", ">Find Your Calm</h1>").replace(
        '<span class="ph">Phone number</span>', '<span class="ph">(480) 555-0100</span>')
