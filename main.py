import os
import logging
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware  # NEW IMPORT
from pydantic import BaseModel
from e2b_code_interpreter import Sandbox
from dotenv import load_dotenv

# INITIALIZATION
load_dotenv()
app = FastAPI(title="AETHER", description="The Execution Layer for AI Agents")

# --- SECURITY PATCH: CORS (ALLOW BROWSER ACCESS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL domains (GitHub Pages, Localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers (x-api-key, etc.)
)
# ---------------------------------------------------

# LOGGING
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aether")

# SECURITY
AETHER_MASTER_KEY = os.getenv("AETHER_MASTER_KEY", "sk_aether_dev_123")

# DATA MODEL
class ExecutionRequest(BaseModel):
    code: str
    timeout: int = 60

# ENDPOINTS
@app.get("/")
def health_check():
    return {"status": "ONLINE", "system": "AETHER v1.2 (CORS PATCHED)", "location": "Addis Ababa Node"}

@app.post("/v1/execute")
def execute_code(request: ExecutionRequest, x_api_key: str = Header(None)):
    """
    Executes Python code in a secure cloud sandbox.
    """
    # 1. AUTHENTICATION
    if x_api_key != AETHER_MASTER_KEY:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    try:
        logger.info("Spawning Sandbox...")
        
        with Sandbox.create() as sandbox:
            logger.info("Sandbox Active. Running Code...")
            
            execution = sandbox.run_code(request.code)

            output_stdout = "\n".join(execution.logs.stdout)
            output_stderr = "\n".join(execution.logs.stderr)

            return {
                "status": "success",
                "stdout": output_stdout,
                "stderr": output_stderr,
                "sandbox_id": sandbox.sandbox_id
            }

    except Exception as e:
        logger.error(f"Execution Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)