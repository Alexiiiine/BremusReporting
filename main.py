import json, pandas as pd
from datetime import datetime
from nicegui import ui, native

def SalesforceCallsReport(file, start_date, end_date):
    report = {}
    logs = json.loads(pd.read_csv(file, encoding='ISO-8859-1', dtype=str).to_json(orient='records'))
    logs = [x for x in logs if x['Call Type'] == 'Outbound']
    for l in logs:
        l['Completed Date/Time'] = datetime.strptime(l['Completed Date/Time'], '%m/%d/%Y %I:%M %p')
    print(f'{start_date} --> {end_date}')
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    filtered_data = []
    for item in logs:
        item_date = item['Completed Date/Time']
        if start_date <= item_date <= end_date:
            filtered_data.append(item)

    Reps = []
    for call in filtered_data:
        if call['Call Duration (seconds)'] is None:
            call['Call Duration (seconds)'] = 0
        if call['Created By'] not in Reps:
            Reps.append(call['Created By'])


    totalCalls = 0
    totalTalkTime = 0
    totalSeedsCalled = 0
    summary = ''
    for Rep in Reps:
        calls = [x for x in filtered_data if x['Created By'] == Rep]
        talkTime = round(sum([int(x['Call Duration (seconds)']) for x in calls])/60,2)
        seeds = []
        for call in calls:
            if call['Bremus Id'] not in seeds:
                seeds.append(call['Bremus Id'])

        print(f"{Rep}: {len(calls)} calls ({talkTime} minutes) to {len(seeds)} seeds")
        summary = f"{summary}<br>{Rep}: {len(calls)} calls ({talkTime} minutes) to {len(seeds)} seeds"
        totalCalls = totalCalls + len(calls)
        totalTalkTime = totalTalkTime + talkTime
        totalSeedsCalled = totalSeedsCalled + len(seeds)
        report[Rep] = {
            "Calls":len(calls),
            "talkTime":talkTime,
            "Seeds":len(seeds)
        }
    print(f"Overall: {totalCalls} calls ({round(totalTalkTime,2)} minutes) to {totalSeedsCalled} seeds")
    summary = f"{summary}<br>Overall: {totalCalls} calls ({round(totalTalkTime,2)} minutes) to {totalSeedsCalled} seeds"
    report['Overall'] = {
        "Calls": totalCalls,
        "talkTime": totalTalkTime,
        "Seeds": totalSeedsCalled
    }
    report['Summary'] = summary
    result.set_content(summary)
    return report

def updateFile(file):
    with open('Report.csv', 'wb') as f:
        f.write(file.read())

def pickEnd(start):
    ui.label('Now pick a end date:')
    end = ui.date(value='2023-01-01', on_change=lambda e: result.set_text(e.value))
    ui.button('Run', on_click= lambda e: SalesforceCallsReport('Report.csv', start, end.value))



ui.label(text='Pick file')
ui.upload(auto_upload=True, on_upload=lambda e: updateFile(e.content)).classes('max-w-full')

ui.label('Start:')
start = ui.date(value='2024-01-01')

ui.label('End:')
end = ui.date(value='2024-01-01')

ui.button('Run', on_click=lambda e: SalesforceCallsReport('Report.csv', start.value, end.value))


result = ui.html()
ui.run()
# SalesforceCallsReport('2024Logs.csv', '5/1/2024', '6/1/2024')
