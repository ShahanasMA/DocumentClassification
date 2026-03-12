from werkzeug.security import generate_password_hash

USERS = {
    "admin": {
        "password": generate_password_hash("admin123"),
        "role": "admin"
    },
    "user": {
        "password": generate_password_hash("user123"),
        "role": "user"
    }
}
