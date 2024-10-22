from models.models import TeamToken
from fastapi import HTTPException, status
import secrets
import string
from configs import ADMIN_TOKEN, TOKEN_LENGTH

# Fake database
fake_db = {
    "teams_tokens": {},
    "drone_control_teams_tokens": {},
    "drone_control_queue": [],
}
active_drone_control_token = ""


def get_current_team(token: str):
    if token in fake_db["teams_tokens"]:
        return TeamToken(token=token, name=fake_db["teams_tokens"][token])
    return False


def verify_admin_token(token: str):
    if token != ADMIN_TOKEN:
        return False
    return token


def verify_drone_control_token(token: str):
    if token not in fake_db["drone_control_teams_tokens"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )
    return token


def verify_token(token: str):
    if len(token) != TOKEN_LENGTH or token not in fake_db["teams_tokens"]:
        return False
    return token


def get_not_used_stream_from_team_token(token: str):
    team = get_current_team(token)
    for stream in fake_db["drone_control_teams_tokens"]:
        if (
            fake_db["drone_control_teams_tokens"][stream]["owner"] == team.name
            and not fake_db["drone_control_teams_tokens"][stream]["used"]
        ):
            return stream


def check_if_team_name_exists(team_name: str):
    for token in fake_db["teams_tokens"]:
        if fake_db["teams_tokens"][token] == team_name:
            return TeamToken(token=token, name=team_name)
    return False


def generate_token(length=TOKEN_LENGTH):
    # Define the characters to choose from
    characters = string.ascii_letters + string.digits  # Letters and digits
    # Generate a token with the desired length
    token = "".join(secrets.choice(characters) for _ in range(length))
    return token
