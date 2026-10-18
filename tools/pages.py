"""Builds the inner pages: article, the wall, money, moving, the count, the olive harvest,
tell us your work, about, search and 404.

python -I tools/pages.py   (from the project root; run tools/photos.py first when photos change)

Every fact comes from research/news.json (items read and checked between 1 and 15 Oct 2026)
or from the edition; each page lists its own sources in the footer.
Never hand-edit the generated HTML.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I leaves the script's folder off the path
from common import *  # noqa: E402,F401,F403

NEWS = {it['id']: it for it in json.load(open(os.path.join(ROOT, 'research', 'news.json'), encoding='utf-8'))['items']}
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def day(iso):
    y, m, d = iso.split('-')
    return f'{int(d)} {MON[int(m) - 1]}' + ('' if y == '2026' else f' {y}')


def outlet(nid):
    s = NEWS[nid]['source']
    for cut in (',', '('):
        s = s.split(cut)[0]
    return s.strip()


def cite(nid, by=None):
    """'Outlet, 7 Oct' with a link to the item's page."""
    it = NEWS[nid]
    return f'<a href="{e(it["url"])}" rel="noopener">{e(by or outlet(nid))}, {day(it["date"])}</a>'


def src_pair(nid, what=''):
    it = NEWS[nid]
    return (f'{outlet(nid)}, {day(it["date"])}' + (f': {what}' if what else ''), it['url'])


def write(name, html_text):
    open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(html_text)
    print(name, len(html_text), 'bytes')


def page(name, title, desc, active, main, sources, credits=(), js=('pages',), ld=None, crumb=None, printable=False):
    scripts = ''.join(f'<script src="assets/js/{j}.js?v={V}" defer></script>\n' for j in ['po'] + list(js))
    lds = [crumbs((crumb or title.split(' — ')[0], name))] + list(ld or [])
    seen, uniq = set(), []
    for t, u in sources:                     # one line per report, even when a page cites it twice
        if u not in seen:
            seen.add(u)
            uniq.append((t, u))
    sources = uniq
    write(name, f'''{head(title, desc, ['home', 'pages'], name, ld=lds, printable=printable)}
<body>
<!--
{CONTRACT}
-->
<a class="skip" href="#main">Skip to the page</a>
{strip()}
{mast(active, inner=True)}
<main id="main">
{main}
</main>
{foot(sources, list(credits))}
{scripts}</body>
</html>
''')


REBAR = '<div class="rebar" aria-hidden="true">' + '<i></i>' * 7 + '</div>'


def phead(h1, dek, lid, tag, meta=''):
    return (f'<header class="phead wrap"><div class="phead-grid"><h1>{e(h1)}</h1><p class="dek">{rich(dek)}</p></div>'
            f'{meta}{line(lid, tag, REBAR)}</header>')


def credit(pid, what):
    p = PH[pid]
    return f'{what} — {p["author"]}, {p["licence"]}'


EXT = '<svg class="ext-ico" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 9L9 3M4.2 3H9v4.8"/></svg>'

# ---------- people: one block each, the unit of the site ----------
# work groups: rubble (building and rubble), land (land and sea), trades (shops and trades),
# pay (wages and aid work), none (out of work)
PEOPLE = [
    dict(n='Qassam al-Sane’e', a=35, t='Breaks reinforced concrete to free iron and tiles; built websites before the war', p='Khan Younis', r='$20', u='a day, via a middleman', g='Gaza', w='rubble', id='rubble-sanee-it-to-sledgehammer', href='article.html'),
    dict(n='Saleh Musbah', a=33, t='Breaks and carries debris for 12 hours a day; a construction worker before', p='Khan Younis', r='₪50', u='a day, about $16.50', g='Gaza', w='rubble', id='rubble-musbah-50-shekels', href='article.html#chain'),
    dict(n='Nahid Nabil Zo’rub', a=33, t='Leads a demolition crew of about 15 men, by hand', p='Buraq camp, Khan Younis', r='$16.50–30', u='a day', g='Gaza', w='rubble', id='rubble-zorub-demolition-by-hand', href='article.html#chain'),
    dict(n='Tamir Breis', a=35, t='Buys what hammer crews recover and sells it on', p='al-Amal, Khan Younis', r='$16.50–20', u='a day', g='Gaza', w='rubble', id='rubble-breis-scrap-dealer', href='article.html#chain'),
    dict(n='Warda Aliwa', a=38, t='Unpicks flour sacks into bags in a WFP cash-for-work factory', p='Gaza City', r='₪1,000', u='a month, three-month shift', g='Gaza', w='pay', id='wfp-cash-for-work-aliwa'),
    dict(n='Khaled al-Kurd', a=50, t='Builds shelves from aid pallets; lost his sewing business', p='Gaza City', r='₪1,000', u='a month', g='Gaza', w='pay', id='wfp-cash-for-work-kurd-pallets'),
    dict(n='Abu Ibrahim', a=43, t='Civil servant, paid in worn banknotes (name changed for his safety)', p='Gaza', r='₪1,500', u='every 45–50 days; it was ₪2,000 every 30–35', g='Gaza', w='pay', id='gaza-civil-servant-salary-shrinks', href='money.html#pay'),
    dict(n='Rasha Al-Dos', a=44, t='Teaching again, in a classroom with a tarp for one wall', p='Gaza City', r=None, u='pay not reported', g='Gaza', w='pay', id='teacher-al-dos-back-in-class'),
    dict(n='Hilal al-Zuwaidi', a=34, t='Runs a phone-charging point; a builder and fruit trader before', p='Gaza City', r='₪1', u='a phone; ₪2 if he lends the charger', g='Gaza', w='trades', id='zuwaidi-phone-charging'),
    dict(n='Majed Shrafi', a=30, t='Barber behind a single chair; his shop was bombed', p='Tal al-Hawa, Gaza City', r='< ₪50', u='a day: under half of the ₪80–100 his family needs', g='Gaza', w='trades', id='shrafi-barber-half-of-needs'),
    dict(n='Ahmad Mohsen', a=24, t='Sells prepaid internet cards; a nursing graduate', p='Deir el-Balah', r=None, u='pay not reported', g='Gaza', w='trades', id='mohsen-nurse-to-internet-cards'),
    dict(n='Nidaa', a=35, t='Raises poultry, ducks and rabbits on a UNDP grant; trained as a teacher', p='Khan Younis', r=None, u='pay not reported', g='Gaza', w='trades', id='undp-women-businesses-khan-younis'),
    dict(n='Nasr Ouda', a=None, t='Olive-press owner; one production line rebuilt from the rubble', p='al-Zawayda', r='1 of 7', u='press lines running again', g='Gaza', w='trades', id='gaza-olives-45-shekels-one-press-line', href='harvest.html'),
    dict(n='Ahmed Khader', a=38, t='Harvest day labourer; the season used to give him two or three months', p='Deir al-Balah', r='1 day', u='of olive work this season', g='Gaza', w='land', id='khader-one-day-of-harvest', href='harvest.html'),
    dict(n='Haidar Abu Middain', a=60, t='Olive grower with 20 or 30 trees left', p='Deir al-Balah', r='2 drums', u='of oil expected; up to 900 before', g='Gaza', w='land', id='khader-one-day-of-harvest', href='harvest.html'),
    dict(n='Kamel Baraka', a=None, t='Olive farmer working only the land he can still reach', p='Deir al-Balah', r='−70–80%', u='yield per tree; pressing costs three times more', g='Gaza', w='land', id='baraka-olive-yields-pressing-cost', href='harvest.html'),
    dict(n='Mahmoud Dweima', a=None, t='Olive grower; every tree bulldozed', p='Shuja’iyya, Gaza City', r='$13–15k', u='a year from oil before the war; nothing now', g='Gaza', w='land', id='dweima-olive-income-gone', href='harvest.html'),
    dict(n='Abu Mohammed', a=40, t='Fisherman; used to sell his catch, now stays within 500 m of shore', p='Gaza coast', r='Lunch', u='all a day at sea brings home', g='Gaza', w='land', id='fisherman-abu-mohammed-lunch-only', href='home.html#sea'),
    dict(n='Ghassan Marwan', a=53, t='Carries water for his family; a goldsmith who built a factory', p='Central Gaza', r=None, u='no work', g='Gaza', w='none', id='marwan-goldsmith-carries-water'),
    dict(n='Hakim Mar’i', a=None, t='Cannot work; injured labouring inside Israel, displaced four times', p='Tulkarem', r='Credit', u='food on credit from a shop', g='West Bank', w='none', id='hakim-mari-tulkarem-hands-empty'),
    dict(n='Bassem Yassin', a=None, t='Odd farm days in the Jordan Valley; worked inside Israel until 2023', p='Jordan Valley', r=None, u='“small amounts” only', g='West Bank', w='land', id='bassem-yassin-from-israel-to-jordan-valley'),
    dict(n='Abd al-Halim Mansour', a=None, t='Olive farmer with 500 trees, racing to pick them', p='Deir Istiya', r='₪64,000', u='for the season’s oil, if he can pick it', g='West Bank', w='land', id='mansour-deir-istiya-64000', href='harvest.html'),
    dict(n='Hazem Sanaf', a=61, t='Olive farmer; his trees were his only income', p='Beit Rima', r='400', u='trees uprooted, his and his neighbour’s', g='West Bank', w='land', id='sanaf-beit-rima-400-trees', href='harvest.html'),
    dict(n='Fares al-Dik', a=None, t='Olive farmer who cannot reach his two plots', p='Kafr ad-Dik', r='4 years', u='without reaching his 550 trees', g='West Bank', w='land', id='al-dik-550-trees-out-of-reach', href='harvest.html'),
]
WORK = [('all', 'Everyone'), ('rubble', 'Rubble'), ('land', 'Land & sea'), ('trades', 'Shops & trades'), ('pay', 'Wages & aid work'), ('none', 'Out of work')]


