from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import hashlib  # 导入 hashlib 用于 MD5 加密

from dao.database import get_db
from entitymodels.entities import User
from entitymodels.schemas import LoginRequest, LoginResponse, TokenData, JWTPayload

# JWT配置
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 生产环境应从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# OAuth2方案 作用就是自动从请求头中提取 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") # 这个参数只影响Swagger文档  只是告诉前端开发者："如果你想获取token，可以去这个地址登录"

# 创建路由实例
router = APIRouter(prefix="/auth", tags=["authentication"])


# 创建 MD5 哈希函数
def md5_hash(text: str) -> str:
    """生成 MD5 哈希值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return get_password_hash(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    # 当前使用 MD5
    return md5_hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户凭据"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):  # 注意：你的字段名是password
        return None
    return user


def create_access_token(data: JWTPayload, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT令牌"""
    to_encode = data.model_dump()  # 转换为字典
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # to_encode.update({"exp": expire})
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=LoginResponse)
def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    用户登录接口
    成功返回格式：
    {
        "status": 0,
        "message": "登陆成功",
        "token": "jwt_token_here"
    }
    """
    # 验证用户
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        # 返回统一错误格式
        return LoginResponse(
            status=-1,
            message="用户名或密码错误",
            token=""
        )

    # 检查用户状态
    if not user.status:
        return LoginResponse(
            status=-1,
            message="用户账户已被禁用",
            token=""
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=JWTPayload(
            user_id=user.id,
            username=user.username,
            usertype=user.usertype,
            exp=0,
        ),
        expires_delta=access_token_expires
    )

    # 返回指定格式的响应
    return LoginResponse(
        status=0,
        message="登陆成功",
        token=access_token,
    )



'''
# 多个路由可以复用同一个依赖
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {"profile": "..."}

@router.put("/profile")
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    # 业务逻辑
    pass

这正是FastAPI依赖注入系统的强大之处。你可以把 get_current_user当作认证中间件来使用。

请求 → FastAPI → 检查Depends(get_current_user) → 验证token → 失败→返回401
                                     ↓
                              成功 → 获取用户 → 注入current_user → 执行路由逻辑

'''
# async def get_current_user(
#         token: str = Depends(oauth2_scheme),
#         db: Session = Depends(get_db)
# ) -> User:
#     # todo token失效就返回一个空的user  token有效正常返回user即可。
#     # todo 下游的逻辑代码先判断得到的这个user是否是空，是空就返回-2 code 让前端感知，重新登录 不是空就继续正常执行逻辑。
#     """获取当前用户依赖"""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail={
#             "status": -2,
#             "message": "token 无效",
#             "data": None,
#         },# detail="无法验证凭据",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # todo 超时要验证一下
#         username: str = payload.get("username")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#
#     user = db.query(User).filter(User.username == token_data.username).first()
#     if user is None:
#         raise credentials_exception
#     return user
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    # todo token失效就返回一个空的user  token有效正常返回user即可。
    # todo 下游的逻辑代码先判断得到的这个user是否是空，是空就返回-2 code 让前端感知，重新登录 不是空就继续正常执行逻辑。
    """获取当前用户依赖"""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:  # 当JWT token超时（过期）时，jwt.decode()会抛出 JWTError异常
        return None

    user = db.query(User).filter(User.username == token_data.username).first()
    return user


# 检查token是否有效的接口
@router.post("/checktoken")
async def check_token(current_user: User = Depends(get_current_user)):
    if not current_user:
        return {
            "status": -2,  # token失效的status
            "message": "token 无效",
            "data": None
        }
    return {
        "status": 0,
        "message": "token 有效",
        "data": None
    }

# 受保护的路由示例 - 获取当前用户信息
@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):  # Depends(get_current_user) FastAPI的依赖注入装饰器 从 get_current_user依赖函数返回的值
    """获取当前用户信息（需要认证）"""
    if not current_user:
        return {
            "status": -2,  # token失效的status
            "message": "token 无效",
            "data": None
        }
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "usertype": current_user.usertype,
        "status": current_user.status
    }

