import requests
import streamlit as st
import numpy as np

def get_upcoming_and_live_games(league=None):
    """Obtém jogos ao vivo e próximos via API (exemplo fictício)"""
    url = 'https://api.basketballdata.com/games/upcoming'
    params = {"league": league} if league and league != "Todas" else {}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("games", [])  # Certificando-se de que retorna uma lista válida
    except Exception as e:
        st.error("Erro ao buscar jogos: " + str(e))
    
    return []

def get_team_stats(team):
    """Obtém estatísticas recentes do time via API (exemplo fictício)"""
    url = f'https://api.basketballdata.com/team/stats'
    params = {"team": team}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                'OffRtg': data.get('offensive_rating', 100),
                'DefRtg': data.get('defensive_rating', 100),
                'Pace': data.get('pace', 100),
                'Last5_TeamPoints': np.mean(data.get('last5_games', [])) if 'last5_TeamPoints' in data else 100
            }
        else:
            return None

def predict_winner(team1, team2):
    """Previsão do vencedor e placares prováveis."""
    stats1 = get_team_stats(team1)
    stats2 = get_team_stats(team2)
    
    if not stats1 or not stats2:
        return "Não foi possível prever este jogo. Dados insuficientes."
    
    predicted_score1 = round(stats1['Last5_TeamPoints'] * stats1['Pace'] / 100 * np.random.uniform(0.95, 1.05))
    predicted_score2 = round(stats2['Last5_TeamPoints'] * stats2['Pace'] / 100 * np.random.uniform(0.95, 1.05))
    
    winner = team1 if predicted_score1 > predicted_score2 else team2
    return f"Previsão: {team1} {predicted_score1} x {predicted_score2} {team2} (Vencedor: {winner})"

st.title("🏀 Previsão de Jogos de Basquetebol 🏀")

league = st.selectbox("Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])

games = get_upcoming_and_live_games(league)
if not games:
    st.warning("Nenhum jogo ao vivo ou programado para esta liga.")
else:
    game_options = [f"{g['team1']} vs {g['team2']} ({g['status']})" for g in games]
    selected_game = st.selectbox("Escolha um jogo para previsão", game_options)
    
    game = next((g for g in games if f"{g['team1']} vs {g['team2']}" in selected_game), None)
    
    if game and st.button("Prever Resultado"):
        st.subheader(f"🔮 {predict_winner(game)}")

