from fastapi import FastAPI, Request
from database import database as connection
from fastapi.responses import  RedirectResponse
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from array import array
import json

# miembros propios
from bussiness.tabla_posiciones import TablaPosiciones
from utilities.utilities_montecarlo import UtilitiesMontecarlo

# trabajo con fechas
from datetime import datetime
from datetime import timedelta

# importing module
import time

from urllib.request import urlopen, Request


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
import pandas as pd




app = FastAPI(
    title='Live de CF',
    description='Prueba de API',
    version='1.0.1'
)

platforms = {
    "spotify": {
        "base_url":"https://spotifycharts.com/regional/"
    },
    "youtube": {
        "base_url":"https://charts.youtube.com/charts/TopSongs/"
    },
    "resultados-futbol": [
        {
            "url_liga_colombia": "https://www.resultados-futbol.com/apertura_colombia2023/grupo1/calendario",
            "bloque_jornada": ".boxhome.boxhome-2col",
            "bloque_tabla_matches_resultados": "table"
        }
    ]
}

# eventos
# @app.on_event('startup')
# def startup():
    # CONEXIÓN COMENTADA DE MOMENTO
    # if connection.is_closed():
    #     connection.connect()

# @app.on_event('shutdown')
# def shutdown():
    # DESCONEXIÓN COMENTADA DE MOMENTO
    # if not connection.is_closed():
    #     connection.close()

@app.get('/')
def index():
    return {
        'success': True
    }
    
@app.get("/regions")
async def regions():
    spot_countries = await get_regions_spotify(platforms["spotify"]["base_url"])
    return {
        "spotify_countries":spot_countries
        }
    
async def get_regions_spotify(url):
    asession = AsyncHTMLSession()
    html = await asession.get(url)
    await html.html.arender(sleep=3)
    soup = BeautifulSoup(html.text, "html.parser")
    drop_down = soup.find_all("div",{"class": "responsive-select", "data-type":"country"})[0]
    countries = {}
    lists = drop_down.find_all("li")
    for l in lists:
        countries[l.text] = {
            "tag":l.attrs.get("data-value", None),
            "url":url + l.attrs.get("data-value", None)
        }

    return countries    
    
@app.get('/scanear')
async def scrapper():
    print('iniciuandoles')
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    })
    
    resp = session.get('https://footystats.org/colombia/categoria-primera-a')
    soup = BeautifulSoup(resp.text, "html.parser")
    
    data = {
        "table": soup.select_one("#league-tables-wrapper div div.table-wrapper table")
    }
    
    return {
        'about': True,
        'success': True,
        'retorno': 817,
        'table': soup
    } 

