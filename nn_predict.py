from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np
import os

#loaded_model = load_model('first_model.keras')
loaded_model = load_model(os.path.join("models_data", 'second_model.keras'))

#Lo separamos en 2 porque era muy pesado para github
players1 = pd.read_csv(os.path.join("models_data", "players1.csv"))
players2 = pd.read_csv(os.path.join("models_data", "players2.csv"))

# Fusionar los DataFrames en uno solo
stats_players_data = pd.read_csv(os.path.join("models_data", "players_stats.csv"))
stats_teams_data = pd.read_csv(os.path.join("models_data", "teams_stats.csv"))
history_players_data = pd.concat([players1, players2], ignore_index=True)

stats_players_data.rename(columns={'earned gpm': 'egpm'}, inplace=True)
stats_teams_data.rename(columns={'team kpm': 'teamkpm'}, inplace=True)
print("Dataframes loaded and ready!")

def generate_base_dict():
    game_data_dict = {
        "blue_team_rating": None,
        "blue_team_rd": None,
        "blue_team_kills": None,
        "blue_team_deaths": None,
        "blue_team_assists": None,
        "blue_team_ckpm": None,
        "blue_team_teamkpm": None,

        "blue_bot_rating": None,
        "blue_bot_rd": None,
        "blue_bot_kills": None,
        "blue_bot_deaths": None,
        "blue_bot_assists": None,
        "blue_bot_egpm": None,

        "blue_jng_rating": None,
        "blue_jng_rd": None,
        "blue_jng_kills": None,
        "blue_jng_deaths": None,
        "blue_jng_assists": None,
        "blue_jng_egpm": None,

        "blue_mid_rating": None,
        "blue_mid_rd": None,
        "blue_mid_kills": None,
        "blue_mid_deaths": None,
        "blue_mid_assists": None,
        "blue_mid_egpm": None,

        "blue_sup_rating": None,
        "blue_sup_rd": None,
        "blue_sup_kills": None,
        "blue_sup_deaths": None,
        "blue_sup_assists": None,
        "blue_sup_egpm": None,

        "blue_top_rating": None,
        "blue_top_rd": None,
        "blue_top_kills": None,
        "blue_top_deaths": None,
        "blue_top_assists": None,
        "blue_top_egpm": None,

        "red_team_rating": None,
        "red_team_rd": None,
        "red_team_kills": None,
        "red_team_deaths": None,
        "red_team_assists": None,
        "red_team_ckpm": None,
        "red_team_teamkpm": None,

        "red_bot_rating": None,
        "red_bot_rd": None,
        "red_bot_kills": None,
        "red_bot_deaths": None,
        "red_bot_assists": None,
        "red_bot_egpm": None,

        "red_jng_rating": None,
        "red_jng_rd": None,
        "red_jng_kills": None,
        "red_jng_deaths": None,
        "red_jng_assists": None,
        "red_jng_egpm": None,

        "red_mid_rating": None,
        "red_mid_rd": None,
        "red_mid_kills": None,
        "red_mid_deaths": None,
        "red_mid_assists": None,
        "red_mid_egpm": None, 

        "red_sup_rating": None,
        "red_sup_rd": None,
        "red_sup_kills": None,
        "red_sup_deaths": None,
        "red_sup_assists": None,
        "red_sup_egpm": None, 

        "red_top_rating": None,
        "red_top_rd": None,
        "red_top_kills": None,
        "red_top_deaths": None,
        "red_top_assists": None,
        "red_top_egpm": None
    }
    return game_data_dict

def get_stats_for_prediction(blue: str, red:str):
    base_dict = generate_base_dict()

    #get team players
    history_players_data['date'] = pd.to_datetime(history_players_data['date'])

    def find_players(team):
        #Buscamos azul
        team_players = {
            "bot":None,
            "jng":None,
            "mid":None,
            "sup":None,
            "top":None}

        team_history_data = history_players_data[history_players_data["teamname"] == team].copy()
        most_recent_date = team_history_data.sort_values(by='date', ascending=False).iloc[0]["date"]
        most_recent_match = team_history_data[team_history_data["date"] == most_recent_date]
        players = most_recent_match.sort_values(by=['position'])[["position", "playername"]]
        for _, player in players.iterrows():
            team_players[player["position"]] = player["playername"]
        return team_players
    
    all_players = {
        "blue": find_players(blue),
        "red": find_players(red),
        }

    try:
        for i, team in enumerate([blue, red]):
            sides = ["blue", "red"]
            column_base = f"{sides[i]}_team"

            filtered_data = stats_teams_data[stats_teams_data["teamname"] == team][['rating', 'rd', 'kills', 'deaths', 
                                                                                        'assists', 'ckpm', 'teamkpm']]
            column_names = filtered_data.columns.tolist()
            row_values = filtered_data.iloc[0].tolist()

            for column_name, value in zip(column_names, row_values):
                base_dict[f"{column_base}_{column_name}"] = value

        #Ahora obtenemos por jugador
        for side, players in all_players.items():
            for position, playername in players.items():
                column_base = f"{side}_{position}"
                filtered_data = stats_players_data[stats_players_data["playername"] == playername][['rating', 'rd', 
                                                                                                'kills', 'deaths', 'assists', 
                                                                                                'egpm']]
                column_names = filtered_data.columns.tolist()
                row_values = filtered_data.iloc[0].tolist()

                for column_name, value in zip(column_names, row_values):
                    base_dict[f"{column_base}_{column_name}"] = value

        return base_dict
    except Exception as e:
        # print(f"Error in game {blue} vs {red}: {e}")
        raise e

def predict_match(blue:str, red:str):
    stats_data = get_stats_for_prediction(blue, red)
    stats_df = pd.DataFrame([stats_data])
    
    prediction = loaded_model.predict(stats_df)
    return prediction
