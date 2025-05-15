from fastapi import FastAPI, Form, Request
from pathlib import Path
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.tennisapi import Platzbuchung
from ai.api.model import Model
from fastapi.templating import Jinja2Templates
from api.gmail import gmailAPI

from pydantic import BaseModel
import logging.config
import yaml
import json


# setup logging from config file
with open("logging_config.yaml", 'r') as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)


# setup logger for this file
LOGGER = logging.getLogger(__name__)

# initalize fastapi
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# mount static files (contains css and js files)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

# log
LOGGER.info("FastAPI successfully initalized")

# initlaize booking API wrapper
platzbuchung = Platzbuchung()

# log
LOGGER.info("Platzbuchung API successfully initalized")

# initalize AI model
model = Model()

# log
LOGGER.info("Finetuned llama 3.2 3B model successfully initalized")

# Initialize Gmail API
gmail_api = gmailAPI()

class User(BaseModel):
    firstname: str
    secondname: str
    password: str


class bookingObj(BaseModel):
    court: int
    startDate: str
    duration: int
    category: str


class AiRequest(BaseModel):
    content: str


class ActionRequest(BaseModel):
    category: str
    username: str


@app.get("/")
async def root():
    try:
        with open(BASE_DIR / "template" / "index.html") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("Template not found", status_code=404)
    

@app.get("/users")  # Changed from "/users.html" to "/users"
async def users():
    try:
        with open(BASE_DIR / "template" / "users.html") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("Template not found", status_code=404)
    

@app.get("/booking")
async def booking():
    try:
        with open(BASE_DIR / "template" / "recurrentBooking.html") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("Template not found", status_code=404)
    
@app.post("/recurrentBook", response_class=JSONResponse)
async def recurrentBooking(bookingObj: bookingObj):
    try:
        
        return JSONResponse(content={'success': True, 'message': 'success'})
    except Exception as e:
        return JSONResponse(content={'success': False, 'message': str(e)})

@app.post("/addUser", response_class=JSONResponse)
async def addUser(user: User):
    try:
        platzbuchung.addUser(vorname=user.firstname, nachname=user.secondname, psswd=user.password)
        return JSONResponse(content={'success': True, 'message': 'success'})
    except Exception as e:
        return JSONResponse(content={'success': False, 'message': str(e)})
    
@app.post("/analyze", response_class=JSONResponse)
async def analyze(req: AiRequest):
    try:
        return JSONResponse(content={**{'success': True, 'message': 'success'}, **model.generate_response(req.content)})
    except Exception as e:
        return JSONResponse(content={'success': False, 'message': str(e)})


@app.post("/execute-action", response_class=JSONResponse)
async def execute_action(req: ActionRequest):
    try:
        LOGGER.info(f"Executing action: {req.category} for user: {req.username}")
        
        if req.category == "Benutzer anlegen":
            names = req.username.split(sep=".")
            platzbuchung.addUser(vorname=names[0], nachname=names[1], psswd="tsv-etting#1234")  # TODO change for deployment

        elif req.category == "Password zurücksetzen":  # Made that typo in the training data so I gotta live with it
            names = req.username.split(sep=".")
            platzbuchung.resetPassword(username=req.username, pswd="tsv-etting#1234")  # TODO change for deployment

        elif req.category == "Sonstiges":
            pass
        else:
            LOGGER.info(f"Model classified invalid operation, name: {req.category}")
        
        return JSONResponse(content={
            'success': True, 
            'message': f'Successfully executed {req.category} for {req.username}'
        })
    except Exception as e:
        LOGGER.error(f"Error executing action: {str(e)}")
        return JSONResponse(content={'success': False, 'message': str(e)})


@app.get("/jobs", response_class=HTMLResponse)
async def getJobs():
    try:
        with open(BASE_DIR / "template" / "jobs.html") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("Template not found", status_code=404)

@app.get("/api/emails", response_class=JSONResponse)
async def get_emails():
    try:
        emails = gmail_api.fetch()
        return JSONResponse(content={'success': True, 'emails': emails})
    except Exception as e:
        LOGGER.error(f"Error fetching emails: {str(e)}")
        return JSONResponse(content={'success': False, 'message': str(e)})

@app.post("/api/analyze-email", response_class=JSONResponse)
async def analyze_email(req: AiRequest):
    try:
        analysis_result = model.generate_response(req.content)
        return JSONResponse(content={**{'success': True, 'message': 'success'}, **analysis_result})
    except Exception as e:
        LOGGER.error(f"Error analyzing email: {str(e)}")
        return JSONResponse(content={'success': False, 'message': str(e)})