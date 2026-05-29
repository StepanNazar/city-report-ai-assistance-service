Behaviors of the Component: AI Assistance Service
This document defines the generic business operations (behaviors) exposed and handled by the AI Assistance Service.

1. Synchronous Operations
These are direct request-response operations invoked by end-users or moderators through the API Gateway.

1.1. Retrieve Locality AI Prompt
Description:
Fetches the currently configured AI prompt for a specific locality.
Actor:
Moderator.
Behavior:
Receives a locality identifier and returns the currently stored locality-specific AI prompt used during AI comment generation.

1.2. Create Locality AI Prompt
Description:
Creates a new locality-specific AI prompt.
Actor:
Moderator.
Behavior:
Validates the provided prompt content, stores the locality-specific prompt in the database, and records the creation event in structured logs.

1.3. Update Locality AI Prompt
Description:
Updates an existing locality-specific AI prompt.
Actor:
Moderator.
Behavior:
Validates the updated prompt content, modifies the existing locality prompt, updates metadata fields, and records the modification event in structured logs.

1.4. Submit Prompt Suggestion
Description:
Allows users to submit locality-specific contextual suggestions for improving AI-generated recommendations.
Actor:
User.
Behavior:
Receives user-provided suggestion text and locality identifier, validates the request payload, stores the suggestion with PENDING review status, and records the submission event in structured logs.

1.5. Retrieve Prompt Suggestions
Description:
Fetches a paginated filtered by status list of submitted prompt suggestions.
Actor:
Moderator.
Behavior:
Returns stored prompt suggestions together with their review statuses and metadata required for moderation.

1.6. Review Prompt Suggestion
Description:
Approves or rejects a user-submitted prompt suggestion.
Actor:
Moderator.
Behavior:
Updates the suggestion review status (APPROVED or REJECTED), stores reviewer information and review timestamp, and records the moderation action in structured logs.

2. Asynchronous Operations
These are background operations triggered through asynchronous event-driven communication.

2.1. Generate AI Recommendation Comment
Description:
Generates a public AI recommendation comment for a report.
Trigger:
Consumption of an AICommentRequested event from Kafka.
Behavior:
Consumes the event together with report data and locality information.
Checks whether a generated result already exists in temporary storage for the given ai_request_id.
If no temporary result exists:
Loads the locality-specific AI prompt.
Performs prompt-injection validation using a guardrail LLM chain.
Generates a recommendation comment using the external LLM provider.
Temporarily stores the generated comment in the database.
If a temporary result already exists:
Reuses the previously generated comment instead of generating a duplicate response.
Publishes an AICommentGenerated event to Kafka containing the generated recommendation comment, ai_request_id, report_id.
Commits the Kafka offset only after successful event publication.
Deletes the temporary stored result after a successful offset commit.
Records all processing stages and failures in structured logs.
