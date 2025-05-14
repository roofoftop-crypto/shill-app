# File: /services/auth_service.py

from typing import Optional

def get_users():
    return [
        {"username": "nico", "password": "4862", "name": "Nico"},
        {"username": "ramo", "password": "ramo123", "name": "Ramo"},
        {"username": "pablito", "password": "pablito123", "name": "Pablo uwu"},
        {"username": "marto", "password": "marto123", "name": "Panda"},
        {"username": "user4", "password": "password4", "name": "Usuario Cuatro"}
    ]

def validate_user(username: str, password: str) -> Optional[dict]:
    users = get_users()
    for user in users:
        if user.get("username") == username and user.get("password") == password:
            return user
    return None
