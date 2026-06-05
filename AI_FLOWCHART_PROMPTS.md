# AI Flowchart Generation Prompts for InstaGuard

Use these prompts in ChatGPT, DALL-E, Midjourney, or any AI image generator to create professional flowcharts.

---

## 🎨 General Prompt Template

```
Create a professional, modern flowchart diagram for [TOPIC] with the following specifications:

Style:
- Clean, minimalist design with a dark theme
- Use rounded rectangles for processes
- Use diamonds for decision points
- Use cylinders for databases
- Color scheme: Blue (#3B82F6) for processes, Green (#10B981) for success, Red (#EF4444) for errors, Yellow (#F59E0B) for warnings, Purple (#8B5CF6) for authentication

Layout:
- Top-to-bottom flow
- Clear labels and arrows
- Icons for users, databases, APIs
- Professional typography (sans-serif)

Content: [SPECIFIC CONTENT BELOW]
```

---

## 1️⃣ System Overview Prompt

```
Create a professional system architecture diagram for "InstaGuard - AI-Powered Content Safety Platform" with these components:

Components:
1. User (icon: person silhouette)
2. Frontend (Vercel) - green color
3. Backend API (Render) - red color
4. PostgreSQL Database (Supabase) - blue color
5. Groq AI (Llama 4 Scout) - orange color
6. Supabase Auth - purple color
7. Google OAuth - multicolor Google logo

Connections:
- User → Frontend
- Frontend ↔ Backend API
- Backend → Database
- Backend → Groq AI
- Backend → Supabase Auth
- Frontend → Google OAuth → Supabase Auth

Style: Modern tech stack diagram with cloud elements, professional business presentation style, 16:9 aspect ratio
```

---

## 2️⃣ User Authentication Flow Prompt

```
Create a detailed sequence diagram showing Google OAuth authentication flow with these steps:

Actors (from left to right):
1. User (person icon)
2. Frontend (browser icon)
3. Google OAuth (Google logo)
4. Supabase Auth (database icon)
5. Backend API (server icon)
6. Database (cylinder)

Steps with arrows:
1. User clicks "Sign in with Google" on Frontend
2. Frontend redirects to Google OAuth
3. Google shows login page to User
4. User enters credentials
5. Google sends OAuth callback to Supabase Auth
6. Supabase creates/verifies user
7. Supabase redirects to Frontend with access_token
8. Frontend sends token to Backend (/auth/me)
9. Backend validates token with Supabase
10. Backend queries user profile from Database
11. Database returns user data (id, email, role)
12. Backend sends user data to Frontend
13. Frontend stores token & user, redirects to Dashboard

Style: UML sequence diagram, professional colors, clear timeline arrows, modern tech documentation style
```

---

## 3️⃣ Image Analysis Flow Prompt

```
Create a comprehensive flowchart for AI-powered image analysis with these elements:

Start: "User uploads image"

Flow:
1. File validation (diamond) → If invalid → Show error (red box)
2. If valid → Send to Backend API
3. Backend receives image
4. Resize if > 10MB
5. Convert to base64
6. Send to Groq AI (Llama 4 Scout)
7. AI analyzes and returns vision labels
8. Calculate safety score (0-100)
9. Score decision (diamond):
   - Score < 50 → Status: Approved ✓ (green)
   - Score >= 80 → Status: Rejected ✗ (red)
   - Score 50-79 → Status: Manual Review ⚠️ (yellow)
10. Manual review items → Add to moderation queue
11. Save all results to database
12. Return result to frontend
13. Display score & verdict
14. If approved → Show "Post to Instagram" button (blue)
15. If rejected → Show rejection warning (red)

Colors:
- Green boxes: Approved states
- Red boxes: Rejected states
- Yellow boxes: Review states
- Blue boxes: Action states
- Gray boxes: Process states

Style: Modern flowchart, vertical layout, clear decision diamonds, professional business diagram
```

---

## 4️⃣ Complete System Architecture Prompt

```
Create a comprehensive multi-layer architecture diagram for InstaGuard platform:

Layer 1 - Client (Top):
- User Browser (laptop/mobile icon)
- Frontend Application (HTML/CSS/JS)
- Hosted on Vercel

Layer 2 - Application (Middle):
- Backend API (FastAPI + Python)
- Hosted on Render
- JWT Authentication module
- Image Analysis Logic

Layer 3 - External Services (Bottom):
- Supabase (PostgreSQL + Auth) - database icon
- Groq AI API (Llama 4 Scout) - AI brain icon
- Google OAuth - Google logo
- UptimeRobot - monitor icon

Connections:
- All layers connected with bidirectional arrows
- Show data flow direction
- Label each connection (e.g., "REST API", "OAuth", "SQL")

Additional Elements:
- Color code by function (auth=purple, data=blue, AI=orange)
- Include technology logos
- Show security shields for auth points
- Add cloud icons for hosted services

Style: Enterprise architecture diagram, isometric 3D view, professional color palette, suitable for technical documentation
```

