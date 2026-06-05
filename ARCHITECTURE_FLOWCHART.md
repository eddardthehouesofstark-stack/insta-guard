# InstaGuard - Complete Architecture Flowchart

## 1. System Overview

```mermaid
graph TB
    User[👤 User] --> Frontend[🌐 Frontend<br/>Vercel]
    Frontend --> Backend[⚙️ Backend API<br/>Render]
    Backend --> DB[(🗄️ PostgreSQL<br/>Supabase)]
    Backend --> GroqAPI[🤖 Groq AI<br/>Llama 4 Scout]
    Backend --> SupabaseAuth[🔐 Supabase Auth]
    Frontend --> GoogleOAuth[🔑 Google OAuth]
    GoogleOAuth --> SupabaseAuth
    
    style Frontend fill:#4FC08D
    style Backend fill:#FF6B6B
    style DB fill:#3B82F6
    style GroqAPI fill:#F59E0B
    style SupabaseAuth fill:#8B5CF6
```

---

## 2. User Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant G as Google OAuth
    participant SA as Supabase Auth
    participant B as Backend
    participant DB as Database

    U->>F: Click "Sign in with Google"
    F->>G: Redirect to Google
    G->>U: Google Login Page
    U->>G: Enter credentials
    G->>SA: OAuth callback
    SA->>SA: Create/verify user
    SA->>F: Redirect with access_token
    F->>B: GET /auth/me (with token)
    B->>SA: Validate token
    SA->>B: Token valid
    B->>DB: Query user profile
    DB->>B: User data (id, email, role)
    B->>F: User data
    F->>F: Store token & user in localStorage
    F->>U: Redirect to Dashboard
```

---

## 3. Image Analysis Flow

```mermaid
graph TD
    A[User uploads image] --> B{File valid?}
    B -->|No| C[Show error]
    B -->|Yes| D[Send to Backend API]
    D --> E[Backend receives image]
    E --> F[Resize image if > 10MB]
    F --> G[Convert to base64]
    G --> H[Send to Groq API]
    H --> I[Groq analyzes with Llama 4 Scout]
    I --> J[Get vision labels & confidence scores]
    J --> K[Calculate safety score 0-100]
    K --> L{Score < 50?}
    L -->|Yes| M[Status: Approved ✓]
    L -->|No| N{Score >= 80?}
    N -->|Yes| O[Status: Rejected ✗]
    N -->|No| P[Status: Manual Review ⚠️]
    M --> Q[Save to database]
    O --> Q
    P --> Q
    P --> R[Add to moderation queue]
    Q --> S[Return result to frontend]
    S --> T[Display score & verdict]
    T --> U{Approved?}
    U -->|Yes| V[Show 'Post to Instagram' button]
    U -->|No| W[Show rejection warning]
    
    style M fill:#10B981
    style O fill:#EF4444
    style P fill:#F59E0B
    style V fill:#3B82F6
```

---

## 4. Feed Analysis Flow

```mermaid
graph TD
    A[User enters Instagram username] --> B[Click 'Analyze Feed']
    B --> C[Backend generates mock feed data]
    C --> D[Analyze each post]
    D --> E[Calculate overall feed score]
    E --> F{Score >= 80?}
    F -->|Yes| G[Feed flagged as unsafe]
    F -->|No| H{Score >= 50?}
    H -->|Yes| I[Some content needs review]
    H -->|No| J[Feed approved]
    G --> K[Save analysis to DB]
    I --> K
    J --> K
    K --> L[Return results to frontend]
    L --> M[Display feed analysis]
    M --> N{Feed flagged?}
    N -->|Yes| O[Show 'Request Feed Reboot' button]
    N -->|No| P[Show feed stats only]
    
    style G fill:#EF4444
    style I fill:#F59E0B
    style J fill:#10B981
```

---

## 5. Feed Reboot Request Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant A as Admin

    U->>F: Click "Request Feed Reboot"
    F->>F: Confirm dialog
    U->>F: Confirm request
    F->>B: POST /feed/reboot-request
    B->>DB: Create reboot request
    DB->>B: Request saved
    B->>F: Success response
    F->>U: Show success message
    
    Note over A: Admin logs in
    A->>F: Open Admin Panel
    F->>B: GET /admin/reboot-requests
    B->>DB: Query pending requests
    DB->>B: List of requests
    B->>F: Return requests
    F->>A: Display requests
    A->>F: Approve/Reject request
    F->>B: POST /admin/reboot-action
    B->>DB: Update request status
    DB->>B: Updated
    B->>F: Success
    F->>A: Show updated status
```

