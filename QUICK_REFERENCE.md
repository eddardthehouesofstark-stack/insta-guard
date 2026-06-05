# InstaGuard - Quick Reference Architecture

## 🎯 System at a Glance

```
┌─────────────┐
│    USER     │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│  FRONTEND (Vercel)                  │
│  - HTML/CSS/JavaScript              │
│  - Google OAuth Login               │
│  - Dashboard, Image Checker, Feed   │
└───────────┬─────────────────────────┘
            │
            ↓
┌─────────────────────────────────────┐
│  BACKEND (Render)                   │
│  - FastAPI + Python                 │
│  - JWT Authentication               │
│  - Image Analysis Logic             │
└───┬───────┬─────────┬───────────┬───┘
    │       │         │           │
    ↓       ↓         ↓           ↓
┌───────┐ ┌────┐  ┌─────┐    ┌────────┐
│Supabase│ │Groq│  │Google│   │UptimeRobot│
│PostgreSQL Auth  Llama4│   │Keep-Alive │
└───────┘ └────┘  └─────┘    └────────┘
```

---

## 🔄 Core Workflows

### 1️⃣ User Signs In
```
User → Click Google Sign-In → Google OAuth → Supabase Auth → 
Backend validates → Fetch user from DB → Redirect to Dashboard ✅
```

### 2️⃣ Image Analysis
```
Upload Image → Backend → Resize → Groq AI (Llama 4) → 
Calculate Score (0-100) → Save to DB → Show Result
```

### 3️⃣ Feed Analysis
```
Enter Instagram Username → Generate Mock Feed → Analyze Posts → 
Calculate Overall Score → Save Analysis → Show Results
```

### 4️⃣ Admin Moderation
```
Flagged Content → Moderation Queue → Admin Reviews → 
Approve/Reject → Update Status → Log Action
```

---

## 📊 Scoring Logic

```
Score 0-49:   ✅ APPROVED      (Auto-post allowed)
Score 50-79:  ⚠️ MANUAL REVIEW (Needs admin check)
Score 80-100: ❌ REJECTED      (Cannot post)
```

---

## 🗄️ Database Tables

```
users ────┬──── image_checks
          ├──── feed_analyses
          ├──── feed_reboot_requests
          └──── admin_logs

moderation_queue ← (references images/feeds)
thresholds (global config)
```

---

## 🔐 Authentication Flow

```
1. User clicks "Sign in with Google"
2. Redirect to Google OAuth
3. Google → Supabase callback
4. Supabase creates/finds user
5. Frontend gets access_token
6. Backend validates token
7. Fetch user profile from DB
8. Store in localStorage
9. Redirect to dashboard
```

---

## 🚀 Deployment Stack

| Component | Platform | URL |
|-----------|----------|-----|
| Frontend | Vercel | https://insta-guard-lyart.vercel.app |
| Backend | Render | https://insta-guard.onrender.com |
| Database | Supabase | PostgreSQL + Auth |
| AI | Groq | Llama 4 Scout Model |
| Monitor | UptimeRobot | Keep-Alive Service |

---

## 🔧 Tech Stack

**Frontend:**
- Vanilla JavaScript
- HTML5/CSS3
- No frameworks

**Backend:**
- Python 3.11
- FastAPI
- Uvicorn ASGI server

**Database:**
- PostgreSQL (Supabase)
- Row Level Security (RLS)

**AI:**
- Groq API
- Llama 4 Scout 17B model

**Auth:**
- Google OAuth 2.0
- Supabase Auth
- JWT tokens

---

## 📡 API Endpoints

```
/auth
  POST   /signup          - Create new user
  POST   /login           - Email/password login
  GET    /me              - Get current user

/images
  POST   /check           - Analyze image
  GET    /history         - User's checks

/feed
  POST   /analyze         - Analyze feed
  GET    /history         - User's analyses
  POST   /reboot-request  - Request cleanup

/dashboard
  GET    /stats           - User statistics
  GET    /activity        - Recent activity

/admin
  GET    /queue           - Moderation queue
  POST   /review          - Review decision
  GET    /thresholds      - Get thresholds
  PUT    /thresholds      - Update thresholds
  GET    /reboot-requests - Pending requests
  POST   /reboot-action   - Approve/reject
```

---

## 🛡️ Security Features

✅ Row Level Security (RLS)
✅ JWT token authentication
✅ Google OAuth integration
✅ Service role for admin ops
✅ CORS configuration
✅ Input validation
✅ SQL injection prevention
✅ XSS protection

---

## ⚡ Performance Features

✅ Keep-alive system (no cold starts)
✅ Image resizing before upload
✅ Database indexing
✅ Efficient queries
✅ Auto-redeploy on push
✅ CDN for static assets

---

## 🔄 Auto-Deployment

```
GitHub Push → Triggers:
├── Vercel (Frontend) - Auto deploy in ~1 min
└── Render (Backend)  - Auto deploy in ~3 min
```

---

## 📞 Support Resources

- **GitHub**: https://github.com/eddardthehouesofstark-stack/insta-guard
- **Live Site**: https://insta-guard-lyart.vercel.app
- **API Docs**: https://insta-guard.onrender.com/docs
- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Supabase Dashboard**: https://supabase.com/dashboard

---

**🎉 InstaGuard - Built with ❤️ for safer online communities**
