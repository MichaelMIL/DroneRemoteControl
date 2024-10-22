from pydantic import BaseModel


# Models for request validation
class TeamToken(BaseModel):
    token: str
    name: str


class DroneControlToken(BaseModel):
    token: str
    timestamp: float
    datetime: str
    duration: int
    owner: str
    used: bool = False


class TokenData(BaseModel):
    username: str | None = None


class NewTeamToken(BaseModel):
    token: str
