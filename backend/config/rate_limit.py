from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://redis:6379",
    default_limits=["100 per hour"]
)
