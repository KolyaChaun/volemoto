import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv()

ADMIN_LOGIN = os.getenv("ADMIN_LOGIN")
ADMIN_PASS  = os.getenv("ADMIN_PASS")

templates = Jinja2Templates(directory="src/templates")
