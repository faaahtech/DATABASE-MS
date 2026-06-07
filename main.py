from fastapi import FastAPI, status, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from repositories.postgres_conn import engine, create_db_and_tables
from sqlalchemy import text
from contextlib import asynccontextmanager
from starlette.exceptions import HTTPException as StarletteHTTPException
from routes.auth_routes import router as auth_router
from routes.usuario_routes import router as usuario_router
from routes.aluno_routes import router as aluno_router
from routes.professor_routes import router as professor_router
from routes.curso_unidade_routes import router as curso_unidade_router
from routes.presenca_routes import router as presenca_router
from routes.nota_routes import router as nota_router
from routes.consulta_academica_routes import router as consulta_academica_router
from routes.endereco_routes import router as endereco_router
from routes.curso_routes import router as curso_router
from routes.unidade_routes import router as unidade_router
from routes.disciplina_routes import router as disciplina_router
from routes.periodo_letivo_routes import router as periodo_letivo_router
from routes.matriz_curricular_routes import router as matriz_curricular_router
from routes.oferta_disciplina_routes import router as oferta_disciplina_router
from routes.aula_routes import router as aula_router
from routes.avaliacao_routes import router as avaliacao_router
from routes.matricula_curso_routes import router as matricula_curso_router
from routes.matricula_academica_routes import router as matricula_academica_router
from routes.matricula_disciplina_routes import router as matricula_disciplina_router
from routes.seed_routes import router as seed_router
from routes.calendario_academico_routes import router as calendario_academico_router
from routes.base_conhecimento_routes import router as base_conhecimento_router
from routes.solicitacao_academica_routes import router as solicitacao_academica_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

#set CORS config for deploy

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], 
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)


app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(aluno_router)
app.include_router(professor_router)
app.include_router(curso_unidade_router)
app.include_router(presenca_router)
app.include_router(nota_router)
app.include_router(consulta_academica_router)
app.include_router(endereco_router)
app.include_router(curso_router)
app.include_router(unidade_router)
app.include_router(disciplina_router)
app.include_router(periodo_letivo_router)
app.include_router(matriz_curricular_router)
app.include_router(oferta_disciplina_router)
app.include_router(aula_router)
app.include_router(avaliacao_router)
app.include_router(matricula_curso_router)
app.include_router(matricula_academica_router)
app.include_router(matricula_disciplina_router)
app.include_router(seed_router)
app.include_router(calendario_academico_router)
app.include_router(base_conhecimento_router)
app.include_router(solicitacao_academica_router)


@app.get("/healthcheck")
def healthcheck_database():
    return {"Status": "Online","Service": "API" , "Version": "1.0.0","Current_Time": datetime.today()}


@app.get("/healthcheck/database")
async def healthcheck_database():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {"Status": "Online","Service": "Database", "Version": "1.0.0","Current_Time": datetime.today()}
    except:
        return {"Status": "Offline","Service": "Database" ,"Version": "1.0.0","Current_Time": datetime.today()}

# @app.exception_handler(StarletteHTTPException)
# async def custom_404_handler(request: Request, exc: StarletteHTTPException):
#     if exc.status_code == 404:
#         # Redirect to your home page or any specific route
#         return RedirectResponse(url="/healthcheck", status_code=status.HTTP_303_SEE_OTHER)