---

## 5️⃣ Database Schema ER Diagram Prompt

```
Create a professional Entity-Relationship (ER) diagram for InstaGuard database:

Tables (boxes with rounded corners):

1. USERS (purple)
   - id (PK, uuid)
   - email (text)
   - role (text)
   - created_at (timestamp)

2. IMAGE_CHECKS (blue)
   - id (PK, uuid)
   - user_id (FK → users.id)
   - image_url (text)
   - safety_score (integer)
   - status (text)
   - vision_labels (json)
   - checked_at (timestamp)

3. FEED_ANALYSES (green)
   - id (PK, uuid)
   - user_id (FK → users.id)
   - feed_snapshot (json)
   - overall_score (integer)
   - status (text)
   - analysed_at (timestamp)

4. MODERATION_QUEUE (orange)
   - id (PK, uuid)
   - ref_id (FK)
   - ref_type (text)
   - score (integer)
   - decision (text)
   - reviewed_at (timestamp)

5. FEED_REBOOT_REQUESTS (yellow)
   - id (PK, uuid)
   - user_id (FK → users.id)
   - instagram_username (text)
   - post_ids (json)
   - status (text)
   - requested_at (timestamp)

6. ADMIN_LOGS (red)
   - id (PK, uuid)
   - admin_id (FK → users.id)
   - action (text)
   - payload (json)
   - logged_at (timestamp)

7. THRESHOLDS (gray)
   - id (PK, uuid)
   - auto_approve_max (integer)
   - manual_review_min (integer)
   - auto_reject_min (integer)
   - updated_at (timestamp)

Relationships:
- USERS (1) → (many) IMAGE_CHECKS
- USERS (1) → (many) FEED_ANALYSES
- USERS (1) → (many) FEED_REBOOT_REQUESTS
- USERS (1) → (many) ADMIN_LOGS
- IMAGE_CHECKS (1) → (0..1) MODERATION_QUEUE
- FEED_ANALYSES (1) → (0..1) MODERATION_QUEUE

Style: Professional database ER diagram with crow's foot notation, color-coded tables, clear PK/FK indicators, suitable for technical documentation
```

---

## 6️⃣ Deployment Pipeline Prompt

```
Create a CI/CD pipeline diagram showing the deployment workflow:

Stages (left to right):

1. Developer (person icon)
   ↓
2. Git Commit & Push
   ↓
3. GitHub Repository (GitHub logo)
   ↓ (splits into two branches)
   
Branch 1 - Frontend:
4a. Vercel detects push
5a. Build frontend (HTML/CSS/JS)
6a. Deploy to CDN
7a. Live at: insta-guard-lyart.vercel.app (green check)

Branch 2 - Backend:
4b. Render detects push
5b. Install dependencies (pip install)
6b. Build Docker container
7b. Deploy FastAPI server
8b. Live at: insta-guard.onrender.com (green check)

External connections from deployed services:
- Both connect to Supabase Database
- Backend connects to Groq AI
- Frontend connects to Google OAuth

Monitoring:
- UptimeRobot pings backend every 5 minutes

Style: DevOps pipeline diagram, horizontal flow, use standard CI/CD colors (green for success, blue for building, gray for pending), include platform logos, modern tech style
```

---

## 7️⃣ Security & Authentication Flow Prompt

```
Create a detailed security flow diagram showing request authentication:

Entry point: "User Request Arrives"

Main Flow (vertical):
1. Check if request has JWT token (diamond)
   → NO: Return 401 Unauthorized (red exit)
   → YES: Continue

2. Extract JWT token from header

3. Validate with Supabase (diamond)
   → Valid Supabase token: Continue to step 5
   → Invalid: Try custom JWT

4. Validate custom JWT (diamond)
   → Valid: Continue to step 5
   → Invalid: Return 401 Unauthorized (red exit)

5. Fetch user from database

6. Check if user exists (diamond)
   → NO: Auto-create user
   → YES: Load user profile

7. Check Row Level Security policies (shield icon)

8. Verify user authorization (diamond)
   → NO: Return 403 Forbidden (red exit)
   → YES: Continue

9. Process request (green)

10. Return response (green exit)

Side elements:
- Security shields at authentication points
- Lock icons for protected resources
- Error boxes in red
- Success boxes in green

Style: Security-focused flowchart with emphasis on decision points, use shield and lock icons, professional cybersecurity diagram style, clear visual separation of success vs error paths
```

---

## 8️⃣ User Journey Map Prompt

