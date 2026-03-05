"""LiteLLM tool definition for submit_triage_result. Ensures LLM returns structured params."""

# OpenAI-style tool schema for submit_triage_result
SUBMIT_TRIAGE_RESULT_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_triage_result",
        "description": "Submit the triage result for the analyzed text. Call this with the classification, actionability, routing, and metadata.",
        "parameters": {
            "type": "object",
            "properties": {
                "classification": {
                    "type": "string",
                    "enum": [
                        "BUG_REPORT",
                        "FEATURE_REQUEST",
                        "COMPLAINT",
                        "POSITIVE_FEEDBACK",
                        "SUPPORT_REQUEST",
                        "CANCELLATION",
                        "NEW_SUBSCRIPTION",
                        "NON_ENGLISH",
                        "NOISE",
                        "EMPTY",
                    ],
                    "description": "Classification category",
                },
                "actionability": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW", "NONE"],
                    "description": "Actionability level",
                },
                "routing_destination": {
                    "type": "string",
                    "enum": [
                        "ENGINEERING",
                        "CUSTOMER_SUPPORT",
                        "PRODUCT_MANAGEMENT",
                        "FEEDBACK",
                        "ESCALATION",
                        "LOCALIZATION",
                        "DISCARD",
                    ],
                    "description": "Where to route this submission",
                },
                "confidence": {
                    "type": "string",
                    "enum": ["high", "medium", "low", "none"],
                    "description": "Confidence in the classification",
                },
                "detected_language": {
                    "type": "string",
                    "description": "ISO 639-1 code or 'en'",
                },
                "summary": {
                    "type": "string",
                    "description": "One sentence summary of the submission",
                },
                "flags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Relevant flags (e.g. urgent, noise, empty)",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Relevant tags (e.g. bug, feature, complaint)",
                },
            },
            "required": [
                "classification",
                "actionability",
                "routing_destination",
                "confidence",
                "detected_language",
                "summary",
                "flags",
                "tags",
            ],
        },
    },
}

TOOLS = [SUBMIT_TRIAGE_RESULT_TOOL]
