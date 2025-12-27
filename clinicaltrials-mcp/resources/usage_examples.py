"""MCP resource with usage examples and best practices."""


def get_usage_examples() -> str:
    """
    Return usage examples and best practices for clinical trial searches.
    
    Returns:
        Markdown-formatted guide with examples
    """
    return """
# ClinicalTrials.gov API Usage Examples

## Basic Searches

### By Condition
```
condition: "diabetes"
condition: "lung cancer"
condition: "(head OR neck) AND pain"
```

### By Intervention
```
intervention: "pembrolizumab"
intervention: "chemotherapy"
```

### By Location
```
location: "California"
location: "United States"
location: "San Francisco, CA"
```

## Status Filters

Common status values:
- `RECRUITING` - Currently enrolling participants
- `ACTIVE_NOT_RECRUITING` - Ongoing but not enrolling
- `COMPLETED` - Study has concluded
- `NOT_YET_RECRUITING` - Approved but not started
- `ENROLLING_BY_INVITATION` - Limited enrollment

## Geographic Filtering

Use the `filter.geo` parameter with distance function:
```
filter.geo: "distance(39.0035707,-77.1013313,50mi)"
```

Format: `distance(latitude,longitude,distance)`
Distance can be in `mi` (miles) or `km` (kilometers)

## Advanced Query Syntax (Essie)

### Date Ranges
```
other_terms: "AREA[LastUpdatePostDate]RANGE[2023-01-01,MAX]"
other_terms: "AREA[StartDate]2022"
```

### Age Ranges
```
other_terms: "AREA[MinimumAge]RANGE[MIN, 16 years] AND AREA[MaximumAge]RANGE[16 years, MAX]"
```

### Field-Specific Searches
```
other_terms: "AREA[LeadSponsorName]Pfizer"
```

## Field Selection

### Essential Fields
```
fields: ["NCTId", "BriefTitle", "OverallStatus", "Condition"]
```

### For Eligibility Info
```
fields: ["EligibilityModule", "EnrollmentInfo"]
```

### For Location Data
```
fields: ["ContactsLocationsModule"]
```

## Pagination

- Always use `page_size` to control results (max 1000)
- Use `nextPageToken` from response for subsequent pages
- Set `countTotal=true` only on first page for performance

## Best Practices

1. **Be Specific**: Use multiple criteria to narrow results
2. **Use Filters**: Prefer filters over broad searches when possible
3. **Field Selection**: Request only needed fields for faster responses
4. **Status Filtering**: Most queries want `RECRUITING` studies
5. **Geographic Proximity**: Use geo filters for location-based searches
6. **Date Filtering**: Use date ranges to find recent/upcoming trials
"""


# Resource metadata
RESOURCE_URI = "ct://usage-examples"
RESOURCE_NAME = "Usage Examples and Best Practices"
RESOURCE_DESCRIPTION = "Common query patterns, field selection tips, and best practices for searching clinical trials"
