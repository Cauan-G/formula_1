from django.http import JsonResponse
from django.shortcuts import render
import fastf1

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
