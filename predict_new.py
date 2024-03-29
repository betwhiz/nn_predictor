import datetime as dt
from dotenv import dotenv_values
from schedule_generator import PandascoreSchedule

from typing import Optional
import pandas as pd

import numpy as np

import nn_predict as nnp

config = dotenv_values(".env")
def schedule_generate(start = dt.datetime.now()):

    time_format = "%Y-%m-%dT%H:%M:%SZ"
    panda = PandascoreSchedule(api_key=config.get("PANDASCORE_KEY"))
    end = (dt.datetime.now() + dt.timedelta(days=1))

    schedule = panda.get_schedule(start_datetime=start.strftime(time_format), end_datetime=end.strftime(time_format))
    return schedule

# Helper/Utility Functions:
def __team_namer(team_name: str) -> str:
    """
    Rename teams to ensure consistency between Oracles Elixir data and the schedule API.

    Parameters
    ----------
    team_name : str
        Name of team from the data set.
    Returns
    -------
    str
        The correct team name.
    """

    # Misnomers Format: (API Name) : (Flattened Teams Name)
    misnomers = {
        "Schalke 04": "FC Schalke 04 Esports",
        "Edward Gaming": "EDward Gaming",
        "kt Rolster": "KT Rolster",
        "TT": "ThunderTalk Gaming",
        "Thunder Talk Gaming": "ThunderTalk Gaming",
        "NONGSHIM REDFORCE": "Nongshim RedForce",
        "NongShim REDFORCE": "Nongshim RedForce",
        "Nongshim Red Force": "Nongshim RedForce",
        "EXCEL": "Excel Esports",
        "Dignitas QNTMPAY": "Dignitas",
        "Immortals Progressive": "Immortals",
        "Team SoloMid": "TSM",
        "Team SoloMid Academy": "TSM Academy",
        "Team SoloMid Amateur": "TSM Amateur",
        "BDS": "Team BDS",
        "BDS Academy": "Team BDS Academy",
        "INTZ e-Sports": "INTZ",
        "EDward Gaming Youth Team": "EDG Youth Team",
        "Istanbul Wildcats": "İstanbul Wildcats",
        "KaBuM! eSports": "KaBuM! e-Sports",
        "MAX E-Sports Club": "MAX",
        "Hive Athens": "Hive Athens EC",
        "Komil&Friends": "Komil&amp;Friends",
        "GG&Esports": "GGEsports",
        "UCAM Esports Club": "UCAM Tokiers",
        "We Love Gaming": "WLGaming Esports",
        "⁠Entropiq": "Entropiq",
        "FURIA Esports": "FURIA",
        "Vivo Keyd": "Vivo Keyd Stars",
        "NRG Esports": "NRG",
        "West Point Esports PH": "West Point Esports"
    }

    if team_name in misnomers.keys():
        return misnomers[team_name]
    else:
        return team_name

def __schedule_predictor(blue_name: str, red_name: str):
    """
    Parameters
    ----------
    blue_name: str
        String containing the name of blue team, matching OE data.
    red_name: str
        String containing the name of the red team, matching OE data.

    Returns
    -------
    probability: int
        Likelihood that the blue team will win.
    """
    try:
        match_prediction = nnp.predict_match(blue_name, red_name)
        match = match_prediction[0,0]
        print("Las predicciones se extraen correctamente")
        return match
    except Exception as e:
        print(f"Error: {blue_name}, {red_name}, {e}")
        return "Error al calcular"

def schedule_predict(schedule: Optional[pd.DataFrame]):
    predictions = schedule.copy()
    predictions["Blue win"] = predictions.apply(lambda row: __schedule_predictor(row["Blue"], row["Red"]), axis=1)
    #matches.to_csv(filepath.joinpath('data', 'processed', 'schedule.csv'), index=False)
    return predictions

def main():
    print("Schedule generation...")
    schedule = schedule_generate()
    try:
        schedule['Blue'] = schedule['Blue'].apply(lambda x: __team_namer(x))
        schedule['Red'] = schedule['Red'].apply(lambda x: __team_namer(x))
    except Exception as e:
        print("No se han encontrado un nuevo schedule para el dia de hoy")
        raise e
    
    print(schedule)
    print("Schedule generated! Strarting predicctions...")
    
    predictions = schedule_predict(schedule=schedule)
    return predictions

if __name__ in ('__main__', '__builtin__', 'builtins'):
    start = dt.datetime.now()
    main()
    end = dt.datetime.now()
    elapsed = end - start
    print(f"Schedule and predictions generated in {elapsed}.")