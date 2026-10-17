from typing import List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: lets the grader's web page call your API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- The four layers (weakest to strongest) ----
DEFAULTS = {
    "port": 8000, "workers": 1, "debug": False,
    "log_level": "info", "api_key": "default-secret-000",
}
YAML_LAYER = {"port": 8951, "workers": 4, "debug": False, "log_level": "warning"}
DOTENV_LAYER = {"APP_LOG_LEVEL": "error"}
OS_ENV_LAYER = {"APP_WORKERS": "11", "APP_DEBUG": "false"}

ALIASES = {"num_workers": "workers"}


def normalize_key(key: str) -> str:
    key = key.strip().lower()
    if key.startswith("app_"):
        key = key[4:]
    return ALIASES.get(key, key)


def coerce(key: str, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)


@app.get("/effective-config")
def effective_config(sets: List[str] = Query(default=[], alias="set")):
    config = {}

    for layer in (DEFAULTS, YAML_LAYER, DOTENV_LAYER, OS_ENV_LAYER):
        for raw_key, value in layer.items():
            key = normalize_key(raw_key)
            config[key] = coerce(key, value)

    for item in sets:
        raw_key, _, value = item.partition("=")
        key = normalize_key(raw_key)
        try:
            config[key] = coerce(key, value)
        except ValueError:
            pass

    config["api_key"] = "****"
    return config