PLACES = {'Khan Younis': 'khan-younis.html'}


def place_link(text):
    for name, href in PLACES.items():
        if name in text:
            return e(text).replace(e(name), f'<a href="{href}">{e(name)}</a>', 1)
    return e(text)


def pblock(p, cls='w', old=None):
    it = NEWS[p['id']]
    if old is None:
        old = it['date'] < '2026-10-01'          # reports from before this month sit on the older face
    age = f', {p["a"]}' if p.get('a') else ''
    href = p.get('href') or it['url']
    ext = not p.get('href')
    rate = (f'<p class="rate num">{e(p["r"])}<small>{e(p["u"])}</small></p>' if p['r']
            else f'<p class="rate rate--none">{e(p["u"].capitalize())}</p>')
    rel = ' rel="noopener"' if ext else ''
    when = f'<p class="when">{e(outlet(p["id"]))}, {day(it["date"])}{EXT if ext else ""}</p>'
    return (f'<article class="blk who {cls}{" ext" if ext else ""}{" blk--old" if old else ""}" data-g="{e(p["g"])}" data-w="{p["w"]}">'
            f'<h3><a href="{e(href)}"{rel}>{e(p["n"])}{age}</a></h3>'
            f'<p class="trade">{e(p["t"])}</p><p class="place">{place_link(p["p"])}</p>{rate}{when}</article>')


def find_person(name):
    return next(p for p in PEOPLE if p['n'] == name)


# =====================================================================
# article.html — the lead story
# =====================================================================
q = find_person('Qassam al-Sane’e')
art_sources = [src_pair('rubble-sanee-it-to-sledgehammer', 'the rubble trade'),
               src_pair('gaza-rubble-61m-tonnes-1-5pct-cleared', 'Gaza’s rubble'),
               src_pair('gaza-construction-1pct-of-2022', 'construction at 1%')]
article_main = f'''<div class="wrap"><article class="art" aria-labelledby="art-h">
<div>
<h1 id="art-h">He used to design websites. Now he breaks concrete for $20 a day</h1>
<p class="dek">In Khan Younis, where almost no bulldozers work, the city’s rubble is cleared by hand. Qassam al-Sane’e, 35, is one link in a trade that runs from the hammer to the tent.</p>
<p class="byline"><span><b>Rewritten by Pal-Online</b> from Fedaa al-Qedra’s report for The Electronic Intifada, 25 Sep (republished by Countercurrents, 26 Sep)</span><span>Figures: Arab News and Al Jazeera, 7 Oct</span><span>4 min read</span></p>
<figure class="opening">{img('gaza-man-on-rubble', 'A man stands on a mound of concrete rubble and twisted debris from collapsed houses in Gaza.', sizes='(max-width:1100px) 100vw, 860px', eager=True)}
<figcaption>Rubble of destroyed houses, Gaza, 2023–25. Photo: Jaber Jehad Badwan, CC BY-SA 4.0, Wikimedia Commons. Not the man named.</figcaption></figure>
<div class="body">
<p>Qassam al-Sane’e used to build websites and repair computers. The war took his computer, his work and his home in Rafah. Now, in the ruins of Khan Younis, he swings a sledgehammer into reinforced concrete to free what can still be sold: iron, tiles, wood, pipes and cable.</p>
<p>A middleman pays him about <b>$20 a day</b>. On it he supports six children, and he sends money to his mother, who is on dialysis in Egypt.</p>
<blockquote class="pull">“Never, never. I never even thought for a day that I would do this kind of work.”<footer>Qassam al-Sane’e, to Fedaa al-Qedra</footer></blockquote>
<h2>No machines</h2>
<p>The work is dangerous and done without protection. The crews have no face masks, and they have found missile fragments in the debris.</p>
<p>Nahid Nabil Zo’rub, 33, has worked in demolition for more than ten years. With most heavy machinery destroyed and fuel scarce, his crew of about 15 men breaks concrete with hammers. A building that took two or three days to bring down now takes <b>three or four weeks</b>. At one site the team found human remains and six unexploded rockets and shells.</p>
<p>Saleh Musbah, 33, was a construction worker before the war. He breaks and carries debris for about 12 hours a day for <b>50 shekels</b>, about $16.50, and around ten people live on his pay. Injuries from falling concrete, he says, are routine.</p>
<p>Tamir Breis, 35, buys what the hammer crews recover and sells it on: tiles to cover the mud floors of tents, wood for shelters, iron for tent frames or for a sorting centre. He has been displaced nine times and lives in a tent where his house stood.</p>
<h2>Sixty-one million tonnes</h2>
<p>The trade exists because of the scale of what has to be moved. UN figures put Gaza’s rubble at <b>61 million tonnes</b>. By early October about 907,000 tonnes had been removed, roughly 1.5 percent, a third of it recycled, using seven crushers that were in Gaza before the war, two of them rebuilt by local engineers, {cite("gaza-rubble-61m-tonnes-1-5pct-cleared")} reported. At this pace the UN estimates clearance will take seven to fourteen years.</p>
<p>Construction itself is running at <b>1 percent</b> of its 2022 output, {cite("gaza-construction-1pct-of-2022")} reported, citing UNCTAD; the same review puts unemployment in Gaza at 78 percent.</p>
<p>For the men on the rubble the arithmetic is shorter. “Fifty shekels, what can that do?” Musbah asked.</p>
</div>
<div class="share" aria-label="Share this story">
<button type="button" data-copy>Copy link</button>
<a href="https://wa.me/?text=He%20used%20to%20design%20websites.%20Now%20he%20breaks%20concrete%20for%20%2420%20a%20day%20{SITE}article.html" rel="noopener">WhatsApp</a>
<a href="https://t.me/share/url?url={SITE}article.html" rel="noopener">Telegram</a>
<a href="https://x.com/intent/post?url={SITE}article.html" rel="noopener">X</a>
<a href="tell.html">Report an error</a>
</div>
</div>
<aside class="aside" aria-label="The person in this story and our sources">
<div class="blk idb">
<h2>Qassam al-Sane’e, 35</h2>
<p class="lbl">Was</p><p class="was"><span class="spray">Web designer and repair-shop technician</span></p>
<p class="lbl">Now</p><p class="now">Breaks reinforced concrete for iron and tiles</p>
<p class="lbl">Where</p><p class="now"><a href="khan-younis.html">Khan Younis</a>; displaced from Rafah</p>
<p class="rate num">$20<small>a day, paid by a middleman</small></p>
<span class="chalk">6 children on his pay</span>
</div>
<div class="howknow"><h2>How we know</h2><ul>
<li>{OPEN}<span>Names, ages, rates and quotes: {cite("rubble-sanee-it-to-sledgehammer", "Fedaa al-Qedra, The Electronic Intifada")}</span></li>
<li>{OPEN}<span>Rubble, crushers and clearance time: {cite("gaza-rubble-61m-tonnes-1-5pct-cleared")}</span></li>
<li>{OPEN}<span>Construction output and unemployment: {cite("gaza-construction-1pct-of-2022")}, citing UNCTAD</span></li>
<li>{LIMIT}<span>Rates are as each worker told the reporter. Pal-Online did not interview them.</span></li>
<li>{LIMIT}<span>The photograph does not show the people named.</span></li>
</ul></div>
</aside>
</article></div>
{chain()}
<section class="pblock wrap" aria-labelledby="more-h"><div class="sec-head"><h2 id="more-h">More people at work</h2><p>From the wall: everyone Pal-Online has written about, with what they are paid. <a href="wall.html">See the whole wall</a></p></div>
<div class="wall more lay" data-bond>{"".join(pblock(find_person(n)) for n in ["Hilal al-Zuwaidi", "Abu Ibrahim", "Ahmed Khader", "Majed Shrafi"])}</div></section>'''
ART_LD = {'@context': 'https://schema.org', '@type': 'NewsArticle',
          'headline': 'He used to design websites. Now he breaks concrete for $20 a day',
          'description': 'In Khan Younis the rubble is cleared by hand. Qassam al-Sane’e, 35, is one link in a trade that runs from the hammer to the tent.',
          'image': [SITE + 'assets/img/photo/gaza-man-on-rubble-1800.webp', SITE + 'assets/og.png'],
          'datePublished': '2026-10-15', 'dateModified': '2026-10-15', 'inLanguage': 'en',
          'author': ORG, 'publisher': ORG, 'mainEntityOfPage': SITE + 'article.html',
          'contentLocation': {'@type': 'Place', 'name': 'Khan Younis, Gaza'},
          'isBasedOn': NEWS['rubble-sanee-it-to-sledgehammer']['url'],
          'about': [{'@type': 'Person', 'name': 'Qassam al-Sane’e', 'jobTitle': 'Rubble worker'}]}
