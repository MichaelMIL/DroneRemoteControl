from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse

from fastapi.templating import Jinja2Templates
from configs import (
    ADMIN_TOKEN,
    DRONE_FLIGHT_CONTROLLER_TIME,
    STREAM_URL,
    DRONE_FLIGHT_CONTROLLER_THROTTLE_KEY,
    DRONE_FLIGHT_CONTROLLER_ARM_KEY,
)
import uvicorn
import datetime
import time
from models.models import TeamToken, DroneControlToken, NewTeamToken
from actions.db_actions import (
    get_current_team,
    verify_admin_token,
    verify_token,
    get_not_used_stream_from_team_token,
    check_if_team_name_exists,
    fake_db,
    generate_token,
    active_drone_control_token,
)

is_armed = False  # Initial state for the drone's ARM/DISARM
throttle_value = 0  # Initial throttle value

# Initialize FastAPI app
app = FastAPI()
# Jinja2 templates location
templates = Jinja2Templates(directory="templates")


token = generate_token()
# print(f"Admin Token: {token}")


@app.post("/generate_new_team_token", response_model=NewTeamToken)
async def generate_new_team_token(token: str, team_name: str):
    if token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
        )
    team_if = check_if_team_name_exists(team_name)
    if team_if:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team: {team_if.name} already exists, Token: {team_if.token}",
        )
    new_token = generate_token()
    fake_db["teams_tokens"][new_token] = team_name
    return {"token": new_token}


@app.get("/teams")
async def get_teams(token: str = Depends(verify_admin_token)):
    if token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
        )
    return fake_db["teams_tokens"]


@app.post("/get_drone_controller_key", response_model=DroneControlToken)
async def get_drone_controller_key(team_token: TeamToken = Depends(verify_token)):
    if not team_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    team = get_current_team(team_token)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    stream_item = get_not_used_stream_from_team_token(team_token)
    if stream_item:
        return DroneControlToken(
            token=stream_item,
            timestamp=fake_db["drone_control_teams_tokens"][stream_item]["timestamp"],
            datetime=fake_db["drone_control_teams_tokens"][stream_item]["datetime"],
            duration=fake_db["drone_control_teams_tokens"][stream_item]["duration"],
            owner=fake_db["drone_control_teams_tokens"][stream_item]["owner"],
            used=fake_db["drone_control_teams_tokens"][stream_item]["used"],
        )

    # Generate a new stream token
    stream_token = generate_token()
    # Store the stream token in the database
    fake_db["drone_control_teams_tokens"][stream_token] = {
        "timestamp": time.time(),
        "datetime": str(datetime.datetime.now()),
        "duration": DRONE_FLIGHT_CONTROLLER_TIME,
        "owner": team.name,
        "used": False,
    }
    fake_db["drone_control_queue"].append(stream_token)
    return {
        "token": stream_token,
        "timestamp": fake_db["drone_control_teams_tokens"][stream_token]["timestamp"],
        "datetime": fake_db["drone_control_teams_tokens"][stream_token]["datetime"],
        "duration": fake_db["drone_control_teams_tokens"][stream_token]["duration"],
        "owner": fake_db["drone_control_teams_tokens"][stream_token]["owner"],
        "used": fake_db["drone_control_teams_tokens"][stream_token]["used"],
    }


last_stream_start_time = 0


