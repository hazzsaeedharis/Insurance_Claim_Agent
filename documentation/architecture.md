<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## File \& Folder Structure

```plaintext
Insurance_Claim_Agent/                    # 🏠 Root directory (FLAT STRUCTURE)
├── 📚 documentation/                     # 📋 All documentation organized
│   ├── business-strategy.md              # Market analysis & business model
│   ├── architecture.md                  # Technical architecture
│   ├── agent-architecture.md             # AI agent implementation
│   ├── cost-analysis-gtm.md             # Pricing & go-to-market
│   ├── user-journey.md                   # User workflows & requirements
│   └── tasks.md                          # Development roadmap
│
├── 🐍 backend/                           # Python FastAPI backend (FLAT)
│   ├── main.py                          # FastAPI application entry
│   ├── requirements.txt                 # Python dependencies
│   ├── config.py                        # Configuration management
│   ├── ai_service.py                    # Multi-provider AI integration
│   ├── claim_orchestrator.py            # Core business logic
│   ├── schemas.py                        # Pydantic data models
│   ├── claims.py                         # Claims API routes
│   ├── ai.py                            # AI processing routes
│   └── dashboard.py                     # Dashboard & analytics routes
│
├── ⚛️ frontend/                          # Simple HTML/CSS/JS frontend (FLAT)
│   ├── index.html                       # Main dashboard page
│   ├── main.css                         # All styles
│   └── app.js                           # All JavaScript functionality
│
├── 🗄️ database/                          # Database schemas & migrations
│   └── supabase/                        # Supabase configurations
│       └── migrations/                  # SQL migration files
│           └── 001_initial_schema.sql
│
├── 📖 README.md                          # Comprehensive setup guide
├── 🔧 env.example                        # Environment configuration template
└── 📄 LICENSE                            # MIT License
```

### 🎯 **FLAT STRUCTURE BENEFITS**

- ✅ **No nested folders** - Everything at root level
- ✅ **Easy navigation** - All files visible immediately  
- ✅ **Faster development** - No folder hunting
- ✅ **Simpler deployment** - Just copy files
- ✅ **Perfect for MVP** - Focus on functionality, not organization
- ✅ **Easy to understand** - New developers can see everything

[source: dev.to][^2][^1]

***

## AI & Machine Learning Components

### AI Service Architecture
```plaintext
src/
├── ai/                      # AI/ML service layer
│   ├── models/              # AI model configurations and wrappers
│   │   ├── claimClassifier.ts   # Claim type classification
│   │   ├── fraudDetection.ts    # Fraud scoring models
│   │   └── documentExtraction.ts # OCR and data extraction
│   ├── services/            # AI service orchestration
│   │   ├── claimProcessor.ts    # Main AI processing pipeline
│   │   ├── riskAssessment.ts    # Risk scoring and evaluation
│   │   └── automatedDecision.ts # Decision engine with human-in-loop
│   ├── workflows/           # Multi-step AI workflows
│   │   ├── claimIntake.ts       # Automated claim intake workflow
│   │   ├── documentAnalysis.ts  # Document processing workflow
│   │   └── approvalWorkflow.ts  # Automated approval chains
│   └── config/              # AI model configurations
│       ├── modelEndpoints.ts    # External AI API configurations
│       └── confidenceThresholds.ts # Decision confidence levels
```

### Integration Strategy
- **External AI APIs:** OpenAI GPT-4, Google Document AI, AWS Textract
- **Human-in-the-Loop:** Automated decisions with confidence thresholds
- **Model Training:** Continuous improvement with customer feedback
- **Fallback Systems:** Rule-based processing when AI confidence is low

***

## Security & Compliance Architecture

### Data Security
```plaintext
src/
├── security/                # Security implementation layer
│   ├── encryption/          # Data encryption utilities
│   │   ├── fieldEncryption.ts   # Database field-level encryption
│   │   └── fileEncryption.ts    # Document encryption at rest
│   ├── audit/               # Audit logging and compliance
│   │   ├── auditLogger.ts       # Comprehensive audit trails
│   │   ├── complianceReports.ts # GDPR/SOC2 compliance reporting
│   │   └── accessLogs.ts        # User access and action logging
│   ├── validation/          # Input validation and sanitization
│   │   ├── claimValidation.ts   # Business rule validation
│   │   └── inputSanitization.ts # XSS and injection prevention
│   └── rbac/                # Role-based access control
│       ├── permissions.ts       # Permission definitions
│       └── roleAssignment.ts    # User role management
```

### Compliance Features
- **GDPR Compliance:** Data portability, right to deletion, consent management
- **SOC 2 Type II:** Security controls and audit logging
- **HIPAA Ready:** Healthcare insurance claim processing capabilities
- **PCI DSS:** Payment information security (if handling payments)

