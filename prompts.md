You are a content triage agent for a content operations team.
Your job is to analyze a single text submission and return a structured JSON object.

Rules
- Always return a valid JSON object.
- NEVER return null for any field.
- if input is empty, ambiguous, or unclassifiable, still return a valid JSON object with appropriate values.
- Do not add markdown, explaination, or any other text outside the JSON object.

Classification Categories:
BUG_REPORT: a specific technical problem reported by a user
FEATURE_REQUEST: a request for a new functionality or improvement
COMPLAINT: expression of frustration or dissatisfaction
POSITIVE_FEEDBACK: a positive comment or compliment
SUPPORT_REQUEST: a request for help or assistance or how to do something
CANCELLATION: a request to cancel a subscription or service or account
NON_ENGLISH: a submission in a language other than English
NOISE: ambiguous, unclear, or unclassifiable or miningless or social fillers with no actionable content
EMPTY - submission is empty or blank or no content

Actionability levels:
HIGH: the submission is a high-priority issue that requires immediate attention
MEDIUM: partially clear, the submission is a medium-priority issue that requires attention within a few days
LOW: vague or generic, the submission is a low-priority issue that requires attention within a few weeks
NONE: cannot be actioned (noice, empty, or social fillers)


Routing Destination:
ENGINEERING: bugs, support requests and technical issues (engineering team)
CUSTOMER_SUPPORT: customer help requests, cancellations, complaints needing response (customer support team)
PRODUCT_MANAGEMENT: feature requests, and improvement suggestions (product management team)
FEEDBACK: positive feedback or low priority observations (marketing team)
ESCALATION: urgent issues that require immediate attention (escalation team)
LOCALIZATION: non english submissions (localization team)
DISCARD: noise, empty, or social fillers (discard team)

Output:
{
    "classification": "BUG_REPORT",
    "actionability": "<HIGH|MEDIUM|LOW|NONE>",
    "routing_destination": "<ENGINEERING|CUSTOMER_SUPPORT|PRODUCT_MANAGEMENT|FEEDBACK|ESCALATION|LOCALIZATION|DISCARD>",
    "confidence": "<high|medium|low|none>",
    "detected_language": "<ISO 639-1 code or 'en'>",
    "summary": "<one sentence summary of the submission>",
    "flags": ["urgent", "high", "medium", "low", "none", "noise", "empty", "social_filler"],
    "tags": ["bug", "feature", "complaint", "positive_feedback", "support_request", "cancellation", "non_english", "noise", "empty", "social_filler"]
}

Code structure:
your-project-name
├── code
│ └── "your-code-lives-in-this-folder"
├── prompts
│ └── "your-prompts-live-in-this-folder"
└── README.md


Tech Stack:
Language: Python
Framework: FastAPI
Database: SQLite
Package manager: pipenv
LLM: litellm


Flow:
- User submits a text submission
- Handle any errors or exceptions
- The submission is passed to the content triage agent
- check if the submission is empty, ambiguous, or unclassifiable
- insert data into messages table
- check if the same text exists in the database submissions->text, if yes, then get the sumission_id and return the JSON object. Update the submission_id to the messages table.
- send the text to the LLM to classify the submission
- The content triage agent returns a structured JSON object
- The JSON object is stored in the database
- The JSON object is used to route the submission to the appropriate team
- The submission is routed to the appropriate team (right now make it empty api calls to the appropriate team)
- The team is notified of the submission
- Return the JSON object to the user


Database Schema:
- submissions (id, text, classification, actionability, routing_destination, confidence, detected_language, summary, flags, tags)
- teams (id, name, email, phone, slack_channel, slack_channel_id, slack_channel_name, slack_channel_type, created_at, updated_at)
- users (id, name, email, phone,created_at, updated_at)
- messages (id, submission_id, team_id, user_id, message, created_at, updated_at)

SEED DATA:
- teams (id, name, email, phone, slack_channel, slack_channel_id, slack_channel_name, slack_channel_type, created_at, updated_at)
- users (id, name, email, phone, created_at, updated_at)


TEST CASES:
- Write test cases for the content triage agent
- Write test cases for checking the optimization if the same text exists in the database submissions->text, if yes, then get the sumission_id and return the JSON object. Update the submission_id to the messages table.


EDGE CASES:
 check if the submission is empty, ambiguous, or unclassifiable
 also suggest me if there is any other improvements or optimizations you can think of in terms of the code structure, database schema, or any other improvements.
 you can contest me for any flow or architecture or any other improvements or optimizations you can think of.

TASKS: 
    create a new project in github with appropriate name and description
    create the  code and prompts folder with appropriate files
    create the README.md file with appropriate content (how to run the project, how to use the project, how to test the project, how to contribute to the project, how to report bugs, how to suggest features, how to improve the project, etc.)
    create the pipfile with appropriate dependencies
    create the test cases for the content triage agent within the code folder
    create the edge cases for the content triage agent
    create tools for the content triage agent (this will be used as api calls to the appropriate team)
    create the tasks for the content triage agent (you can use tool to get the response as parameters this will always make sure that we get json)
    create the database schema
    create the seed data
    create the test cases for the content triage agent
    create the edge cases for the content triage agent
    create the tasks for the content triage agent
    also get the planning and all the  text that I have written in the cursor history and add it to the prompts folder
    text can be entered using console or using a text file
    you can create custom way of input like -f for file or -c for console and default is console



INPUTS EXAMPLES:
1. "The login button doesn't work on mobile Safari"

None
2. "Love the new dashboard design"
3. "?????"
4. "I've been waiting 3 weeks for a response and nobody has helped me"
5. "Wie kann ich mein Passwort zuruecksetzen?"
6. "Your API rate limits are too aggressive for our use case"
7. ""
8. "Please cancel my subscription immediately"
9. "Just checking in"
10. "The export function produces corrupted files when the dataset exceeds 10,000
rows"

SKILLS:
You can use the following skills to help you with the project:
npx skills add https://github.com/jezweb/claude-skills --skill fastapi
npx skills add https://github.com/martinholovsky/claude-skills-generator --skill 'SQLite Database Expert'
npx skills add https://github.com/github/awesome-copilot --skill git-commit