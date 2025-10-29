"""
Main FastAPI application entry point.

This module initializes the FastAPI app, configures middleware, includes all API routers,
and handles the application lifecycle events.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.app.router.user_router import router as user_router
from api.app.router.athlete_router import router as athlete_router
from api.app.router.gender_router import router as gender_router
from api.app.router.country_router import router as country_router
from api.app.router.profile_router import router as profile_router
from api.app.router.professional_role_router import router as professional_role_router
from api.app.router.institution_router import router as institution_router
from api.app.utils.lifespan import lifespan
from api.app.utils.middlewares import DBSessionMiddleware, LanguageMiddleware
from api.app.utils.db_functions import handler_db


logging.info("Starting database handler")
handler_db()

logging.info("Starting FastAPI server")

# Initialize the FastAPI app
app = FastAPI(lifespan=lifespan)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBSessionMiddleware)
app.add_middleware(LanguageMiddleware)

# Include API routers
app.include_router(athlete_router)
app.include_router(country_router)
app.include_router(gender_router)
app.include_router(institution_router)
app.include_router(professional_role_router)
app.include_router(profile_router)
app.include_router(user_router)

"""
Notes:
- `lifespan`: Manages the application lifecycle events, like starting and shutting down.
- `CORSMiddleware`: Enables Cross-Origin Resource Sharing for the API.
    Replace `["*"]` with specific domains in production.
- Each router (e.g., `user`) should be properly defined in its respective module and
    organized with prefixes and tags for better documentation.
"""
