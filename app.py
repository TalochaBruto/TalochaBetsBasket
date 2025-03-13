import requests
import pandas as pd
import numpy as np
import streamlit as st

def get_upcoming_and_live_games(league=None):
    """Obtém jogos ao vivo e próximos via API (exemplo fictício)"""
    url = 'https://api.sofascore.com/api/v1/sport/basketball/events/live'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("events", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados da API: {e}")
        return []

def get_team_stats(team):
    """Obtém estatísticas recentes do time."""
    url = 'https://api.sportsdata.io/v3/nba/scores/json/teams'
    try:
        response = requests.get(url)
        response.raise_for_status()
        teams = response.json()
        for team_data in teams:
            if team_data['name'] == team:
                return {
                    'OffRtg': team_data.get('offensiveRating', 100),
                    'DefRtg': team_data.get('defensiveRating', 100),
                    'Pace': team_data.get('pace', 100),
                    'Last5_OppAvg': team_data.get('last5OpponentAvgPoints', 100),
                    'Last5_Scored': team_data.get('last5_scored', 100)
                }
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter estatísticas da equipe: {e}")
        return None

def predict_winner(game):
    """Prevê o vencedor e a pontuação provável."""
    team1 = game['homeTeam']['name']
    team2 = game['awayTeam']['name']
    
    stats1 = get_upcoming_and_live_games(team1)
    stats2 = get_upcoming_and_live_games(team2)
    
    if not stats1 or not stats2:
        return "Dados insuficientes para previsão."
    
    score_mod1 = np.random.uniform(0.9, 1.1)
    score_mod2 = np.random.uniform(0.9, 1.1)
    
    predicted_score1 = round(stats1['Last5_Scored'] * stats1['OffRtg'] / 100 * score_mod1)
    predicted_score2 = round(stats2['Last5_Scored'] * stats2['Pace'] / 100 * score_mod1)
    
    winner = team1 if predicted_score1 > predicted_score2 else team2
    
    return f"{team1}: {predicted_score1} - {team2} {predicted_score2} (Vencedor: {winner})"

def main():
    st.title("📊 Previsão de Jogos de Basquetebol 🏀")
    
    league = st.selectbox("🏀 Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])
    
    games = get_upcoming_and_live_games(league)
    if not games:
        st.error("Nenhum jogo encontrado para esta liga.")
        return
    
    st.subheader("Jogos Ao Vivo e Próximos Jogos")
    for game in games:
        game_info = f"{game['team1']} vs {game['team2']} ({game['status']})"
        st.write(game["time"] + " - " + game['league'])
        st.text(game_info)
    
    selected_game = st.selectbox("Escolha um jogo para prever o resultado", [f"{g['team1']} vs {g['team2']}" for g in games])
    game = next((g for g in games if f"{g['team1']} vs {g['team2']}" in selected_game), None)
    
    if game and st.button("Prever Resultado"):
        prediction = predict_winner(game)
        st.success(prediction)
    
    if st.button("Atualizar Jogos"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
