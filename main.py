from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from repositories.AlunoRepo import AlunoRepo
from repositories.ProjetoRepo import ProjetoRepo
from routes.MainRoutes import router as mainRouter
from routes.ProjetoRoutes import router as projetoRouter
from routes.AlunoRoutes import router as alunoRouter
from util.exceptionHandler import configurar as configurarExcecoes

ProjetoRepo.criarTabela()
AlunoRepo.criarTabela()
AlunoRepo.criarUsuarioAdmin()

app = FastAPI()

configurarExcecoes(app)

app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

app.include_router(mainRouter)
app.include_router(projetoRouter)
app.include_router(alunoRouter)

# if __name__ == "__main__":
#     uvicorn.run(app="main:app", reload=True, port=8001)

# TODO: fazer cadastro de foto dos alunos e dos projetos
# TODO: fazer cadastro de algum item 1 para muitos (tags, ou coisa parecida)