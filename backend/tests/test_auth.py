from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)

password = "Minh210905@@@"

hashed = hash_password(password)

print(hashed)

print(
    verify_password(
        "123456",
        hashed
    )
)

token = create_access_token({
    "sub": "test@gmail.com"
})

print(token)