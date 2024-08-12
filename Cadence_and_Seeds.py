import json, pandas as pd
def unique(list_):
    u = []
    for l in list_:
        if l not in u:
            u.append(l)
    return u


# this is how to find out what seed have not been sent to from a list of cadence names

logs = json.loads(pd.read_csv('Cadence_and_Seeds+half+opp.csv', encoding='ISO-8859-1', dtype=str).to_json(orient='records'))
nono = ['Half Opp Massacre', "Aged Opps"]
seeds = unique([x['Record Id'] for x in logs])

final = []

for seed in seeds:
    seed_logs = [x for x in logs if x['Record Id'] == seed]
    has = False
    for l in seed_logs:
        for n in nono:
            if n in l['Log Name']:
                has = True
    print(f"https://purplegod.pythonanywhere.com/divine-ape/{seed[5:]}", has)
    if has is False:
        final.append(seed)

print(len(final))






