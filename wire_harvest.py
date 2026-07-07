#!/usr/bin/env python3
"""
wire_harvest.py  --  server-side Global Wire (runs in GitHub Actions, not the browser)
--------------------------------------------------------------------------------------
Fetches the accountability RSS feeds, keeps only BIG-PICTURE, LEGISLATIVE stories,
maintains a SHARED archive (wire_archive.json) that grows over time for every
visitor. No API key, account, or cost — the map computes the "legislative climate"
meta-narrative itself from this archive.

The map reads both files from GitHub raw. Because this runs on a server, there is
no CORS limit and the history is the same for everyone (not per-browser).

Deps:  pip install feedparser
"""

import json, os, re, time, html, datetime, urllib.request
import feedparser

FEEDS = [
    ("ICIJ", "https://www.icij.org/feed/"),
    ("OCCRP", "https://www.occrp.org/en/feed"),
    ("Transparency Int'l", "https://www.transparency.org/en/news/rss"),
    ("GIJN", "https://gijn.org/feed/"),
    ("Bellingcat", "https://www.bellingcat.com/feed/"),
    ("ProPublica", "https://www.propublica.org/feeds/propublica/main"),
    ("The Intercept", "https://theintercept.com/feed/"),
    ("Reveal", "https://revealnews.org/feed/"),
    ("The Markup", "https://themarkup.org/feeds/rss.xml"),
    ("Mother Jones", "https://www.motherjones.com/feed/"),
    ("Coda Story", "https://www.codastory.com/feed/"),
    ("Global Voices", "https://globalvoices.org/feed/"),
    ("IPS News", "http://www.ipsnews.net/news/feed/"),
    ("Democracy Digest", "https://www.demdigest.org/feed/"),
    ("openDemocracy", "https://www.opendemocracy.net/en/rss/"),
    ("Democracy Now", "https://www.democracynow.org/democracynow.rss"),
    ("VoxEurop", "https://voxeurop.eu/en/feed/"),
    ("EUobserver", "https://euobserver.com/rss"),
    ("Balkan Insight", "https://balkaninsight.com/feed/"),
    ("Declassified UK", "https://declassifieduk.org/feed/"),
    ("The Bureau (TBIJ)", "https://www.thebureauinvestigates.com/feed"),
    ("Rest of World", "https://restofworld.org/feed/latest/"),
    ("New Humanitarian", "https://www.thenewhumanitarian.org/rss.xml"),
    ("Article 19", "https://www.article19.org/feed/"),
    ("Access Now", "https://www.accessnow.org/feed/"),
    ("EFF", "https://www.eff.org/rss/updates.xml"),
    ("Daily Maverick", "https://www.dailymaverick.co.za/dmrss/"),
    ("Premium Times", "https://www.premiumtimesng.com/feed"),
    ("The Wire (India)", "https://thewire.in/rss"),
    ("Scroll.in", "https://scroll.in/feeds/all.rss"),
    ("Rappler", "https://www.rappler.com/feed/"),
    ("Mada Masr", "https://www.madamasr.com/en/feed/"),
    ("CORRECTIV", "https://correctiv.org/feed/"),
    ("Civio", "https://civio.es/feed/"),
    ("\u00c1tl\u00e1tsz\u00f3", "https://english.atlatszo.hu/feed/"),
    ("Sludge", "https://readsludge.com/feed/"),
    ("Popular Information", "https://popular.info/feed"),
    ("Follow the Money", "https://www.ftm.eu/rss"),
]

# ---- significance: big-picture momentum vs small incidents ----
BIG = ["reform","overhaul","sweeping","landmark","historic","nationwide","bill","legislation"," act ",
       "passed","approve","vote","ban","mandate","register","inquiry","probe","investigation","ruling",
       "commission","parliament","congress","senate","assembly","government","federal","billion",
       "crackdown","watchdog","oversight","lawsuit","regulat","directive","referendum","scandal","state capture"]
