# routes/ProjetoRoutes.py
from io import BytesIO
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
from models.Projeto import Projeto
from models.Usuario import Usuario
from repositories.ProjetoRepo import ProjetoRepo
from util.security import validar_usuario_logado
from util.templateFilters import capitalizar_nome_proprio, formatarData
from util.validators import *


router = APIRouter(prefix="/projeto")
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
            projetos = ProjetoRepo.obterPagina(pa, tp)
            totalPaginas = ProjetoRepo.obterQtdePaginas(tp)
            return templates.TemplateResponse(
                "projeto/listagem.html",
                {
                    "request": request,
                    "projetos": projetos,
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
    if usuario:
        if usuario.admin:
            return templates.TemplateResponse(
                "projeto/novo.html", {"request": request, "usuario": usuario}
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/novo")
async def postNovo(
    request: Request,
    nome: str = Form(""),
    descricao: str = Form(""),
    arquivoImagem: UploadFile = File(...),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    if usuario:
        if usuario.admin:
            # normalização de dados
            nome = capitalizar_nome_proprio(nome).strip()
            descricao = descricao.strip()

            # tratamento de erros
            erros = {}
            
            # validação do campo nome
            is_not_empty(nome, "nome", erros)
            is_size_between(nome, "nome", 4, 32, erros)
            is_project_name(nome, "nome", erros)
            
            # validação do campo descricao
            is_not_empty(descricao, "descricao", erros)
            is_size_between(descricao, "descricao", 4, 512, erros)
            
            # validação da imagem
            conteudo_arquivo = await arquivoImagem.read()
            imagem = Image.open(BytesIO(conteudo_arquivo))
            if not imagem:
                add_error("arquivoImagem", "Nenhuma imagem foi enviada.", erros)
            if imagem.width != imagem.height:
                add_error("arquivoImagem", "A imagem precisa ser quadrada.", erros)

            # se tem erro, mostra o formulário novamente
            if len(erros) > 0:
                valores = {}
                valores["nome"] = nome
                valores["descricao"] = descricao
                return templates.TemplateResponse(
                    "projeto/novo.html",
                    {
                        "request": request,
                        "usuario": usuario,
                        "erros": erros,
                        "valores": valores,
                    },
                )

            # grava os dados no banco e redireciona para a listagem
            novo_projeto = ProjetoRepo.inserir(Projeto(0, nome, descricao))
            if (novo_projeto):
                imagem.save(f"static/img/projetos/{novo_projeto.id:04d}.jpg", "JPEG")
            return RedirectResponse(
                "/projeto/listagem", status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/excluir/{id:int}", response_class=HTMLResponse)
async def getExcluir(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    id: int = Path(),
):
    if usuario:
        if usuario.admin:
            projeto = ProjetoRepo.obterPorId(id)
            return templates.TemplateResponse(
                "projeto/excluir.html",
                {"request": request, "usuario": usuario, "projeto": projeto},
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
            if ProjetoRepo.excluir(id):
                return RedirectResponse("/projeto/listagem", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise Exception("Não foi possível excluir o projeto.")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)