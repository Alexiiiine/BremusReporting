import json, pandas as pd
from nicegui import ui
import json, requests as r
from datetime import datetime

def unique(list_):
    u = []
    for l in list_:
        if l not in u:
            u.append(l)
    return u
def CalcReport(start, end):
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    logs = json.loads(pd.read_csv('Reports/Logs_ALL.csv', encoding='ISO-8859-1', dtype=str).to_json(orient='records'))
    SMS = json.loads(pd.read_csv('Reports/SMS_ALL.csv', encoding='ISO-8859-1', dtype=str).to_json(orient='records'))
    Emails = json.loads(pd.read_csv('Reports/Emails_ALL.csv', encoding='ISO-8859-1', dtype=str).to_json(orient='records'))
    VCalls = json.loads(pd.read_csv('Reports/AiCalls_ALL.csv', encoding='ISO-8859-1', dtype=str).to_json(orient='records'))
    Salesforce_Logs = json.loads(pd.read_csv('Reports/Salesforce_Logs.csv', encoding='ISO-8859-1', dtype=str).to_json(orient='records'))

    data = []

    for l in VCalls:
        data.append({
            "Type":"Ai Call",
            "Seed":l['Record Id'].replace('zcrm_',''),
            "Created":datetime.strptime(l['Created Time (Vapi Calls)'], '%m/%d/%Y %I:%M %p'),
            "Data":l
        })
    for l in logs:
        data.append({
            "Type":"Log",
            "Seed": l['Record Id'].replace('zcrm_',''),
            "Created":datetime.strptime(l['Created Time (Logs)'], '%m/%d/%Y %I:%M %p'),
            "Data":l
        })
    for l in SMS:
        data.append({
            "Type":"SMS",
            "Seed": l['Record Id'].replace('zcrm_',''),
            "Created":datetime.strptime(l['Created Time (SMS Touches)'], '%m/%d/%Y %I:%M %p'),
            "Data":l
        })
    for l in Emails:
        data.append({
            "Type":"Email",
            "Seed": l['Record Id'].replace('zcrm_',''),
            "Created":datetime.strptime(l['Created Time (Email Touches)'], '%m/%d/%Y %I:%M %p'),
            "Data":l
        })
    for l in Salesforce_Logs:
        try:
            if l['Call Duration (seconds)'] is not None:
                data.append({
                    "Type":"Call",
                    "Seed": l['Bremus Id'],
                    "Created":datetime.strptime(l['Completed Date/Time'], '%m/%d/%Y %I:%M %p'),
                    "Data":l
                })
        except:pass

    data = sorted(data, key= lambda x: x['Created'])

    # filter within range
    filtered = []
    for item in data:
        item_date = item['Created']
        if start_date <= item_date <= end_date:
            filtered.append(item)

    # SMS
    SMS = [x for x in filtered if x['Type']=='SMS']
    SMS_OUTBOUND = [x for x in SMS if x['Data']['SMS Touch Name'] != 'IN']
    SMS_INBOUND = [x for x in SMS if x['Data']['SMS Touch Name'] == 'IN']

    SMS_Cadences = []
    for cadence in unique([x['Data']['Cadence'] for x in SMS_OUTBOUND]):
        SMS_Cadences.append({"Name":cadence,
                               "Total":len([x for x in SMS_OUTBOUND if x['Data']['Cadence'] == cadence]),
                               "Seeds":len(unique([x['Seed'] for x in SMS_OUTBOUND if x['Data']['Cadence'] == cadence]))
                               })
    # Emails
    Emails = [x for x in filtered if x['Type'] == 'Email']
    Emails_OUTBOUND = [x for x in Emails if x['Data']['Email Touch Name'] != 'IN']
    Emails_INBOUND = [x for x in Emails if x['Data']['Email Touch Name'] == 'IN']
    Emails_Cadences = []
    for cadence in unique([x['Data']['Cadence'] for x in Emails_OUTBOUND]):
        Emails_Cadences.append({"Name":cadence,
                               "Total":len([x for x in Emails_OUTBOUND if x['Data']['Cadence'] == cadence]),
                               "Seeds":len(unique([x['Seed'] for x in Emails_OUTBOUND if x['Data']['Cadence'] == cadence]))
                               })
    # Calls
    Calls = [x for x in filtered if x['Type'] == 'Call' and int(x['Data']['Call Duration (seconds)']) > 0 and x['Data']['Created By'] is not None]

    Reps = []
    for c in Calls:
        try:
            if c['Data']['Created By'] not in Reps:
                Reps.append(c['Data']['Created By'])
        except:
            pass
    RepCalls = []
    for Rep in Reps:
        RepCalls.append({"Name":Rep, "Total":len([x for x in Calls if x['Data']['Created By'] == Rep]), "Seeds":len(unique([x['Seed'] for x in Calls if x['Data']['Created By'] == Rep]))})

    # Ai Calls
    Ai_Calls = [x for x in filtered if x['Type'] == 'Ai Call']
    Ai_Call_Agents = []
    for agent in unique([x['Data']['Agent (Vapi Calls)'] for x in Ai_Calls if x['Data']['Agent (Vapi Calls)'] is not None]):
        # Ai_Call_Agents[agent] = len([x for x in Ai_Calls if x['Data']['Agent (Vapi Calls)'] == agent])
        Ai_Call_Agents.append({"Name":agent,
                               "Total":len([x for x in Ai_Calls if x['Data']['Agent (Vapi Calls)'] == agent]),
                               "Seeds":len(unique([x['Seed'] for x in Ai_Calls if x['Data']['Agent (Vapi Calls)'] == agent]))
                               })
    Ai_Call_Cadences = []
    for cadence in unique([x['Data']['Cadence'] for x in Ai_Calls]):
        Ai_Call_Cadences.append({"Name":cadence, "Total":len([x for x in Ai_Calls if x['Data']['Cadence'] == cadence]),
                                 "Seeds":len(unique([x['Seed'] for x in Ai_Calls if x['Data']['Cadence'] == cadence]))})


    # logs
    Logs = [x for x in filtered if x['Type'] == 'Log']
    Interested_Logs = [x for x in Logs if 'Status changed to Interested' in x['Data']['Log Name']]

    seeds = []
    for d in filtered:
        if d['Seed'] not in seeds:
            seeds.append(d['Seed'])
    print('\n')
    print(start, end)
    print('\n')

    # Touched
    print('Touched Overview:')
    print(f"Total Seeds Touched: {len(seeds)}")
    print(f"Total SMS: {len(SMS_OUTBOUND)} ({len(unique([x['Seed'] for x in SMS_OUTBOUND]))} Seeds)")
    print(f"Total Emails: {len(Emails_OUTBOUND)} ({len(unique([x['Seed'] for x in Emails_OUTBOUND]))} Seeds)")
    print(f"Total Calls: {len(Calls)} ({len(unique([x['Seed'] for x in Calls]))} Seeds)")
    print(f"Total Ai Calls: {len(Ai_Calls)} ({len(unique([x['Seed'] for x in Ai_Calls]))} Seeds)")

    print('\n')

    print('Calls By Rep:')
    for rep in RepCalls:
        print(f"{rep['Name']}: {rep['Total']} Calls ({rep['Seeds']} Seeds)")


    #Engaged
    Engaged = unique([x['Seed'] for x in SMS_INBOUND] +
                     [x['Seed'] for x in Emails_INBOUND] +
                     [x['Seed'] for x in Logs if 'Inbound' in x['Data']['Log Name']]
                     )

    print('\n')
    print(f"Engaged: {len(Engaged)} ")
    print(f"{len(SMS_INBOUND)} Inbound SMS")
    print(f"{len(Emails_INBOUND)} Inbound Emails")
    print(f"{len([x['Seed'] for x in Logs if 'Inbound Call' in x['Data']['Log Name']])} Inbound Calls")


    #Interested
    Interested = unique(
        [x['Seed'] for x in Logs if 'Status changed to Interested' in x['Data']['Log Name']] +
        [x['Seed'] for x in Logs if 'Status changed to App Sent' in x['Data']['Log Name']] +
        [x['Seed'] for x in Logs if 'Status changed to Form Complete' in x['Data']['Log Name']] +
        [x['Seed'] for x in Logs if 'Entered Mailer Code' in x['Data']['Log Name']]
    )

    print('\n')
    print(f'Interested: {len(Interested)}')
    print(f"{len(unique([x['Seed'] for x in Logs if 'Status changed to Interested' in x['Data']['Log Name']]))} Interested Seeds")
    print(f"{len(unique([x['Seed'] for x in Logs if 'Status changed to App Sent' in x['Data']['Log Name']]))} App Sent Seeds")
    print(f"{len(unique([x['Seed'] for x in Logs if 'Status changed to Form Complete' in x['Data']['Log Name']]))} Form Complete Seeds")
    print(f"{len(unique([x['Seed'] for x in Logs if 'Entered Mailer Code' in x['Data']['Log Name']]))} Mailer Scans Seeds")


    Converted = unique(
        [x['Seed'] for x in Logs if 'Stage changed to Submitted' in x['Data']['Log Name']] +
        [x['Seed'] for x in Logs if 'Stage changed to Offer' in x['Data']['Log Name']] +
        [x['Seed'] for x in Logs if 'Stage changed to Funded' in x['Data']['Log Name']] +
        [x['Seed'] for x in Logs if 'Stage changed to Dead' in x['Data']['Log Name']]
    )

    print('\n')
    print(f'Converted: {len(Converted)}')
    print(f"{len(unique([x['Seed'] for x in Logs if 'Stage changed to Submitted' in x['Data']['Log Name']]))} Submitted Seeds")
    print(f"{len(unique([x['Seed'] for x in Logs if 'Stage changed to Offer' in x['Data']['Log Name']]))} Offers Seeds")
    print(f"{len(unique([x['Seed'] for x in Logs if 'Stage changed to Funded' in x['Data']['Log Name']]))} Funded Seeds")
    print(f"{len(unique([x['Seed'] for x in Logs if 'Stage changed to Dead' in x['Data']['Log Name']]))} Dead Seeds")


    print('\n\n\n\--------\n\nBreakdown of Agents and Cadences: \n\nAi Calls By Agent:')
    for agent in Ai_Call_Agents:
        print(f"{agent['Name']}: {agent['Total']} Calls ({agent['Seeds']} Seeds)")
    print('\n\n')

    print('Ai Calls By Cadence:')
    for cadence in Ai_Call_Cadences:
        print(f"{cadence['Name']}: {cadence['Total']} Calls ({cadence['Seeds']} Seeds)")
    print('\n\n')
    print('Emails By Cadence:')
    for cadence in Emails_Cadences:
        print(f"{cadence['Name']}: {cadence['Total']} Emails ({cadence['Seeds']} Seeds)")
    print('\n\n')
    print('SMS By Cadence:')
    for cadence in SMS_Cadences:
        print(f"{cadence['Name']}: {cadence['Total']} Emails ({cadence['Seeds']} Seeds)")

with ui.row():
    with ui.column():
        ui.label('Start:')
        start = ui.date()
    with ui.column():
        ui.label('End:')
        end = ui.date()

ui.button('Run', on_click=lambda e: CalcReport(start.value, end.value))

result = ui.html()
ui.run()
