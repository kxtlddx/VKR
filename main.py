from fastapi import FastAPI
from controllers.achievement_controller import router as ach_router
from controllers.event_controller       import router as ev_router
from controllers.leaderboard_controller import router as lb_router

app = FastAPI(title="Achievement Microservice", docs_url="/swagger")

app.include_router(ach_router, prefix="/api/v1")
app.include_router(ev_router,  prefix="/api/v1")
app.include_router(lb_router,  prefix="/api/v1")
