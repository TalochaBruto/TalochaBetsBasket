import requests
import pandas as pd
import numpy as np
import streamlit as st
import time

def get_upcoming_and_live_games(league=None):
    """Obtém jogos ao vivo e próximos via API (exemplo fictício)"""
    url = f'https://api.basketballdata.com/games/upcoming'
    params = { "league": league } if league and league != "Todas" else {}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json().get("games", [])
    return []

def get_team_stats(team):
    """Obtém estatísticas recentes do time via API."""
    url = f'https://api.basketballdata.com/team/stats'
    params = {"team": team}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return {
            'OffRtg': data.get('offensive_rating', 100),
            'DefRtg': data.get('defensive_rating', 100),
            'Pace': data.get('pace', 100),
            'Last5_TeamPoints': np.mean(data.get('last5_avg_points', [100])),
            'Opp_AvgPoints': np.mean(data.get('opponent_avg_points', [100])),
        }
    return None

def predict_winner(game):
    """Prevê o vencedor e os pontos prováveis."""
    team1 = game['team1']
    team2 = game['team2']
    team1_stats = get_team_stats(team1)
    team2_stats = get_team_stats(team2)
    
    if not team1 or not team2:
        return "Dados insuficientes para previsão."
    
    score_factor = np.random.uniform(0.95, 1.05)
    predicted_score1 = round((team1_stats['OffRtg'] + team2_stats['DefRtg']) / 2 * team1_stats['Pace'] * score_factor)
    predicted_score2 = round((team2_stats['OffRtg'] + team1_stats['DefRtg']) / 2 * team2_stats['Pace'] * score_factor)
    
    winner = team1 if predicted_score1 > predicted_score2 else team2
    return f"Previsão: {team1} {predicted_score1} x {predicted_score2} {team2}"

st.title("🏀 Previsão de Jogos de Basquete 🏀")

league = st.selectbox("Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])
games = get_upcoming_and_live_games(league)

if not games:
    st.warning("Nenhum jogo encontrado para a liga selecionada.")
else:
    st.subheader("📢 Jogos ao Vivo e Próximos Jogos")
    game_options = [f"{g['team1']} vs {g['team2']} ({'Ao Vivo' if g['live'] else g['start_time']})" for g in games]
    selected_game = st.selectbox("Escolha um jogo para prever:", game_options)
    
    game = next((g for g in games if f"{g['team1']} vs {g['team2']} ({g['start_time']})" == selected_game), None)
    
    if game and st.button("Prever Resultado"):
        prediction = predict_winner(game)
        st.success(prediction)
    
if st.button("🔄 Atualizar Jogos ao Vivo e Próximos"):
    games = get_upcoming_and_live_games(league)
    st.experimental_rerun()
