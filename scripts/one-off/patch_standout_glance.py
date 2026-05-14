"""
Patch standout and glance text for the 13 towns that have null values.
These are all from the Suffolk / Middlesex batch added before Norfolk.
"""
import re
from pathlib import Path

HTML_FILE = Path(__file__).parent.parent / "civica-v5.html"

PATCHES = {
    "Boston": {
        "standout": (
            "Boston’s ~79% non-residential tax base is the largest commercial subsidy of any "
            "municipality in Massachusetts, keeping the FY2024 residential rate at $10.51/thousand "
            "despite being the state’s largest city — and no community in New England "
            "matches its subway network coverage (Red, Orange, Green, Blue, Silver lines)."
        ),
        "glance": (
            "Boston is the economic and cultural center of New England, with world-class hospitals, "
            "universities, and an MBTA network that no suburb can replicate. The 79% commercial tax "
            "base keeps residential rates low. Trade-offs: urban-scale violent crime (449/100k), "
            "school quality that varies widely by neighborhood, and meaningful pension obligations "
            "(BERS ~70% funded). Home prices vary enormously by neighborhood."
        ),
    },
    "Revere": {
        "standout": (
            "Revere Beach — the first public beach in the US — sits directly on the Blue Line, "
            "giving residents oceanfront access and a direct subway ride to Downtown Boston at home "
            "prices well below the inner-metro average, making it one of the most affordable "
            "transit-connected cities on the MBTA network."
        ),
        "glance": (
            "Revere is an affordable, diverse, Blue Line-connected coastal city with some of the "
            "lowest home prices in the inner metro. Trade-offs are real: elevated violent crime "
            "(380/100k), mid-tier schools, significant coastal flood risk (~22% of properties), and "
            "an A+ bond rating that reflects tighter fiscal margins than suburban peers. A value "
            "pick for buyers who prioritize transit and waterfront access over top-tier schools."
        ),
    },
    "Winthrop": {
        "standout": (
            "Winthrop faces some of the most severe flood exposure of any town we score — a "
            "peninsula nearly surrounded by Boston Harbor with ~40% of properties in a flood zone "
            "and the highest projected 2050 flood growth in our dataset. Above-average schools and "
            "low crime are genuine strengths, but flood risk is the defining constraint."
        ),
        "glance": (
            "Winthrop is a compact, close-knit peninsula community with above-average schools, low "
            "violent crime, and a residential character rare this close to Boston. The overriding "
            "caveat is geography: nearly surrounded by water, the town carries severe flood risk "
            "today and worsening exposure by 2050. No commuter rail or subway access — "
            "residents rely on bus connections to the Blue Line."
        ),
    },
    "Newton": {
        "standout": (
            "Newton is the only community in Greater Boston combining top-5% schools statewide, "
            "Green Line subway access across three branches (B, C, D), violent crime below 70/100k, "
            "an AAA bond rating, and a Civica score of 83 — the highest of any city with over "
            "80,000 residents in our dataset."
        ),
        "glance": (
            "Newton is one of Massachusetts’s premier cities: exceptional schools, the most "
            "extensive Green Line coverage of any single municipality, very low crime, and AAA "
            "finances. Eight distinct villages give it a town-within-a-city character. Home prices "
            "are among the highest in the state and reflect every one of those advantages. One of "
            "the most comprehensively desirable communities we score."
        ),
    },
    "Waltham": {
        "standout": (
            "Waltham hosts one of the densest concentrations of biotech and life science employers "
            "outside Cambridge along the Route 128 corridor — a commercial base that supports "
            "the municipal levy, keeps residential rates competitive, and has driven a 10-year "
            "income growth rate of nearly 50% in the surrounding area."
        ),
        "glance": (
            "Waltham is a mid-size city with solid finances (AA+), Fitchburg line commuter rail to "
            "North Station, and a robust biotech and pharma commercial corridor along Route 128. "
            "Schools are mid-tier. Crime is moderate. Home prices are meaningfully more accessible "
            "than neighboring Newton or Lexington while still offering reasonable commuter access "
            "to Boston."
        ),
    },
    "Malden": {
        "standout": (
            "Malden is one of the very few communities in Greater Boston with Orange Line subway "
            "access and median home prices under $550,000 — making it among the most "
            "affordable transit-connected cities on the MBTA rapid transit network and a standout "
            "entry point for first-time buyers who need rail access to downtown Boston."
        ),
        "glance": (
            "Malden combines Orange Line access to Downtown Boston, affordable housing, and a "
            "diverse, growing population. The trade-offs are moderate violent crime (250/100k), a "
            "mid-tier school district, and an A+ bond rating that reflects tighter fiscal margins "
            "than higher-rated suburban neighbors. A strong value proposition for buyers "
            "prioritizing transit access and price."
        ),
    },
    "Everett": {
        "standout": (
            "Encore Boston Harbor — a $2.6B resort casino on the Mystic River — has become "
            "one of the largest single commercial tax contributors in the state, injecting tens of "
            "millions annually into Everett’s budget and funding significant municipal "
            "improvements in a city that was historically underfunded."
        ),
        "glance": (
            "Everett is a densely urban, rapidly changing city with Green Line Extension access, "
            "some of the lowest home prices of any subway-connected community in Greater Boston, "
            "and a commercial tax base now anchored by Encore Boston Harbor. Violent crime is "
            "elevated (280/100k), schools are among the weaker performers in our dataset, and "
            "fiscal margins are tighter than suburban peers. A high-risk, high-upside pick for "
            "investors and buyers comfortable with urban tradeoffs."
        ),
    },
    "Watertown": {
        "standout": (
            "Watertown carries an AAA bond rating, violent crime below 100/100k, and a strong "
            "commercial corridor along Arsenal Street and Route 9 — all within 6 miles of "
            "downtown Boston — with more accessible home prices than neighboring Newton or "
            "Belmont, making it a rare inner-suburb that balances fiscal strength and affordability."
        ),
        "glance": (
            "Watertown is a well-managed inner suburb (AAA-rated) with low crime, good schools "
            "(top third statewide), and home prices more accessible than Newton or Belmont. The "
            "main limitation is transit: no subway or commuter rail, with buses connecting to the "
            "Green Line. Arsenal Yards development has added commercial tax base. A solid "
            "all-around performer for buyers who can accept bus-only transit."
        ),
    },
    "Framingham": {
        "standout": (
            "Framingham is the commercial hub of MetroWest — the only city in the region with "
            "commuter rail access, a state university, and a large industrial and retail tax base "
            "that keeps residential rates moderate, while home prices remain well below those of "
            "the eastern suburbs at comparable commute distances."
        ),
        "glance": (
            "Framingham is MetroWest’s largest city, with Framingham/Worcester commuter rail "
            "service to Back Bay and South Station, a diversified commercial and industrial tax "
            "base, and housing that is materially more affordable than eastern suburbs. School "
            "rankings are mid-table. Violent crime is elevated for the region. Pension and debt "
            "obligations are meaningful for a city of this size."
        ),
    },
    "Natick": {
        "standout": (
            "Natick has an AAA bond rating, two commuter rail stations on the Framingham/Worcester "
            "line, violent crime well below the state average, and Natick Collection — one of "
            "the largest regional malls in New England — providing substantial commercial tax "
            "support that moderates the residential levy."
        ),
        "glance": (
            "Natick is a well-rounded MetroWest suburb with top-tier finances (AAA), solid schools "
            "(top quarter statewide), low crime, and commuter rail to Back Bay and South Station. "
            "Home prices are moderate relative to eastern suburbs. The Natick Collection anchors "
            "the commercial tax base. A consistently strong performer across nearly every Civica "
            "metric — one of the best all-around communities in MetroWest."
        ),
    },
    "Acton": {
        "standout": (
            "Acton has the lowest violent crime rate of any town in our dataset with over 20,000 "
            "residents — just 30 per 100,000 — paired with the Acton-Boxborough Regional "
            "District ranking in the top 12% statewide and an AAA bond rating, making it one of "
            "the safest and academically strongest communities in MetroWest."
        ),
        "glance": (
            "Acton is a quiet, family-oriented suburb with exceptional safety (among the lowest "
            "crime rates in Greater Boston), strong schools in the Acton-Boxborough Regional "
            "District, and Fitchburg commuter rail service to North Station. Home prices are "
            "meaningful. The tax-efficiency ratio (TER) comes in below average because the "
            "predominantly residential tax base puts the full levy on homeowners at a higher rate."
        ),
    },
    "Concord": {
        "standout": (
            "Concord-Carlisle Regional ranks in the top 8% of Massachusetts school districts, and "
            "Concord’s median household income exceeds $200,000 — placing it among the "
            "most affluent and academically excellent communities in our dataset, with Fitchburg "
            "commuter rail to North Station and an AAA bond rating that reflects decades of "
            "disciplined fiscal management."
        ),
        "glance": (
            "Concord is a historic, affluent suburb with exceptional schools (Concord-Carlisle "
            "top 8% statewide), AAA finances, very low crime, and commuter rail to North Station. "
            "Home prices are among the highest in MetroWest and reflect every one of those "
            "advantages. The town’s character is defined by its historic center, extensive "
            "conservation land, and a strong civic identity. A consistently premium community."
        ),
    },
    "Stoneham": {
        "standout": (
            "Stoneham scores 79 — in the top third of our 70-town dataset — while "
            "maintaining home prices well below neighboring Winchester or Woburn, giving buyers "
            "a way into the Middlesex inner-ring suburb market at a meaningful discount with "
            "comparable school performance and lower crime than many peer communities."
        ),
        "glance": (
            "Stoneham is a solid inner-suburban community with good schools (top 22% statewide), "
            "low crime, and home prices well below neighboring Winchester or Woburn. The main "
            "limitation is transit: no commuter rail or subway, bus-only. The AA bond rating "
            "reflects sound but not elite fiscal management. A good value pick for buyers who can "
            "drive or work remotely and want quality suburban life at a lower price point."
        ),
    },
}

