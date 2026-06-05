# 🛡️ InstaGuard

**AI-powered content safety and feed management for Instagram**

InstaGuard helps users maintain a safe online experience by analyzing images and Instagram feeds using advanced AI, providing real-time content moderation with administrative oversight.

---

## ✨ Features

- 🔐 **Google OAuth Authentication** - Secure sign-in with Supabase
- 🤖 **AI-Powered Image Analysis** - Real-time safety scoring using Groq API (Llama 4 Scout)
- 📊 **Dashboard** - View stats, recent activity, and safety thresholds
- 🖼️ **Image Checker** - Upload and analyze images before posting
- 📱 **Feed Analyzer** - Review Instagram feed content (mock data)
- 👨‍💼 **Admin Panel** - Moderation queue and feed reboot request management
- 🔄 **Feed Reboot Requests** - Users can request admin approval to clean flagged content

---

## 🏗️ Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Python HTTP Server for local development

**Backend:**
- FastAPI (Python)
- Supabase (PostgreSQL + Auth)
- Groq API (Llama 4 Scout for image analysis)
- JWT Authentication

**Database:**
- PostgreSQL (via Supabase)
- Row Level Security (RLS) policies

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip
- Supabase account
- Groq API key
- Google OAuth credentials

### Backend Setup

```bash
cd instaGuard/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see .env.example)
# Add your credentials

# Run server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd instaGuard/frontend

# Run HTTP server
python -m http.server 3000
```

Access the app at: **http://localhost:3000**

---

## 🔑 Environment Variables

Create `backend/.env` file:

```env
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Groq API
GROQ_API_KEY=your-groq-api-key

# JWT
JWT_SECRET=your-secret-key
```

---

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

**Quick Deploy:**
- Backend: Render
- Frontend: Vercel
- Database: Supabase

---

## 📊 Database Schema

- **users** - User profiles with roles
- **image_checks** - Image analysis records
- **feed_analyses** - Feed analysis history
- **moderation_queue** - Items requiring manual review
- **thresholds** - Configurable safety score thresholds
- **admin_logs** - Admin action audit trail
- **feed_reboot_requests** - User requests for feed cleanup

---

## 🔐 Security Features

- Row Level Security (RLS) policies
- JWT token authentication
- Google OAuth integration
- Service role for admin operations
- CORS configuration
- Input validation

---

## 📝 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - Email/password login
- `GET /auth/me` - Get current user

### Images
- `POST /images/check` - Analyze image
- `GET /images/history` - User's image history

### Feed
- `POST /feed/analyze` - Analyze Instagram feed (mock)
- `GET /feed/history` - User's feed analysis history
- `POST /feed/reboot-request` - Request feed cleanup

### Dashboard
- `GET /dashboard/stats` - User statistics
- `GET /dashboard/activity` - Recent activity

### Admin
- `GET /admin/queue` - Moderation queue
- `POST /admin/review` - Review queued item
- `GET /admin/thresholds` - Get safety thresholds
- `PUT /admin/thresholds` - Update thresholds
- `GET /admin/reboot-requests` - Get reboot requests
- `POST /admin/reboot-action` - Approve/reject reboot request

---

## 🎨 UI Features

- Modern dark theme
- Responsive design
- Real-time score visualization
- Badge system for content status
- Toast notifications
- Loading states

---

## 🔮 Future Enhancements

- [ ] Real Instagram API integration
- [ ] Image storage (Supabase Storage)
- [ ] Email notifications
- [ ] Export reports
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Mobile app

---

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

MIT License - feel free to use this project for learning and development.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Supabase](https://supabase.com/)
- [Groq](https://groq.com/)
- [Vercel](https://vercel.com/)
- [Render](https://render.com/)

---

Made with ❤️ for safer online communities
