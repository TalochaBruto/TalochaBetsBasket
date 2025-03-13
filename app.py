import requests
import pandas as pd
import numpy as np
import streamlit as st
import time

def get_game_data(league=None):
    """Obtém os jogos ao vivo e próximos jogos de uma liga específica (ou todas as ligas)."""
    url = "https://api.basketballdata.com/games/live_and_upcoming"
    params = {"league": league} if league else {}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    return []

def get_team_stats(team):
    """Obtém estatísticas avançadas do time."""
    url = f"https://api.basketballdata.com/team_stats?team={team}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'OffRtg': data.get('offensive_rating', 100),
            'DefRtg': data.get('defensive_rating', 100),
            'Pace': data.get('pace', 100),
            'Last5_Opponent_Strength': np.mean([g['opponent_rating'] for g in data['last_5_games']]),
            'Last5_Team_Points': np.mean([g['team_score'] for g in data['last_5_games']]),
            'Last5_Opponent_Points': np.mean([g['opponent_score'] for g in data['last_5_games']])
        }
    return None

def predict_winner(game):
    team1_stats = get_team_stats(game['team1'])
    team2_stats = get_team_stats(game['team2'])
    
    if not team1_stats or not team2_stats:
        return "Sem dados suficientes para previsão."
    
    score1 = (team1_stats['OffRtg'] + team2_stats['DefRtg']) / 2 * team1_stats['Pace'] / 100
    score2 = team2_stats['OffRtg'] * team1_stats['Pace'] / 100
    
    if team1_stats['Last5_Opponent_Strength'] > team2_stats['Last5_Opponent_Strength']:
        score_mod = 1.05  # Ajuste para o time que enfrentou adversários mais fortes recentemente
    else:
        score_mod = 0.95
    
    predicted_score1 = round(score_mod * score_mod * score_mod * team1_stats['Last5_Opponent_Strength'])
    predicted_score2 = team2_stats['Last5_Opponent_Strength'] * score_mod
    
    winner = game['team1'] if predicted_score1 > predicted_score2 else game['team2']
    return f"Previsão: {winner} vence. Placar Estimado: {predicted_score1} - {predicted_score2}"

st.set_page_config(page_title="🏀 Previsões de Basquetebol - Live & Próximos Jogos")

# Selecionar liga
league = st.selectbox("Escolha a Liga", ["NBA", "EuroLeague", "NBB", "Todas"])

games = get_upcoming_and_live_games()

def format_game_title(game):
    return f"{game['team1']} vs {game['team2']} ({game['time_status']})"

games_filtered = [game for game in games if league is None or game['league'] == league]
selected_game = st.selectbox("Selecione um jogo para previsão:", options=[format_game_status(game) for game in games_filtered])
if st.button("Prever Resultado") and selected_game:
    game_info = next((g for g in games_filtered if format_game_status(g) == selected_game), None)
    if game_data:
        st.write(predict_winner(game['team1'], game['team2']))

st.write("🔄 Acompanhe os jogos ao vivo e previsões para os próximos 4h.")

def update_live_scores():
    """Atualiza os placares dos jogos que estão em andamento."""
    live_games = [game for game in games_filtered if game['time_status'] == "AO VIVO"]
    for game in live_games:
        game_data = get_game_data()
        live_score = [g for g in games if g['team1'] == game['team1'] and g['team2'] == game['team2']]
        if live_score:
            game['score'] = live_score[0]['score']
    
    st.rerun()

# Atualização automática a cada 30 segundos para os jogos ao vivo
if any(game['time_status'] == "AO VIVO" for game in games_filtered):
    while True:
        time.sleep(30)
        update_game_status()
