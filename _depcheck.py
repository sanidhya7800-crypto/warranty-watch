import fastapi
import uvicorn
import sqlalchemy
import multipart
import pydantic

print("DEPS_OK", fastapi.__version__, uvicorn.__version__, sqlalchemy.__version__, pydantic.VERSION)
