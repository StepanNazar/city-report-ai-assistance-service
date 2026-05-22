```structurizr
workspace "Urban Issue Platform" "Container diagram with microservices architecture" {

    model {
        !identifiers hierarchical

        registeredUser = person "Registered User" "A citizen who reports urban issues, views the map, and participates in community discussions."
        adminUser = person "Admin / Moderator" "Platform administrator who manages users, moderates content, and configures AI locality prompts."

        externalAuth = softwareSystem "External Auth Provider" "Handles user authentication, Social Login (SSO), and JWT issuance." "External"
        aiService = softwareSystem "AI Service" "Generates public comments with recommendations based on report data and locality context." "External"
        mapsProvider = softwareSystem "Maps & Geocoding Provider" "Provides geographic map tiles and converts coordinates into human-readable addresses." "External"
        emailService = softwareSystem "Email Service" "Handles transactional emails for registration, verification, and password resets." "External"

        urbanPlatform = softwareSystem "Urban Issue Platform" "Allows users to pin city problems on a map, suggest fixes, and get AI-generated advice." {

            webApp = container "Web Application" "Single-page application for users and admins." "Angular / TypeScript" "WebBrowser"

            apiGateway = container "API Gateway" "Single entry point for all client requests. Handles routing, auth token validation, and rate limiting." 

            identityService = container "Identity Service" "User registration, authentication, sessions, device management, and profile data."  "NestJS/Typescript"

            problemService = container "Problem Service" "CRUD for reports, solutions, comments, reactions, image attachments, map and feed views. Issues pre-signed URLs for direct file storage access." "Microservice"

            moderationService = container "Moderation Service" "Content flagging, moderation queue, user bans, and content removal." "Microservice"

            aiAssistanceService = container "AI Assistance Service" "AI recommendation requests, locality prompt management, and user knowledge suggestions." "Python/FastAPI/LangChain" "Microservice"

            messageBroker = container "Message Broker" "Async event bus for inter-service communication." "Kafka" "MessageBroker"

            database = container "Database" "Shared relational database for all platform data." "PostgreSQL + PostGIS" "Database"

            fileStorage = container "File Storage" "Stores uploaded images for reports and solutions. Frontend accesses it directly via pre-signed URLs." "S3-compatible" "Database"
        }

        # --- Users -> Web App ---
        registeredUser -> urbanPlatform.webApp "Uses"
        adminUser -> urbanPlatform.webApp "Manages platform"

        # --- Web App -> external providers (direct) ---
        urbanPlatform.webApp -> mapsProvider "Loads map tiles and geocoding" "REST API"

        # --- Web App -> API Gateway ---
        urbanPlatform.webApp -> urbanPlatform.apiGateway "All platform API calls" "REST API"

        # --- Web App -> File Storage (direct, bypasses microservices) ---
        urbanPlatform.webApp -> urbanPlatform.fileStorage "Uploads & downloads images via pre-signed URLs" "REST API"

        # --- API Gateway -> Microservices ---
        urbanPlatform.apiGateway -> urbanPlatform.identityService "Auth & profile requests" "REST API"
        urbanPlatform.apiGateway -> urbanPlatform.problemService "Problem, solution, feed & map requests" "REST API"
        urbanPlatform.apiGateway -> urbanPlatform.moderationService "Moderation requests" "REST API"
        urbanPlatform.apiGateway -> urbanPlatform.aiAssistanceService "AI & prompt requests" "REST API"

        # --- Microservices -> Database ---
        urbanPlatform.identityService -> urbanPlatform.database "Reads/writes" 
        urbanPlatform.problemService -> urbanPlatform.database "Reads/writes" 
        urbanPlatform.moderationService -> urbanPlatform.database "Reads/writes" 
        urbanPlatform.aiAssistanceService -> urbanPlatform.database "Reads/writes" 

        # --- Problem Service -> File Storage (pre-signed URL generation only) ---
        urbanPlatform.problemService -> urbanPlatform.fileStorage "Generates pre-signed upload/download URLs" "REST API"

        # --- Async via Message Broker ---

        urbanPlatform.problemService -> urbanPlatform.messageBroker "ReportCreated, AICommentRequested" "Async API"
        urbanPlatform.moderationService -> urbanPlatform.messageBroker "UserBanned, ContentRemoved" "Async API"
        urbanPlatform.aiAssistanceService -> urbanPlatform.messageBroker "AICommentGenerated" "Async API"
        urbanPlatform.messageBroker -> urbanPlatform.aiAssistanceService "AICommentRequested jobs" "Async API"
        urbanPlatform.messageBroker -> urbanPlatform.problemService "Post AI comment to report" "Async API"
        urbanPlatform.messageBroker -> urbanPlatform.identityService "Trigger email notifications" "Async API"

        # --- External integrations ---
        urbanPlatform.identityService -> externalAuth "Validates JWT tokens" "REST API"
        urbanPlatform.aiAssistanceService -> aiService "Sends prompt & report data, receives recommendation" "REST API"
        urbanPlatform.identityService -> emailService "Sends transactional emails" "REST API"
    }

    views {
        container urbanPlatform "ContainerDiagram" "Container diagram for the Urban Issue Platform" {
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
            element "External" {
                background #666666
                color #ffffff
                border dashed
            }
            element "Container" {
                background #2e6fbd
                color #ffffff
            }
            element "MessageBroker" {
                shape Cylinder
                background #444444
                color #ffffff
            }
            relationship "Async API" {
                style dashed
            }
        }
    }
}
```