@app.get("/get_drone_controller_access", response_class=JSONResponse)
async def get_drone_controller_access(team_token: str = Depends(verify_token)):
    global last_stream_start_time, active_drone_control_token
    if not team_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    if (
        active_drone_control_token == team_token
        and last_stream_start_time + DRONE_FLIGHT_CONTROLLER_TIME > time.time()
    ):
        raise HTTPException(
            status_code=status.HTTP_226_IM_USED,
            detail={
                "message": f"Your token is active (time left: {int(last_stream_start_time + DRONE_FLIGHT_CONTROLLER_TIME - time.time())}s)",
                "time_left": int(
                    last_stream_start_time + DRONE_FLIGHT_CONTROLLER_TIME - time.time()
                ),
            },
        )
    stream_token = get_not_used_stream_from_team_token(team_token)
    if not stream_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available stream",
        )

    if fake_db["drone_control_queue"][0] == stream_token:
        if (
            last_stream_start_time > 0
            and last_stream_start_time + DRONE_FLIGHT_CONTROLLER_TIME > time.time()
        ):
            raise HTTPException(
                status_code=status.HTTP_226_IM_USED,
                detail={
                    "message": f"Another team(s) [{fake_db["drone_control_queue"].index(stream_token) + 1}]  is currently controlling the drone (time left: {int((last_stream_start_time + DRONE_FLIGHT_CONTROLLER_TIME - time.time())+(DRONE_FLIGHT_CONTROLLER_TIME*fake_db["drone_control_queue"].index(stream_token)))}s)",
                    "queue_position": fake_db["drone_control_queue"].index(stream_token)
                    + 1,
                },
            )

        fake_db["drone_control_queue"].pop(0)
        fake_db["drone_control_teams_tokens"][stream_token]["used"] = True
        active_drone_control_token = team_token
        last_stream_start_time = time.time()
        return {"Drone Control": "Active"}

    raise HTTPException(
        status_code=status.HTTP_226_IM_USED,
        detail={
            "message": f"Another team(s) [{fake_db["drone_control_queue"].index(stream_token) + 1}] is currently controlling the drone (time left: {int((last_stream_start_time + DRONE_FLIGHT_CONTROLLER_TIME - time.time())+(DRONE_FLIGHT_CONTROLLER_TIME*fake_db["drone_control_queue"].index(stream_token)))}s)",
            "queue_position": fake_db["drone_control_queue"].index(stream_token) + 1,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(token: str = Form(...)):
    if verify_token(token):
        return RedirectResponse(f"/welcome/{token}", status_code=302)
    else:
        return templates.TemplateResponse(
            "login.html", {"error": "Invalid token", "request": {}}
        )


@app.get("/welcome/{token}", response_class=HTMLResponse)
async def welcome_page(request: Request, token: str = Depends(verify_token)):
    if token:
        return templates.TemplateResponse(
            "welcome.html", {"request": request, "token": token}
        )
    else:
        return RedirectResponse("/", status_code=302)


@app.get("/drone/{token}", response_class=HTMLResponse)
async def drone_controller(request: Request, token: str = Depends(verify_token)):
    if not token:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "drone.html", {"request": request, "session_time": DRONE_FLIGHT_CONTROLLER_TIME}
    )


@app.post("/toggle_arm/{token}")
async def toggle_arm(pass_key: str = Form(...), token: str = Depends(verify_token)):
    global is_armed, active_drone_control_token
    if not token:
        return RedirectResponse("/", status_code=302)
    if pass_key != DRONE_FLIGHT_CONTROLLER_ARM_KEY:
        return JSONResponse({"armed": is_armed})
    if (
        active_drone_control_token == token
        and time.time() - last_stream_start_time < DRONE_FLIGHT_CONTROLLER_TIME
    ):
        is_armed = not is_armed
        return JSONResponse({"armed": is_armed})

    return JSONResponse({"armed": is_armed})


@app.post("/set_throttle/{token}")
async def set_throttle(
    throttle: int = Form(...),
    pass_key: str = Form(...),
    token: str = Depends(verify_token),
):
    global throttle_value, active_drone_control_token
    if not token:
        return RedirectResponse("/", status_code=302)

    if pass_key != DRONE_FLIGHT_CONTROLLER_THROTTLE_KEY:
        return JSONResponse({"throttle": throttle_value})
    if (
        active_drone_control_token == token
        and time.time() - last_stream_start_time < DRONE_FLIGHT_CONTROLLER_TIME
    ):
        throttle_value = throttle
        return JSONResponse({"throttle": throttle_value})

    return JSONResponse({"throttle": throttle_value})


# Add the main entry point to run the app with Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
