# routes/MainRoutes.py
from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Usuario import Usuario
from repositories.AlunoRepo import AlunoRepo
from repositories.ProjetoRepo import ProjetoRepo
from util.security import (
    gerar_token,    
    validar_usuario_logado,
    verificar_senha,
)
from util.templateFilters import formatarData, formatarIdParaImagem
from util.validators import *


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData
    templates.env.filters["id_img"] = formatarIdParaImagem


@router.get("/")
async def getIndex(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    projetos = ProjetoRepo.obterTodos()    
    for projeto in projetos:
        projeto.integrantes = ProjetoRepo.obterIntegrantes(projeto.id)
    return templates.TemplateResponse(
        "main/index.html", {"request": request, "usuario": usuario, "projetos": projetos}
    )


@router.get("/login")
async def getLogin(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    return templates.TemplateResponse(
        "main/login.html", {"request": request, "usuario": usuario}
    )


@router.post("/login")
async def postLogin(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    email: str = Form(""),
    senha: str = Form(""),
    returnUrl: str = Query("/"),
):
    # normalização de dados
    email = email.strip().lower()
    senha = senha.strip()
    
    # validação de dados
    erros = {}
    # validação do campo email
    is_not_empty(email, "email", erros)
    is_email(email, "email", erros)
    # validação do campo senha
    is_not_empty(senha, "senha", erros)
        
    # só checa a senha no BD se os dados forem válidos
    if len(erros) == 0:
        hash_senha_bd = AlunoRepo.obterSenhaDeEmail(email)
        if hash_senha_bd:
            if verificar_senha(senha, hash_senha_bd):
                token = gerar_token()
                if AlunoRepo.alterarToken(email, token):
                    response = RedirectResponse(returnUrl, status.HTTP_302_FOUND)
                    response.set_cookie(
                        key="auth_token", value=token, max_age=1800, httponly=True
                    )
                    return response
                else:
                    raise Exception(
                        "Não foi possível alterar o token do usuário no banco de dados."
                    )
            else:            
                add_error("senha", "Senha não confere.", erros)
        else:
            add_error("email", "Usuário não cadastrado.", erros)

    # se tem algum erro, mostra o formulário novamente
    if len(erros) > 0:
        valores = {}
        valores["email"] = email        
        return templates.TemplateResponse(
            "main/login.html",
            {
                "request": request,
                "usuario": usuario,
                "erros": erros,
                "valores": valores,
            },
        )

@router.get("/logout")
async def getLogout(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):   
    if (usuario):
        AlunoRepo.alterarToken(usuario.email, "") 
    response = RedirectResponse("/", status.HTTP_302_FOUND)
    response.set_cookie(
        key="auth_token", value="", httponly=True, expires="1970-01-01T00:00:00Z"
    )    
    return response
