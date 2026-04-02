from fastapi import Request, HTTPException

def get_current_user(request: Request) -> str:
    """
    Extracts the user identity from the headers passed by the frontend.
    
    WARNING: This is a prototype implementation using the `X-User-Sub` header.
    In a production application, you MUST strictly validate a signed JWT 
    from Auth0 here (e.g., using PyJWT and JWKS validation).
    """
    user_sub = request.headers.get("X-User-Sub")
    if not user_sub:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing X-User-Sub header. Please log in.",
        )
    return user_sub
