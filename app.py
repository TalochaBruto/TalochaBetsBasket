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
        response.raise_for_status()  # Garante que erros da API são tratados
        games = response.json()
        if not games:
            st.warning("Nenhum jogo encontrado para a liga selecionada ou erro na API.")
            return []
        return games
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados da API: {e}")
        return []

def get_team_stats(team):
    """Obtém estatísticas recentes de um time via API (exemplo fictício)."""
    url = 'https://api.basketballdata.com/teams/stats'
    params = {"team": team}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            'OffRtg': data.get('offensive_rating', 100),
            'DefRtg': data.get('defensive_rating', 100),
            'Pace': data.get('pace', 100),
            'Last5_TeamPoints': np.mean([game['team_score'] for game in data.get('last_5_games', []) if 'team_score' in game])
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados da API: {e}")
        return None

def predict_winner(game):
    """Prevê o vencedor e a pontuação provável com base nos dados recentes."""
    team1 = game.get('home_team', 'Time 1')
    team2 = game.get('away_team', 'Time 2')
    
    team1_stats = get_team_stats(team1)
    team2_stats = get_team_stats(team2)
    
    if not team1_stats or not team2_stats:
        st.error("Erro ao obter estatísticas para um ou ambos os times.")
        return "Erro ao processar previsão. Dados indisponíveis."
    
    score_factor = np.random.uniform(0.9, 1.1)
    pred_score1 = round(team1_stats['Last5_TeamPoints'] * team1_stats['Pace'] / 100 * score_mod)
    pred_score2 = round(team2_stats['Last5_TeamPoints'] * team2_stats['Pace'] / 100 * score_mod)
    
    winner = team1 if pred_score1 > pred_score2 else team2
    return f"Previsão: {winner} vence - Placar estimado: {team1} {predicted_score1} x {predicted_score2} {team2}"

st.title("Previsão de Jogos de Basquetebol 🏀")
league = st.selectbox("Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])

if st.button("Carregar Jogos"):
    games = get_upcoming_and_live_games(league)
    if games:
        selected_game = st.selectbox("Selecione um jogo para prever:", [f"{g.get('team1')} vs {g.get('team2')} - {g.get('status', 'Agendado')}" for g in games])
        
        game = next((g for g in games if f"{g['team1']} vs {g['team2']}" in selected_game), None)
        
        if game and st.button("Prever Resultado"):
            prediction = predict_winner(game)
            if prediction:
                st.success(f"Previsão de placar: {prediction}")
            else:
                st.error("Não foi possível calcular a previsão do jogo.")
    else:
        st.warning("Nenhum jogo encontrado ou erro na API.")
