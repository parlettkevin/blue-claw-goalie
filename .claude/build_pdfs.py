# -*- coding: utf-8 -*-
"""Regenerate the 4 companion PDFs from the app's exact drill content,
rebranded to the Blue Claws identity (Royal Blue #0047AB + Red #FF0000),
print-optimized on white paper with the crest logo in the header.

Outputs (color + inksaver):
  Goalie-CheatSheet-1page-color.pdf / -inksaver.pdf   (1pg landscape)
  Goalie-Playbook-FULL-color.pdf    / -inksaver.pdf   (portrait, multi-page)
"""
import base64, pathlib, re
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP  = ROOT / "Goalie-Season-System-APP.html"

CREST = "data:image/jpeg;base64," + base64.b64encode((ROOT/"blue claws.jpg").read_bytes()).decode()

soup = BeautifulSoup(APP.read_text(encoding="utf-8"), "html.parser")

POD_OF = {"track":"track","foot":"foot","clear":"clear","comm":"comm"}

def txt(el):
    return el.get_text(" ", strip=True) if el else ""

# ---- parse pod headers ----
pods = {}
for ph in soup.select(".podhead"):
    pod = next(c for c in ph["class"] if c in POD_OF)
    pods[pod] = {"letter": txt(ph.select_one(".chip")),
                 "name": txt(ph.select_one("h2")),
                 "tag": txt(ph.select_one("p"))}

# ---- parse drills ----
drills = []
for card in soup.select("article.card"):
    pod = next(c for c in card["class"] if c in POD_OF)
    h3 = card.select_one(".card-head h3")
    tagmini = h3.select_one(".tagmini")
    tag = txt(tagmini) if tagmini else ""
    tagcls = ""
    if tagmini:
        tagcls = next((c for c in tagmini["class"] if c != "tagmini"), "")
        tagmini.extract()
    setup = card.select_one(".block.setup")
    logi  = card.select_one(".block.logi")
    def block_html(b):
        ps = b.select("p"); ps[0].extract()  # drop blabel
        return b.select_one("p").decode_contents()
    one = card.select_one(".lvl.one"); one.select_one(".lt").extract()
    two = card.select_one(".lvl.two"); two.select_one(".lt").extract()
    mrows = []
    for mr in card.select(".mastery .mrow"):
        mrows.append((txt(mr.select_one(".ml")), txt(mr.select_one(".mtx"))))
    drills.append({
        "code": txt(card.select_one(".card-num")),
        "pod": pod,
        "title": txt(h3),
        "tag": tag, "tagcls": tagcls,
        "obj": txt(card.select_one(".obj")),
        "svg": str(card.select_one(".diagram svg")),
        "goal": [txt(li) for li in card.select(".goal li")],
        "setup": block_html(setup),
        "logi": block_html(logi),
        "beginner": one.get_text(" ", strip=True),
        "advanced": two.get_text(" ", strip=True),
        "mastery": mrows,
        "cues": [txt(c) for c in card.select(".cues .cue")],
    })

# ---- practice cards ----
pcards = []
for pc in soup.select(".pcard"):
    rows = [(txt(r.select_one("b")), txt(r.select_one("span"))) for r in pc.select(".pc-row")]
    pod = next((c for c in pc.get("class", []) if c in POD_OF), "track")
    pcards.append({"n": txt(pc.select_one(".pc-n")), "title": txt(pc.select_one("h3")),
                   "time": txt(pc.select_one(".pc-t")), "rows": rows, "pod": pod})

# ---- season ----
season = []
for tr in soup.select(".seasonwrap tbody tr"):
    if "phase" in (tr.get("class") or []):
        season.append(("phase", txt(tr.select_one("td"))))
    else:
        tds = tr.select("td")
        season.append(("wk", [txt(t) for t in tds]))