```
Create a user journey map showing the complete user experience:

Timeline (left to right):

1. DISCOVER (Blue)
   - User hears about InstaGuard
   - Visits website
   - Reads about features
   Emotion: Curious 😊

2. SIGN UP (Purple)
   - Clicks "Sign in with Google"
   - Authenticates
   - Redirected to dashboard
   Emotion: Excited 🎉

3. FIRST USE (Green)
   - Uploads first image
   - Sees AI analysis in real-time
   - Gets instant safety score
   Emotion: Impressed 🤩

4. REGULAR USE (Orange)
   - Checks multiple images
   - Analyzes feed
   - Reviews history
   Emotion: Satisfied 😌

5. POWER USER (Red)
   - Admin moderates content
   - Adjusts thresholds
   - Reviews reboot requests
   Emotion: In control 💪

Touchpoints (below each stage):
- Website, Dashboard, Image Checker, Feed Analyzer, Admin Panel

Pain points (marked with ⚠️):
- Cold start delay (solved with UptimeRobot)
- Token expiration (clear messaging)

Gains (marked with ✅):
- Fast AI analysis
- Beautiful UI
- No account creation friction

Style: Modern user journey map with emotion indicators, color-coded stages, timeline visualization, include emoji for emotions, professional UX design style
```

---

## 9️⃣ API Endpoint Tree Prompt

```
Create a hierarchical tree diagram of all API endpoints:

Root: InstaGuard API (https://insta-guard.onrender.com)

Main Branches:

🔐 /auth (Purple branch)
├── POST /signup - Create new user account
├── POST /login - Email/password authentication
└── GET /me - Get current user profile

🖼️ /images (Blue branch)
├── POST /check - Analyze uploaded image
└── GET /history - Get user's image check history

📱 /feed (Green branch)
├── POST /analyze - Analyze Instagram feed
├── GET /history - Get user's feed analysis history
└── POST /reboot-request - Request feed cleanup

📊 /dashboard (Orange branch)
├── GET /stats - Get user statistics
└── GET /activity - Get recent activity

👨‍💼 /admin (Red branch)
├── GET /queue - Get moderation queue
├── POST /review - Submit moderation decision
├── GET /thresholds - Get safety thresholds
├── PUT /thresholds - Update safety thresholds
├── GET /reboot-requests - Get pending reboot requests
└── POST /reboot-action - Approve/reject reboot request

Visual Elements:
- Each endpoint shows HTTP method (color-coded: GET=blue, POST=green, PUT=orange)
- Brief description under each endpoint
- Branch colors match the function (auth=purple, data=blue, etc.)
- Root node at top, branches flowing downward

Style: API documentation tree diagram, color-coded by HTTP methods, clear hierarchy, professional technical documentation style, suitable for API reference
```

---

## 🔟 Performance & Monitoring Prompt

```
Create a system monitoring and performance diagram:

Center: Backend Server (Render)

Incoming monitoring sources (pointing to center):

1. UptimeRobot (top-left)
   - Status: UP ✓
   - Ping interval: 5 minutes
   - Uptime: 99.9%
   - Response time: ~250ms

2. Frontend Keep-Alive (top-right)
   - Status: ACTIVE
   - Ping interval: 10 minutes
   - Only when users active

3. User Requests (bottom)
   - Real traffic
   - WebSocket connections
   - API calls

Outgoing connections from center:

4. Database (Supabase) - left
   - Connection pool: 5 connections
   - Query time: <50ms
   - Status: Healthy ✓

5. Groq AI API - right
   - Image analysis requests
   - Response time: ~2s
   - Rate limit: 100/min
   - Status: Operational ✓

Performance Metrics (dashboard style):
- CPU Usage: 15%
- Memory: 256MB / 512MB
- Requests/min: ~50
- Error rate: 0.1%
- Average response time: 200ms

Visual Style: 
- Real-time monitoring dashboard
- Graphs and gauges
- Green indicators for healthy
- Status lights (green=good, yellow=warning, red=error)
- Professional DevOps monitoring tool style (like Grafana/DataDog)
```

---

## 💡 How to Use These Prompts

### In ChatGPT:
1. Copy any prompt above
2. Paste into ChatGPT
3. Ask: "Create this as a detailed description for an image"
4. Use DALL-E to generate the image

### In Midjourney/Stable Diffusion:
1. Copy the prompt
2. Add at the end: `--ar 16:9 --v 6 --style raw`
3. Generate the image

### In Figma/Design Tools:
1. Use the prompts as a specification
2. Create manually using the exact layout described

### In Mermaid/PlantUML:
1. Convert the prompts to syntax
2. Generate in tools like:
   - https://mermaid.live
   - https://plantuml.com

---

## 🎨 Style Presets

**Corporate Style:**
Add: "in a professional corporate presentation style, suitable for business meetings, clean and minimal"

**Tech Startup Style:**
Add: "in a modern startup style with vibrant colors, trendy design, suitable for pitch decks"

**Academic Style:**
Add: "in a formal academic style, suitable for research papers and technical documentation"

**Infographic Style:**
Add: "as a colorful infographic with icons and illustrations, suitable for social media"

---

**Created for InstaGuard Project**
Use these prompts to generate professional diagrams for documentation, presentations, or portfolio!
