```structurizr
workspace "Urban Issue Platform" "AI Assistance Service component diagram" {

    model {
        !identifiers hierarchical

        registeredUser = person "Registered User" "Citizen who requests AI recommendations and submits locality-specific prompt suggestions."
        moderator = person "Moderator" "Reviews prompt suggestions and manages locality-specific AI prompts."

        externalLlmProvider = softwareSystem "External LLM Provider" "External provider used for prompt-injection checking and AI comment generation." "External"

        urbanPlatform = softwareSystem "Urban Issue Platform" "Platform for reporting urban issues, proposing solutions, and receiving AI recommendations." {

            webApp = container "Web Application" "Single-page web application for users and moderators." "Angular / TypeScript" "WebBrowser"

            apiGateway = container "API Gateway" "Single entry point for client requests. Handles routing, authentication, and rate limiting." "API Gateway"

            problemService = container "Problem Service" "Manages reports, comments, solutions, reactions, images, feed, and map data." "Microservice"

            aiAssistanceService = container "AI Assistance Service" "Handles locality prompts, prompt suggestions, and asynchronous AI comment generation." "Python / FastAPI / LangChain" "Microservice" {

                apiModule = component "API Module" "FastAPI routes, request validation, and response serialization for prompts and prompt suggestions." "FastAPI + Pydantic"

                promptManagementModule = component "Prompt Management Module" "Business logic for locality prompt management and moderation of prompt suggestions." "Application Layer"

                aiProcessingModule = component "AI Processing Module" "Consumes AICommentRequested events, performs prompt injection validation, generates AI comments, temporarily stores generated results, publishes AICommentGenerated events, and commits Kafka offsets after successful delivery." "LangChain + Kafka"

                persistenceModule = component "Persistence Module" "Database access layer for prompts, prompt suggestions, and pending AI results." "SQLAlchemy"

                observabilityModule = component "Observability Module" "Structured logging for AI lifecycle events, prompt changes, failures, and Kafka operations." "structlog"
            }

            messageBroker = container "Message Broker" "Asynchronous event bus for inter-service communication." "Kafka" "MessageBroker"

            database = container "Database" "Relational database for platform data." "PostgreSQL + PostGIS" "Database"
        }

        registeredUser -> urbanPlatform.webApp "Requests AI comments and submits prompt suggestions"
        moderator -> urbanPlatform.webApp "Manages prompts and reviews suggestions"

        urbanPlatform.webApp -> urbanPlatform.apiGateway "Sends AI-related HTTP requests" "REST API"

        urbanPlatform.apiGateway -> urbanPlatform.aiAssistanceService.apiModule "Routes prompt and suggestion requests" "REST API"

        urbanPlatform.aiAssistanceService.apiModule -> urbanPlatform.aiAssistanceService.promptManagementModule "Delegates prompt and suggestion operations"

        urbanPlatform.aiAssistanceService.promptManagementModule -> urbanPlatform.aiAssistanceService.persistenceModule "Reads/writes prompts and suggestions"

        urbanPlatform.messageBroker -> urbanPlatform.aiAssistanceService.aiProcessingModule "Delivers AICommentRequested events" "Kafka"

        urbanPlatform.aiAssistanceService.aiProcessingModule -> urbanPlatform.aiAssistanceService.persistenceModule "Reads/writes pending AI results"

        urbanPlatform.aiAssistanceService.aiProcessingModule -> externalLlmProvider "Performs prompt injection validation and AI comment generation" "HTTPS"

        urbanPlatform.aiAssistanceService.aiProcessingModule -> urbanPlatform.messageBroker "Publishes AICommentGenerated events" "Kafka"

        urbanPlatform.messageBroker -> urbanPlatform.problemService "Delivers AICommentGenerated events for public comment creation" "Kafka"

        urbanPlatform.aiAssistanceService.persistenceModule -> urbanPlatform.database "Reads/writes AI service tables"

        urbanPlatform.aiAssistanceService.apiModule -> urbanPlatform.aiAssistanceService.observabilityModule "Logs API operations"

        urbanPlatform.aiAssistanceService.promptManagementModule -> urbanPlatform.aiAssistanceService.observabilityModule "Logs prompt management events"

        urbanPlatform.aiAssistanceService.aiProcessingModule -> urbanPlatform.aiAssistanceService.observabilityModule "Logs AI processing lifecycle and Kafka operations"
    }

    views {
        component urbanPlatform.aiAssistanceService "AIServiceComponentDiagram" "Component diagram for the AI Assistance Service" {
            include *
            autoLayout lr
        }

        styles {
            element "Person" {
                shape Person
                background #1a3a6b
                color #ffffff
            }

            element "WebBrowser" {
                shape WebBrowser
                background #2e6fbd
                color #ffffff
            }

            element "Microservice" {
                background #2e6fbd
                color #ffffff
            }

            element "Database" {
                shape Cylinder
                background #444444
                color #ffffff
            }

            element "MessageBroker" {
                shape Cylinder
                background #444444
                color #ffffff
            }

            element "External" {
                background #666666
                color #ffffff
                border dashed
            }

            element "Component" {
                background #2e6fbd
                color #ffffff
            }

            relationship "Kafka" {
                style dashed
            }
        }
    }
}

```
