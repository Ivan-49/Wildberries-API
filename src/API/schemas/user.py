from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserShema(BaseModel):
    username: str = Field(alias="username")
    password: str = Field(alias="password")
    first_name: Optional[str] = Field(alias="first_name")
    last_name: Optional[str] = Field(alias="last_name")
    language: Optional[str] = Field(alias="language")
    is_bot: Optional[bool] = Field(alias="is_bot")
    premium_status: Optional[str] = Field(alias="premium_status")

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value