page('article.html', 'He used to design websites. Now he breaks concrete for $20 a day — Pal-Online',
     'In Khan Younis the rubble is cleared by hand. Qassam al-Sane’e, 35, is one link in a trade that runs from the hammer to the tent.',
     'home', article_main, art_sources, [credit('gaza-man-on-rubble', 'Rubble of destroyed houses, Gaza, 2023–25')], ld=[ART_LD], crumb='The rubble trade', printable=True)

# =====================================================================
# wall.html — everyone we have met
# =====================================================================
groups = ''.join(f'<button type="button" data-w="{k}" aria-pressed="{"true" if k == "all" else "false"}">{t}</button>' for k, t in WORK)
regions = ''.join(f'<button type="button" data-g="{k}" aria-pressed="{"true" if k == "all" else "false"}">{t}</button>'
                  for k, t in [('all', 'Everywhere'), ('Gaza', 'Gaza'), ('West Bank', 'West Bank')])
wall_main = (phead('The wall', 'Everyone Pal-Online has written about, each with a trade, a place and what they are paid, as they told the reporter. One block a person.',
                   'line-wall', f'The wall · <b>{len(PEOPLE)} people · newest on top</b>')
             + f'''<section class="wrap" aria-labelledby="ppl-h"><h2 class="sr" id="ppl-h">People on the wall</h2>
<div class="filters"><div role="group" aria-label="Where"><span class="lab">WHERE</span>{regions}</div>
<div role="group" aria-label="Work"><span class="lab">WORK</span>{groups}</div>
<p class="tally" aria-live="polite"><b>{len(PEOPLE)}</b> people</p></div>
<div class="wall people lay" data-bond data-line="line-wall"><a class="blk--gap w gapblk" href="tell.html" data-g="all" data-w="all"><span>Your block</span><small>Tell us your work</small></a>{"".join(pblock(p) for p in sorted(PEOPLE, key=lambda p: NEWS[p['id']]['date'], reverse=True))}
<div class="empty" hidden><p>No one on the wall matches both. <a href="tell.html">Tell us your work</a> and yours can be the first block here.</p></div></div>
<p class="note"><b>One older report:</b> Abu Mohammed’s story was published by The Palestine Chronicle on 14 January 2026 and is kept because nothing on Gaza’s boats has changed since. Blocks with an arrow open the original report; the others open a Pal-Online page.</p>
</section>''')
wall_sources = sorted({src_pair(p['id']) for p in PEOPLE}, key=lambda s: s[0])
page('wall.html', 'The wall: everyone we have met — Pal-Online', 'Everyone Pal-Online has written about, with their trade, place and pay.',
     'wall', wall_main, wall_sources)

# =====================================================================
# money.html
# =====================================================================
fx = NEWS['fx-shekel-dollar-dinar-oct15']
fuel = NEWS['fuel-october-petrol-cut']
rates_wall = ''.join(
    f'<div class="slab fx {c}"><h3>{t}</h3><p class="rate num">{r}</p><p class="bs">{bs}</p></div>' for c, t, r, bs in [
        ('w', 'US dollar', '₪3.05', 'buy 3.05 · sell 3.09 · SadaNews, 15 Oct'),
        ('w', 'Jordanian dinar', '₪4.31', 'buy 4.31 · sell 4.39 · SadaNews, 15 Oct'),
        ('w', 'Euro', '₪3.42', 'buy 3.42 · sell 3.46 · SadaNews, 15 Oct'),
        ('w', 'Dollar, September average', '₪3.03', 'PCBS, 14 Oct'),
        ('h', 'Petrol 95', '₪7.67', 'a litre, from 5 Oct'),
        ('w', 'Diesel', '₪8.99', 'a litre, unchanged for October'),
        ('w', 'Cooking gas', '₪90', 'a 12 kg cylinder'),
        ('w', 'Petrol 98', '₪9.73', 'a litre'),
        ('h', 'Subsidy', '₪10m', 'extra for October')])
gap = ''.join('<span></span>' for _ in range(8)) + '<span class="maybe"></span>' + ''.join('<span class="short"></span>' for _ in range(6))
months = ''.join(f'<span title="Month {i + 1}">{XMARK}</span>' for i in range(18))
prices = [
    ('Gaza prices, September', 'Consumer price index, month on month', '+11.36%', 'pcbs-cpi-september-gaza-up-11pct', 'w'),
    ('White flour, 25 kg', 'Gaza, September average', '₪56', 'price-levels-flour-56-shekels', 'w'),
    ('Two dozen eggs', 'Gaza City market', '₪30', 'gaza-city-market-eggs-potatoes', 'w'),
    ('One potato', 'Gaza City market', '₪5', 'gaza-city-market-eggs-potatoes', 'w'),
    ('Olives, a kilo', 'Khan Younis market, first time in three years', '₪45', 'gaza-olives-45-shekels-one-press-line', 'w'),
    ('Olive oil, a drum', 'Deir al-Balah, about triple pre-war', '~$500', 'khader-one-day-of-harvest', 'w'),
    ('Generator power', 'a kilowatt-hour, Gaza City', '₪30–35', 'zuwaidi-phone-charging', 'w'),
    ('Frozen beef, a kilo', 'Gaza, September average', '₪41', 'price-levels-flour-56-shekels', 'w'),
    ('Eggs, 2 kg carton', 'West Bank, September average', '₪15', 'price-levels-flour-56-shekels', 'w'),
    ('Tomatoes, a kilo', 'West Bank, September average', '₪7', 'price-levels-flour-56-shekels', 'w'),
    ('West Bank prices, September', 'Consumer price index, month on month', '+0.53%', 'pcbs-cpi-september-gaza-up-11pct', 'w'),
    ('A family tent', 'Al-Maqousi camp, Gaza City', '₪2,000', 'gaza-city-market-eggs-potatoes', 'w')]
prices_html = ''.join(f'<article class="slab price {c}"><h3>{e(t)}</h3><p class="where">{e(w)}</p><p class="rate num">{e(v)}</p>'
                      f'<p class="src">{cite(nid)}</p></article>' for t, w, v, nid, c in prices)
