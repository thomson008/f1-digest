import requests
import xml.etree.ElementTree as ET
from datetime import date, datetime

class Race(object):
    def __init__(self, race_xml):
        self.name = race_xml[0].text
        self.date = race_xml[2].text
        self.time = race_xml[3].text
        self.round = race_xml.attrib['round']


    def __str__(self):
        return (f"{self.name}, Round {self.round}, {self.date} "
            f"{self.time.replace('Z', ' UTC')}")


def get_all_races():
    url = 'http://ergast.com/api/f1/current'
    response_xml = get_data_from_api(url)
    races = response_xml[0]

    races_list = []
    for race in races:
        race_object = Race(race)
        races_list.append(race_object)

    return races_list


def get_data_from_api(url):
    response = requests.get(url).content
    response_xml = ET.fromstring(response)

    return response_xml.find('.')


def get_next_race():
    all_races = get_all_races()

    for race in all_races:
        year, month, day = get_ymd(race.date)

        if date(year, month, day) > date.today():
            return race

    return None


def get_last_results_and_standings():
    race, race_results = get_last_results()
    year = race.date.split('-')[0]
    standings = get_driver_standings(year, race.round)

    return race, race_results, standings
    

def get_last_results():
    url = 'http://ergast.com/api/f1/current/last/results'
    response_xml = get_data_from_api(url)

    race = response_xml[0][0]
    results = race[4]

    race_object = Race(race)

    result_list = []
    for result in results:
        position = result.attrib['position']
        points = result.attrib['points']
        number = result.attrib['number']
        name = f'{result[0][1].text} {result[0][2].text}'

        result_list.append(f'{position}. {name} [{number}]: +{points} pts')

    return race_object, '\n'.join(result_list)


def get_driver_standings(year, round):
    url = f'http://ergast.com/api/f1/{year}/{round}/driverStandings'
    response_xml = get_data_from_api(url)
    standings = response_xml[0][0]
    
    standings_list = []
    for standing in standings:
        position = standing.attrib['position']
        points = standing.attrib['points']
        number = standing[0][0].text
        name = f'{standing[0][1].text} {standing[0][2].text}'

        standings_list.append(f'{position}. {name} [{number}]: {points} pts')

    return '\n'.join(standings_list)


def get_ymd(race_date):
    dt = datetime.strptime(race_date, "%Y-%m-%d")
    year = dt.year
    month = dt.month
    day = dt.day

    return year, month, day