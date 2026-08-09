
from dataclasses import dataclass
from datetime import datetime



@dataclass
class User:

    user_id: str
    username: str

    credits: int = 30
    xp: int = 0
    streak: int = 0



@dataclass
class Exercise:

    exercise_id: str
    user_id: str

    subject: str
    level: str

    content: str

    created_at: str = str(datetime.now())



@dataclass
class ChatMessage:

    message_id: str
    exercise_id: str

    role: str
    content: str

    created_at: str = str(datetime.now())



@dataclass
class Skill:

    skill_id: str
    user_id: str

    name: str
    level: int = 1

