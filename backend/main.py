from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, images, feed, dashboard, admin

app = FastAPI(title="InstaGuard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins - change this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router,      prefix="/auth",      tags=["Auth"])
app.include_router(images.router,    prefix="/images",    tags=["Images"])
app.include_router(feed.router,      prefix="/feed",      tags=["Feed"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(admin.router,     prefix="/admin",     tags=["Admin"])


@app.get("/")
def root():
    return {"status": "InstaGuard API running"}