money_main = (phead('Money', 'Salaries, prices and cash, told by what they do to a working week.', 'line-money',
                    'Money · <b>rates of 15 Oct, prices of September</b>')
              + f'''<section class="wrap" id="pay" aria-labelledby="pay-h"><h2 class="sr" id="pay-h">A payslip first</h2>
<div class="pane"><div class="wall" style="--halves:2">{pblock(find_person('Abu Ibrahim'), old=False).replace('href="money.html#pay"', 'href="https://mondoweiss.net/2026/10/in-gaza-even-cash-comes-at-a-cost/" rel="noopener"')}</div>
<div><h3>A Gaza payslip</h3>
<div class="pay"><p class="was num">₪2,000<small>every 30–35 days</small></p>{ARROW}<p class="now num">₪1,500<small>every 45–50 days</small></p></div>
<p class="note">Abu Ibrahim, 43, a civil servant in Gaza (name changed for his safety), says 100 shekels once fed his family for a week and now does not cover a day’s food. Shopkeepers resist his worn notes. {cite("gaza-civil-servant-salary-shrinks")}</p></div></div></section>
<section class="pblock wrap" aria-labelledby="fx-h"><div class="sec-head"><h2 id="fx-h">At the changer</h2><p>Rates against the shekel and the price at the pump.</p></div>
<div class="wall rates-wall">{rates_wall}</div>
<p class="note">Exchange rates: {cite("fx-shekel-dollar-dinar-oct15", "SadaNews currency table")}. Fuel: {cite("fuel-october-petrol-cut", "SadaNews, General Petroleum Authority and Ministry of Finance")}.</p></section>
<section class="pblock wrap" aria-labelledby="sal-h"><div class="sec-head"><h2 id="sal-h">Salaries</h2><p>The Palestinian Authority pays part of each salary, late; in Gaza, wages come smaller, slower and in worn notes.</p></div>
<div class="pane"><div>
<h3>The treasury’s month</h3>
<p class="big num">₪1.5bn<small>needed every month</small></p>
<div class="gap-row" role="img" aria-label="Fifteen blocks of 100 million shekels: eight available, one possibly available, six short">{gap}</div>
<p class="gap-key"><span><i></i>Available, ₪100m each</span><span><i class="m"></i>₪800m or ₪850m: the minister gave both</span><span><i class="s"></i>Short</span></p>
<p class="note">Finance minister Istifan Salameh: the government needs about ₪1.5bn a month and has ₪800–850m for salaries and basic services. Half a salary is the floor; more than 51% of employees receive 80% or more. {cite("salameh-needs-1-5bn-has-850m", "WAFA")}</p>
<h3 style="margin-top:30px">June’s pay, in September</h3>
<p class="big num">50%<small>of June’s salary, at least ₪2,000, paid 23 Sep</small></p>
<p class="note">No announcement of July’s salary had been made by 15 October. {cite("pa-june-salaries-50pct", "Ministry of Finance via WAFA")}</p>
</div><div>
<h3>Eighteen months withheld</h3>
<div class="months" role="img" aria-label="Eighteen months, each marked as withheld">{months}</div>
<p class="note">Israel has withheld the clearance revenues it collects for the Palestinian Authority, about <b>68%</b> of public revenue, for an 18th consecutive month. {cite("pa-wage-bill-18th-month")}</p>
<h3 style="margin-top:30px">UNRWA</h3>
<p class="big num">$100m<small>short in its 2026 core budget</small></p>
<p class="note">The agency has cut some staff’s working hours and salaries, and school and clinic hours. {cite("unrwa-100m-gap-salary-cuts")}</p>
</div></div></section>
<section class="pblock wrap" aria-labelledby="cash-h"><div class="sec-head"><h2 id="cash-h">Cash</h2><p>In Gaza a banknote is worth less than its face once it is worn.</p></div>
<div class="pane"><div><p class="big num">10%<small>charged to accept worn notes</small></p>
<p class="note">Muhammad Hussam, 38, displaced from Shuja’iyya, had 200 shekels of aid cash refused for apples; a second seller took it only with a 10% cut. At the height of the war people paid up to 50% to turn bank balances into cash. Gaza’s media office says refusing legal notes, or charging to accept them, has been criminalised. {cite("gaza-cash-commission-10pct")}</p></div>
<div><p class="big num">₪6,000<small>above which payments must be electronic</small></p>
<p class="note">The cap cited by economist Sami al-Khaldi in the same report.</p>
<blockquote class="pull" style="margin-top:18px;border-top:6px solid var(--line);padding-top:14px;font:800 24px/1.2 var(--display)">“Now, some sellers demand 120 shekels in cash for goods worth only 100 shekels.”<footer style="font:550 14px/1.45 var(--text);color:var(--ink-2);margin-top:8px">Abu Ibrahim, to Mondoweiss</footer></blockquote></div></div></section>
<section class="pblock wrap" aria-labelledby="prices-h"><div class="sec-head"><h2 id="prices-h">Prices</h2><p>What things cost in September and the first half of October. Gaza prices are still far above what they were before the war, and moving fast.</p></div>
<figure class="opening wide" style="margin:0 0 var(--joint)">{img('nablus-spice-prices-2011', 'Open sacks of spices in a Nablus market with handwritten Arabic and English price cards.', sizes='100vw')}<figcaption class="note">Handwritten prices in Nablus’s old city, 2011 (archive). Photo: Wikimedia Commons, see credits below.</figcaption></figure>
<div class="wall prices">{prices_html}</div></section>''')
money_ids = ['fx-shekel-dollar-dinar-oct15', 'fuel-october-petrol-cut', 'salameh-needs-1-5bn-has-850m', 'pa-june-salaries-50pct',
             'pa-wage-bill-18th-month', 'gaza-civil-servant-salary-shrinks', 'unrwa-100m-gap-salary-cuts', 'gaza-cash-commission-10pct',
             'pcbs-cpi-september-gaza-up-11pct', 'price-levels-flour-56-shekels', 'gaza-city-market-eggs-potatoes',
             'gaza-olives-45-shekels-one-press-line', 'khader-one-day-of-harvest', 'zuwaidi-phone-charging']
page('money.html', 'Money — Pal-Online', 'Salaries, prices and cash in Palestine, with the source and date of every figure.', 'money', money_main,
     [src_pair(i) for i in money_ids], [credit('nablus-spice-prices-2011', 'Spice prices, Nablus old city, 2011')])

# =====================================================================
# moving.html — the board
# =====================================================================
ROADS = [
    ('Gaza', 'limited', 'Open, limited', 'Kerem Shalom', 'Gaza–Israel, goods', 'The only cargo crossing working. Traders collected 788 truckloads between 21 and 27 September, about 10% below the four-week average of 871.', 'kerem-shalom-only-cargo-crossing'),
    ('Gaza', 'closed', 'Closed since 24 May', 'Zikim', 'Gaza–Israel, goods, north', 'Shut for nearly five months, leaving the north to goods brought from the south.', 'kerem-shalom-only-cargo-crossing'),
    ('Gaza', 'limited', '15 trucks a week', 'Shelter materials from Jordan', 'Offloaded at Kerem Shalom one day a week', 'At this pace 500 truckloads of shelter items would take more than seven months. Timber, cement and metal sheeting for repairs are still blocked.', 'nrc-15-trucks-a-week-cement-blocked'),
    ('West Bank', 'closed', 'Barred despite coordination', 'Farmland south and south-west of Jenin', 'Fandaqumiya, Jaba’, Silat al-Dhahr, around Tarsala', 'Tear gas fired at farmers heading to the harvest; hundreds of families barred from their land on 13 and 14 October.', 'jenin-farmers-barred-despite-coordination'),
    ('West Bank', 'closed', 'Owners turned away', 'Deir Istiya, Farkha, Haris, az-Zawiya, Silwan', 'Olive groves', 'In the harvest’s first days owners were sent back from their own land, their ID cards and sometimes their tools taken.', 'farmers-turned-away-ids-taken'),
    ('West Bank', 'closed', 'Out of reach for four years', 'Kafr ad-Dik groves', 'Two plots north of the village', 'Fares al-Dik has not reached his 550 olive trees in four years.', 'al-dik-550-trees-out-of-reach'),
    ('West Bank', 'limited', 'Waits of up to four hours', 'Awarta checkpoint', 'Nablus', 'Milk trucks from Al-Kamel Dairy wait up to four hours; sales fell 30–40% and at least 12 workers were laid off.', 'checkpoints-cost-working-hours'),
    ('West Bank', 'closed', 'Closed 27 Sep–3 Oct', 'Settlements and industrial zones', 'Holiday “general closure”', 'Palestinian labourers were kept out through Sukkot; about 9,000 hold permits for settlements or nearby industrial zones. No later report of the permits’ state.', 'sukkot-closure-workers-barred'),
]
board = ''.join(f'<li data-g="{g}">{mark(st)}<div><h3>{e(pl)}</h3><p class="state">{e(lbl)}</p><p class="kind">{e(kind)}</p></div>'
                f'<p class="eff">{e(eff)}</p><p class="src">{cite(nid)}</p></li>' for g, st, lbl, pl, kind, eff, nid in ROADS)
stats = [('925', 'checkpoints and military gates in the West Bank, 147 of them in Nablus governorate', 'checkpoints-cost-working-hours', 'Colonization and Wall Resistance Commission'),
         ('191,146', 'working hours lost to checkpoint delays every day, about ₪2.8m', 'checkpoints-cost-working-hours', 'MAS study'),
         ('+20%', 'transport costs since checkpoint and gate closures', 'bassem-yassin-from-israel-to-jordan-valley', 'Federation of Chambers of Commerce'),
         ('737', 'olive plots where coordination is required or Israelis are barred, 70 more than last year', 'mansour-deir-istiya-64000', 'Israeli Civil Administration')]
