import os
import json
import asyncio
import time
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from urllib.parse import urlparse, urljoin

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("nba_scraper")

# Base URL and headers to mimic a browser
BASE_URL = "https://www.covers.com"
NBA_PLAYERS_URL = f"{BASE_URL}/sport/basketball/nba/players"
HEADERS = {
    "User-Agent": "PerformaBot/1.0 (https://github.com/PerformaApp/nba-scraper; contact@performa-app.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.covers.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}

# Directory for storing data
DATA_DIR = Path("../data")

# Robots.txt settings
ROBOTS_CACHE_TIMEOUT = 86400  # 24 hours in seconds
ROBOTS_CACHE_FILE = Path("../data/robots_cache.json")


class RobotsParser:
    """Class to parse and check robots.txt rules"""

    def __init__(self):
        self.robots_rules = {}
        self.cache = {}

        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)

        # Load cached robots.txt data if it exists
        if os.path.exists(ROBOTS_CACHE_FILE):
            try:
                with open(ROBOTS_CACHE_FILE, 'r') as f:
                    cache_data = json.load(f)
                    self.cache = {k: (v['rules'], v['timestamp']) for k, v in cache_data.items()}
            except Exception as e:
                logger.error(f"Error loading robots cache: {e}")

    def parse_robots_txt(self, robots_content: str, user_agent: str = "PerformaBot") -> Dict[str, List[str]]:
        """Parse a robots.txt file and return rules for our user-agent"""
        rules = {'allow': [], 'disallow': [], 'crawl_delay': None}
        current_agent = None
        user_agent_lower = user_agent.lower()
        general_rules = None  # Rules for '*' user-agent

        for line in robots_content.split('\n'):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse user-agent lines
            if line.lower().startswith('user-agent:'):
                agent = line.split(':', 1)[1].strip().lower()
                current_agent = agent
                continue

            # Only process rules for our user-agent or '*'
            if current_agent and (current_agent == user_agent_lower or current_agent == '*'):
                if line.lower().startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:  # Only add non-empty paths
                        if current_agent == '*':
                            if general_rules is None:
                                general_rules = {'allow': [], 'disallow': [], 'crawl_delay': None}
                            general_rules['disallow'].append(path)
                        else:
                            rules['disallow'].append(path)

                elif line.lower().startswith('allow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:  # Only add non-empty paths
                        if current_agent == '*':
                            if general_rules is None:
                                general_rules = {'allow': [], 'disallow': [], 'crawl_delay': None}
                            general_rules['allow'].append(path)
                        else:
                            rules['allow'].append(path)

                elif line.lower().startswith('crawl-delay:'):
                    try:
                        delay = float(line.split(':', 1)[1].strip())
                        if current_agent == '*':
                            if general_rules is None:
                                general_rules = {'allow': [], 'disallow': [], 'crawl_delay': None}
                            general_rules['crawl_delay'] = delay
                        else:
                            rules['crawl_delay'] = delay
                    except ValueError:
                        pass

        # If we didn't find specific rules for our user-agent but found rules for '*',
        # use the general rules
        if not rules['allow'] and not rules['disallow'] and not rules['crawl_delay'] and general_rules:
            rules = general_rules

        return rules

    def is_allowed(self, url: str, user_agent: str = "PerformaBot") -> Tuple[bool, float]:
        """Check if a URL is allowed by robots.txt rules

        Returns:
            Tuple containing (is_allowed, crawl_delay)
        """
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        path = parsed_url.path or "/"

        # Check if we have cached rules for this domain
        if base_url in self.cache:
            rules, timestamp = self.cache[base_url]
            # If cache is fresh, use it
            if time.time() - timestamp < ROBOTS_CACHE_TIMEOUT:
                return self._check_path_against_rules(path, rules), rules.get('crawl_delay', 0)

        # Otherwise fetch and parse robots.txt
        try:
            robots_url = f"{base_url}/robots.txt"
            response = requests.get(robots_url, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                robots_content = response.text
                rules = self.parse_robots_txt(robots_content, user_agent)

                # Update cache
                self.cache[base_url] = (rules, time.time())
                self._save_cache()

                return self._check_path_against_rules(path, rules), rules.get('crawl_delay', 0)
            elif response.status_code == 404:
                # No robots.txt means everything is allowed
                self.cache[base_url] = ({'allow': [], 'disallow': [], 'crawl_delay': None}, time.time())
                self._save_cache()
                return True, 0
            else:
                logger.error(f"Failed to fetch robots.txt at {robots_url}, status code: {response.status_code}")
                # If we can't fetch robots.txt, assume everything is allowed
                return True, 0
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            # If there's an error, assume everything is allowed (but log the error)
            return True, 0

    def _check_path_against_rules(self, path: str, rules: Dict[str, List[str]]) -> bool:
        """Check if a path is allowed by the provided rules"""
        # By default, everything is allowed
        allowed = True

        # Find the most specific matching disallow rule
        most_specific_disallow = 0
        for rule in rules.get('disallow', []):
            if self._path_matches_rule(path, rule) and len(rule) > most_specific_disallow:
                most_specific_disallow = len(rule)
                allowed = False

        # Find the most specific matching allow rule
        most_specific_allow = 0
        for rule in rules.get('allow', []):
            if self._path_matches_rule(path, rule) and len(rule) > most_specific_allow:
                most_specific_allow = len(rule)
                # Allow rule only overrides a disallow rule if it's more specific
                if most_specific_allow > most_specific_disallow:
                    allowed = True

        return allowed

    def _path_matches_rule(self, path: str, rule: str) -> bool:
        """Check if a path matches a robots.txt rule, handling wildcards"""
        # Handle wildcards by converting to regex
        if '*' in rule:
            # Escape special regex chars except '*'
            rule_regex = re.escape(rule).replace('\\*', '.*')
            # Add ^ at the beginning to match start of the path
            rule_regex = '^' + rule_regex
            return bool(re.match(rule_regex, path))
        else:
            # Simple case: path starts with rule
            return path.startswith(rule)

    def _save_cache(self):
        """Save the robots.txt cache to a file"""
        try:
            cache_data = {k: {'rules': v[0], 'timestamp': v[1]} for k, v in self.cache.items()}
            with open(ROBOTS_CACHE_FILE, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving robots cache: {e}")


class NBATeamScraper:
    def __init__(self):
        """Initialize the NBA team scraper"""
        self.session = None
        self.teams = []
        self.robots_parser = RobotsParser()

        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)

    async def fetch_page(self, url: str) -> str:
        """Fetch a page and return its content"""
        # First check robots.txt to see if we're allowed to fetch this URL
        is_allowed, crawl_delay = self.robots_parser.is_allowed(url)

        if not is_allowed:
            logger.warning(f"URL {url} is blocked by robots.txt, skipping")
            return ""

        # Apply crawl delay if specified
        if crawl_delay:
            await asyncio.sleep(crawl_delay)

        try:
            async with self.session.get(url, headers=HEADERS) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 429:  # Too Many Requests
                    logger.warning(f"Rate limit hit, sleeping for 30 seconds before retrying {url}")
                    await asyncio.sleep(30)
                    return await self.fetch_page(url)
                else:
                    logger.error(f"Failed to fetch {url}, status code: {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""

    async def get_teams(self) -> List[Dict[str, str]]:
        """Get all NBA teams from the main page"""
        logger.info("Fetching NBA teams...")
        html = await self.fetch_page(NBA_PLAYERS_URL)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        team_containers = soup.select('div.league-home-page__teams a')

        teams = []
        for team in team_containers:
            team_url = team.get('href')
            if team_url and '/teams/' in team_url:
                team_name = team.select_one('h4').text.strip() if team.select_one('h4') else "Unknown"
                teams.append({
                    'id': team_url.split('/')[-1],
                    'name': team_name,
                    'url': f"{BASE_URL}{team_url}"
                })

        logger.info(f"Found {len(teams)} NBA teams")
        return teams

    async def get_team_players(self, team: Dict[str, str]) -> List[Dict[str, Any]]:
        """Get all players for a specific team"""
        logger.info(f"Fetching players for {team['name']}...")
        html = await self.fetch_page(team['url'])
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        player_containers = soup.select('div.team-roster__player')

        players = []
        for player in player_containers:
            player_link = player.select_one('a')
            if player_link:
                player_url = player_link.get('href')
                player_name = player_link.text.strip()

                # Extract other player info
                position_elem = player.select_one('.team-roster__player-position')
                position = position_elem.text.strip() if position_elem else "Unknown"

                players.append({
                    'id': player_url.split('/')[-1] if player_url else None,
                    'name': player_name,
                    'team': team['name'],
                    'team_id': team['id'],
                    'position': position,
                    'url': f"{BASE_URL}{player_url}" if player_url else None
                })

        logger.info(f"Found {len(players)} players for {team['name']}")
        return players

    async def get_player_stats(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Get stats for a specific player"""
        if not player['url']:
            return player

        logger.info(f"Fetching stats for {player['name']}...")
        html = await self.fetch_page(player['url'])
        if not html:
            return player

        soup = BeautifulSoup(html, 'html.parser')

        # Extract player basic info
        try:
            info_section = soup.select_one('.player-card__info')
            if info_section:
                # Update player info with additional details
                player_image = soup.select_one('.player-card__image img')
                if player_image:
                    player['image_url'] = player_image.get('src')

                # Try to get more detailed position
                detailed_position = info_section.select_one(
                    '.player-card__label:contains("Position") + .player-card__value')
                if detailed_position:
                    player['detailed_position'] = detailed_position.text.strip()

                # Get additional info like height, weight, etc.
                height_elem = info_section.select_one('.player-card__label:contains("Height") + .player-card__value')
                if height_elem:
                    player['height'] = height_elem.text.strip()

                weight_elem = info_section.select_one('.player-card__label:contains("Weight") + .player-card__value')
                if weight_elem:
                    player['weight'] = weight_elem.text.strip()
        except Exception as e:
            logger.error(f"Error extracting player info for {player['name']}: {e}")

        # Extract stats tables
        try:
            stats_tables = soup.select('.sortable-stats-table')
            player_stats = {}

            for table in stats_tables:
                # Get table title
                table_title_elem = table.find_previous('h3') or table.find_previous('h2')
                table_title = table_title_elem.text.strip() if table_title_elem else "Unknown Stats"

                # Extract headers
                headers = [th.text.strip() for th in table.select('thead th')]

                # Extract rows
                rows = []
                for tr in table.select('tbody tr'):
                    row_data = {}
                    for i, td in enumerate(tr.select('td')):
                        if i < len(headers):
                            row_data[headers[i]] = td.text.strip()
                    rows.append(row_data)

                player_stats[table_title] = {
                    "headers": headers,
                    "data": rows
                }

            player['stats'] = player_stats
        except Exception as e:
            logger.error(f"Error extracting stats for {player['name']}: {e}")

        # Add a short delay to be respectful to the website
        await asyncio.sleep(1)
        return player

    async def process_team(self, team: Dict[str, str]) -> List[Dict[str, Any]]:
        """Process a team and all its players"""
        players = await self.get_team_players(team)
        player_details = []

        # Process players in batches to avoid overwhelming the server
        batch_size = 3
        for i in range(0, len(players), batch_size):
            batch = players[i:i + batch_size]
            batch_tasks = [self.get_player_stats(player) for player in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            player_details.extend(batch_results)

            # Add a small delay between batches
            if i + batch_size < len(players):
                await asyncio.sleep(2)

        # Save team data
        team_data = {
            'team': team,
            'players': player_details
        }

        with open(DATA_DIR / f"{team['id']}.json", 'w', encoding='utf-8') as f:
            json.dump(team_data, f, indent=2)

        return player_details

    async def run(self) -> Dict[str, Any]:
        """Run the scraper"""
        try:
            logger.info("Starting scraper run...")

            # Check if the main NBA players page is allowed by robots.txt
            is_allowed, crawl_delay = self.robots_parser.is_allowed(NBA_PLAYERS_URL)

            if not is_allowed:
                logger.error(f"The main NBA players URL {NBA_PLAYERS_URL} is blocked by robots.txt, aborting")
                return {
                    'status': 'error',
                    'message': f"The URL {NBA_PLAYERS_URL} is not allowed by robots.txt"
                }

            logger.info(f"Robots.txt check passed for {NBA_PLAYERS_URL}")
            if crawl_delay:
                logger.info(f"Using crawl delay of {crawl_delay} seconds as specified in robots.txt")

            # Use a client session for better performance
            async with aiohttp.ClientSession() as self.session:
                # Get all NBA teams
                self.teams = await self.get_teams()

                if not self.teams:
                    logger.error("Failed to fetch any teams, aborting")
                    return {
                        'status': 'error',
                        'message': "No teams found"
                    }

                logger.info(f"Successfully fetched {len(self.teams)} teams")

                # Store teams data
                with open(DATA_DIR / "teams.json", 'w', encoding='utf-8') as f:
                    json.dump(self.teams, f, indent=2)

                # Process each team
                all_players = []
                for team_index, team in enumerate(self.teams):
                    logger.info(f"Processing team {team_index + 1}/{len(self.teams)}: {team['name']}")
                    players = await self.process_team(team)
                    all_players.extend(players)

                    # Add a delay between teams (respect crawl delay if specified)
                    delay = max(3, crawl_delay if crawl_delay else 0)
                    logger.info(f"Waiting {delay} seconds before processing next team")
                    await asyncio.sleep(delay)

                # Create player index
                player_index = {
                    'players': [
                        {
                            'id': player['id'],
                            'name': player['name'],
                            'team': player['team'],
                            'team_id': player['team_id'],
                            'position': player['position'],
                        }
                        for player in all_players
                    ]
                }

                with open(DATA_DIR / "players.json", 'w', encoding='utf-8') as f:
                    json.dump(player_index, f, indent=2)

                # Create stats summary for visualization
                logger.info("Preparing visualization data")
                visualization_data = self.prepare_visualization_data(all_players)
                with open(DATA_DIR / "visualization_data.json", 'w', encoding='utf-8') as f:
                    json.dump(visualization_data, f, indent=2)

                logger.info(
                    f"Scraping completed successfully: {len(self.teams)} teams and {len(all_players)} players processed")
                return {
                    'teams': len(self.teams),
                    'players': len(all_players),
                    'status': 'complete'
                }
        except Exception as e:
            logger.error(f"Error in scraper: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'message': str(e)
            }

    def prepare_visualization_data(self, players: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for visualization"""
        visualization_data = {}

        for player in players:
            if 'stats' not in player:
                continue

            player_stats = {
                'id': player['id'],
                'name': player['name'],
                'team': player['team'],
                'position': player['position'],
                'stats': {}
            }

            # Process season stats if available
            if 'Regular Season Stats' in player['stats']:
                season_stats = player['stats']['Regular Season Stats']

                # Parse stat rows to historical data format
                points_data = []
                rebounds_data = []
                assists_data = []

                for stat_row in season_stats['data']:
                    season = stat_row.get('Season', '')

                    # Points
                    if 'PPG' in stat_row:
                        points_data.append({
                            'date': season,
                            'value': self.safe_float(stat_row['PPG'])
                        })

                    # Rebounds
                    if 'RPG' in stat_row:
                        rebounds_data.append({
                            'date': season,
                            'value': self.safe_float(stat_row['RPG'])
                        })

                    # Assists
                    if 'APG' in stat_row:
                        assists_data.append({
                            'date': season,
                            'value': self.safe_float(stat_row['APG'])
                        })

                # Sort by date (season) to ensure proper ordering
                player_stats['stats']['points'] = sorted(points_data, key=lambda x: x['date'])
                player_stats['stats']['rebounds'] = sorted(rebounds_data, key=lambda x: x['date'])
                player_stats['stats']['assists'] = sorted(assists_data, key=lambda x: x['date'])

            visualization_data[player['id']] = player_stats

        return visualization_data

    @staticmethod
    def safe_float(value: str) -> float:
        """Safely convert string to float"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0


async def main():
    """Main function to run the scraper"""
    start_time = time.time()
    logger.info("Starting NBA scraper...")

    scraper = NBATeamScraper()
    result = await scraper.run()

    elapsed_time = time.time() - start_time
    logger.info(f"Scraper finished in {elapsed_time:.2f} seconds with result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
