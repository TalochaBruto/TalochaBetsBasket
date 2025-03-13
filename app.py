import requests
import pandas as pd
import numpy as np
import streamlit as st

def get_upcoming_and_live_games(league=None):
    """Obtém jogos ao vivo e próximos via API alternativa (exemplo fictício)."""
    url = 'https://api.sofascore.com/games/upcoming'
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
    """Obtém estatísticas recentes do time usando API alternativa."""
    url = 'https://api.alternativebasketballdata.com/stats'
    params = {"team": team}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            'OffRtg': data.get('offensive_rating', 100),
            'DefRtg': data.get('defensive_rating', 100),
            'Pace': data.get('pace', 100),
            'Last5_OppAvg': np.mean([game['opponent_score'] for game in data.get('last5_games', [])]) if 'last5_games' in data else 100,
            'Last5_TeamPoints': np.mean([game['team_score'] for game in data.get('last5_games', [])]) if 'last5_games' in data else 100,
        }

def predict_winner(game):
    """Prevê o vencedor e a pontuação provável com base nos dados recentes."""
    team1, team2 = game['team1'], game['team2']
    
    stats1 = get_team_stats(team1)
    stats2 = get_team_stats(team2)
    
    if not stats1 or not stats2:
        return "Estatísticas insuficientes para previsão."
    
    score_mod1 = np.random.uniform(0.9, 1.1)
    score_mod2 = np.random.uniform(0.9, 1.1)
    
    predicted_score1 = round(stats1['Last5_TeamPoints'] * stats1['Pace'] / 100 * score_mod1)
    predicted_score2 = round(stats2['Last5_TeamPoints'] * stats2['Pace'] / 100 * score_mod2)
    
    winner = team1 if predicted_score1 > predicted_score2 else team2
    return f"{team1}: {predicted_score1} - {team2} {predicted_score2} (Vencedor: {winner})"

def main():
    st.title("Previsão de Jogos de Basquetebol 🏀")
    
    league = st.selectbox("Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])
    
    games = get_upcoming_and_live_games(league)
    if not games:
        st.warning("Nenhum jogo ao vivo ou próximo encontrado.")
        return
    
    selected_game = st.selectbox("Escolha um jogo para prever o resultado", [f"{g['team1']} vs {g['team2']}" for g in games])
    
    game = next((g for g in games if f"{g['team1']} vs {g['team2']}" == selected_game), None)
    
    if game and st.button("Prever Resultado"):
        prediction = predict_winner(game)
        st.success(prediction)

if __name__ == "__main__":
    main()