---

## 6. Admin Moderation Flow

```mermaid
graph TD
    A[Content flagged for review] --> B[Added to moderation queue]
    B --> C[Admin opens panel]
    C --> D[View queued items]
    D --> E{Admin decision}
    E -->|Approve| F[Update status: approved]
    E -->|Reject| G[Update status: rejected]
    F --> H[Remove from queue]
    G --> H
    H --> I[Log admin action]
    I --> J[Update content status in DB]
    J --> K[Notify user if needed]
    
    style E fill:#8B5CF6
    style F fill:#10B981
    style G fill:#EF4444
```

---

## 7. Dashboard Data Flow

```mermaid
graph LR
    A[Dashboard loads] --> B[Fetch user stats]
    A --> C[Fetch recent activity]
    A --> D[Fetch thresholds]
    
    B --> E[GET /dashboard/stats]
    C --> F[GET /dashboard/activity]
    D --> G[GET /admin/thresholds]
    
    E --> H[(Database)]
    F --> H
    G --> H
    
    H --> I[Count images checked]
    H --> J[Count feed analyses]
    H --> K[Count rejected items]
    H --> L[Count pending reviews]
    H --> M[Get latest activities]
    H --> N[Get threshold config]
    
    I --> O[Display on dashboard]
    J --> O
    K --> O
    L --> O
    M --> O
    N --> O
    
    style O fill:#4FC08D
```

---

## 8. Database Schema Relationships

```mermaid
erDiagram
    USERS ||--o{ IMAGE_CHECKS : creates
    USERS ||--o{ FEED_ANALYSES : creates
    USERS ||--o{ FEED_REBOOT_REQUESTS : submits
    USERS ||--o{ ADMIN_LOGS : performs
    
    IMAGE_CHECKS ||--o| MODERATION_QUEUE : queued_in
    FEED_ANALYSES ||--o| MODERATION_QUEUE : queued_in
    
    USERS {
        uuid id PK
        text email
        text role
        timestamptz created_at
    }
    
    IMAGE_CHECKS {
        uuid id PK
        uuid user_id FK
        text image_url
        int safety_score
        text status
        jsonb vision_labels
        timestamptz checked_at
    }
    
    FEED_ANALYSES {
        uuid id PK
        uuid user_id FK
        jsonb feed_snapshot
        int overall_score
        text status
        timestamptz analysed_at
    }
    
    MODERATION_QUEUE {
        uuid id PK
        uuid ref_id FK
        text ref_type
        int score
        text decision
        text reviewer_note
        timestamptz reviewed_at
    }
    
    FEED_REBOOT_REQUESTS {
        uuid id PK
        uuid user_id FK
        text instagram_username
        jsonb post_ids
        int flagged_count
        text status
        timestamptz requested_at
    }
    
    ADMIN_LOGS {
        uuid id PK
        uuid admin_id FK
        text action
        jsonb payload
        timestamptz logged_at
    }
    
    THRESHOLDS {
        uuid id PK
        int auto_approve_max
        int manual_review_min
        int auto_reject_min
        timestamptz updated_at
    }
```

---

## 9. API Endpoint Map

```mermaid
graph TB
    API[InstaGuard API] --> AUTH[/auth]
    API --> IMAGES[/images]
    API --> FEED[/feed]
    API --> DASHBOARD[/dashboard]
    API --> ADMIN[/admin]
    
    AUTH --> A1[POST /signup]
    AUTH --> A2[POST /login]
    AUTH --> A3[GET /me]
    
    IMAGES --> I1[POST /check]
    IMAGES --> I2[GET /history]
    
    FEED --> F1[POST /analyze]
    FEED --> F2[GET /history]
    FEED --> F3[POST /reboot-request]
    
    DASHBOARD --> D1[GET /stats]
    DASHBOARD --> D2[GET /activity]
    
    ADMIN --> AD1[GET /queue]
    ADMIN --> AD2[POST /review]
    ADMIN --> AD3[GET /thresholds]
    ADMIN --> AD4[PUT /thresholds]
    ADMIN --> AD5[GET /reboot-requests]
    ADMIN --> AD6[POST /reboot-action]
    
    style AUTH fill:#8B5CF6
    style IMAGES fill:#3B82F6
    style FEED fill:#10B981
    style DASHBOARD fill:#F59E0B
    style ADMIN fill:#EF4444
```

---

## 10. Deployment Architecture

