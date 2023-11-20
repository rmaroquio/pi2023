# routes/ProjetoRoutes.py
from fastapi import APIRouter, Depends, Form, Path, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Aluno import Aluno
from models.Usuario import Usuario
from repositories.AlunoRepo import AlunoRepo
from repositories.ProjetoRepo import ProjetoRepo
from util.security import obter_hash_senha, validar_usuario_logado, verificar_senha
from util.templateFilters import capitalizar_nome_proprio, formatarData
from util.validators import *


router = APIRouter(prefix="/aluno")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData


@router.get("/listagem", response_class=HTMLResponse)
async def getListagem(
    request: Request,
    pa: int = 1,
    tp: int = 6,
    usuario: Usuario = Depends(validar_usuario_logado),
):
    if usuario:
        if usuario.admin:
            alunos = AlunoRepo.obterPagina(pa, tp)
            totalPaginas = AlunoRepo.obterQtdePaginas(tp)
            qtdeAprovar = AlunoRepo.obterQtdeAprovar()
            return templates.TemplateResponse(
                "aluno/listagem.html",
                {
                    "request": request,
                    "alunos": alunos,
                    "totalPaginas": totalPaginas,
                    "paginaAtual": pa,
                    "tamanhoPagina": tp,
                    "usuario": usuario,
                    "qtdeAprovar": qtdeAprovar,
                },
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/aprovar/{id:int}", response_class=HTMLResponse)
async def getAprovar(
    request: Request,
    id: int,
    usuario: Usuario = Depends(validar_usuario_logado),
):
    if usuario:
        if usuario.admin:
            return JSONResponse({"ok": AlunoRepo.aprovarCadastro(id)})
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/desaprovar/{id:int}", response_class=HTMLResponse)
async def getDesaprovar(
    request: Request,
    id: int,
    usuario: Usuario = Depends(validar_usuario_logado),
):
    if usuario:
        if usuario.admin:
            return JSONResponse({"ok": AlunoRepo.aprovarCadastro(id, False)})
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/aprovar", response_class=HTMLResponse)
async def getAprovar(
    request: Request,
    pa: int = 1,
    tp: int = 6,
    usuario: Usuario = Depends(validar_usuario_logado),
):
    if usuario:
        if usuario.admin:
            alunos = AlunoRepo.obterPaginaAprovar(pa, tp)
            totalPaginas = AlunoRepo.obterQtdePaginasAprovar(tp)
            return templates.TemplateResponse(
                "aluno/aprovar.html",
                {
                    "request": request,
                    "alunos": alunos,
                    "totalPaginas": totalPaginas,
                    "paginaAtual": pa,
                    "tamanhoPagina": tp,
                    "usuario": usuario,
                },
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/novo", response_class=HTMLResponse)
async def getNovo(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    projetos = ProjetoRepo.obterTodosParaSelect()
    return templates.TemplateResponse(
        "aluno/novo.html",
        {"request": request, "usuario": usuario, "projetos": projetos},
    )


@router.post("/novo_json")
async def postNovoJson(
    nome: str = Form(
        ..., min_length=3, max_length=50, regex=r"^((\b[A-zÀ-ú']{2,40}\b)\s*){2,}$"
    ),
    email: str = Form(
        ...,
        regex=r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    ),
    senha: str = Form(..., min_length=6, max_length=20),
    confSenha: str = Form(..., min_length=6, max_length=20),
    idProjeto: int = Form(..., gt=0),
):
    if senha.strip() != confSenha.strip():
        listaErros = []
        listaErros.append(
            {
                "type": "field_dont_match",
                "loc": ("body", "senha"),
                "msg": "Senhas não conferem.",
            }
        )
        listaErros.append(
            {
                "type": "field_dont_match",
                "loc": ("body", "confSenha"),
                "msg": "Senhas não conferem.",
            }
        )
        raise RequestValidationError(listaErros)
    AlunoRepo.inserir(
        Aluno(
            id=0,
            nome=nome.strip(),
            email=email.strip(),
            senha=senha.strip(),
            idProjeto=idProjeto,
        )
    )
    return JSONResponse({"ok": True, "returnUrl": "/"}, status_code=status.HTTP_200_OK)


@router.post("/novo")
async def postNovo(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    nome: str = Form(""),
    email: str = Form(""),
    senha: str = Form(""),
    confSenha: str = Form(""),
    idProjeto: int = Form(0),
):
    # normalização dos dados
    nome = capitalizar_nome_proprio(nome).strip()
    email = email.lower().strip()
    senha = senha.strip()
    confSenha = confSenha.strip()

    # verificação de erros
    erros = {}
    # validação do campo nome
    is_not_empty(nome, "nome", erros)
    is_person_fullname(nome, "nome", erros)
    # validação do campo email
    is_not_empty(email, "email", erros)
    if is_email(email, "email", erros):
        if AlunoRepo.emailExiste(email):
            add_error("email", "Já existe um aluno cadastrado com este e-mail.", erros)
    # validação do campo senha
    is_not_empty(senha, "senha", erros)
    is_password(senha, "senha", erros)
    # validação do campo confSenha
    is_not_empty(confSenha, "confSenha", erros)
    is_matching_fields(confSenha, "confSenha", senha, "Senha", erros)
    # validação do campo idProjeto
    is_selected_id_valid(idProjeto, "idProjeto", erros)

    # se tem erro, mostra o formulário novamente
    if len(erros) > 0:
        valores = {}
        valores["nome"] = nome
        valores["email"] = email.lower()
        valores["idProjeto"] = idProjeto
        projetos = ProjetoRepo.obterTodosParaSelect()
        return templates.TemplateResponse(
            "aluno/novo.html",
            {
                "request": request,
                "usuario": usuario,
                "projetos": projetos,
                "erros": erros,
                "valores": valores,
            },
        )

    # inserção no banco de dados
    AlunoRepo.inserir(
        Aluno(
            id=0,
            nome=nome,
            email=email,
            senha=obter_hash_senha(senha),
            idProjeto=idProjeto,
        )
    )

    # mostra página de sucesso
    return templates.TemplateResponse(
        "aluno/cadastrado.html",
        {"request": request, "usuario": usuario},
    )


@router.get("/excluir/{id:int}", response_class=HTMLResponse)
async def getExcluir(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    id: int = Path(),
):
    if usuario:
        if usuario.admin:
            aluno = AlunoRepo.obterPorId(id)
            return templates.TemplateResponse(
                "aluno/excluir.html",
                {"request": request, "usuario": usuario, "aluno": aluno},
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/excluir", response_class=HTMLResponse)
async def postExcluir(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    id: int = Form(0),
):
    if usuario:
        if usuario.admin:
            if AlunoRepo.excluir(id):
                return RedirectResponse(
                    "/aluno/listagem", status_code=status.HTTP_303_SEE_OTHER
                )
            else:
                raise Exception("Não foi possível excluir o aluno.")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/dashboard", response_class=HTMLResponse)
async def getDashboard(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    if usuario:
        aluno = AlunoRepo.obterPorId(usuario.id)
        if aluno:
            return templates.TemplateResponse(
                "aluno/dashboard.html",
                {"request": request, "usuario": usuario, "aluno": aluno},
            )
        else:
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/alterarsenha", response_class=HTMLResponse)
async def getAlterarSenha(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    if usuario:
        return templates.TemplateResponse(
            "aluno/alterarsenha.html", {"request": request, "usuario": usuario}
        )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/alterarsenha", response_class=HTMLResponse)
async def postAlterarSenha(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    senhaAtual: str = Form(""),
    novaSenha: str = Form(""),
    confNovaSenha: str = Form(""),    
):
    # normalização dos dados
    senhaAtual = senhaAtual.strip()
    novaSenha = novaSenha.strip()
    confNovaSenha = confNovaSenha.strip()    

    # verificação de erros
    erros = {}
    # validação do campo senhaAtual
    is_not_empty(senhaAtual, "senhaAtual", erros)
    is_password(senhaAtual, "senhaAtual", erros)    
    # validação do campo novaSenha
    is_not_empty(novaSenha, "novaSenha", erros)
    is_password(novaSenha, "novaSenha", erros)
    # validação do campo confNovaSenha
    is_not_empty(confNovaSenha, "confNovaSenha", erros)
    is_matching_fields(confNovaSenha, "confNovaSenha", novaSenha, "Nova Senha", erros)
    
    # só verifica a senha no banco de dados se não houverem erros de validação
    if len(erros) == 0:    
        hash_senha_bd = AlunoRepo.obterSenhaDeEmail(usuario.email)
        if hash_senha_bd:
            if not verificar_senha(senhaAtual, hash_senha_bd):            
                add_error("senhaAtual", "Senha atual está incorreta.", erros)
    
    # se tem erro, mostra o formulário novamente
    if len(erros) > 0:
        valores = {}        
        return templates.TemplateResponse(
            "aluno/alterarsenha.html",
            {
                "request": request,
                "usuario": usuario,                
                "erros": erros,
                "valores": valores,
            },
        )

    # se passou pelas validações, altera a senha no banco de dados
    hash_nova_senha = obter_hash_senha(novaSenha)
    AlunoRepo.alterarSenha(usuario.id, hash_nova_senha)
    
    # mostra página de sucesso
    return templates.TemplateResponse(
        "aluno/alterousenha.html",
        {"request": request, "usuario": usuario},
    )
    
    # TODO: Não está mostrando mensagens de erros nos campos do formulário