### Security Implementation
- **Row Level Security (RLS):** Supabase-native data isolation
- **API Rate Limiting:** DDoS protection and abuse prevention
- **Multi-factor Authentication:** Required for admin and sensitive operations
- **Encryption:** AES-256 for data at rest, TLS 1.3 for data in transit
- **Vulnerability Scanning:** Automated security testing in CI/CD

***

## Scalability & Performance Architecture

### Database Optimization
```plaintext
supabase/
├── migrations/              # Database schema evolution
│   ├── 001_initial_schema.sql   # Base tables and indexes
│   ├── 002_audit_tables.sql     # Audit and compliance tables
│   ├── 003_ai_metadata.sql      # AI processing metadata
│   └── 004_performance_indexes.sql # Performance optimization
├── functions/               # Supabase Edge Functions
│   ├── claim-processor/         # Serverless claim processing
│   ├── ai-orchestrator/         # AI workflow coordination
│   └── notification-sender/     # Real-time notifications
└── policies/                # Row Level Security policies
    ├── claims-access.sql        # Claims data access rules
    └── admin-access.sql         # Administrative access rules
```

### Performance Features
- **Database Read Replicas:** High-volume query distribution
- **CDN Implementation:** Global asset delivery
- **Caching Strategy:** Redis for session and frequently accessed data
- **Queue System:** Background job processing for AI workflows
- **Microservices Ready:** Modular architecture for future scaling

### Monitoring & Observability
```plaintext
src/
├── monitoring/              # Application monitoring
│   ├── metrics/            # Performance metrics collection
│   │   ├── claimMetrics.ts     # Claim processing metrics
│   │   └── aiMetrics.ts        # AI model performance metrics
│   ├── alerts/             # Alerting and notification
│   │   ├── errorAlerts.ts      # Error threshold monitoring
│   │   └── performanceAlerts.ts # Performance degradation alerts
│   └── analytics/          # Business intelligence
│       ├── dashboards.ts       # Real-time dashboard data
│       └── reporting.ts        # Automated report generation
```

***

## Folder \& File Role Breakdown

- **public/** \& **styles/**
Store static files and global stylesheets used across the application (logos, claim docs, Tailwind base, etc.).[^1]
- **src/app/**
    - Each folder in `app/` maps to a route. Feature folders like `claims/` and `admin/` encapsulate pages and actions per domain.
    - Nested folders such as `[id]/` allow dynamic routing for resources like individual claim detail views.[^1]
    - The `auth/` section handles authentication flows (login, register forms), integrated with Supabase Auth.[^2]
- **components/**
Includes shared visual/UI components—inputs, tables, modals, notifications, buttons, etc.
- **layouts/**
Layout templates and wrappers, such as dashboard layouts, multi-column/fixed header app shells.
- **hooks/**
Custom React hooks: data fetching (useClaims), state (useLocalState), auth tracking (useUserAuth), etc.
- **context/**
Provides global state via React Context API (e.g., AuthProvider, ClaimsProvider), accessible throughout app.
- **services/**
    - Handles all client interaction with Supabase: database CRUD ops, authentication, and real-time updates.
    - `supabaseClient.ts` initializes the Supabase client using env variables.[^2]
    - Feature-specific files like `claims.ts` hold all claim API utilities/business logic.
- **middleware/**
    - Route protection, server-side auth, API guards are defined here.
- **utils/**
Miscellaneous helpers: validation, transformation, formatting (dates, currency), or mapping status codes.
- **constants/**
Enums, role maps, claim statuses, field name lists, etc.
- **store/**
Optional: Advanced state management (Zustand, Redux) for non-trivial state not easily held in context/hooks.
- **config/**
Static configuration for multiple environments, API endpoints, feature flags, or testing settings.
- **.env.local**
Stores sensitive keys/secrets, e.g.,

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_public_anon_key
```


***

## State Management \& Service Connections

- **Auth State**
Managed by Supabase Auth; available via React Context or hooks (e.g., `useUserAuth`). Auto-synced with sessions/cookies and can be hydrated server/client side.[^2]
- **Global State**
    - For user, claims, and notification state, use React Context API combined with custom hooks or a lightweight global store in `/store/` (Zustand or Redux), especially for multi-user admin features or notifications.
    - Per-page state (e.g. claim form progress) is local to the component via React’s `useState`/`useReducer` hooks.
- **Services/DB Connection**
    - All data and auth actions go through `/services/`, which use the initialized `supabaseClient` for queries/mutations.
    - SSR/SSG: Via server-side functions in Next.js (server components/routes).
    - Client-side: Direct with Supabase API and client—enabled by Row Level Security (RLS) for RBAC.[^3][^2]
- **API interactions**
    - Supabase client is used directly from components, hooks, or service files to perform real-time data operations.
    - For workflows requiring orchestration (e.g., multi-step AI claim assessment), implement orchestrating hooks/services in `/services/` and split business logic cleanly.[^2]

***