html = HTML_FILE.read_text(encoding="utf-8")
patched = 0

for town, texts in PATCHES.items():
    standout = texts["standout"].replace("\\", "\\\\").replace('"', '\\"')
    glance   = texts["glance"].replace("\\", "\\\\").replace('"', '\\"')

    # Replace standout:null
    old = f'name:"{town}"'
    m = re.search(re.escape(old) + r'.{0,3000}?standout:null', html, re.DOTALL)
    if not m:
        print(f"  WARNING: could not find standout:null for {town}")
        continue

    # Replace standout:null -> standout:"..."
    span_start = m.start()
    span_end   = m.end()
    html = html[:span_end - len("standout:null")] + f'standout:"{standout}"' + html[span_end:]

    # Now replace glance:null (search from span_start in updated html)
    m2 = re.search(re.escape(old) + r'.{0,3500}?glance:null', html[span_start:], re.DOTALL)
    if not m2:
        print(f"  WARNING: could not find glance:null for {town}")
        continue
    abs_start = span_start + m2.start()
    abs_end   = span_start + m2.end()
    html = html[:abs_end - len("glance:null")] + f'glance:"{glance}"' + html[abs_end:]

    patched += 1
    print(f"  Patched {town}")

HTML_FILE.write_text(html, encoding="utf-8")
print(f"\nDone — patched {patched} towns")
