import requests
import re
import sys
from urllib.parse import urlparse


def get_robots_txt(url):
    """
    Retrieve the robots.txt file for a given URL
    """
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    try:
        response = requests.get(robots_url, timeout=10)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            print(f"No robots.txt found at {robots_url} (404 status)")
            return None
        else:
            print(f"Failed to fetch robots.txt, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching robots.txt: {e}")
        return None


def parse_robots_txt(content, user_agent="*"):
    """
    Parse robots.txt content and extract rules for the specified user agent
    """
    if not content:
        return {"allow": [], "disallow": [], "crawl_delay": None, "sitemap": []}

    rules = {"allow": [], "disallow": [], "crawl_delay": None, "sitemap": []}
    current_agent = None
    user_agent_specific_rules = None
    general_rules = None

    for line in content.split('\n'):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Parse sitemap declaration (can appear anywhere)
        if line.lower().startswith('sitemap:'):
            sitemap_url = line.split(':', 1)[1].strip()
            rules["sitemap"].append(sitemap_url)
            continue

        # User-agent declaration starts a new block
        if line.lower().startswith('user-agent:'):
            agent = line.split(':', 1)[1].strip().lower()
            current_agent = agent

            # If this is the user agent we're looking for, prepare for collecting its rules
            if current_agent == user_agent.lower():
                if user_agent_specific_rules is None:
                    user_agent_specific_rules = {"allow": [], "disallow": [], "crawl_delay": None,
                                                 "sitemap": rules["sitemap"].copy()}

            # Always collect rules for the wildcard user agent
            if current_agent == '*':
                if general_rules is None:
                    general_rules = {"allow": [], "disallow": [], "crawl_delay": None,
                                     "sitemap": rules["sitemap"].copy()}

            continue

        # Only process rules for relevant user agents
        if current_agent is None:
            continue

        # Process rules based on current user agent
        if current_agent == user_agent.lower() or current_agent == '*':
            if line.lower().startswith('disallow:'):
                path = line.split(':', 1)[1].strip()
                if current_agent == user_agent.lower() and user_agent_specific_rules is not None:
                    user_agent_specific_rules["disallow"].append(path)
                elif current_agent == '*' and general_rules is not None:
                    general_rules["disallow"].append(path)

            elif line.lower().startswith('allow:'):
                path = line.split(':', 1)[1].strip()
                if current_agent == user_agent.lower() and user_agent_specific_rules is not None:
                    user_agent_specific_rules["allow"].append(path)
                elif current_agent == '*' and general_rules is not None:
                    general_rules["allow"].append(path)

            elif line.lower().startswith('crawl-delay:'):
                try:
                    delay = float(line.split(':', 1)[1].strip())
                    if current_agent == user_agent.lower() and user_agent_specific_rules is not None:
                        user_agent_specific_rules["crawl_delay"] = delay
                    elif current_agent == '*' and general_rules is not None:
                        general_rules["crawl_delay"] = delay
                except ValueError:
                    pass

    # Prioritize specific user agent rules over general rules
    if user_agent_specific_rules:
        return user_agent_specific_rules
    elif general_rules:
        return general_rules
    else:
        return rules


def is_url_allowed(url, rules):
    """
    Check if a URL is allowed by the robots.txt rules
    """
    parsed_url = urlparse(url)
    path = parsed_url.path or "/"

    # By default, everything is allowed
    allowed = True

    # Find the most specific matching disallow rule
    most_specific_disallow = 0
    matching_disallow_rule = None

    for rule in rules["disallow"]:
        if rule and path_matches_rule(path, rule) and len(rule) > most_specific_disallow:
            most_specific_disallow = len(rule)
            matching_disallow_rule = rule
            allowed = False

    # Find the most specific matching allow rule
    most_specific_allow = 0
    matching_allow_rule = None

    for rule in rules["allow"]:
        if rule and path_matches_rule(path, rule) and len(rule) > most_specific_allow:
            most_specific_allow = len(rule)
            matching_allow_rule = rule
            # Allow rule only overrides a disallow rule if it's more specific
            if most_specific_allow > most_specific_disallow:
                allowed = True

    return {
        "allowed": allowed,
        "matching_disallow_rule": matching_disallow_rule,
        "matching_allow_rule": matching_allow_rule,
        "crawl_delay": rules["crawl_delay"]
    }


def path_matches_rule(path, rule):
    """
    Check if a path matches a robots.txt rule
    """
    # Empty rule matches nothing
    if not rule:
        return False

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


def main():
    """Main function to check robots.txt for a URL"""
    if len(sys.argv) < 2:
        print("Usage: python check_robots.py URL [USER_AGENT]")
        sys.exit(1)

    url = sys.argv[1]
    user_agent = sys.argv[2] if len(sys.argv) > 2 else "*"

    print(f"Checking robots.txt for: {url}")
    print(f"Using user agent: {user_agent}")

    robots_txt = get_robots_txt(url)

    if robots_txt:
        print("\nRobots.txt content:")
        print("-" * 50)
        print(robots_txt)
        print("-" * 50)

        rules = parse_robots_txt(robots_txt, user_agent)

        print("\nRules for user agent:", user_agent)
        print("Allow rules:", rules["allow"])
        print("Disallow rules:", rules["disallow"])
        print("Crawl delay:", rules["crawl_delay"])
        print("Sitemaps:", rules["sitemap"])

        # Check if the specific URL is allowed
        result = is_url_allowed(url, rules)

        print("\nURL accessibility check:")
        print(f"URL: {url}")
        print(f"Allowed: {result['allowed']}")

        if result["matching_disallow_rule"]:
            print(f"Matching disallow rule: {result['matching_disallow_rule']}")

        if result["matching_allow_rule"]:
            print(f"Matching allow rule: {result['matching_allow_rule']}")

        if result["crawl_delay"]:
            print(f"Crawl delay: {result['crawl_delay']} seconds")
    else:
        print("No robots.txt found or error fetching it. All URLs are allowed by default.")


if __name__ == "__main__":
    main()