@app.get('/extract-info-by-league')
async def extract_info_by_league():
    
    utilidades_global = UtilitiesMontecarlo()
    fecha_actual = datetime.now()
    url_liga_betplay_jornadas = platforms["resultados-futbol"][0]
    
    print("arr liga bet play jornadas:; ", url_liga_betplay_jornadas)
    print("json.dumps ::::::::::::::::::::::::::", url_liga_betplay_jornadas["url_liga_colombia"])
    
    url0_finalizacion = "https://www.resultados-futbol.com/finalizacion_colombia2023/grupo1/calendario"
    page0 = urlopen(url0_finalizacion).read()
    soup0 = BeautifulSoup(page0)
    
    # adding 2 seconds time delay
    time.sleep(2)
    tabla0 = soup0.select(".boxhome-2col")
    
    arr_aplazados = []
    arr_contenido_partidos = []
    arr_jornadas_content = []
    
    # Recorriendo todos los partidos por jornadas de una temporada (semestre)
    for table in tabla0:         
         
        jornada = table.find_all("span", class_="titlebox") 
        jornada = jornada[0].text
        rows    = table.select('table tr')
         
        for row in rows:
            
            # ANCHOR - Obteniendo los nombres de los equipos
            equipos = row.find_all("img")
            
            if len(equipos) > 0:
                equipo_1 = equipos[0]
                equipo_1 = equipo_1.get("alt")                
                equipo_2 = equipos[1]
                equipo_2 = equipo_2.get("alt")
        
            
            # validar partido aplazado
            posible_partido_aplazado = row.select("td.rstd")
            
            # posible marcador/fecha partido
            contenido_partido = row.select("td.rstd :not(span)")
            
            # fecha del partido
            fecha_corta_partido = row.select("td.fecha")

            # fecha & hora
            fecha_hora_partido = row.select("td.rstd span.dtstart")
            
            if len(fecha_hora_partido) > 0:
                fecha_hora_partido = fecha_hora_partido[0].text
                
                if fecha_hora_partido is not None:
                    particion_fecha_partido = fecha_hora_partido.split("T")
                    
                    if len(particion_fecha_partido) > 0:
                        fecha_hora_partido = particion_fecha_partido[0].strip() + " " + particion_fecha_partido[1].strip()                    
                            
                        fecha_p = datetime.strptime(fecha_hora_partido, '%Y-%m-%d %H:%M:%S')
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> ", type(fecha_p))
                        print("---------------------------- ", " ahora: ",type(fecha_actual))
                        print("::::::::::::::::::::::::::::", (fecha_p - fecha_actual))
            
            if len(fecha_corta_partido) > 0:
                print(fecha_corta_partido)
                fecha_corta_partido = fecha_corta_partido[0].text


            # ANCHOR Validación del contenido del partido
            if len(contenido_partido) > 0:

                # ANCHOR Validación de partidos aplazados
                if len(posible_partido_aplazado) > 0:
                    
                    cadena_texto_val_partido = posible_partido_aplazado[0].text.strip('\n')
                    cadena_texto_val_partido = cadena_texto_val_partido.strip('\t')                

                    arr_aplazados.append({
                        'aplazado': cadena_texto_val_partido,
                        'coincidencia': 'Apl' in cadena_texto_val_partido
                    })

                
                # ANCHOR - Validar que el partido ya haya pasado
                contenido_a_evaluar = contenido_partido[0].text
                contenido_a_evaluar = contenido_a_evaluar.strip()
                
                goles_equipo_1 = ''
                goles_equipo_2 = ''
                
                if "-" or ":" in contenido_a_evaluar:
                    # test
                    if "-" in contenido_a_evaluar:
                        contenido_a_evaluar = contenido_a_evaluar.split("-")
                        goles_equipo_1 = contenido_a_evaluar[0].strip()
                        goles_equipo_2 = contenido_a_evaluar[1].strip()
                        
                    elif ":" in contenido_a_evaluar:
                        contenido_a_evaluar = contenido_a_evaluar.split(":")
                        goles_equipo_1 = "x"
                        goles_equipo_2 = "x"
                        
                    detalle_partido_jornada = {
                        'jornada'              : jornada,
                        'fecha_corta_partido'  : fecha_corta_partido,
                        'fecha_hora_partido'   : fecha_hora_partido,
                        'equipo1'              : utilidades_global.retornar_cadena_sin_acento(equipo_1),
                        'equipo2'              : utilidades_global.retornar_cadena_sin_acento(equipo_2),
                        'contenido_partido'    : contenido_partido[0].text,
                        'goles_equipo1'        : goles_equipo_1,
                        'goles_equipo2'        : goles_equipo_2,
                        'partido_aplazado_flag': cadena_texto_val_partido,
                    }
                    
                    arr_contenido_partidos.append(detalle_partido_jornada)
                    
        # solo partidos jugados
        if len(arr_contenido_partidos) > 0:
            arr_jornadas_content.append(arr_contenido_partidos)

        arr_contenido_partidos = []                        
                    
    return {
        'about': True,
        'success': True,
        'retorno': 817,
        'matches_league_path': None,
        'position_table_league_path': None,
        'matches': None,
        'aplazados': arr_aplazados,
        'partidos_por_jornada': arr_jornadas_content,
        'tabla_posiciones': None
    }

