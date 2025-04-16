import asyncio
import time
from typing import Dict, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("rate_limiter")


class RateLimiter:
    """
    Rate limiter to ensure we don't overwhelm the target server with requests.
    Maintains separate rate limits per domain.
    """

    def __init__(self, default_requests_per_minute: int = 20):
        """
        Initialize the rate limiter

        Args:
            default_requests_per_minute: Default number of requests allowed per minute
        """
        self.default_rate = default_requests_per_minute
        self.domain_rates: Dict[str, int] = {}
        self.domain_last_request: Dict[str, float] = {}
        self.domain_tokens: Dict[str, float] = {}
        self.domain_locks: Dict[str, asyncio.Lock] = {}

    def set_domain_rate(self, domain: str, requests_per_minute: int):
        """
        Set the rate limit for a specific domain

        Args:
            domain: The domain to set the rate for
            requests_per_minute: Number of requests allowed per minute
        """
        self.domain_rates[domain] = requests_per_minute
        # Initialize with full tokens
        self.domain_tokens[domain] = requests_per_minute
        self.domain_last_request[domain] = time.time()

        # Create a lock if one doesn't exist
        if domain not in self.domain_locks:
            self.domain_locks[domain] = asyncio.Lock()

    def _get_domain_lock(self, domain: str) -> asyncio.Lock:
        """Get the lock for a domain, creating it if necessary"""
        if domain not in self.domain_locks:
            self.domain_locks[domain] = asyncio.Lock()
        return self.domain_locks[domain]

    def _get_domain_rate(self, domain: str) -> int:
        """Get the rate limit for a domain"""
        return self.domain_rates.get(domain, self.default_rate)

    async def acquire(self, domain: str) -> None:
        """
        Acquire permission to make a request to the domain.
        This method will block until a request token is available.

        Args:
            domain: The domain for the request
        """
        domain_lock = self._get_domain_lock(domain)

        async with domain_lock:
            rate = self._get_domain_rate(domain)

            # Initialize if this is the first request to this domain
            if domain not in self.domain_last_request:
                self.domain_last_request[domain] = time.time()
                self.domain_tokens[domain] = rate - 1  # Use one token
                return

            # Calculate how many tokens have been added since the last request
            current_time = time.time()
            time_passed = current_time - self.domain_last_request[domain]
            tokens_to_add = time_passed * (rate / 60.0)

            # Add tokens up to the maximum
            current_tokens = self.domain_tokens.get(domain, 0)
            new_tokens = min(rate, current_tokens + tokens_to_add)
            self.domain_tokens[domain] = new_tokens

            # If we have less than 1 token, wait until we have at least 1
            if new_tokens < 1:
                wait_time = (1 - new_tokens) * (60.0 / rate)
                logger.info(f"Rate limiting {domain}, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.domain_tokens[domain] = 0  # We used our token
            else:
                self.domain_tokens[domain] = new_tokens - 1  # Use one token

            # Update the last request time
            self.domain_last_request[domain] = time.time()


class URLQueue:
    """
    A queue for URLs to be processed, with rate limiting and prioritization.
    """

    def __init__(self, rate_limiter: RateLimiter = None):
        """
        Initialize the URL queue

        Args:
            rate_limiter: Rate limiter instance to use
        """
        self.rate_limiter = rate_limiter or RateLimiter()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processed_urls = set()
        self.enqueued_urls = set()
        self.lock = asyncio.Lock()

    async def enqueue(self, url: str, priority: int = 0):
        """
        Add a URL to the queue if it hasn't been processed or enqueued already

        Args:
            url: URL to add
            priority: Priority (lower number = higher priority)
        """
        async with self.lock:
            if url in self.processed_urls or url in self.enqueued_urls:
                return

            self.enqueued_urls.add(url)
            await self.queue.put((priority, url))

    async def dequeue(self) -> str:
        """
        Get the next URL from the queue, respecting rate limits

        Returns:
            The next URL to process
        """
        priority, url = await self.queue.get()

        # Calculate domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc

        # Apply rate limiting
        await self.rate_limiter.acquire(domain)

        # Mark URL as processed
        async with self.lock:
            self.enqueued_urls.remove(url)
            self.processed_urls.add(url)

        return url

    def task_done(self):
        """Mark a task as done"""
        self.queue.task_done()

    async def join(self):
        """Wait for all URLs to be processed"""
        await self.queue.join()

    def qsize(self) -> int:
        """Get the current queue size"""
        return self.queue.qsize()

    def empty(self) -> bool:
        """Check if the queue is empty"""
        return self.queue.empty()


# Example usage
async def main():
    """Example of how to use the rate limiter and URL queue"""
    rate_limiter = RateLimiter(default_requests_per_minute=30)

    # Set a specific rate for a particular domain
    rate_limiter.set_domain_rate("example.com", 10)

    # Create a URL queue with the rate limiter
    url_queue = URLQueue(rate_limiter)

    # Add some URLs to the queue
    await url_queue.enqueue("https://example.com/page1", priority=1)
    await url_queue.enqueue("https://example.com/page2", priority=2)
    await url_queue.enqueue("https://example.org/page1", priority=1)

    # Process the URLs
    while not url_queue.empty():
        url = await url_queue.dequeue()
        print(f"Processing {url}")

        # Simulate processing time
        await asyncio.sleep(0.5)

        # Mark the task as done
        url_queue.task_done()

    # Wait for all URLs to be processed
    await url_queue.join()
    print("All URLs processed")


if __name__ == "__main__":
    asyncio.run(main())
