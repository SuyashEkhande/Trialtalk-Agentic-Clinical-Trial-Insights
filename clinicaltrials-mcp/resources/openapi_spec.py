"""MCP resource exposing the OpenAPI specification."""
import yaml
import os


def get_openapi_spec() -> str:
    """
    Load and return the ClinicalTrials.gov OpenAPI specification.
    
    Returns:
        YAML content of the OpenAPI spec
    """
    spec_path = os.path.join(
        os.path.dirname(__file__),
        "../../.docs/ctg-oas-v2.yaml"
    )
    
    with open(spec_path, "r") as f:
        return f.read()


# Resource metadata
RESOURCE_URI = "ct://openapi-spec"
RESOURCE_NAME = "ClinicalTrials.gov OpenAPI Specification"
RESOURCE_DESCRIPTION = """
Complete OpenAPI v3 specification for the ClinicalTrials.gov REST API v2.
This specification defines all available endpoints, parameters, and response schemas.
Useful for understanding the API structure and constructing complex queries.
"""
