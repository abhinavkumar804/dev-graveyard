from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import engine, Base, get_db
from app.models import Project

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dev Graveyard")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"projects": projects}
    )

@app.get("/search", response_class=HTMLResponse)
def search_projects(request: Request, q: str = "", db: Session = Depends(get_db)):
    query = db.query(Project)
    if q:
        query = query.filter(
            or_(
                Project.title.ilike(f"%{q}%"),
                Project.description.ilike(f"%{q}%"),
                Project.tech_stack.ilike(f"%{q}%")
            )
        )
    projects = query.order_by(Project.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request, 
        name="partials/project_cards.html", 
        context={"projects": projects}
    )

@app.get("/projects/new", response_class=HTMLResponse)
def new_project_form(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="create.html"
    )

@app.post("/projects", response_class=HTMLResponse)
def create_project(
    title: str = Form(...),
    description: str = Form(...),
    tech_stack: str = Form(...),
    repo_url: str = Form(""),
    db: Session = Depends(get_db)
):
    project = Project(
        title=title,
        description=description,
        tech_stack=tech_stack,
        repo_url=repo_url,
        status="Orphaned"
    )
    db.add(project)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/projects/{project_id}/adopt", response_class=HTMLResponse)
def adopt_project(
    request: Request,
    project_id: int,
    adopter_name: str = Form("Anonymous"),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        project.status = "Adopted"
        project.adopter_name = adopter_name
        db.commit()
        db.refresh(project)
    
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request, 
        name="partials/project_cards.html", 
        context={"projects": projects}
    )