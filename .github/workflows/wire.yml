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
    ("100Reporters", "https://100r.org/feed/"),
    ("Abzas Media", "https://abzas.org/en/rss.xml"),
    ("African Network of Centers for Investigative Reporting (ANCIR)", "https://investigate.africa/feed"),
    ("Agência Pública", "https://apublica.org/feed/"),
    ("Alqatiba", "https://alqatiba.com/feed/"),
    ("amaBhungane Centre for Investigative Journalism", "https://amabhungane.org/feed/"),
    ("Arab Reporters for Investigative Journalism (ARIJ)", "http://en.arij.net/feed"),
    ("Armando.info", "https://armando.info/feed/"),
    ("atlatszo.hu", "https://atlatszo.hu/feed/"),
    ("Balkan Investigative Reporting Network (BIRN)", "https://birn.eu.com/feed/"),
    ("Bellingcat", "https://www.bellingcat.com/feed"),
    ("Bihus.info", "https://bihus.info/feed"),
    ("Bivol.bg", "https://bivol.bg/feed"),
    ("Bolts", "https://boltsmag.org/feed"),
    ("BudgIT", "https://budgit.org/feed/"),
    ("Byline Times", "https://bylinetimes.com/feed/"),
    ("CAinfo (Centro de Archivo y Acceso a la Información Pública)", "http://cainfo.org.uy/feed"),
    ("Carter Center — Election Standards", "https://electionstandards.cartercenter.org/feed/"),
    ("Center for Investigative Journalism of Montenegro (CIN-CG)", "http://www.cin-cg.me/feed"),
    ("Center for Investigative Journalism of Serbia (CINS)", "https://www.cins.rs/web-stories/feed/"),
    ("Center for Investigative Reporting (CIN)", "https://cin.ba/feed/"),
    ("Center for Investigative Reporting (Reveal)", "https://revealnews.org/feed/"),
    ("Center for Investigative Reporting, Sri Lanka", "https://cir.lk/feed/"),
    ("Center for Public Integrity", "https://publicintegrity.org/feed/"),
    ("Centre for Investigative Journalism Malawi (CIJM)", "https://www.investigative-malawi.org/feed/"),
    ("Centro de Periodismo Investigativo — Puerto Rico", "https://periodismoinvestigativo.com/feed/"),
    ("Centro Latinoamericano de Investigación Periodística (CLIP)", "https://www.elclip.org/feed/"),
    ("Chronicles.Media", "https://chronicles.media/feed/"),
    ("CIPER — Centro de Investigación Periodística", "https://www.ciperchile.cl/feed/"),
    ("Civil Discourse (Joyce Vance)", "https://joycevance.substack.com/feed"),
    ("Coda Media", "https://www.codastory.com/feed/"),
    ("Confidencial", "https://confidencial.digital/feed"),
    ("Congressional Dish (Jennifer Briney)", "https://congressionaldish.com/feed"),
    ("Connectas", "https://www.connectas.org/feed/"),
    ("Context.ro", "https://context.ro/feed/"),
    ("CONVOCA", "https://convoca.pe/rss.xml"),
    ("CORRECTIV", "https://www.correctiv.org/feed"),
    ("Crimean Center for Investigative Journalism", "http://investigator.org.ua/feed"),
    ("CU Sens", "https://cusens.md/ro/feed/"),
    ("Cyprus Investigative Reporting Network (CIReN)", "http://www.ciren.cy/feed"),
    ("Czech Centre for Investigative Journalism", "https://www.investigace.cz/feed/"),
    ("Danwatch", "https://danwatch.dk/en/feed/"),
    ("Data Cameroon", "https://datacameroon.com/feed/"),
    ("DCReport", "https://www.dcreport.org/feed/"),
    ("Declassified UK", "https://www.declassifieduk.org/feed/"),
    ("Direkt36", "http://www.direkt36.hu/en/feed"),
    ("DISCLOSE", "https://disclose.ngo/feed/?lang=en"),
    ("Drop Site News", "https://www.dropsitenews.com/feed"),
    ("El Surtidor", "https://elsurti.com/feed"),
    ("Election Law Blog (Rick Hasen)", "https://electionlawblog.org/?feed=rss2"),
    ("emptywheel (Marcy Wheeler)", "https://emptywheel.net/feed/"),
    ("Environmental Investigative Forum", "https://eiforum.org/feed/"),
    ("Epicentro.TV", "https://epicentro.tv/rss/global.xml"),
    ("Fiquem Sabendo", "https://fiquemsabendo.com.br/rss/"),
    ("Follow the Money", "https://www.ftm.eu/feed"),
    ("Forbidden Stories", "https://forbiddenstories.org/feed/"),
    ("FrontStory / Fundacja Reporterów", "https://frontstory.pl/feed/"),
    ("Fundación Ciudadana Civio", "http://www.civio.es/feed.xml"),
    ("GIJN — Global Investigative Journalism Network", "https://gijn.org/rss"),
    ("Global Reporting Center", "https://globalreportingcentre.org/feed/"),
    ("HETQ — Investigative Journalists of Armenia", "https://hetq.am/en/rss"),
    ("ICIJ — International Consortium of Investigative Journalists", "https://www.icij.org/feed"),
    ("IDL-Reporteros", "https://www.idl-reporteros.pe/feed/"),
    ("inewsource", "https://inewsource.org/feed/"),
    ("Inhlase Centre for Investigative Journalism", "https://inhlase.com/feed/"),
    ("Inkyfada", "https://inkyfada.com/fr/feed/"),
    ("InSight Crime", "https://insightcrime.org/feed/"),
    ("Instituto Prensa y Sociedad (IPYS)", "http://www.ipys.org/rss.xml"),
    ("International Centre for Investigative Reporting (ICIR)", "https://www.icirnigeria.org/feed/"),
    ("Investico", "https://www.platform-investico.nl/feed"),
    ("Investigative Center of Jan Kuciak (ICJK)", "https://www.icjk.sk/rss"),
    ("Investigative Journalism Bureau", "https://ijb.utoronto.ca/feed/"),
    ("Investigative Journalism Center of Moldova", "https://anticoruptie.md/ro/feed"),
    ("Investigative Reporting Denmark", "https://www.ir-d.dk/feed/"),
    ("Investigative Reporting Lab Macedonia", "https://irl.mk/mk/feed/"),
    ("Investigative Reporting Workshop", "http://investigativereportingworkshop.org/feed"),
    ("IStories (Important Stories)", "https://istories.media/rss/all.xml"),
    ("iWatch Africa", "http://iwatchafrica.org/feed/"),
    ("JARING", "https://jaring.id/feed/"),
    ("Just Security", "https://www.justsecurity.org/feed/"),
    ("Kloop Media", "https://kloop.kg/feed/"),
    ("KRIK — Crime and Corruption Reporting Network", "https://www.krik.rs/feed/"),
    ("La Maison des Reporters", "https://lamaisondesreporters.sn/feed/"),
    ("Lighthouse Reports", "https://www.lighthousereports.com/feed/"),
    ("LUPA — Crime and Corruption Reporting Network", "https://lupa.co.me/feed/"),
    ("Mada Masr", "https://www.madamasr.com/en/feed"),
    ("Maka Angola", "https://www.makaangola.org/feed/"),
    ("Makanday", "https://makanday.org/feed/"),
    ("Maldita.es", "https://maldita.es/feed"),
    ("MapLight", "https://www.maplight.org/blog-feed.xml"),
    ("Mexicanos Contra la Corrupción y la Impunidad (MCCI)", "https://contralacorrupcion.mx/feed/"),
    ("Midwest Center for Investigative Reporting", "https://investigatemidwest.org/feed/"),
    ("Mikroskop Media", "https://mikroskopmedia.com/feed/"),
    ("Ministério Público – Amapá", "https://www.mpap.mp.br/rss"),
    ("Ministério Público – Ceará", "https://mpce.mp.br/feed/"),
    ("Ministério Público – Maranhão", "https://www.mpma.mp.br/feed"),
    ("Ministério Público – Paraíba", "https://www.mppb.mp.br/rss"),
    ("MNN Centre for Investigative Journalism", "https://lescij.org/feed/"),
    ("MPDFT (Ministério Público)", "https://www.mpdft.mp.br/portal/index.php?format=feed&type=rss"),
    ("MUSEBA Journalism Project", "https://www.themusebaproject.org/feed/"),
    ("Nashi Groshi (“Our Money”)", "https://nashigroshi.org/feed/"),
    ("Nikolaev Center for Investigative Reporting (NikCIR)", "https://nikcenter.org/feed/"),
    ("Notes on the Crises (Nathan Tankus)", "https://www.crisesnotes.com/rss/"),
    ("OCCRP — Organized Crime & Corruption Reporting Project", "https://www.occrp.org/en/feed"),
    ("openDemocracy", "https://www.opendemocracy.net/rss/"),
    ("Ortak", "https://ortak.org/feed/"),
    ("Oxpeckers", "https://oxpeckers.org/feed/"),
    ("Oštro", "https://ostro.si/feed/"),
    ("Periodismo de Barrio", "https://periodismodebarrio.org/feed/"),
    ("Philippine Center for Investigative Journalism (PCIJ)", "https://pcij.org/feed/"),
    ("Plaza Pública", "https://plazapublica.com.gt/feed/"),
    ("Pod črto", "https://podcrto.si/feed"),
    ("Popular Information (Judd Legum)", "https://popular.info/feed"),
    ("Prachatai", "https://prachatai.com/feed"),
    ("Proekt (The Project)", "https://www.proekt.media/feed/"),
    ("ProPublica", "https://www.propublica.org/feeds/propublica/main"),
    ("Public Herald", "https://publicherald.org/feed/"),
    ("Quinto Elemento Lab", "https://quintoelab.org/feed"),
    ("Rappler / Newsbreak", "https://www.rappler.com/feed/"),
    ("Re:Baltica — Baltic Centre for Investigative Journalism", "https://rebaltica.lv/feed/"),
    ("REFLEKT", "http://reflekt.ch/api/rss-feed"),
    ("REJI-RDC", "https://www.reji-rdc.org/feed/"),
    ("Reporters United", "https://www.reportersunited.gr/feed/"),
    ("Republik", "https://www.republik.ch/feed.xml"),
    ("Repórter Brasil", "https://reporterbrasil.org.br/feed/"),
    ("RISE Moldova", "https://www.rise.md/feed/"),
    ("RISE Project", "http://www.riseproject.ro/feed"),
    ("SCOOP-Macedonia", "http://scoop.mk/feed/"),
    ("Siena", "https://www.siena.lt/blog-feed.xml"),
    ("SIRAJ — Syrian Investigative Reporting for Accountability Journalism", "https://sirajsy.net/ar/feed"),
    ("Slidstvo.info", "https://www.slidstvo.info/feed/"),
    ("Sludge", "https://readsludge.com/rss/"),
    ("Solomon", "https://wearesolomon.com/feed/"),
    ("Studio Monitor", "https://monitori.ge/feed"),
    ("Tansa — Tokyo Investigative Newsroom", "https://en.tansajp.org/rss.xml"),
    ("Temirov Live", "https://www.youtube.com/feeds/videos.xml?channel_id=UCpZtteaL03_LrVORzSfxwZg"),
    ("Texas Observer", "https://www.texasobserver.org/feed/"),
    ("Texty.org.ua — Data Journalism Agency", "http://texty.org.ua/feed.xml"),
    ("The Bristol Cable", "https://thebristolcable.org/feed"),
    ("The Centre for Climate Reporting", "https://climate-reporting.org/feed/"),
    ("The Elephant", "https://www.theelephant.info/feed/"),
    ("The Ferret", "https://www.theferret.scot/latest/rss/"),
    ("The Investigative Desk", "https://investigativedesk.com/feed/"),
    ("The Lever", "https://www.levernews.com/rss/"),
    ("The Marshall Project", "https://www.themarshallproject.org/rss/recent"),
    ("The Public Source", "https://thepublicsource.org/feed"),
    ("The Reporter (Taiwan)", "https://www.twreporter.org/a/rss2.xml"),
    ("The War Horse", "https://thewarhorse.org/feed/"),
    ("Turkmen.News", "https://turkmen.news/feed/"),
    ("Type Investigations", "https://typeinvestigations.org/feed"),
    ("Viewfinder", "https://viewfinder.org.za/feed/"),
    ("Watershed Investigations", "https://watershedinvestigations.com/feed"),
    ("Wisconsin Watch", "https://wisconsinwatch.org/feed/"),
    ("Wole Soyinka Centre for Investigative Journalism", "https://wscij.org/feed/"),
    ("Ziarul de Gardă", "https://www.zdg.md/feed"),
    ("Átlátszó Erdély", "https://atlatszo.ro/feed/"),
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