stats_html = ''.join(f'<div class="slab stat w"><p class="rate num">{v}</p><p>{e(t)}</p><p class="src">{e(by)}, via {cite(nid)}</p></div>' for v, t, nid, by in stats)
moving_main = (phead('Moving', 'Crossings, gates, checkpoints and closed land: the state of each place that decides whether people reach their work.',
                     'line-moving', f'Moving · <b>{len(ROADS)} places · reports of 10 Sep–14 Oct</b>')
               + f'''<section class="wrap" aria-labelledby="board-h"><h2 class="sr" id="board-h">The board</h2>
<div class="filters"><div role="group" aria-label="Where"><span class="lab">WHERE</span>
<button type="button" data-g="all" aria-pressed="true">Everywhere</button><button type="button" data-g="Gaza" aria-pressed="false">Gaza</button><button type="button" data-g="West Bank" aria-pressed="false">West Bank</button></div>
<p class="legend" aria-label="What the marks mean"><span>{XMARK}Closed or barred</span><span>{LIMIT}Open, limited or slow</span><span>{OPEN}Open</span></p></div>
<ul class="board" data-board>{board}</ul>
<p class="note">Each place keeps its last reported state and the date of that report. No report, no mark: a place drops off the board when nobody has reported on it for a month.</p></section>
<section class="pblock wrap" aria-labelledby="cost-h"><div class="sec-head"><h2 id="cost-h">What the closures cost</h2><p>Counts from the West Bank, each with who counted.</p></div>
<div class="wall stats">{stats_html}</div></section>
<section class="pblock wrap" aria-labelledby="ph-h"><h2 class="sr" id="ph-h">Photograph</h2>
<figure class="opening wide" style="margin:0">{img('qalandia-queue-2019', 'People queue in a narrow roofed corridor between perforated metal panels inside the Qalandia checkpoint terminal.', sizes='100vw')}
<figcaption class="note">Inside the Qalandia checkpoint terminal on its opening day, February 2019 (archive). Photo: Wikimedia Commons, see credits below.</figcaption></figure></section>''')
page('moving.html', 'Moving: crossings, gates and closed land — Pal-Online', 'The state of each crossing, gate and checkpoint that decides whether Palestinians reach their work.',
     'moving', moving_main, sorted({src_pair(r[-1]) for r in ROADS} | {src_pair('bassem-yassin-from-israel-to-jordan-valley'), src_pair('mansour-deir-istiya-64000')}),
     [credit('qalandia-queue-2019', 'Qalandia checkpoint terminal, 2019')])

# =====================================================================
# count.html
# =====================================================================
FIGS = [
    ('68%', 68, 'unemployment in Gaza', 'Gaza Ministry of Labour', 'gaza-labour-ministry-68pct', 'A statement on the war’s damage to the labour market.'),
    ('74%', 74, 'of Gaza’s workers who lost their jobs and are now unemployed or outside the labour force', 'Gaza Ministry of Labour', 'gaza-labour-ministry-68pct', 'Counts people who stopped looking, too.'),
    ('78%', 78, 'unemployment in Gaza in 2025', 'UNCTAD, via Al Jazeera', 'gaza-construction-1pct-of-2022', 'A yearly figure, not this month’s.'),
    ('~80%', 80, 'unemployment in Gaza', 'Palestinian General Federation of Trade Unions', 'pgftu-570k-unemployed', 'Released in early July; cited on 13 Oct.'),
    ('90%+', 91, 'of Gaza’s working-age population unemployed', 'UNCTAD annual report, via Al Jazeera', 'unctad-90pct-working-age-jobless', 'Working age, not labour force: the base is everyone of working age.'),
    ('27.9%', 28, 'unemployment in the West Bank, April–June', 'Palestinian Central Bureau of Statistics', 'pcbs-west-bank-lfs-q2-2026', 'The latest labour-force survey; 29.5% in January–March.'),
    ('38%', 38, 'unemployment in the West Bank', 'Palestinian General Federation of Trade Unions', 'pgftu-570k-unemployed', 'Released in early July.'),
    ('85%', 85, 'of people forced from the Jenin, Tulkarem and Nur Shams camps with no regular income', 'UNRWA, via Al Jazeera', 'unrwa-85pct-displaced-no-income', 'About 33,000 people were forced out in early 2025.'),
]
btns = ''.join(f'<button class="fig-btn" type="button" aria-pressed="{"true" if i == 0 else "false"}" data-out="{o}" '
               f'data-cap="{e(v)} — {e(w)}: {e(by)}, {day(NEWS[nid]["date"])}."><span class="big num">{e(v)}</span>'
               f'<span class="what">{e(w)}</span><span class="who-said">{e(by)}, {day(NEWS[nid]["date"])}</span></button>'
               for i, (v, o, w, by, nid, _) in enumerate(FIGS))
cells = ''
for r in range(10):
    row = ''.join(f'<span{" class=" + chr(34) + "is-out" + chr(34) if r * 10 + c < FIGS[0][1] else ""}></span>' for c in range(10))
    cells += f'<div class="crs">{row}{"<span class=bat></span>" if r % 2 else ""}</div>'
table = ''.join(f'<tr><td class="n">{e(v)}</td><td>{e(w)}<br><span class="src">{e(note)}</span></td><td>{cite(nid, by)}</td></tr>'
                for v, o, w, by, nid, note in FIGS)


def mini(n):
    return '<div class="mini" aria-hidden="true">' + ''.join(f'<i{" class=o" if i >= n else ""}></i>' for i in range(100)) + '</div>'


def bars(rows):
    top = max(v for _, v, _ in rows)
    return '<div class="bars" aria-hidden="true">' + ''.join(
        f'<div><span style="width:auto;background:none;height:auto">{e(lbl)}</span><span class="{c}" style="width:{max(2, round(v / top * 100))}%"></span></div>'
        for lbl, v, c in rows) + '</div>'


DB = [
    ('A day’s wage', '₪134.3', 'average daily wage in the West Bank; ₪263.4 in Israel and the settlements', bars([('West Bank', 134.3, ''), ('Israel', 263.4, 'l')]), 'pcbs-west-bank-lfs-q2-2026', 'PCBS'),
    ('Working in Israel', '~53,000', 'West Bank residents employed in Israel (about 35,000) and the settlements (about 17,600)', '', 'pcbs-west-bank-lfs-q2-2026', 'PCBS'),
    ('Under the minimum wage', '15.5%', 'of West Bank private-sector employees earn below the ₪1,880 monthly minimum', mini(16), 'pcbs-west-bank-lfs-q2-2026', 'PCBS'),
    ('Young graduates', '38.3%', 'unemployment among West Bank graduates aged 19–29; 51.2% for women', mini(38), 'pcbs-west-bank-lfs-q2-2026', 'PCBS'),
    ('Out of school and work', '74%', 'of 15–29-year-olds in Gaza not in education, training or work', mini(74), 'gaza-labour-ministry-68pct', 'Gaza Ministry of Labour'),
    ('Building', '1%', 'of 2022 construction output; agriculture and industry at 6%', bars([('Construction', 1, 'l'), ('Farms, industry', 6, ''), ('2022', 100, '')]), 'gaza-construction-1pct-of-2022', 'UNCTAD via Al Jazeera'),
    ('Workplaces', '92%', 'of Gaza’s economic establishments damaged or destroyed', mini(92), 'unctad-90pct-working-age-jobless', 'UNCTAD via Al Jazeera'),
    ('Rubble cleared', '1.5%', 'of 61 million tonnes, about 907,000 tonnes, a third recycled; seven crushers', mini(2), 'gaza-rubble-61m-tonnes-1-5pct-cleared', 'Arab News'),
    ('Wages erased', '$2.8bn', 'cumulative labour income erased in the occupied Palestinian territory', '', 'unctad-90pct-working-age-jobless', 'UNCTAD via Al Jazeera'),
    ('On the way to work', '52', 'workers killed going to or at work; more than 38,000 workers arrested', '', 'pgftu-570k-unemployed', 'PGFTU via Palestinian Information Center'),
    ('Herds', '17,000', 'sheep left in the northern Jordan Valley, from about 30,000; cattle from about 2,000 to 500', bars([('Sheep before', 30000, ''), ('Sheep now', 17000, 'l')]), 'jordan-valley-herds-halved', 'Northern Jordan Valley Agriculture Dept'),
    ('Hours at checkpoints', '191,146', 'working hours lost to checkpoint delays every day', '', 'checkpoints-cost-working-hours', 'MAS study via Al Jazeera'),
]
db_html = ''.join(f'<article class="slab dblk w"><h3>{e(h)}</h3><p class="rate num">{e(v)}</p><p>{e(t)}</p>{viz}<p class="src">{e(by)}, {cite(nid)}</p></article>'
                  for h, v, t, viz, nid, by in DB)
