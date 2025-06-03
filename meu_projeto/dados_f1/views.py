from django.http import JsonResponse
from django.shortcuts import render
import fastf1
from fastf1.ergast import Ergast
from django.utils import timezone

fastf1.Cache.enable_cache('cache')

def pagina_f1(request):
    ergast = Ergast()
    drivers_response = ergast.get_driver_standings(season='current')
    constructors_response = ergast.get_constructor_standings(season='current')
    
    standings_df = drivers_response.content[0] 
    standings_cf = constructors_response.content[0] 


    drivers = []
    for _, row in standings_df.iterrows():
        drivers.append({
            'position': row['position'],
            'name': f"{row['givenName']} {row['familyName']}",
            'points': row['points'],
            'constructorNames': row['constructorNames'],
        })
    
    constructors = []
    for _, row in standings_cf.iterrows():
        constructors.append({
            'position': row['position'],
            'points': row['points'],
            'constructorName': row['constructorName'],
        })

    return render(request, 'home.html', {'drivers': drivers, 'constructors': constructors})

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
                'time': driver.get('Time', 'N/A'),
                'status': driver['Status'],
                'color': driver['TeamColor'],
                'grid': driver['GridPosition']
            })
    context = {
        'race_name': f"{last_race['EventName']} - {last_race['Country']}" if last_race is not None else 'Race not found',
        'results': results
    }

    return render(request, 'last_race.html', context)