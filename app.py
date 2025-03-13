import requests
import pandas as pd
import numpy as np
import streamlit as st

def get_upcoming_and_live_games(league=None):
    """Obtém jogos ao vivo e próximos via API (exemplo fictício)"""
    url = 'https://api.basketballdata.com/games/upcoming'
    params = {"league": league} if league and league != "Todas" else {}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("games", [])  # Certificando que retornamos uma lista válida
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados da API: {e}")
        return []

def get_team_stats(team):
    """Obtém estatísticas recentes do time via API (exemplo fictício)"""
    url = f'https://api.basketballdata.com/team/stats'
    params = {"team": team}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            'OffRtg': data.get('offensive_rating', 100),
            'DefRtg': data.get('defensive_rating', 100),
            'Pace': data.get('pace', 100),
            'Last5_OpponentAvg': sum(game['opponent_score'] for game in data.get('last5_games', [])) / 5 if 'last5_games' in data else 100,
            'Last5_TeamPoints': sum(game['team_score'] for game in data.get('last5_games', [])) / 5 if 'last5_games' in data else 100
        }
    except requests.RequestException:
        return None

def predict_winner(game):
    """Prevê o vencedor e a pontuação provável com base nos dados recentes."""
    team1 = game['team1']
    team2 = game['team2']
    
    stats1 = get_team_stats(team1)
    stats2 = get_team_stats(team2)
    
    if not stats1 or not stats2:
        return "Não foi possível prever este jogo. Dados insuficientes."
    
    score_mod1 = np.random.uniform(0.95, 1.05)
    score_mod2 = np.random.uniform(0.9, 1.1)
    
    predicted_score1 = round(stats1['Last5_TeamPoints'] * (stats1['Pace'] / 100) * score_mod)
    predicted_score2 = round(stats2['Last5_TeamPoints'] * stats2['Pace'] / 100 * score_mod)
    
    winner = team1 if predicted_score1 > predicted_score2 else team2
    return f"Previsão: {team1} {predicted_score1} x {predicted_score2} {team2} (Vencedor: {winner})"

st.title("🏀 Previsão de Jogos de Basquetebol 🏀")

league = st.selectbox("Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])

games = get_upcoming_and_live_games(league)

if not games:
    st.write("Nenhum jogo ao vivo ou próximo disponível.")
else:
    st.subheader("🏀 Jogos ao vivo e próximos 🏀")
    for game in games:
        game_desc = f"{game['team1']} vs {g['team2']} ({game['status']})"
        if st.button(game_options):
            prediction = predict_winner(game)
            st.write(prediction)


