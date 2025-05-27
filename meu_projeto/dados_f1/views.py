from django.http import JsonResponse
from django.shortcuts import render
import fastf1
from django.utils import timezone

fastf1.Cache.enable_cache('cache')

def pagina_f1(request):
    return render(request, 'home.html')

def corrida_view(request):
    session = fastf1.get_session(2025, 'Monaco', 'R')
    session.load()
    pilotos = session.laps['Driver']
    
    print(pilotos)
    
    ver_voltas = session.laps.pick_drivers(['HAM'])
    volta_rapida = ver_voltas.pick_fastest()
    
    return JsonResponse({
        'piloto': volta_rapida['Driver'],
        'tempo_volta': str(volta_rapida['LapTime']),
        'volta': volta_rapida['LapNumber'],
    })

def last_race(request):

    year = timezone.now().year
    now = timezone.now()

    schedule = fastf1.get_event_schedule(year)

    last_race = None
    for _, row in schedule.iterrows():
        if row['Session5Date'] < now:
            last_race = row

    results = []

    if last_race is not None:
        event = fastf1.get_event(year, last_race['RoundNumber'])
        race = event.get_session('R')
        race.load()

        results_df = race.results

        for _, driver in results_df.iterrows():
            results.append({
                'position': driver['Position'],
                'full_name': driver['FullName'],
                'abbreviation': driver['Abbreviation'],
                'team': driver['TeamName'],
                'status': driver['Status']
            })

    context = {
        'race_name': f"{last_race['EventName']} - {last_race['Country']}" if last_race is not None else 'Race not found',
        'results': results
    }

    return render(request, 'last_race.html', context)