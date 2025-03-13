import requests
import streamlit as st
import numpy as np

def get_upcoming_and_live_games(league=None):
    """Obtém jogos ao vivo e próximos via API (exemplo fictício)"""
    url = 'https://api.sofascore.com/api/v1/sport/basketball/scheduled'
    params = {"league": league} if league and league != "Todas" else {}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("events", [])
    except Exception as e:
        st.error(f"Erro ao obter dados da API: {str(e)}")
        return []

def get_team_stats(team):
    """Obtém estatísticas recentes do time."""
    url = 'https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/2025'
    params = {"team": team, "key": "SUA_API_KEY"}  # Substituir pela chave real
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        team_data = next((t for t in data if t['Name'] == team), None)
        
        if team_data:
            return {
                'OffRtg': team_data.get('OffensiveRating', 100),
                'DefRtg': team_data.get('DefensiveRating', 100),
                'Pace': team_data.get('Pace', 100),
                'Last5_OppAvg': team_data.get('OpponentPointsPerGame', 100),
                'Last5_Scored': team_data.get('PointsPerGame', 100)
            }
    except Exception as e:
        st.error(f"Erro ao obter dados da equipe: {str(e)}")
        return None

def predict_winner(game):
    """Prevê o vencedor e a pontuação provável."""
    try:
        team1 = game['homeTeam']['name']
        team2 = game['awayTeam']['name']
        
        stats1 = get_team_stats(team1)
        stats2 = get_team_stats(team2)
        
        if not stats1 or not stats2:
            return "Não foi possível obter dados suficientes para previsão."
        
        score_mod1 = np.random.uniform(0.9, 1.1)
        score_mod2 = np.random.uniform(0.9, 1.1)
        
        predicted_score1 = round(stats1['Last5_Scored'] * stats1['Pace'] / 100 * score_mod1)
        predicted_score2 = round(stats2['Last5_Scored'] * stats2['Pace'] / 100 * score_mod1)
        
        winner = team1 if predicted_score1 > predicted_score2 else team2
        return f"Previsão: {team1} {predicted_score1} - {predicted_score2} {team2}. Vencedor provável: {winner}" 

def main():
    st.title("📊 Previsão de Jogos de Basquetebol 🏀")
    
    league = st.selectbox("🏀 Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])
    games = get_upcoming_and_live_games(league)
    
    if not games:
        st.error("Nenhum jogo encontrado para esta liga.")
        return
    
    st.subheader("🏀 Jogos ao Vivo e Próximos Jogos")
    
    selected_game = st.selectbox("Selecione um jogo para previsão:", 
                                 [f"{game['homeTeam']['name']} vs {game['awayTeam']['name']}" for game in games])
    
    game = next((g for g in games if f"{g['homeTeam']['name']} vs {g['awayTeam']['name']}" in selected_game), None)
    
    if game and st.button("Prever Resultado"):
        prediction = predict_winner(game)
        st.success(prediction)
    
    if st.button("Atualizar Jogos"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
