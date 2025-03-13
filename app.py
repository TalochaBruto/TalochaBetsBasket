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
        return data.get("games", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados da API: {e}")
        return []

def get_team_stats(team):
    """Obtém estatísticas do time via API."""
    url = 'https://api.basketballdata.com/team/stats'
    params = {"team": team}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            'OffRtg': data.get('offensive_rating', 100),
            'DefRtg': data.get('defensive_rating', 100),
            'Pace': data.get('pace', 100),
            'Last5_TeamPoints': np.mean(data.get('last_5_games', [100]))
        }
    except (requests.exceptions.RequestException, KeyError, TypeError) as e:
        st.error(f"Erro ao obter dados da equipe: {e}")
        return None

def predict_winner(game):
    """Prevê o vencedor e a pontuação provável com base nos dados recentes."""
    team1 = game.get('team1')
    team2 = game.get('team2')
    
    if not team1 or not team2:
        return "Dados insuficientes para prever o vencedor."
    
    team1_stats = get_team_stats(team1)
    team2_stats = get_team_stats(team2)
    
    if not team1_stats or not team2:
        return "Estatísticas do time não disponíveis."
    
    predicted_score1 = round(team1_stats['Last5_TeamPoints'] * team1_stats['OffRtg'] / 100 * np.random.uniform(0.9, 1.1))
    predicted_score2 = round(team2_stats['Last5_TeamPoints'] * team2_stats['OffRtg'] / 100 * np.random.uniform(0.9, 1.1))
    
    winner = team1 if predicted_score1 > predicted_score2 else team2
    return f"Previsão de Placar: {team1} {predicted_score1} x {predicted_score2} {team2}" 

st.title("🏀 Previsão de Jogos de Basquete")

league = st.selectbox("Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])

games = get_upcoming_and_live_games(league)
if not games:
    st.error("Nenhum jogo encontrado ou erro na API.")
else:
    st.subheader("Jogos ao Vivo e Próximos")
    game_options = [f"{g['team1']} vs {g['team2']} ({g.get('status', 'Desconhecido')})" for g in games]
    selected_game = st.selectbox("Selecione um jogo para previsão:", game_options if game_options else ["Nenhum jogo disponível"])
    
    game = next((g for g in games if f"{g['team1']} vs {g['team2']}" in selected_game), None)
    
    if game and st.button("Prever Resultado"):
        prediction = predict_winner(game)
        st.success(prediction)
    
    if not games:
        st.warning("Nenhum jogo disponível no momento.")