count_main = (phead('The count', 'How many are out of work depends on who counts, what they count and when. Every figure here keeps its source, its date and what it measures; none is averaged with another.',
                    'line-count', f'The count · <b>{len(FIGS) + len(DB)} figures from 10 sources</b>')
              + f'''<section class="wrap" aria-label="Unemployment, by who counts"><div class="count"><div><div class="figs" role="group" aria-label="Choose whose figure the wall shows">{btns}</div></div>
<div><div class="hundred" aria-hidden="true">{cells}</div><p class="count-cap" aria-live="polite">{e(FIGS[0][0])} — {e(FIGS[0][2])}: {e(FIGS[0][3])}, {day(NEWS[FIGS[0][4]]["date"])}.</p>
<p class="note">The wall is a hundred people. Pick a figure and that many blocks come out. Percentages above 90 are shown as 91.</p></div></div></section>
<section class="pblock wrap" aria-labelledby="wc-h"><div class="sec-head"><h2 id="wc-h">Who counts what</h2><p>The same question, asked of different people, on different dates.</p></div>
<table class="who-counts"><thead><tr><th>Figure</th><th>What it measures</th><th>Who, when</th></tr></thead><tbody>{table}</tbody></table></section>
<section class="pblock wrap" aria-labelledby="oc-h"><div class="sec-head"><h2 id="oc-h">Other counts</h2><p>Wages, workplaces and what the war has taken, each cast on the slab, kept apart from the people.</p></div>
<div class="wall dblocks">{db_html}</div></section>''')
count_ids = sorted({f[4] for f in FIGS} | {d[4] for d in DB})
page('count.html', 'The count: who is out of work, by who counts — Pal-Online', 'Unemployment and work in Gaza and the West Bank, every figure with its source and date.',
     'count', count_main, [src_pair(i) for i in count_ids], js=('pages', 'home'))

# =====================================================================
# harvest.html
# =====================================================================
gaza_people = ''.join(pblock(find_person(n)) for n in ['Ahmed Khader', 'Haidar Abu Middain', 'Kamel Baraka', 'Mahmoud Dweima', 'Nasr Ouda'])
wb_people = ''.join(pblock(find_person(n)) for n in ['Abd al-Halim Mansour', 'Hazem Sanaf', 'Fares al-Dik'])
G_FIGS = [('~150,000', 'of 2 million olive trees still standing', 'khader-one-day-of-harvest', 'Gaza agriculture authorities via Reuters'),
          ('700 t', 'of oil expected, instead of the usual 5,000', 'khader-one-day-of-harvest', 'Reuters'),
          ('9', 'olive presses working, from 41 in 2022 (Reuters was told 7 of about 40)', 'dweima-olive-income-gone', 'Gaza Ministry of Agriculture via Mondoweiss'),
          ('22,000+', 'daily work opportunities the season gave before the war', 'dweima-olive-income-gone', 'Gaza Ministry of Agriculture via Mondoweiss'),
          ('₪45', 'a kilo of olives in Khan Younis, on sale for the first time in three years', 'gaza-olives-45-shekels-one-press-line', 'Palestinian Information Center')]
W_FIGS = [('219', 'settler attacks in the first 12 days of October; 136 tied to the harvest', 'harvest-attacks-219-in-12-days', 'Wall and Settlement Resistance Commission via WAFA'),
          ('109', 'harvest-related incidents in 75 communities, 27 Sep–6 Oct', 'sanaf-beit-rima-400-trees', 'Yesh Din via Al Jazeera'),
          ('~50,000', 'trees destroyed by settlers and soldiers this year', 'sanaf-beit-rima-400-trees', 'Colonization and Wall Resistance Commission via Al Jazeera'),
          ('737', 'plots where coordination is required or Israelis are barred, 70 more than last year', 'mansour-deir-istiya-64000', 'Israeli Civil Administration via The Times of Israel'),
          ('100,000+', 'families rely on the olive industry', 'mansour-deir-istiya-64000', 'Israeli Civil Administration via The Times of Israel')]


def figs2(rows):
    return '<ul class="figs2">' + ''.join(f'<li><span class="v num">{e(v)}</span><p>{e(t)}<span class="src">{e(by)}, {cite(nid)}</span></p></li>' for v, t, nid, by in rows) + '</ul>'


harvest_main = (phead('The olive harvest, 2026', 'The season officially opened on 15 October. In Gaza most of the trees are gone. In the West Bank the trees stand, and the way to them is closed.',
                      'line-harvest', 'Olive harvest · <b>reports of 6–14 Oct · 8 people</b>')
                + f'''<section class="wrap split" aria-label="Gaza and the West Bank">
<section aria-labelledby="hg-h"><h2 id="hg-h">Gaza: the trees are gone</h2>
<p class="sub">Farms near the “yellow line” and east of Salah al-Din Street are out of reach; fertiliser, water, labour and containers are short, and pressing costs about three times what it did.</p>
<div class="wall lay" data-bond>{gaza_people}</div>{figs2(G_FIGS)}<div class="mourn"><h3>Ali Al Bazzari, 44</h3><p>A farmer and father of four, killed on 7 October when settlers on tractors opened fire on farmers between Ramin and Burqa, near Nablus. His cousin says eight people were hurt, two by gunfire. {cite("bazzari-killed-in-his-grove")}</p><q>He irrigated the tree with his blood.</q><p>Abdul Latif Al Bazzari, his cousin</p></div></section>
<section aria-labelledby="hw-h"><h2 id="hw-h">West Bank: the way is closed</h2>
<figure class="opening">{img('olive-picker-hands-nablus', 'A man in a cap, seen from behind, picks olives from a branch with both hands.', sizes='(max-width:860px) 100vw, 50vw', eager=True)}<figcaption>Picking olives near Nablus (archive, date not recorded). Photo: Oday yaish, CC BY-SA 4.0, Wikimedia Commons. Not the farmers named.</figcaption></figure>
<p class="sub">Owners turned back from their own land, ID cards taken, harvests halted when settlers arrive. <a href="moving.html">The closures, place by place</a></p>
<div class="wall lay" data-bond>{wb_people}</div>{figs2(W_FIGS)}

</section></section>''')
harvest_ids = ['khader-one-day-of-harvest', 'baraka-olive-yields-pressing-cost', 'dweima-olive-income-gone', 'gaza-olives-45-shekels-one-press-line',
               'mansour-deir-istiya-64000', 'sanaf-beit-rima-400-trees', 'al-dik-550-trees-out-of-reach', 'harvest-attacks-219-in-12-days', 'bazzari-killed-in-his-grove']
page('harvest.html', 'The olive harvest, 2026 — Pal-Online', 'The 2026 olive season in Gaza and the West Bank: the people, the yields, the closed land.',
     'harvest', harvest_main, [src_pair(i) for i in harvest_ids], [credit('olive-picker-hands-nablus', 'Picking olives near Nablus')])

# =====================================================================
# tell.html
# =====================================================================
steps = ''.join(f'<li class="{"blk yours" if i == 3 else "slab"} w"><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate([
    ('You tell us', 'Your trade, your town or camp, and what changed. A few sentences is enough.'),
    ('A reporter calls you', 'Within a week, on the number or address you leave. Nothing is published before that call.'),
    ('We check what we can', 'Places, prices and dates against other reports. What we cannot check, we say.'),
    ('Your block goes up', 'With your name or a changed one, your trade and what you are paid, if you want it said.')]))
