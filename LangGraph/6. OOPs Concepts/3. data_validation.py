# pip install pydantic[email]
from typing import TypedDict, Annotated, Optional, Literal, List, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, conint, constr, SecretStr, HttpUrl

class UserData(TypedDict):
    name: str
    age: int
    email: str

user_data = {"name":"John Doe", "age" : 30, "email" : "email@example.com"}
data = UserData(user_data)
print("User Data 1:", data)

# 정의하지 않은 멤버변수까지 사용 가능
user_data = {"name": "John Doe", "address": "mumbai"}
data = UserData(user_data)
print("User Data 2:", data)

# using pydantic BaseModel for validation in runtime
class UserModel(BaseModel):
    name : str = Field(..., min_length=3, max_length=50, description="Name of the user")         # min_length, max_length : 문자열 길이 제한
    age : int = Field(..., gt=0, description="Age of the user")                                  # gt : 0보다 큰 정수만 입력 가능
    email : EmailStr = Field(..., description="Email of the user")                               # EmailStr : 이메일 형식으로만 입력 가능
    gender : Optional[Literal["male", "female", "other"]] = "other"                              # 정해진 문자열만 입력 가능

data = UserModel(name="John Doe", age=30, email="email@example.com")
print("User Data 3:", data)

data = UserModel(name="John Doe", age=30, email="email@example.com", gender="male")
print("User Data 4:", data)