@app.get('/ext-position-table-by-league')
async def extPositionTableByLeague(matches_league_path: str = None, position_table_league_path: str = None):

    utilidades_global = UtilitiesMontecarlo()

    # URL SEMILLA
    url = "https://www.goal.com/es-co/primera-a/clasificaci%C3%B3n/2ty8ihceabty8yddmu31iuuej"
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # REQUERIMIENTO AL SERVIDOR
    driver.get(url)
    soup_posiciones = BeautifulSoup(driver.page_source, 'lxml')
    lista_de_equipos = soup_posiciones.find_all('div', class_='wff_standings_table_row') 
    equipos_posicion = []
    
    for equipo in lista_de_equipos: # ITERAR ELEMENTO POR ELEMENTO    

        posicion_equipo = equipo.find(class_='wff_standings_position_marker').text.lstrip().rstrip()
        nombre_equipo = equipo.find(class_='wff_participant_name').text.lstrip().rstrip()
        
        # Grupo de estadísticas
        estadisticas_equipo = equipo.find_all(class_='wff_standings_stats_box')
        cantidad_estadisticas = len(estadisticas_equipo)        
        dict_estadisticas = {}
        contador = 0
        
        goles_a_favor = ''
        goles_en_contra = ''        

        # recorriendo estadísticas
        while contador < cantidad_estadisticas:
            est = estadisticas_equipo[contador]
            item_dynamic = est.select_one('div > div').text
            # dict_estadisticas[contador] = item_dynamic.strip()
            
            if contador == 4:
                goles_favor_y_contra = item_dynamic.strip().replace(" ", "")
                goles_favor_y_contra = goles_favor_y_contra.split('-')
                
                print("elemento #4: split ", goles_favor_y_contra)
                
                if len(goles_favor_y_contra) > 0:
                    goles_a_favor = goles_favor_y_contra[0]
                    goles_en_contra = goles_favor_y_contra[1]
                
                dict_estadisticas[contador] = item_dynamic.strip().replace(" ", "")
            else:
                dict_estadisticas[contador] = item_dynamic.strip()            
            
            contador+=1        
        
        # grupo de últimos partidos jugados
        ultimos_partidos_jugados_container = equipo.find(class_='wff_form')
        ultimos_jugados_items = ultimos_partidos_jugados_container.find_all(class_='wff_form_ball')
        cantidad_ultimos_jugados = len(ultimos_jugados_items)        
        contador = 0
        dict_ultimos_jugados = {}
        
        if cantidad_ultimos_jugados > 0:
            operaciones_tabla = TablaPosiciones() 
        
        while contador < cantidad_ultimos_jugados:
            jugado = ultimos_jugados_items[contador]            
            item_dynamic = jugado.select_one('div.wff_label_text').text
            item_dynamic = item_dynamic.strip()
            
            if item_dynamic != '?':                
                res_numerico = operaciones_tabla.transcribir_partidos_jugados(
                    item_dynamic
                )
                dict_ultimos_jugados[contador] = res_numerico
                
            contador+=1            
        
        equipos_posicion.append({
            'nombre_equipo_acronimo':       '',
            'nombre_equipo_full':           utilidades_global.retornar_cadena_sin_acento(nombre_equipo),
            'posicion':                     posicion_equipo,
            'partidos_jugados':             dict_estadisticas[0],
            'partidos_ganados':             dict_estadisticas[1]   if len(dict_estadisticas) > 0 else '',
            'partidos_empatados':           dict_estadisticas[2] if len(dict_estadisticas) > 1 else '',
            'partidos_perdidos':            dict_estadisticas[3]  if len(dict_estadisticas) > 2 else '',
            'goles_a_favor':                goles_a_favor,
            'goles_en_contra':              goles_en_contra,
            'goles_diferencia':             dict_estadisticas[5]   if len(dict_estadisticas) > 4 else '',
            'puntos':                       dict_estadisticas[6] if len(dict_estadisticas) > 5 else '',
            'resultados_ultimos_5_jugados': dict_ultimos_jugados,
        })
    
    return {
        'tabla_posiciones': equipos_posicion
    } 