tell_main = (phead('Tell us your work', 'Pal-Online is built from people, not institutions. If your trade changed, your shop reopened or your shift ended, tell us.',
                   'line-tell', 'Tell us · <b>four steps, one block</b>')
             + f'''<section class="wrap" aria-labelledby="steps-h"><h2 class="sr" id="steps-h">What happens to your story</h2>
<ol class="wall steps">{steps}</ol></section>
<section class="pblock wrap twocol" aria-labelledby="form-h">
<div><h2 id="form-h" style="font-size:clamp(28px,2.7vw,40px)">Your block</h2>
<ul class="promises" style="margin-top:16px">
<li>{OPEN}<span>We never publish your phone number or email.</span></li>
<li>{OPEN}<span>You can stay anonymous. We will change your name and say so, as we did for Abu Ibrahim.</span></li>
<li>{OPEN}<span>You can ask us to take your story down at any time.</span></li>
<li>{LIMIT}<span>This is a prototype: the form checks what you type but sends nothing.</span></li></ul></div>
<form class="tellform" action="#" method="post" novalidate>
<div class="field"><label for="t-trade">Your work now</label><input id="t-trade" name="trade" required autocomplete="organization-title" placeholder="Barber, driver, teacher…"><p class="err">Tell us what you do for work, or that you have none.</p></div>
<div class="field"><label for="t-before">Your work before <span>(if it changed)</span></label><input id="t-before" name="before" autocomplete="off"></div>
<div class="field"><label for="t-town">Town or camp</label><input id="t-town" name="town" required autocomplete="address-level2"><p class="err">Tell us where you work or live.</p></div>
<div class="field"><label for="t-pay">What you are paid <span>(optional)</span></label><input id="t-pay" name="pay" autocomplete="off" placeholder="₪50 a day, ₪1,500 a month…"></div>
<div class="field full"><label for="t-story">What changed</label><textarea id="t-story" name="story" required></textarea><p class="err">A sentence or two is enough.</p></div>
<fieldset><legend>How should the reporter reach you?</legend><div class="choice">
<label><input type="radio" name="via" value="whatsapp" checked> WhatsApp</label><label><input type="radio" name="via" value="telegram"> Telegram</label>
<label><input type="radio" name="via" value="phone"> A call</label><label><input type="radio" name="via" value="email"> Email</label></div></fieldset>
<div class="field full"><label for="t-contact">Number or email <span>(only for our reporter)</span></label><input id="t-contact" name="contact" required autocomplete="tel"><p class="err">We need a way to call you back.</p></div>
<label class="check"><input type="checkbox" name="anon"> Change my name if this is published.</label>
<div class="field full check-field"><label class="check"><input type="checkbox" name="ok" id="t-ok" required> I agree that a reporter may contact me about this story.<span class="sr">Required.</span></label><p class="err" id="t-ok-err">Tick this so a reporter may call you.</p></div>
<div class="actions"><button class="btn" type="submit">Send to the newsroom</button><p class="note" style="margin:0">A reporter reads every message.</p></div>
<p class="sent" role="status" tabindex="-1">Received. Thank you. This is a prototype, so nothing was sent; on the live site a reporter would call you within a week.</p>
</form></section>''')
page('tell.html', 'Tell us your work — Pal-Online', 'Tell Pal-Online about your work: your trade, your town, what changed.', 'tell', tell_main, [])

# =====================================================================
# about.html
# =====================================================================
RULES = [('A person before a number', 'Every story starts with someone at work: a name, a trade, a place. The figures come after, to show how many others share it.'),
         ('Every figure keeps its source and date', 'A number on Pal-Online always says who gave it and when. Competing counts sit side by side and are never averaged.'),
         ('Pay is as the worker told it', 'Rates are given in the currency people are paid in, as they told the reporter, with what the pay has to cover.'),
         ('We say what we could not check', 'When something rests on one person’s word, or a report we could not open, the page says so.'),
         ('Names can be changed, and we say so', 'Some people speak at risk. We change their names on request and mark the change, never silently.'),
         ('Photographs show what the caption says', 'We do not pair a story with a photograph of someone else. Archive photographs carry their year and say that the people named are not in them.')]