```mermaid
graph TB
    subgraph "Client Side"
        User[👤 User Browser]
    end
    
    subgraph "Vercel (Frontend)"
        HTML[HTML/CSS/JS]
        Static[Static Assets]
    end
    
    subgraph "Render (Backend)"
        FastAPI[FastAPI Server]
        Uvicorn[Uvicorn ASGI]
        Python[Python 3.11]
    end
    
    subgraph "External Services"
        Supabase[(Supabase<br/>PostgreSQL + Auth)]
        Groq[Groq AI API<br/>Llama 4 Scout]
        GoogleAuth[Google OAuth]
    end
    
    subgraph "Monitoring"
        UptimeRobot[UptimeRobot<br/>Keep-Alive]
    end
    
    User --> HTML
    HTML --> FastAPI
    FastAPI --> Python
    Python --> Supabase
    Python --> Groq
    HTML --> GoogleAuth
    GoogleAuth --> Supabase
    UptimeRobot -.->|Ping every 5min| FastAPI
    
    style User fill:#4FC08D
    style HTML fill:#3B82F6
    style FastAPI fill:#EF4444
    style Supabase fill:#10B981
    style Groq fill:#F59E0B
```

---

## 11. Security Flow

```mermaid
graph TD
    A[User Request] --> B{Has Token?}
    B -->|No| C[Return 401 Unauthorized]
    B -->|Yes| D[Extract JWT Token]
    D --> E{Valid Supabase Token?}
    E -->|No| F[Try Custom JWT]
    E -->|Yes| G[Fetch user from DB]
    F --> H{Valid Custom JWT?}
    H -->|No| C
    H -->|Yes| G
    G --> I{User exists in DB?}
    I -->|No| J[Auto-create user]
    I -->|Yes| K[Load user profile]
    J --> K
    K --> L{Check RLS policies}
    L --> M{User authorized?}
    M -->|No| N[Return 403 Forbidden]
    M -->|Yes| O[Process request]
    O --> P[Return response]
    
    style C fill:#EF4444
    style N fill:#EF4444
    style O fill:#10B981
    style P fill:#10B981
```

---

## 12. Error Handling Flow

```mermaid
graph TD
    A[Request arrives] --> B{Try processing}
    B -->|Success| C[Return 200 OK]
    B -->|Error| D{Error type?}
    
    D -->|Authentication| E[401 Unauthorized]
    D -->|Authorization| F[403 Forbidden]
    D -->|Not Found| G[404 Not Found]
    D -->|Validation| H[400 Bad Request]
    D -->|Database| I[500 Internal Error]
    D -->|External API| J[503 Service Unavailable]
    
    E --> K[Log error]
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L[Return error response]
    L --> M[Frontend displays user-friendly message]
    
    style C fill:#10B981
    style E fill:#EF4444
    style F fill:#EF4444
    style G fill:#F59E0B
    style H fill:#F59E0B
    style I fill:#EF4444
    style J fill:#EF4444
```

---

## 13. Keep-Alive System

```mermaid
sequenceDiagram
    participant UR as UptimeRobot
    participant FK as Frontend Keep-Alive
    participant B as Backend (Render)
    participant R as Render Platform

    Note over R: Render spins down after 15min idle

    loop Every 5 minutes
        UR->>B: HTTP GET /
        B->>UR: 200 OK
        Note over B: Backend stays awake
    end

    loop Every 10 minutes (when user active)
        FK->>B: HTTP GET /
        B->>FK: 200 OK
    end

    Note over B,R: Backend never reaches 15min idle
    Note over B: Always ready for user requests!
```

---

## How to View These Flowcharts

### Option 1: GitHub (Recommended)
1. Push this file to GitHub
2. View it directly - GitHub renders Mermaid diagrams automatically!

### Option 2: Online Mermaid Editor
1. Go to: https://mermaid.live
2. Copy/paste any diagram code
3. Download as PNG/SVG

### Option 3: VS Code
1. Install "Markdown Preview Mermaid Support" extension
2. Open this file
3. Click "Preview" button

### Option 4: Export as Images
Use Mermaid CLI:
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i ARCHITECTURE_FLOWCHART.md -o flowchart.png
```

---

## Legend

- 🟢 Green: Success/Approved states
- 🔴 Red: Error/Rejected states
- 🟡 Yellow: Warning/Review states
- 🔵 Blue: Process/Action states
- 🟣 Purple: Authentication/Security

---

**Created for InstaGuard - AI-Powered Content Safety Platform**