SMALL = ["councillor","local council","mayor of","resign","quit","stepped down","arrested","charged with",
         "jailed","apolog","expenses claim","affair","girlfriend","boyfriend","wedding","tweeted","gaffe",
         "insult","feud","hospital"," dies","obituary","by-election","personal"]
KW = ["oversight","freedom of information","right to information","foi","anti-corruption","corruption","audit",
      "auditor","electoral commission","watchdog","accountability","transparency","disclosure","lobby","lobbying",
      "register of interests","conflict of interest","asset declaration","whistleblower","rule of law",
      "checks and balances","judicial independence","immunity","parliamentary inquiry","state capture",
      "dark money","campaign finance","reform bill","integrity commission"]
# LEGISLATIVE gate: story must touch the law-making branch (drops pure executive/judicial)
LEG_MUST = ["parliament","parliamentary","congress","senate","senator","assembly","legislat","lawmaker",
            " mp "," mps "," mep ","bill ","bills ","statute","house of representatives","national assembly",
            "chamber of deputies","floor vote","committee","lobbying register","register of interests",
            "campaign finance","freedom of information","transparency law","transparency bill","oversight",
            "whistleblower","bundestag","oireachtas","sejm","knesset","riigikogu"," diet ","duma"]

def sig(t):
    s = " " + t.lower() + " "
    sc = 0
    for w in BIG:   sc += 2 if w in s else 0
    for w in SMALL: sc -= 3 if w in s else 0
    for w in KW:    sc += 1 if w in s else 0
    return sc

def has_leg(t):
    s = " " + t.lower() + " "
    return any(w in s for w in LEG_MUST)

def clean(x): return re.sub(r"<[^>]+>", "", html.unescape(x or "")).strip()

def harvest():
    out = []
    for name, url in FEEDS:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:30]:
                title = clean(e.get("title", ""))
                link  = e.get("link", "")
                desc  = clean(e.get("summary", "") or e.get("description", ""))
                pub   = e.get("published_parsed") or e.get("updated_parsed")
                date  = int(time.mktime(pub) * 1000) if pub else int(time.time() * 1000)
                if not (title and link): continue
                blob = title + " " + desc
                if sig(blob) >= 2 and has_leg(blob):
                    out.append({"name": name, "title": title, "link": link, "date": date})
        except Exception as ex:
            print(f"  feed failed: {name}: {ex}")
    return out

def merge_archive(new):
    try:    arch = json.load(open("wire_archive.json", encoding="utf-8"))
    except Exception: arch = []
    seen = {x["link"] for x in arch}
    added = 0
    for it in new:
        if it["link"] not in seen:
            arch.append(it); seen.add(it["link"]); added += 1
    arch.sort(key=lambda x: -x["date"]); arch = arch[:2000]
    json.dump(arch, open("wire_archive.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"  archive: +{added} new, {len(arch)} total")
    return arch

    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5")   # change to whatever your API offers
    recent = arch[:45]
    lines = "\n".join(f"- {x['title']} ({x['name']})" for x in recent)
    prompt = (
        "Below are recent BIG-PICTURE legislative-accountability headlines from around the world "
        "(law-making transparency, oversight, lobbying, anti-corruption, freedom-of-information, "
        "asset disclosure, checks and balances):\n\n" + lines +
        "\n\nWrite 3\u20134 sentences describing the current GLOBAL LEGISLATIVE-ACCOUNTABILITY CLIMATE \u2014 "
        "the meta-narrative and momentum OVER TIME, not individual events. Think 'the legislative climate, "
        "not today's weather': where is law-making accountability being strengthened, tested, or rolled back "
        "across countries, and how do these threads connect? Neutral, factual, global. No preamble, no lists, "
        "no headline \u2014 just the paragraph."
    )
    body = json.dumps({"model": model, "max_tokens": 400,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
          headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        j = json.load(urllib.request.urlopen(req, timeout=90))
        text = "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text").strip()
        return text or None
    except Exception as ex:
        print(f"  climate call failed: {ex}"); return None

def main():
    arch = merge_archive(harvest())
    print("done. wire_archive.json ready — the map computes the climate from it (no API needed).")

if __name__ == "__main__":
    main()