# ---- games ----
games = []
for g in soup.select("[data-section='games'] .game"):
    games.append({"emoji": txt(g.select_one(".e")), "title": txt(g.select_one("h3")),
                  "desc": txt(g.select_one("p")), "items": [txt(li) for li in g.select("li")]})

# ===================== STYLING =====================
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@600;700;800;900'
         '&family=Readex+Pro:wght@400;500;600;700&family=Azeret+Mono:wght@600;700&display=swap" rel="stylesheet">')

POD_COLOR = {  # (accent, tint) for color variant
    "track": ("#0047AB", "#E9F0FB"),
    "foot":  ("#B57400", "#FAF1DE"),
    "clear": ("#C23A18", "#FBEAE3"),
    "comm":  ("#0C7C77", "#E3F2F1"),
}
PRINT_POD = {  # (header bg, header text) for practice-card headers, color variant
    "track": ("#0047AB", "#ffffff"),
    "foot":  ("#C8861A", "#1a1205"),
    "clear": ("#C23A18", "#ffffff"),
    "comm":  ("#0C7C77", "#04201f"),
}
TAG_LABEL = {"step":"STEP","rebound":"REBOUND","wide":"WIDE","talk":"TALK"}

def ink_svg(svg):
    """Recolor a field diagram for the ink-saver variant (grayscale on white)."""
    repl = {
        '#2f8f43':'#ffffff', '#3f9f53':'#e6e6e6', '#f4f7f1':'#333333',
        '#1b6fe0':'#555555', '#7b3ff2':'#555555', '#e8451f':'#222222',
        '#0e9488':'#555555', '#ffb627':'#999999', '#3a2600':'#000000',
        '#dbe9ff':'#444444', '#ffe6b0':'#444444',
    }
    for a,b in repl.items():
        svg = svg.replace(a,b)
    return svg

def ink_legend_dot(color, ink):
    return "#777" if ink else color

