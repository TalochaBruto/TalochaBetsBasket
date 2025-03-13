import requests
import streamlit as st
import numpy as np

def get_upcoming_and_live_games(league=None):
    """Obtém jogos ao vivo e próximos via API (exemplo fictício)"""
    url = 'https://api.basketballdata.com/games/upcoming'
    params = {"league": league} if league and league != "Todas" else {}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("events", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados da API: {str(e)}")
        return []

def get_team_stats(team):
    """Obtém estatísticas recentes do time via API (exemplo fictício)"""
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
            'Last5_Avg_Score': data.get('last_5_games_avg_score', 100)
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados da API para {team}: {str(e)}")
        return None

def predict_winner(game):
    """Prevê o vencedor e a pontuação provável com base nos dados recentes."""
    try:
        team1 = game['home_team']
        team2 = game['away_team']
        team1_stats = get_team_stats(team1)
        team2_stats = get_team_stats(team2)
        
        if not team1_stats or not team2_stats:
            return "Estatísticas insuficientes para prever o resultado."
        
        score_mod1 = np.random.uniform(0.9, 1.1)
        score_mod2 = np.random.uniform(0.9, 1.1)
        
        predicted_score1 = round(team1_stats['OffRtg'] * (team1_stats['Pace'] / 100) * score_mod1)
        predicted_score2 = round(team2_stats['OffRtg'] * (team2_stats['Pace'] / 100) * score_mod2)
        
        winner = team1 if predicted_score1 > predicted_score2 else team2
        return f"Previsão: {winner} deve vencer - {team1}: {predicted_score1} x {predicted_score2} {team2}"
    except KeyError as e:
        return f"Erro: Chave ausente nos dados - {str(e)}"
    except Exception as e:
        return f"Erro ao prever resultado: {str(e)}"

st.set_page_config(page_title="Previsão de Jogos de Basquetebol", layout="centered")
st.title("Previsão de Jogos de Basquetebol 🏀")

league = st.selectbox("Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])

st.write("Buscando jogos ao vivo e próximos...")
games = get_upcoming_and_live_games(league)
if not games:
    st.error("Nenhum jogo encontrado ou erro na API.")
else:
    game_options = [f"{game['homeTeam']['name']} vs {game['awayTeam']['name']} ({game['status']})" for game in games]
    selected_game = st.selectbox("Selecione um jogo:", game_options)
    
    game = next((g for g in games if f"{g['homeTeam']} vs {g['away_team']}" in selected_game), None)
    
    if game and st.button("Prever Resultado"):
        prediction = predict_winner(game)
        st.success(prediction)

if __name__ == "__main__":
    main()
