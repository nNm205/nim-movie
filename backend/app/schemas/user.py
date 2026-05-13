from pydantic import ( 
    BaseModel, 
    EmailStr, 
    Field,
    model_validator
) 

class UserRegister(BaseModel):
    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=30 
    )

    password: str = Field(
        min_length=6
    )

    confirm_password: str 

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        
        return self 

class UserLogin(BaseModel): 
    email: EmailStr
    password: str 

class UserResponse(BaseModel):
    id: int
    email: EmailStr 
    username: str 

class TokenResponse(BaseModel):
    access_token: str 
    user: UserResponse 