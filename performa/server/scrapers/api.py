from fastapi import FastAPI, HTTPException, BackgroundTasks
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

from nba_scraper import NBATeamScraper

app = FastAPI(
    title="Performa NBA Scraper API",
    description="API for scraping and retrieving NBA player data",
    version="1.0.0"
)

# Directory for storing data
DATA_DIR = Path("../data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize scraper
scraper = NBATeamScraper()

# Tracking background task status
scraper_status = {
    "running": False,
    "last_run": None,
    "progress": {
        "teams_total": 0,
        "teams_processed": 0,
        "players_processed": 0
    }
}


async def run_scraper_task():
    """Background task to run the scraper"""
    global scraper_status

    try:
        scraper_status["running"] = True
        result = await scraper.run()
        scraper_status["running"] = False
        scraper_status["last_run"] = {
            "time": str(pd.Timestamp.now()),
            "result": result
        }
    except Exception as e:
        scraper_status["running"] = False
        scraper_status["last_run"] = {
            "time": str(pd.Timestamp.now()),
            "error": str(e)
        }


@app.get("/")
async def read_root():
    """Root endpoint"""
    return {"message": "Performa NBA Scraper API", "version": "1.0.0"}


@app.post("/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Trigger a new scrape"""
    if scraper_status["running"]:
        return {"message": "Scraper is already running", "status": scraper_status}

    background_tasks.add_task(run_scraper_task)
    return {"message": "Scraper started", "status": "running"}


@app.get("/status")
async def get_status():
    """Get the current scraper status"""
    return scraper_status


@app.get("/teams")
async def get_teams():
    """Get all NBA teams"""
    try:
        teams_file = DATA_DIR / "teams.json"
        if not teams_file.exists():
            return {"teams": []}

        with open(teams_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading teams: {str(e)}")


@app.get("/players")
async def get_players():
    """Get all NBA players"""
    try:
        players_file = DATA_DIR / "players.json"
        if not players_file.exists():
            return {"players": []}

        with open(players_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading players: {str(e)}")


@app.get("/players/{player_id}")
async def get_player(player_id: str):
    """Get details for a specific player"""
    try:
        # Find which team this player belongs to
        players_file = DATA_DIR / "players.json"
        if not players_file.exists():
            raise HTTPException(status_code=404, detail="No player data available")

        with open(players_file, 'r', encoding='utf-8') as f:
            players_data = json.load(f)

        player_info = None
        for player in players_data.get('players', []):
            if player.get('id') == player_id:
                player_info = player
                break

        if not player_info:
            raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")

        # Get detailed player data from team file
        team_file = DATA_DIR / f"{player_info['team_id']}.json"
        if not team_file.exists():
            raise HTTPException(status_code=404, detail=f"Team data for {player_info['team']} not found")

        with open(team_file, 'r', encoding='utf-8') as f:
            team_data = json.load(f)

        for player in team_data.get('players', []):
            if player.get('id') == player_id:
                return player

        raise HTTPException(status_code=404, detail=f"Player data for {player_id} not found in team file")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading player: {str(e)}")


@app.get("/visualization")
async def get_visualization_data():
    """Get formatted data for visualization"""
    try:
        viz_file = DATA_DIR / "visualization_data.json"
        if not viz_file.exists():
            return {"message": "No visualization data available"}

        with open(viz_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading visualization data: {str(e)}")


@app.get("/teams/{team_id}")
async def get_team(team_id: str):
    """Get details for a specific team"""
    try:
        team_file = DATA_DIR / f"{team_id}.json"
        if not team_file.exists():
            raise HTTPException(status_code=404, detail=f"Team with id {team_id} not found")

        with open(team_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading team: {str(e)}")


# Run with: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=5000, reload=True)