# ===================== PLAYBOOK =====================
def playbook(ink=False):
    accent = "#0047AB"; red = "#C8102E" if ink else "#E11900"
    navy = "#0A1A3A"
    line = "#cfcfcf" if ink else "#D7DCE6"
    css = f"""
    @page {{ size: letter; margin: 14mm 13mm; }}
    *{{box-sizing:border-box}}
    html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
    body{{margin:0;font-family:"Readex Pro",Arial,sans-serif;color:#16181d;font-size:9.6px;line-height:1.38}}
    .disp{{font-family:"Saira Condensed","Arial Narrow",sans-serif}}
    .mono{{font-family:"Azeret Mono",ui-monospace,monospace}}
    h1,h2,h3{{font-family:"Saira Condensed","Arial Narrow",sans-serif;margin:0}}
    /* cover */
    .cover{{text-align:center;padding:30mm 0 0}}
    .cover .crest{{width:120px;height:120px;border-radius:24px;overflow:hidden;margin:0 auto 14px;
        border:{'3px solid #111' if ink else '4px solid '+accent};
        {'box-shadow:0 0 0 4px #ddd;' if not ink else ''}}}
    .cover .crest img{{width:100%;height:100%;object-fit:cover;display:block}}
    .cover .kick{{font-size:11px;letter-spacing:.26em;text-transform:uppercase;color:{'#444' if ink else red};font-weight:700;margin-bottom:6px}}
    .cover h1{{font-size:62px;font-weight:900;text-transform:uppercase;line-height:.9;color:{navy}}}
    .cover h1 span{{color:{'#111' if ink else accent}}}
    .cover .sub{{margin:12px auto 0;max-width:74%;color:#3c4150;font-size:12px}}
    .stat-row{{display:flex;gap:8px;justify-content:center;margin:20px auto 0;max-width:80%}}
    .stat{{flex:1;border:1px solid {line};border-radius:10px;padding:8px}}
    .stat b{{font-family:"Saira Condensed",sans-serif;display:block;font-size:24px;color:{navy}}}
    .stat span{{font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:#6a7080}}
    .how{{margin:22px auto 0;max-width:84%;text-align:left}}
    .how .row{{display:flex;gap:10px;padding:8px 0;border-top:1px solid {line}}}
    .how .ic{{flex:0 0 40px;height:30px;border-radius:7px;display:flex;align-items:center;justify-content:center;
        font-family:"Azeret Mono",monospace;font-weight:700;font-size:10px;color:#fff;
        background:{'#222' if ink else accent}}}
    .how h3{{font-size:13px;text-transform:uppercase}} .how p{{margin:1px 0 0;color:#3c4150}}
    .breakp{{page-break-before:always}}
    /* pod header */
    .podh{{display:flex;align-items:center;gap:10px;margin:0 0 8px;padding-bottom:6px;border-bottom:2px solid {accent if not ink else '#111'}}}
    .podh .chip{{font-family:"Saira Condensed",sans-serif;font-weight:900;font-size:18px;color:#fff;width:30px;height:30px;
        border-radius:7px;display:flex;align-items:center;justify-content:center;background:{'#111' if ink else accent}}}
    .podh h2{{font-size:21px;text-transform:uppercase;color:{navy}}}
    .podh p{{margin:0;color:#6a7080;font-size:10px}}
    /* drill */
    .drill{{border:1px solid {line};border-radius:9px;padding:8px 10px;margin:0 0 7px;page-break-inside:avoid}}
    .dhead{{display:flex;gap:9px;align-items:center;margin-bottom:6px}}
    .dnum{{font-family:"Azeret Mono",monospace;font-weight:700;font-size:12px;color:#fff;width:34px;height:34px;border-radius:8px;
        display:flex;align-items:center;justify-content:center;flex:0 0 auto}}
    .dhead h3{{font-size:15px;text-transform:uppercase;color:{navy}}}
    .dhead .obj{{color:#3c4150;font-size:9px;margin-top:0}}
    .tag{{font-family:"Azeret Mono",monospace;font-size:8px;font-weight:700;color:#fff;border-radius:4px;padding:2px 5px;margin-left:5px;vertical-align:middle;
        background:{'#333' if ink else red}}}
    .grid{{display:flex;gap:9px}}
    .col-svg{{flex:0 0 188px}}
    .col-svg svg{{width:188px;height:auto;border:1px solid {line};border-radius:8px;display:block}}
    .legend{{display:flex;flex-wrap:wrap;gap:3px 8px;margin-top:4px;font-size:8px;color:#555}}
    .legend i{{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:3px;vertical-align:-1px}}
    .legend i.sq{{border-radius:2px}}
    .col-txt{{flex:1}}
    .lbl{{font-family:"Saira Condensed",sans-serif;font-weight:800;font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;
        color:{'#222' if ink else accent};margin:0 0 2px}}
    .goal{{background:{'#fff' if ink else '#F6F8FC'};border:1px solid {line};border-radius:7px;padding:5px 7px;margin-bottom:5px}}
    .goal ul{{margin:0;padding-left:13px}} .goal li{{margin-bottom:0}}
    .two{{display:flex;gap:6px;margin-bottom:5px}}
    .blk{{flex:1;border:1px solid {line};border-radius:7px;padding:5px 7px}}
    .blk.logi{{background:{'#fff' if ink else '#EAF0FB'};border-color:{'#bbb' if ink else '#C5D6F2'}}}
    .lvls{{display:flex;gap:6px;margin-bottom:5px}}
    .lvl{{flex:1;border:1px solid {line};border-radius:7px;padding:5px 7px}}
    .lvl .lt{{font-family:"Saira Condensed",sans-serif;font-weight:800;font-size:9px;letter-spacing:.06em;text-transform:uppercase;display:block;margin-bottom:1px;color:#555}}
    .mtbl{{width:100%;border-collapse:collapse;margin-bottom:5px}}
    .mtbl td{{padding:2px 5px;border-top:1px solid {line};vertical-align:top}}
    .mtbl td.k{{white-space:nowrap;font-family:"Azeret Mono",monospace;font-size:8px;font-weight:700;width:80px;color:{'#222' if ink else accent}}}
    .cues{{display:flex;flex-wrap:wrap;gap:5px}}
    .cue{{font-family:"Saira Condensed",sans-serif;font-weight:700;font-size:11px;text-transform:uppercase;border-radius:6px;padding:3px 8px;
        border:1px solid {'#999' if ink else red};color:{'#111' if ink else red}}}
    /* tables */
    h2.sec{{font-size:22px;text-transform:uppercase;color:{navy};margin:0 0 3px}}
    p.sub{{margin:0 0 9px;color:#5a6070;font-size:10px}}
    table.data{{width:100%;border-collapse:collapse;font-size:9.5px}}
    table.data th{{background:{'#111' if ink else navy};color:#fff;text-align:left;padding:6px 7px;font-family:"Saira Condensed",sans-serif;font-size:9px;letter-spacing:.04em;text-transform:uppercase}}
    table.data td{{padding:5px 7px;border-bottom:1px solid {line};vertical-align:top}}
    table.data tr.ph td{{background:{'#eee' if ink else '#EAF0FB'};font-family:"Saira Condensed",sans-serif;font-weight:700;text-transform:uppercase;color:{'#111' if ink else accent};font-size:9.5px}}
    table.data .wk{{font-family:"Azeret Mono",monospace;font-weight:700;color:{'#111' if ink else red}}}
    .pcards{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
    .pc{{border:1px solid {line};border-radius:9px;overflow:hidden;page-break-inside:avoid}}
    .pc .h{{display:flex;gap:7px;align-items:center;padding:6px 9px;color:#fff;background:{'#111' if ink else accent}}}
    .pc .h .n{{font-family:"Azeret Mono",monospace;font-weight:700;font-size:10px;background:rgba(255,255,255,.22);width:19px;height:19px;border-radius:5px;display:flex;align-items:center;justify-content:center}}
    .pc .h h3{{font-size:13px;text-transform:uppercase;flex:1}}
    .pc .h .t{{font-family:"Azeret Mono",monospace;font-size:8.5px;opacity:.85}}
    .pc .b{{padding:6px 9px}}
    .pc .r{{display:flex;gap:6px;padding:2px 0;border-bottom:1px solid {line};font-size:9px}}
    .pc .r:last-child{{border-bottom:0}}
    .pc .r b{{flex:0 0 44px;font-family:"Saira Condensed",sans-serif;text-transform:uppercase;font-size:8.5px;letter-spacing:.04em;color:#6a7080}}
    .game{{border:1px solid {line};border-radius:9px;padding:10px 12px;margin-bottom:8px;page-break-inside:avoid}}
    .game h3{{font-size:15px;text-transform:uppercase;color:{navy}}}
    .game ul{{margin:5px 0 0;padding-left:15px}} .game li{{margin-bottom:2px}}
    .note{{border:1px solid {line};border-radius:9px;padding:10px 12px;margin-bottom:8px}}
    .foot{{margin-top:14px;text-align:center;color:#6a7080;font-size:9px;border-top:1px solid {line};padding-top:8px}}
    .foot b{{color:{'#111' if ink else red}}}
    """
    def drill_block(d):
        ac, tint = POD_COLOR[d["pod"]]
        if ink: ac = "#111"; tint = "#fff"
        svg = ink_svg(d["svg"]) if ink else d["svg"]
        # legend mirrors app: pull from diagram colors per pod
        tag = f'<span class="tag">{d["tag"]}</span>' if d["tag"] else ""
        goal = "".join(f"<li>{g}</li>" for g in d["goal"])
        mrows = "".join(f'<tr><td class="k">{k}</td><td>{v}</td></tr>' for k,v in d["mastery"])
        cues = "".join(f'<span class="cue">{c}</span>' for c in d["cues"])
        return f"""
        <div class="drill">
          <div class="dhead">
            <div class="dnum" style="background:{ac}">{d['code']}</div>
            <div><h3>{d['title']}{tag}</h3><div class="obj">{d['obj']}</div></div>
          </div>
          <div class="grid">
            <div class="col-svg">{svg}</div>
            <div class="col-txt">
              <div class="goal"><p class="lbl" style="color:{ac}">Goal</p><ul>{goal}</ul></div>
              <div class="two">
                <div class="blk"><p class="lbl" style="color:{ac}">Setup &amp; Ball</p><p style="margin:0">{d['setup']}</p></div>
                <div class="blk logi"><p class="lbl" style="color:{ac}">2-Person</p><p style="margin:0">{d['logi']}</p></div>
              </div>
              <div class="lvls">
                <div class="lvl"><span class="lt">Beginner</span>{d['beginner']}</div>
                <div class="lvl"><span class="lt">Advanced</span>{d['advanced']}</div>
              </div>
              <p class="lbl" style="color:{ac}">Mastery Ladder</p>
              <table class="mtbl">{mrows}</table>
              <p class="lbl" style="color:{ac}">Coaching Cues</p>
              <div class="cues">{cues}</div>
            </div>
          </div>
        </div>"""

    # cover
    html = [f"<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>{css}</style></head><body>"]
    html.append(f"""
    <section class="cover">
      <div class="crest"><img src="{CREST}"></div>
      <div class="kick">2037 Age Group · Ages 7–9 · First-Year Goalies</div>
      <h1>Blue <span>Claws</span><br>Goalie System</h1>
      <p class="sub">Full coaching reference. 11 drills · 4 pods · mastery ladder · 16-week map. Build a brave, talking goalie.</p>
      <div class="stat-row">
        <div class="stat"><b>11</b><span>Drills</span></div>
        <div class="stat"><b>4</b><span>Pods</span></div>
        <div class="stat"><b>8</b><span>Cards</span></div>
        <div class="stat"><b>16</b><span>Weeks</span></div>
      </div>
      <div class="how">
        <div class="row"><div class="ic">STEP</div><div><h3>Attack the ball</h3><p>Step AT the shot; the “T” with the back foot happens on its own. Coach the attack, not the letter.</p></div></div>
        <div class="row"><div class="ic">L1·3</div><div><h3>Mastery ladder</h3><p>L1 learning · L2 competent · L3 game-ready. Effort first; numbers only at L3.</p></div></div>
        <div class="row"><div class="ic">TALK</div><div><h3>Communication counts</h3><p>Ball Top, Left, Right, Check, Clear. A goalie who talks beats one with perfect feet.</p></div></div>
      </div>
    </section>""")

    # pods + drills  (one page break after the cover, then drills flow naturally)
    order = ["track","foot","clear","comm"]
    for pi, pod in enumerate(order):
        ph = pods[pod]
        ac = "#111" if ink else POD_COLOR[pod][0]
        cls = "breakp" if pi == 0 else ""
        html.append(f"""<section class="{cls}"><div class="podh" style="page-break-after:avoid"><div class="chip" style="background:{ac}">{ph['letter']}</div>
          <div><h2>{ph['name']}</h2><p>{ph['tag']}</p></div></div>""")
        for d in [x for x in drills if x["pod"]==pod]:
            html.append(drill_block(d))
        html.append("</section>")

    # practice cards
    pc_html = ""
    for pc in pcards:
        rows = "".join(f'<div class="r"><b>{k}</b><span>{v}</span></div>' for k,v in pc["rows"])
        bg, fg = ("#111","#fff") if ink else PRINT_POD.get(pc["pod"], ("#0047AB","#fff"))
        pc_html += f"""<div class="pc"><div class="h" style="background:{bg};color:{fg}"><span class="n">{pc['n']}</span><h3>{pc['title']}</h3><span class="t">{pc['time']}</span></div><div class="b">{rows}</div></div>"""
    html.append(f"""<section class="breakp"><h2 class="sec">Practice Card References</h2>
      <p class="sub">Grab one before practice. Each runs as a tight station. Combine 2 per session.</p>
      <div class="pcards">{pc_html}</div>""")

    # season
    srows = ""
    for kind,val in season:
        if kind=="phase":
            srows += f'<tr class="ph"><td colspan="5">{val}</td></tr>'
        else:
            wk,pri,sec,cards,bench = val
            srows += f'<tr><td class="wk">{wk}</td><td>{pri}</td><td>{sec}</td><td>{cards}</td><td>{bench}</td></tr>'
    html.append(f"""<h2 class="sec" style="margin-top:14px">16-Week Season Map</h2>
      <p class="sub">Skills build in four phases. Cards refer to the references above.</p>
      <table class="data"><thead><tr><th>Wk</th><th>Primary</th><th>Secondary</th><th>Cards</th><th>Benchmark</th></tr></thead><tbody>{srows}</tbody></table>""")

    # practice shape + games
    gm = ""
    for g in games:
        items = "".join(f"<li>{i}</li>" for i in g["items"])
        gm += f'<div class="game"><h3>{g["emoji"]} {g["title"]}</h3><p style="margin:3px 0 0;color:#3c4150">{g["desc"]}</p><ul>{items}</ul></div>'
    html.append(f"""<section class="breakp"><h2 class="sec">Practice Shape &amp; Ball Rule</h2>
      <p class="sub">Kids hold focus ~3–4 min per activity. Keep blocks short.</p>
      <div class="note"><p style="margin:0 0 6px"><b>Each session:</b> gear check → tracking (4m) → footwork (4m) → save/clear or comm block (6m) → finish on a mini-game.</p>
      <p style="margin:0"><b>Ball rule — earned, not assumed:</b> tennis ball → Swax Lax → real ball, only after the no-flinch gate (8 of 10 caught without turning his head or closing his eyes). When in doubt, stay soft.</p></div>
      <h2 class="sec" style="margin-top:12px">Solo Engagement Games</h2>
      <p class="sub">No backup goalie? He competes against a number. Under 5 minutes, always ends on a win.</p>
      {gm}
      <div class="foot">Build the <b>brave kid</b> first, the goalie second. · Blue Claws Lacrosse · 2037 Age Group</div>
    </section>""")

    html.append("</body></html>")
    return "".join(html)

