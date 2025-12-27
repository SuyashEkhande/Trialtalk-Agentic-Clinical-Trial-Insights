"""MCP prompts for guided query building."""


def build_condition_query_prompt(user_input: str) -> str:
    """
    Generate a prompt to help build condition-based search queries.
    
    Args:
        user_input: User's description of the condition
        
    Returns:
        Formatted prompt with query suggestions
    """
    return f"""
# Building Condition Query

User wants to search for: {user_input}

## Suggested Approaches:

1. **Simple Match**: Use exact condition name
   Query: `{user_input}`

2. **Broader Search**: Use OR operators for related terms
   Example: `(lung cancer OR lung carcinoma OR NSCLC)`

3. **Specific Type**: Narrow with AND operators
   Example: `{user_input} AND stage 3`

4. **Exclude Terms**: Use NOT to exclude
   Example: `{user_input} NOT pediatric`

## Tips:
- Use parentheses to group terms
- Common medical abbreviations are recognized
- MeSH terms are automatically mapped
"""


def build_location_query_prompt(location: str) -> str:
    """
    Generate a prompt for location-based queries.
    
    Args:
        location: User's location description
        
    Returns:
        Formatted prompt with location query suggestions
    """
    return f"""
# Building Location Query

User wants trials in: {location}

## Options:

1. **By Name**: Search location names directly
   Query: `{location}`

2. **Geographic Distance**: Use lat/long with radius
   Format: `distance(latitude,longitude,distance)`
   Example: `distance(37.7749,-122.4194,25mi)` for 25 miles from SF

3. **Multiple Locations**: Combine with OR
   Example: `California OR Oregon OR Washington`

## Notes:
- Distance searches require coordinates
- Can specify distance in miles (mi) or kilometers (km)
- Location names include cities, states, countries
"""


def build_advanced_filter_prompt(criteria: dict) -> str:
    """
    Generate a prompt for building complex multi-criteria filters.
    
    Args:
        criteria: Dictionary of filter criteria
        
    Returns:
        Formatted prompt with filter construction guide
    """
    return f"""
# Building Advanced Filter

User criteria: {criteria}

## Available Filters:

1. **Status Filter**
   Parameter: `filter.overallStatus`
   Values: RECRUITING, COMPLETED, ACTIVE_NOT_RECRUITING, etc.

2. **Geographic Filter**
   Parameter: `filter.geo`
   Format: `distance(lat,long,radius)`

3. **NCT ID Filter**
   Parameter: `filter.ids`
   Values: Comma-separated NCT IDs

4. **Advanced Expression**
   Parameter: `filter.advanced`
   Examples:
   - `AREA[StartDate]2022`
   - `AREA[MinimumAge]RANGE[18 years, 65 years]`

## Combining Multiple Filters:

Use multiple parameters together:
- Status + Location: Find recruiting trials nearby
- Condition + Date: Recent trials for specific disease
- Location + Phase: Phase 3 trials in specific area

## Query Parameters vs Filters:

- **Query parameters** (query.cond, query.intr): Affect relevance ranking
- **Filters** (filter.*): Hard filters, no ranking impact
"""


# Prompt metadata
PROMPTS = [
    {
        "name": "build_condition_query",
        "description": "Help construct condition-based search queries using Essie syntax",
        "function": build_condition_query_prompt
    },
    {
        "name": "build_location_query",
        "description": "Help construct location-based search queries",
        "function": build_location_query_prompt
    },
    {
        "name": "build_advanced_filter",
        "description": "Help construct complex multi-criteria filters",
        "function": build_advanced_filter_prompt
    }
]
