import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('civica-v5.html', encoding='utf-8') as f:
    html = f.read()

old = ('glance:"Hull scores 72 on the Civica index — above the statewide median. '
       'Strengths: schools ranked #91 of 396 (math 50.0%, grad 95.3%), low crime (207 violent per 100k). '
       'Key tradeoff: elevated flood or climate risk.",'
       'standout:"Hull: #91 school district (#91 of 396), MCAS math 50.0%; commuter rail in town; strong value (6.4x TER)."')

new = ('glance:"Hull is a 10,000-person coastal peninsula town south of Boston, accessible by MBTA '
       'Harbor Express ferry directly to Rowes Wharf — one of the only MA towns where commuters '
       'travel to downtown Boston by boat. The defining trade-off: 63.2% of Hull\'s properties carry '
       'current flood risk, rising to 67.5% in 30 years, one of the highest rates in the state.",'
       'standout:"Hull: MBTA commuter ferry to Boston; extreme flood exposure (63.2% of properties '
       'at risk); schools #91 of 396 statewide; pension 82.8% funded."')

if old in html:
    html = html.replace(old, new)
    with open('civica-v5.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Updated Hull glance/standout.')
else:
    print('ERROR: old string not found.')
    # Show what we actually have for Hull
    idx = html.find('"Hull"', html.find('const TOWNS'))
    print(html[idx:idx+600])