# ===================== CHEAT SHEET =====================
def cheatsheet(ink=False):
    accent="#0047AB"; red="#C8102E" if ink else "#E11900"; navy="#0A1A3A"
    line="#cfcfcf" if ink else "#D7DCE6"
    css=f"""
    @page {{ size: letter landscape; margin: 7mm; }}
    *{{box-sizing:border-box}} html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
    body{{margin:0;font-family:"Readex Pro",Arial,sans-serif;color:#16181d;font-size:8px;line-height:1.32}}
    h1,h2,h3{{font-family:"Saira Condensed","Arial Narrow",sans-serif;margin:0}}
    .mono{{font-family:"Azeret Mono",monospace}}
    .hdr{{display:flex;align-items:center;gap:11px;background:{'#111' if ink else navy};color:#fff;border-radius:9px;padding:8px 12px;margin-bottom:6px}}
    .hdr .crest{{width:46px;height:46px;border-radius:9px;overflow:hidden;border:2px solid {'#fff' if ink else accent};flex:0 0 auto}}
    .hdr .crest img{{width:100%;height:100%;object-fit:cover;display:block}}
    .hdr .kick{{font-size:8px;letter-spacing:.2em;text-transform:uppercase;color:{'#bbb' if ink else '#9DBFF0'};font-weight:700}}
    .hdr h1{{font-size:24px;text-transform:uppercase;line-height:.95}}
    .hdr .sum{{margin-left:auto;text-align:right;font-size:8.5px;max-width:46%;color:#dfe4ee}}
    .princ{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:5px}}
    .pbox{{border:1px solid {line};border-radius:7px;padding:5px 8px}}
    .pbox h3{{font-size:11px;text-transform:uppercase;color:{'#111' if ink else accent}}}
    .pbox p{{margin:1px 0 0;color:#3c4150}}
    .pods{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:5px}}
    .pod .ph{{display:flex;align-items:center;gap:6px;color:#fff;border-radius:6px;padding:4px 7px;margin-bottom:4px}}
    .pod .ph .c{{font-family:"Saira Condensed",sans-serif;font-weight:900;width:16px;height:16px;border-radius:4px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.25);font-size:10px}}
    .pod .ph h2{{font-size:11px;text-transform:uppercase}}
    .d{{border:1px solid {line};border-radius:6px;padding:5px 6px;margin-bottom:4px}}
    .d .t{{display:flex;align-items:baseline;gap:4px}}
    .d .code{{font-family:"Azeret Mono",monospace;font-weight:700;font-size:8px;color:#fff;border-radius:3px;padding:1px 4px}}
    .d h3{{font-size:10px;text-transform:uppercase;color:{navy}}}
    .d .obj{{color:#555;font-size:7.5px;margin:1px 0 2px}}
    .d .l3{{font-size:7.5px}} .d .l3 b{{color:{'#111' if ink else red}}}
    .d .cues{{margin-top:2px;font-family:"Saira Condensed",sans-serif;font-weight:700;text-transform:uppercase;font-size:8.5px;color:{'#111' if ink else red}}}
    .tag{{font-family:"Azeret Mono",monospace;font-size:6.5px;font-weight:700;color:#fff;border-radius:3px;padding:1px 3px;background:{'#333' if ink else red}}}
    .low{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:5px}}
    h2.sec{{font-size:13px;text-transform:uppercase;color:{navy};margin-bottom:3px}}
    table{{width:100%;border-collapse:collapse;font-size:7.6px}}
    th{{background:{'#111' if ink else navy};color:#fff;text-align:left;padding:3px 5px;font-family:"Saira Condensed",sans-serif;text-transform:uppercase;font-size:7.5px}}
    td{{padding:1.6px 5px;border-bottom:1px solid {line}}}
    tr.ph td{{background:{'#eee' if ink else '#EAF0FB'};font-weight:700;color:{'#111' if ink else accent};padding:1.6px 5px}}
    .wk{{font-family:"Azeret Mono",monospace;font-weight:700;color:{'#111' if ink else red}}}
    .games{{display:grid;grid-template-columns:1fr;gap:6px;margin-top:7px}}
    .game{{border:1px solid {line};border-radius:7px;padding:6px 8px}}
    .game h3{{font-size:11px;text-transform:uppercase;color:{navy}}}
    .game p{{margin:2px 0 0;color:#3c4150;font-size:7.6px}}
    .foot{{text-align:center;color:#6a7080;font-size:7.5px;margin-top:5px}}
    .foot b{{color:{'#111' if ink else red}}}
    """
    def pod_col(pod):
        ph=pods[pod]; ac="#111" if ink else POD_COLOR[pod][0]
        ds=""
        for d in [x for x in drills if x["pod"]==pod]:
            tag=f' <span class="tag">{d["tag"]}</span>' if d["tag"] else ""
            l3=next((v for k,v in d["mastery"] if "L3" in k), "")
            cues=" ".join(d["cues"])
            ds+=f"""<div class="d"><div class="t"><span class="code" style="background:{ac}">{d['code']}</span><h3>{d['title']}{tag}</h3></div>
              <div class="obj">{d['obj']}</div><div class="l3"><b>L3:</b> {l3}</div><div class="cues">{cues}</div></div>"""
        return f"""<div class="pod"><div class="ph" style="background:{ac}"><span class="c">{ph['letter']}</span><h2>{ph['name']}</h2></div>{ds}</div>"""

    # practice cards table
    pc_rows=""
    for pc in pcards:
        drills_cell = dict(pc["rows"]).get("Drills","")
        pc_rows+=f'<tr><td class="wk">{pc["n"]}</td><td>{pc["title"]}</td><td>{drills_cell}</td><td>{pc["time"]}</td></tr>'
    # season table (primary + cards only, compact)
    s_rows=""
    for kind,val in season:
        if kind=="phase":
            s_rows+=f'<tr class="ph"><td colspan="3">{val}</td></tr>'
        else:
            wk,pri,sec,cards,bench=val
            s_rows+=f'<tr><td class="wk">{wk}</td><td>{pri}</td><td>{cards}</td></tr>'
    g0,g1=games[0],games[1]
    html=f"""<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>{css}</style></head><body>
    <div class="hdr">
      <div class="crest"><img src="{CREST}"></div>
      <div><div class="kick">2037 · Ages 7–9 · Goalie</div><h1>Coach’s Cheat Sheet</h1></div>
      <div class="sum">11 drills · 4 pods · mastery ladder · soft balls until earned · end on a save &amp; a cheer.</div>
    </div>
    <div class="princ">
      <div class="pbox"><h3>Attack the ball (B2)</h3><p>Step AT the shot; the “T” happens on its own. Don’t coach the letter.</p></div>
      <div class="pbox"><h3>Mastery: L1/L2/L3</h3><p>Learning → Competent → Game-ready. Effort first; numbers only at L3.</p></div>
      <div class="pbox"><h3>Rebound + Wide Clear</h3><p>Chase pop-loose; clear to the sideline, never up the middle.</p></div>
      <div class="pbox"><h3>Talk (Pod D)</h3><p>Ball Top, Left, Right, Check, One More, Clear. A talking goalie wins.</p></div>
    </div>
    <div class="pods">{pod_col('track')}{pod_col('foot')}{pod_col('clear')}{pod_col('comm')}</div>
    <div class="low">
      <div>
        <h2 class="sec">Practice Cards</h2>
        <table><thead><tr><th>#</th><th>Card</th><th>Drills</th><th>Time</th></tr></thead><tbody>{pc_rows}</tbody></table>
        <div class="games">
          <div class="game"><h3>{g0['emoji']} {g0['title']}</h3><p>{g0['desc']} {g0['items'][0]}</p></div>
          <div class="game"><h3>{g1['emoji']} {g1['title']}</h3><p>{g1['desc']} {g1['items'][0]}</p></div>
        </div>
      </div>
      <div><h2 class="sec">16-Week Map</h2><table><thead><tr><th>Wk</th><th>Primary Focus</th><th>Cards</th></tr></thead><tbody>{s_rows}</tbody></table></div>
    </div>
    <div class="foot">Build the <b>brave kid</b> first, the goalie second. · Blue Claws Lacrosse · 2037 Age Group</div>
    </body></html>"""
    return html

# ===================== WRITE FILES =====================
out = ROOT / ".claude" / "_print"
out.mkdir(exist_ok=True)
specs = [
    ("Goalie-Playbook-FULL-color.pdf",     playbook(False)),
    ("Goalie-Playbook-FULL-inksaver.pdf",  playbook(True)),
    ("Goalie-CheatSheet-1page-color.pdf",  cheatsheet(False)),
    ("Goalie-CheatSheet-1page-inksaver.pdf", cheatsheet(True)),
]
for name, html in specs:
    (out / (name.replace(".pdf",".html"))).write_text(html, encoding="utf-8")
    print("wrote", name.replace(".pdf",".html"))
print("DONE")
