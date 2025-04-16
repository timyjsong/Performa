import asyncio
import argparse
from nba_scraper import NBATeamScraper, logger

async def run_scraper():
    """Run the NBA scraper"""
    scraper = NBATeamScraper()
    result = await scraper.run()
    logger.info(f"Scraper result: {result}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the NBA scraper")
    parser.add_argument('--run_async', action='store_true', help="Run in async mode")
    args = parser.parse_args()

    if args.run_async:
        # For running the scraper as a background process
        logger.info("Starting scraper in async mode")
        asyncio.run(run_scraper())
    else:
        # For running the scraper directly
        logger.info("Starting scraper")
        asyncio.run(run_scraper())