rules = ''.join(f'<li><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for t, d in RULES)
about_main = (phead('About Pal-Online', 'Daily life and livelihoods in Palestine, in English: who is working today, at what, and for how much.',
                    'line-about', 'About · <b>how the wall is built</b>')
              + f'''<section class="wrap twocol" aria-labelledby="ab-h"><h2 class="sr" id="ab-h">What we do</h2>
<div class="prose"><p>Most reporting on Palestine is told by event. Pal-Online tells it by livelihood: the teacher back in a classroom with a tarp for a wall, the builder who now charges phones, the farmer who cannot reach his trees.</p>
<p>Each person is a block on the site, with their trade, their town and what they are paid. Prices, salaries and closed roads are reported by what they do to someone’s working day.</p></div>
<div class="wall contact" style="--halves:4"><div class="slab w"><h3>People on the wall</h3><p class="rate num">{len(PEOPLE)}</p><p>named in reports since 25 September</p></div>
<div class="slab w"><h3>Figures, sourced</h3><p class="rate num">{len(FIGS) + len(DB)}</p><p>on <a href="count.html">the count</a>, none averaged</p></div></div></section>
<section class="pblock wrap" id="how" aria-labelledby="how-h"><div class="sec-head"><h2 id="how-h">How we report</h2><p>Six rules every page keeps.</p></div><ol class="rules">{rules}</ol></section>
<section class="pblock wrap twocol" id="corrections" aria-labelledby="corr-h"><div><h2 id="corr-h" style="font-size:clamp(28px,2.7vw,40px)">Corrections</h2></div>
<div class="prose"><p>When we get something wrong we correct it on the page, say what changed and when, and keep the old version on record. Corrections are never made silently.</p>
<p><b>15 October 2026.</b> The fishermen’s story on our homepage was first dated 26 September. It was published by The Palestine Chronicle on 14 January 2026; 26 September is the date it was reposted on the author’s Substack. The date and link are corrected.</p>
<p>Seen an error? <a href="tell.html">Tell us</a>.</p></div></section>
<section class="pblock wrap twocol" aria-labelledby="ct-h"><div><h2 id="ct-h" style="font-size:clamp(28px,2.7vw,40px)">Contact</h2></div>
<div class="wall contact"><div class="slab w"><h3>Newsroom</h3><p>[newsroom email, to be added]</p></div><div class="slab w"><h3>WhatsApp</h3><p>[number, to be added]</p></div>
<div class="slab w"><h3>Telegram</h3><p>[channel, to be added]</p></div><div class="slab w"><h3>Your work</h3><p><a href="tell.html">The form</a> reaches a reporter directly.</p></div></div></section>''')
page('about.html', 'About Pal-Online and how we report', 'What Pal-Online is, how it reports, and how it corrects mistakes.', 'about', about_main, [])

# =====================================================================
# search.html — the index is every checked item plus the people
# =====================================================================
INDEX = []
for it in NEWS.values():
    p = it.get('person') or {}
    INDEX.append({'t': it['headline'], 's': it['summary'], 'p': it['place'], 'd': day(it['date']), 'k': it['date'],
                  'o': outlet(it['id']), 'u': it['url'], 'n': p.get('name') or '', 'desk': it['desk'],
                  'g': 'Gaza' if it['region'] == 'Gaza' else ('West Bank' if it['region'] in ('West Bank', 'Israel (workers)') else 'Palestine-wide')})
INDEX.sort(key=lambda r: r['k'], reverse=True)
search_main = (f'''<header class="phead wrap"><h1 id="s-h">Search</h1>
<form class="sbox" role="search" action="search.html" aria-labelledby="s-h"><label class="sr" for="q">Search people, trades, places and figures</label>
<input id="q" name="q" type="search" autocomplete="off" placeholder="A trade, a town, a name"><button type="submit">{LOUPE}<span class="sr">Search</span></button></form>
<div class="suggest" aria-label="Try"><button type="button" data-q="rubble">rubble</button><button type="button" data-q="olive">olive</button>
<button type="button" data-q="salary">salary</button><button type="button" data-q="Khan Younis">Khan Younis</button><button type="button" data-q="shekels">shekels</button><button type="button" data-q="checkpoint">checkpoint</button></div>
{line("line-search", '<span data-sum>All reports</span> · <b>' + str(len(INDEX)) + ' checked items</b>')}</header>
<section class="wrap" aria-labelledby="res-h"><h2 class="sr" id="res-h">Results</h2>
<div class="filters"><div role="group" aria-label="Desk"><span class="lab">DESK</span>
<button type="button" data-desk="all" aria-pressed="true">All</button><button type="button" data-desk="work" aria-pressed="false">Work</button><button type="button" data-desk="money" aria-pressed="false">Money</button>
<button type="button" data-desk="prices" aria-pressed="false">Prices</button><button type="button" data-desk="moving" aria-pressed="false">Moving</button><button type="button" data-desk="count" aria-pressed="false">The count</button></div>
<p class="tally" aria-live="polite" data-n></p></div>
<ol class="results" data-results></ol>
<div class="empty" data-empty hidden><p>No block matches. Try a trade (<b>barber</b>), a place (<b>Jenin</b>) or a figure (<b>unemployment</b>), or <a href="tell.html">tell us your work</a>.</p></div>
<noscript><p class="note">Search needs JavaScript. Every item is also listed on <a href="wall.html">the wall</a> and in the sources at the foot of each page.</p></noscript>
</section>
<script type="application/json" id="search-index">{json.dumps(INDEX, ensure_ascii=False).replace("</", "<\\/")}</script>''')
page('search.html', 'Search — Pal-Online', 'Search Pal-Online’s checked reports by trade, place, name or figure.', 'search', search_main, [])

# =====================================================================
# khan-younis.html — a place: the template for any town, camp or tag
# =====================================================================
KY_IDS = ['gaza-olives-45-shekels-one-press-line', 'undp-women-businesses-khan-younis', 'rubble-sanee-it-to-sledgehammer',
          'rubble-musbah-50-shekels', 'rubble-zorub-demolition-by-hand', 'rubble-breis-scrap-dealer']
ky_people = [p for p in PEOPLE if 'Khan Younis' in p['p'] or p['n'] == 'Nasr Ouda']
ky_people.sort(key=lambda p: NEWS[p['id']]['date'], reverse=True)
KY_FIGS = [('$16.50–30', 'a day for breaking and clearing rubble by hand, as the workers told it', 'rubble-zorub-demolition-by-hand'),
           ('3–4 weeks', 'to bring a building down by hand; it took two or three days with machines', 'rubble-zorub-demolition-by-hand'),
           ('₪45', 'a kilo of olives in the market, on sale for the first time in three years', 'gaza-olives-45-shekels-one-press-line'),
           ('12 dunams', 'of one trader’s land east of Rafah, out of reach', 'gaza-olives-45-shekels-one-press-line')]
ky_figs = ''.join(f'<div class="slab stat w"><p class="rate num">{e(v)}</p><p>{e(t)}</p><p class="src">{cite(nid)}</p></div>' for v, t, nid in KY_FIGS)
ky_reports = ''.join(f'<li><div><h3><a href="{"article.html" if nid == "rubble-sanee-it-to-sledgehammer" else e(NEWS[nid]["url"])}"'
                     f'{"" if nid == "rubble-sanee-it-to-sledgehammer" else " rel=" + chr(34) + "noopener" + chr(34)}>{e(NEWS[nid]["headline"])}</a></h3>'
                     f'<p>{e(NEWS[nid]["summary"])}</p><p class="meta"><b>{e({"work": "Work", "prices": "Prices"}[NEWS[nid]["desk"]])}</b> · {e(NEWS[nid]["place"])} · {e(outlet(nid))}, {day(NEWS[nid]["date"])}</p></div></li>'
                     for nid in sorted(KY_IDS, key=lambda i: NEWS[i]['date'], reverse=True))
others = {}
for it in NEWS.values():
    for town in ['Gaza City', 'Deir al-Balah', 'Deir el-Balah', 'Tulkarem', 'Jenin', 'Nablus', 'Jordan Valley', 'Salfit', 'Beit Rima', 'Deir Istiya']:
        if town in it['place'] or town in it['summary']:
            key = 'Deir al-Balah' if town == 'Deir el-Balah' else town
            others[key] = others.get(key, 0) + 1
others_html = ''.join(f'<li><a href="search.html?q={e(t).replace(" ", "+")}"><b>{n}</b>{e(t)}</a></li>' for t, n in sorted(others.items(), key=lambda kv: -kv[1]))
ky_main = (phead('Khan Younis', 'In the south of the Gaza Strip. Much of the rubble trade Pal-Online reports on is cleared here by hand, and olives came back to its market this month.',
                 'line-ky', f'Khan Younis · <b>{len(KY_IDS)} reports · {len(ky_people)} people</b>')
           + f'''<section class="wrap" aria-labelledby="kyp-h"><h2 class="sr" id="kyp-h">People in Khan Younis</h2>
<div class="wall more lay" data-bond data-line="line-ky">{"".join(pblock(p) for p in ky_people)}</div></section>
<section class="pblock wrap" aria-labelledby="kyf-h"><div class="sec-head"><h2 id="kyf-h">Khan Younis in figures</h2><p>As the people here told reporters, and as the market priced it.</p></div>
<div class="wall stats">{ky_figs}</div></section>
<section class="pblock wrap" aria-labelledby="kyr-h"><div class="sec-head"><h2 id="kyr-h">Every report</h2><p>Newest first. The rubble story opens on Pal-Online; the rest open the original report.</p></div>
<ol class="results">{ky_reports}</ol></section>
<section class="pblock wrap" aria-labelledby="kyo-h"><div class="sec-head"><h2 id="kyo-h">Other places in the reports</h2><p>Each opens a search of everything checked from there.</p></div>
<ul class="else places">{others_html}</ul></section>''')
page('khan-younis.html', 'Khan Younis — Pal-Online', 'Everyone and everything Pal-Online has reported from Khan Younis, in the south of the Gaza Strip.',
     'wall', ky_main, [src_pair(i) for i in KY_IDS], crumb='Khan Younis',
     ld=[{'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Khan Younis', 'url': SITE + 'khan-younis.html',
          'about': {'@type': 'Place', 'name': 'Khan Younis', 'containedInPlace': {'@type': 'Place', 'name': 'Gaza Strip'}}, 'publisher': ORG}])

# =====================================================================
# privacy.html
# =====================================================================
privacy_main = (phead('Privacy', 'What happens to what you tell us. Short, because we collect very little.', 'line-privacy', 'Privacy · <b>prototype terms; Pal-Online sets the final ones</b>')
                + '''<section class="wrap twocol" aria-labelledby="pv1-h"><div><h2 id="pv1-h" style="font-size:clamp(26px,2.4vw,34px)">What we collect</h2></div>
<div class="prose"><p>Only what you type into <a href="tell.html">Tell us your work</a>: your trade, your town or camp, what changed, what you are paid if you choose to say, and a number or address for the reporter.</p>
<p><b>This prototype sends nothing.</b> The form checks what you type and stops there.</p></div></section>
<section class="pblock wrap twocol" aria-labelledby="pv2-h"><div><h2 id="pv2-h" style="font-size:clamp(26px,2.4vw,34px)">Who sees it</h2></div>
<div class="prose"><p>The reporter who calls you back, and the editor who checks the story. Your number or address is never published, and your name is changed on request and marked as changed.</p></div></section>
<section class="pblock wrap twocol" aria-labelledby="pv3-h"><div><h2 id="pv3-h" style="font-size:clamp(26px,2.4vw,34px)">How long we keep it</h2></div>
<div class="prose"><p>[Retention period, to be set by Pal-Online.] You can ask at any time for your contact details to be deleted and for your story to be taken down.</p></div></section>
<section class="pblock wrap twocol" aria-labelledby="pv4-h"><div><h2 id="pv4-h" style="font-size:clamp(26px,2.4vw,34px)">What this site stores in your browser</h2></div>
<div class="prose"><p>One note for the length of your visit: that you have already seen the opening animation, so it does not play again. Nothing else. No cookies are set, and the prototype loads no analytics, advertising or tracking scripts; its fonts are served from this site, not a third party. [Analytics on the live site: to be decided.]</p>
<p>Share buttons open WhatsApp, Telegram or X only when you press them.</p></div></section>
<section class="pblock wrap twocol" aria-labelledby="pv5-h"><div><h2 id="pv5-h" style="font-size:clamp(26px,2.4vw,34px)">Ask us</h2></div>
<div class="prose"><p>[Privacy contact, to be added.] Or use <a href="tell.html">the form</a>, and say it is about your data.</p></div></section>''')
page('privacy.html', 'Privacy — Pal-Online', 'What Pal-Online collects, who sees it and how to have it deleted.', 'about', privacy_main, [], crumb='Privacy')

# =====================================================================
# 404.html — GitHub Pages serves it for any missing path, so asset links need the site root
# =====================================================================
lost_wall = ''.join(f'<span class="{c}">{t}</span>' for c, t in [('blk w', ''), ('blk w', ''), ('blk w', ''), ('blk h', ''), ('blk--gap w', '404'), ('blk w', ''), ('blk h', ''), ('blk w', ''), ('blk w', ''), ('blk w', '')])
lost_main = f'''<section class="wrap lost" aria-labelledby="lost-h"><div class="wall" aria-hidden="true">{lost_wall}</div>
<div><h1 id="lost-h">This block is missing</h1><p>The page you asked for is not on the wall. It may have moved, or the link may be wrong.</p>
<div class="go"><a class="btn" href="home.html">Today’s course</a><a class="btn" href="wall.html">The wall</a><a class="btn" href="search.html">Search</a></div></div></section>'''
BASE = ('<script>if(location.hostname.endsWith("github.io")){var b=document.createElement("base");'
        'b.href="/pal-online-prototype/";document.head.appendChild(b)}</script>')
head404 = head('Page not found — Pal-Online', 'This page is not on the wall.', ['home', 'pages'], '404.html').replace(
    '<meta charset="utf-8">', '<meta charset="utf-8">' + chr(10) + BASE, 1)
html404 = f'''{head404}
<body>
<a class="skip" href="#main">Skip to the page</a>
{strip()}
{mast('none', inner=True)}
<main id="main">{lost_main}</main>
{foot([], [])}
<script src="assets/js/po.js?v={V}" defer></script>
</body>
</html>
'''
write('404.html', html404)
