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
    except Exception as e:
        st.error(f"Erro ao obter dados da API: {str(e)}")
        return []

def get_team_stats(team):
    """Obtém estatísticas recentes de um time via API."""
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
            'Last5_AvgPoints': data.get('avg_points_last_5', 100),
        }
    except Exception as e:
        st.error(f"Erro ao obter dados da equipe {team}: {str(e)}")
        return None

def predict_winner(game):
    """Prevê o vencedor e a pontuação provável com base nos dados recentes."""
    try:
        team1 = game['homeTeam']['name']
        team2 = game['awayTeam']['name']
        
        team1_stats = get_team_stats(team1)
        team2_stats = get_team_stats(team2)
        
        if not team1 or not team2 or not team1_stats or not team2_stats:
            return "Estatísticas insuficientes para prever o resultado."
        
        # Modelo básico de previsão de pontuação
        score_mod1 = np.random.uniform(0.9, 1.1)
        score_mod2 = np.random.uniform(0.9, 1.1)
        predicted_score1 = round((team1['OffRtg'] * team1['Pace'] / 100) * score_mod1)
        predicted_score2 = round(team2_stats['Last5_TeamPoints'] * team2_stats['Pace'] / 100 * score_mod1)
        
        winner = team1 if predicted_score1 > predicted_score2 else team2
        return f"Previsão: {team1} {predicted_score1} - {predicted_score2} {team2}"
    except KeyError as e:
        return f"Erro ao acessar dados: {str(e)}. O formato dos dados pode ter mudado."

def main():
    """Interface principal do aplicativo Streamlit."""
    st.title("📊 Previsão de Jogos de Basquetebol 🏀")
    league = st.selectbox("Escolha a Liga", ["Todas", "NBA", "EuroLeague", "NBB"])
    games = get_upcoming_and_live_games(league)
    
    if not games:
        st.error("Nenhum jogo encontrado para esta liga.")
        return
    
    st.subheader("🏀 Jogos Ao Vivo e Próximos")
    game_options = [f"{game['homeTeam']['name']} vs {game['awayTeam']['name']}" for game in games]
    selected_game = st.selectbox("Selecione um jogo:", game_options if games else ["Nenhum jogo disponível"])
    
    game = next((g for g in games if f"{g['homeTeam']['name']} vs {g['awayTeam']['name']}" in selected_game), None)
    
    if game and st.button("Prever Resultado"):
        prediction = predict_winner(game)
        st.write(prediction)
    
    if st.button("Atualizar Jogos em Tempo Real"):
        st.experimental_rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="Previsão de Jogos de Basquetebol", layout="centered")
    main()
