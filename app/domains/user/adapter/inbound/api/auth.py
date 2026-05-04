"""세션 토큰 기반 인증 의존성.

- POST /api/saju/free 응답으로 발급된 session_token을
  Authorization: Bearer <token> 헤더로 전달받는다.
- 토큰이 없거나 일치하는 사용자가 없으면 401.
- 라우터에 비즈니스 로직을 두지 않기 위해 단순 조회만 한다.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from app.domains.user.domain.entity.user import User
from app.domains.user.domain.port.user_repository_port import UserRepositoryPort

_BEARER = "Bearer "


# main.py에서 dependency_overrides로 교체된다.
def get_user_repository() -> UserRepositoryPort:
    raise NotImplementedError


async def get_current_user(
    request: Request,
    user_repo: UserRepositoryPort = Depends(get_user_repository),
) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith(_BEARER):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth[len(_BEARER):].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_repo.find_by_session_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