@app.get('/scanear2')
async def scrapper2(matches_league_path: str = None, position_table_league_path: str = None):    
    
    # TODO: Creación de instancias/utilidades
    tabla_posiciones = TablaPosiciones()
    utilidades_global = UtilitiesMontecarlo()
    
    fecha_actual = datetime.now()
    ahora = fecha_actual #datetime.strptime(fecha_actual, '%Y-%m-%d %H:%M:%S')
    
    
    #     {
    #     "url_liga_colombia": "https://www.resultados-futbol.com/apertura_colombia2023/grupo1/calendario",
    #     "bloque_jornada": ".boxhome.boxhome-2col",
    #     "bloque_tabla_matches_resultados": ".boxhome.boxhome-2col table"
    # }
    
    # calendario_liga = {
    #     'header_info': {            
    #     },
    #     'content_info': {
    #         {
    #             'jornada': None,
    #             'partidos': [
    #                 {
    #                     'fecha': None,
    #                     'estado_partido': 'jugado',
    #                     'equipo1': {
    #                         'nombre_equipo': None,
    #                         'goles_anotados': 0
    #                     }
                        
    #                 }
    #             ]
    #         }
    #     }
    # }
    
    # liga_origen = {
    #     'pais': 'COLOMBIA',
    #     'semestre': 1
    # }
        
    # calendario_liga.update(liga_origen)
    
    
    
    
    url_liga_betplay_jornadas = platforms["resultados-futbol"][0]
    json_url_liga_betplay_jornadas = json.dumps(url_liga_betplay_jornadas)
    # json.loads
    print("arr liga bet play jornadas:; ", url_liga_betplay_jornadas)
    
    print("json.dumps ::::::::::::::::::::::::::", url_liga_betplay_jornadas["url_liga_colombia"])
    
    url0  = "https://www.resultados-futbol.com/apertura_colombia2023/grupo1/calendario"
    url0_finalizacion = "https://www.resultados-futbol.com/finalizacion_colombia2023/grupo1/calendario"
    page0 = urlopen(url0_finalizacion).read()
    soup0 = BeautifulSoup(page0)
    
    # adding 2 seconds time delay
    time.sleep(2)
    
    tabla0 = soup0.select(".boxhome-2col")
    # print("# talba >>>>>>>>>>>>>>>>>>> ", tabla0)
    # rows = tabla.find_all('tr')    
    
    arr_aplazados = []
    arr_contenido_partidos = []
    arr_jornadas_content = []
    
    # Recorriendo todos los partidos por jornadas de una temporada (semestre)
    for table in tabla0:
         
        jornada = table.find_all("span", class_="titlebox") 
        # jornada = jornada.text
        # print("tipo: ", type(jornada), " :::::::::::::::::::::::::::: JORNADA ::::::::::::::::::::::::::::::::::::::::::: ", jornada[0].text)
        jornada = jornada[0].text
         
        rows = table.select('table tr')
        
        # trs = rows.find_all("tr")
        #  print("tabla >>>>>>>>>>>>>>>>>>>  ", rows)
         
        for row in rows:
            # print("tabla >>>>>>>>>>>>>>>>>>>  ", row)
    
            # info por row de partidos por jornada en liga
            # fpartido = row.select(".fecha")
            fpartido = row.select("td.fecha") 
            
            # ANCHOR - Obteniendo los nombres de los equipos
            equipos = row.find_all("img")
            
            if len(equipos) > 0:
                equipo_1 = equipos[0]
                equipo_1 = equipo_1.get("alt")
                
                equipo_2 = equipos[1]
                equipo_2 = equipo_2.get("alt")
        
            
            # validar partido aplazado
            posible_partido_aplazado = row.select("td.rstd")
            
            # posible marcador/fecha partido
            contenido_partido = row.select("td.rstd :not(span)")
            
                        
            
            # resultado:
            resultado_goles_partido = row.select("td.rstd a.url")
            
            # detalles partido, alternativas
            link_detalles_partido = row.find("a", {"class": "c"}).get("href")
            link_detalles_partido = row.find("a", {"class": "link"})
            
            # fecha del partido
            fecha_corta_partido = row.select("td.fecha")
            # fecha & hora
            fecha_hora_partido = row.select("td.rstd span.dtstart")
                        
            
            if len(fecha_hora_partido) > 0:
                fecha_hora_partido = fecha_hora_partido[0].text
                
                if fecha_hora_partido is not None:
                    particion_fecha_partido = fecha_hora_partido.split("T")
                    
                    if len(particion_fecha_partido) > 0:
                        fecha_hora_partido = particion_fecha_partido[0].strip() + " " + particion_fecha_partido[1].strip()                    
                            
                        fecha_p = datetime.strptime(fecha_hora_partido, '%Y-%m-%d %H:%M:%S')
                        fecha_p2 = datetime.strftime(fecha_actual, '%Y-%m-%d %H:%M:%S')
                        print("ttttttttttttttttttttttttttttttttttt ", type(fecha_p))
                        print("ddddddddddddddddddddddddddddd ", " ahora: ",type(fecha_actual))
                        print("reswtassssssssssssssssssss ", (fecha_p - fecha_actual))

            
            if len(fecha_corta_partido) > 0:
                print(fecha_corta_partido)
                fecha_corta_partido = fecha_corta_partido[0].text
                
            

            # ANCHOR Validación del contenido del partido            
            # print("contenido partido:::: ", len(contenido_partido))
            
            if len(contenido_partido) > 0:
                # print("CONTENIDO PARTIDO <<<<<<<<<<<<<<<<<<<<<< ///////////////////  ", contenido_partido[0])


                # ANCHOR Validación de partidos aplazados
                if len(posible_partido_aplazado) > 0:
                    
                    cadena_texto_val_partido = posible_partido_aplazado[0].text.strip('\n')
                    cadena_texto_val_partido = cadena_texto_val_partido.strip('\t')                

                    arr_aplazados.append({
                        'aplazado': cadena_texto_val_partido,
                        'coincidencia': 'Apl' in cadena_texto_val_partido
                    })
                    # if posible_partido_aplazado[0].text == 'Apl':

                
                # ANCHOR - Validar que el partido ya haya pasado
                contenido_a_evaluar = contenido_partido[0].text
                contenido_a_evaluar = contenido_a_evaluar.strip()
                
                goles_equipo_1 = ''
                goles_equipo_2 = ''
                
                if "-" or ":" in contenido_a_evaluar:
                    # test
                    if "-" in contenido_a_evaluar:
                        contenido_a_evaluar = contenido_a_evaluar.split("-")
                        goles_equipo_1 = contenido_a_evaluar[0].strip()
                        goles_equipo_2 = contenido_a_evaluar[1].strip()
                        
                    elif ":" in contenido_a_evaluar:
                        contenido_a_evaluar = contenido_a_evaluar.split(":")
                        goles_equipo_1 = "x"
                        goles_equipo_2 = "x"
                        
                    detalle_partido_jornada = {
                        'jornada'              : jornada,
                        'fecha_corta_partido'  : fecha_corta_partido,
                        'fecha_hora_partido'   : fecha_hora_partido,
                        'equipo1'              : utilidades_global.retornar_cadena_sin_acento(equipo_1),
                        'equipo2'              : utilidades_global.retornar_cadena_sin_acento(equipo_2),
                        'contenido_partido'    : contenido_partido[0].text,
                        'goles_equipo1'        : goles_equipo_1,
                        'goles_equipo2'        : goles_equipo_2,
                        'partido_aplazado_flag': cadena_texto_val_partido,
                    }
                    
                    arr_contenido_partidos.append(detalle_partido_jornada)


                
            # if len(resultado_goles_partido) > 0:
            #     print("goles partido ¿? ????????????????????? ", resultado_goles_partido[0].text)
            
            # link_path_detalles = link_detalles_partido.get('href')
            
            # fpartido = row.select("td.fecha") 
            
            # print("jornada: ", jornada, "fecha partido: ", type(fpartido), " ::: ", fpartido[0].text)
            # print("Resumen partido >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> :::::::::::::: ", link_detalles_partido)
    
            # ******************** https://www.resultados-futbol.com/
            
            # url_details  = "https://www.resultados-futbol.com" + link_detalles_partido
            # page_details = urlopen(url_details).read()
            # soup_details = BeautifulSoup(page_details)            

            # print(" &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& ", soup_details)
            

        # solo partidos jugados
        if len(arr_contenido_partidos) > 0:
            arr_jornadas_content.append(arr_contenido_partidos)

        arr_contenido_partidos = []        
    
















    # ----------------------------------------------------------------------------------------------
    position_table_league_for_date = []
    matches_league_for_date = []
    
    # utilidades = Scrapper()
    
    #      https://apuestas.wplay.co/es/t/19311/Colombia-Primera-A
    url = "https://apuestas.wplay.co/es/t/19311/Colombia-Primera-A"
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    page2 = urlopen(req).read().decode('utf8')
    #page2 = urlopen(req, timeout=10).read()
    
    soup = BeautifulSoup(page2)
    
    
    # TODO: descomentar esto
    tabla = soup.find("table")
    rows = tabla.find_all('tr')
        
    for row in rows:
        # print("row::: ")
        # if (row.find('th', {"scope":"row"}) != None):
        time_hour = row.find_all("span", class_="time")
        time_date = row.find_all("span", class_="date")
        
        # print("hour: ", time_hour[0].text)
        # print("tome: ", time_date[0].text)
        
        partido1 = row.find_all("td", class_="seln")
        
        equipo1 = row.select("td div > button > span > span.seln-label > span > span")
        cuota_equipo = row.select("td div > button > span .price.dec")
        # print("equipo:::::: ", equipo1[0].text, "  cuota: ", cuota_equipo[0].text, " empate.:: ", cuota_equipo[1].text)        
        # print("equipo2:::::: ", equipo1[2].text, " cupta equipo 2: ", cuota_equipo[2].text)
        
        # CREANDO POR CADA PARTIDO EL OBJECTO CON LA INFO CORRESPONDIENTE
        match_date = {
            'time_match': time_hour[0].text,
            'date_match': time_date[0].text,
            'team_local': equipo1[0].text,
            'quota_team_local': cuota_equipo[0].text,
            'quota_tie': cuota_equipo[1].text,
            'team_visiting': equipo1[2].text,
            'quota_team_visiting': cuota_equipo[2].text
        }

        matches_league_for_date.append(match_date)    
 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    # ----------------------------------------------------------------------------------------------        
    ## tabla de posiciones:
    url_posiciones = "https://www.goal.com/es-co/primera-a/clasificaci%C3%B3n/2ty8ihceabty8yddmu31iuuej"
    url_posiciones_test_ligue_fr =  "https://www.flashscore.co/futbol/francia/ligue-1/clasificacion/#/Q1sSPOn5/table/overall"
    
    # req_positions = Request(url_posiciones, headers={'User-Agent': 'XYZ/3.0'})
    
    # page_positions = urlopen(req_positions).read().decode('utf8')
    
    # # page_posiciones = urlopen(url_posiciones_test_ligue_fr).read()
    # soup_posiciones = BeautifulSoup(page_positions)
    # time.sleep(5)
    # # tabla_pos = soup_posiciones.find_all("div", {"class": "wff_standings_table_body"})
    # tabla_pos = soup_posiciones.select('.wff_standings_table_body')
    
    
    # url = url_posiciones
    # browser = webdriver.Chrome()
    # browser.get(url)
    # time.sleep(5)
    # soup_posiciones = BeautifulSoup(browser.page_source, 'html')
    # result = soup_posiciones.findAll('div', {'class':  'wff_standings_table_body'})
    # print (">>>> >>>> >>>>", result)
    
    
    
    
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url_posiciones)
    soup_posiciones = BeautifulSoup(driver.page_source, 'lxml')
    result = soup_posiciones.select('.wff_standings_table_body .wff_standings_table_row')
    rows = result
    
    #print (">>>> >>>> >>>>", result)
    
    # rows = result.select('.wff_standings_table_row')
    # result2 = result.findAll('div', {'class':  'wff_standings_table_row'})
    
    
    # print (">>>> >>>> >>>>", result2)
    
    # page = urlopen(url_posiciones).read()

    # soup = BeautifulSoup(page, "html.parser")
    # time.sleep(3)
    # tabla0 = soup.find_all("div", class_="wff_standings_table_body")
    
    # print("tabla :::>>> ")
    
    posicion_tabla = 0    
    equipos_posicion = []
    
    partidos_jugados     = None
    partidos_ganados     = None
    partidos_empatados   = None
    partidos_perdidos    = None
    goles_a_favor        = None
    goles_en_contra      = None
    goles_diferencia     = None
    resultados_5_ultimos = None
    resultados_5_ultimos = []
    resultados_5_ultimos_int = []
        
    # TODO: descomentar esto
    for row in rows:
        index_columna = 0
        
        for col in row:
            
            colParser = BeautifulSoup(col)
            
            if index_columna == 0:
                #test = col.select("div wff_standings_position_markers") #find_all("div", class_="wff_standings_position_marker")
                texto_procesado = (col)
                print("tipo >>> ", type(col))
                print("tipo >>> ", type(colParser))
                
                #print(">>> este es la posición ::: ", texto_procesado, "tesstt >>> ", test)
                
            if index_columna == 5:
                texto_procesado = (col.text).lstrip()
                equipo_name = texto_procesado.split()
                print("# split equipo >> ", equipo_name, "# lenght ", equipo_name)

                
                if len(equipo_name) == 3:
                    # test
                    print("# split equipo >> ", equipo_name[1] + " " + equipo_name[2])
            
    #         # Partidos jugados, ganados, empatados, perdidos
            if index_columna >= 3 and index_columna <=23:
                operaciones_tabla = TablaPosiciones()                
                
                if index_columna == 3:
                    partidos_jugados = (col.text).lstrip()
                elif index_columna == 4:
                    partidos_ganados = (col.text).lstrip()
                elif index_columna == 5:
                    partidos_empatados = (col.text).lstrip()
                elif index_columna == 6:
                    partidos_perdidos = (col.text).lstrip()
                elif index_columna == 7:
                    goles_a_favor = (col.text).lstrip()
                elif index_columna == 8:
                    goles_en_contra = (col.text).lstrip()
                elif index_columna == 9:
                    goles_diferencia = (col.text).strip()
                elif index_columna == 10:
                    puntos = (col.text).lstrip()
                elif index_columna == 11 and posicion_tabla > 0:
                    ultimos_jugados_text = col.select("td a")

                    if len(ultimos_jugados_text) > 0:
                        i = 0
                        while i <= 4:
                            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!! ", ultimos_jugados_text[i].text)
                            item = ultimos_jugados_text[i].text
                            resultados_5_ultimos.append(item.strip())
                            
                            res_numerico = operaciones_tabla.transcribir_partidos_jugados(
                                item.strip()
                            )
                            resultados_5_ultimos_int.append(res_numerico)

                            i += 1                    


                #     if posicion_tabla > 0: 
                #         resultados_5_ultimos = col                    
                #         print("############## ultimos 5 ::::::::::::::::", resultados_5_ultimos)
                    
                texto_procesado = (col.text).lstrip()
                # print(">>> resto de columnas en la tabla de posiciones ::: ", texto_procesado, " <----¦ index de ese dato: ", index_columna)
            
            index_columna = index_columna + 1
            
        
        # resultados_5_ultimos = []
        if len(equipo_name) > 0:
            if posicion_tabla > 0: 
                equipos_posicion.append({
                    #'nombre_equipo_acronimo': utilidades_global.retornar_cadena_sin_acento(equipo_name[0]),
                    #'nombre_equipo_full': utilidades_global.retornar_cadena_sin_acento(equipo_name[1]),
                    'posicion': posicion_tabla,
                    'partidos_jugados': partidos_jugados,
                    'partidos_ganados': partidos_ganados,
                    'partidos_empatados': partidos_empatados,
                    'partidos_perdidos': partidos_perdidos,
                    'goles_a_favor': goles_a_favor,
                    'goles_en_contra': goles_en_contra,
                    'goles_diferencia': goles_diferencia,
                    'puntos': puntos,
                    'resultados_ultimos_5_jugados': resultados_5_ultimos,
                    'resultados_ultimos_5_jugados_int': resultados_5_ultimos_int
                })
            
        posicion_tabla = posicion_tabla + 1
        
    #     resultados_5_ultimos = []
    #     resultados_5_ultimos_int = []
        
    #     # position = row.find_all("td")

    #     # print("posiciones >>>>> ", position)
    #     # test = tabla_pos.find(position)
    #     # print("test >>>>> ", (test))
            
    # print(tabla)    
    
    return {
        'about': True,
        'success': True,
        'retorno': 817,
        'matches_league_path': matches_league_path,
        'position_table_league_path': position_table_league_path,
        'matches': matches_league_for_date,
        'aplazados': arr_aplazados,
        'partidos_por_jornada': arr_jornadas_content,
        'tabla_posiciones': equipos_posicion
    } 
 
class CalendarioLiga():    
    
    def __init__(self, semestre):
        self.semestre = semestre
        

class Scrapper():
    
    def scrapedata(self, tag):
        url = f'https://quotes/toscrape/tag/{tag}'
        # s = HTMLSession()
        # r = s.get(url)
        # print(r.status_code)
        
    def getTest (self):
        return '817'
    
    # Python3 code to remove whitespace
    def remove(self, string):
        return string.replace(" ", "")       