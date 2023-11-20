# repositories/AlunoRepo.py
from typing import List
from models.Aluno import Aluno
from models.Usuario import Usuario
from util.Database import Database


class AlunoRepo:
    @classmethod
    def criarTabela(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS aluno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            senha TEXT NOT NULL,
            token TEXT,
            admin BOOLEAN NOT NULL DEFAULT 0,
            aprovado BOOLEAN NOT NULL DEFAULT 0,            
            dataCadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            idProjeto INTEGER,
            UNIQUE (email),
            CONSTRAINT fkAlunoProjeto FOREIGN KEY(idProjeto) REFERENCES projeto(id))
        """
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        tableCreated = cursor.execute(sql).rowcount > 0
        conexao.commit()
        conexao.close()
        return tableCreated

    @classmethod
    def criarUsuarioAdmin(cls) -> bool:
        sql = "INSERT OR IGNORE INTO aluno (nome, email, senha, admin) VALUES (?, ?, ?, ?)"
        # hash da senha 123456
        hash_senha = "$2b$12$WU9pnIyBUZOJHN7hgkhWtew8hI0Keiobr8idjIxYDwCyiSb5zh0iq"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(
            sql, ("Administrador do Sistema", "admin@email.com", hash_senha, True)
        )
        if resultado.rowcount > 0:
            conexao.commit()
            conexao.close()
            return True
        else:
            conexao.close()
            return False

    @classmethod
    def inserir(cls, aluno: Aluno) -> Aluno:
        sql = "INSERT INTO aluno (nome, email, senha, idProjeto) VALUES (?, ?, ?, ?)"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(
            sql, (aluno.nome, aluno.email, aluno.senha, aluno.idProjeto)
        )
        if resultado.rowcount > 0:
            aluno.id = resultado.lastrowid
        conexao.commit()
        conexao.close()
        return aluno

    @classmethod
    def alterar(cls, aluno: Aluno) -> Aluno:
        sql = "UPDATE aluno SET nome=?, aluno.email=?, idProjeto=? WHERE id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (aluno.nome, aluno.idProjeto, aluno.id))
        if resultado.rowcount > 0:
            conexao.commit()
            conexao.close()
            return aluno
        else:
            conexao.close()
            return None

    @classmethod
    def alterarSenha(cls, id: int, senha: str) -> bool:
        sql = "UPDATE aluno SET senha=? WHERE id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (senha, id))
        if resultado.rowcount > 0:
            conexao.commit()
            conexao.close()
            return True
        else:
            conexao.close()
            return False

    @classmethod
    def alterarToken(cls, email: str, token: str) -> bool:
        sql = "UPDATE aluno SET token=? WHERE email=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (token, email))
        if resultado.rowcount > 0:
            conexao.commit()
            conexao.close()
            return True
        else:
            conexao.close()
            return False

    @classmethod
    def alterarAdmin(cls, id: int, admin: bool) -> bool:
        sql = "UPDATE aluno SET admin=? WHERE id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (admin, id))
        if resultado.rowcount > 0:
            conexao.commit()
            conexao.close()
            return True
        else:
            conexao.close()
            return False

    @classmethod
    def aprovarCadastro(cls, id: int, aprovar: bool = True) -> bool:
        sql = "UPDATE aluno SET aprovado=? WHERE id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (aprovar, id))
        if resultado.rowcount > 0:
            conexao.commit()
            conexao.close()
            return True
        else:
            conexao.close()
            return False

    @classmethod
    def emailExiste(cls, email: str) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM aluno WHERE email=?)"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (email,)).fetchone()        
        return bool(resultado[0])

    @classmethod
    def obterSenhaDeEmail(cls, email: str) -> str | None:
        sql = "SELECT senha FROM aluno WHERE email=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (email,)).fetchone()
        if resultado:
            return str(resultado[0])
        else:
            return None

    @classmethod
    def excluir(cls, id: int) -> bool:
        sql = "DELETE FROM aluno WHERE id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (id,))
        if resultado.rowcount > 0:
            conexao.commit()
            conexao.close()
            return True
        else:
            conexao.close()
            return False

    @classmethod
    def obterTodos(cls) -> List[Aluno]:
        sql = "SELECT aluno.id, aluno.nome, aluno.email, aluno.admin, aluno.idProjeto, projeto.nome AS nomeProjeto FROM aluno INNER JOIN projeto ON aluno.idProjeto = projeto.id ORDER BY aluno.nome"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql).fetchall()
        objetos = [
            Aluno(
                id=x[0],
                nome=x[1],
                email=x[2],
                admin=x[3],
                idProjeto=x[4],
                nomeProjeto=x[5],
            )
            for x in resultado
        ]
        return objetos

    @classmethod
    def obterPagina(cls, pagina: int, tamanhoPagina: int) -> List[Aluno]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT aluno.id, aluno.nome, aluno.email, aluno.admin, aluno.idProjeto, projeto.nome AS nomeProjeto FROM aluno INNER JOIN projeto ON aluno.idProjeto = projeto.id WHERE aluno.aprovado = 1 ORDER BY aluno.nome LIMIT ?, ?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [
            Aluno(
                id=x[0],
                nome=x[1],
                email=x[2],
                admin=x[3],
                idProjeto=x[4],
                nomeProjeto=x[5],
            )
            for x in resultado
        ]
        return objetos

    @classmethod
    def obterQtdePaginas(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM aluno WHERE aprovado = 1 AND idProjeto IS NOT NULL) AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina,)).fetchone()
        return int(resultado[0])

    @classmethod
    def obterPaginaAprovar(cls, pagina: int, tamanhoPagina: int) -> List[Aluno]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT aluno.id, aluno.nome, aluno.email, aluno.admin, aluno.idProjeto, projeto.nome AS nomeProjeto FROM aluno INNER JOIN projeto ON aluno.idProjeto = projeto.id WHERE aluno.aprovado = 0 ORDER BY aluno.dataCadastro LIMIT ?, ?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [
            Aluno(
                id=x[0],
                nome=x[1],
                email=x[2],
                admin=x[3],
                idProjeto=x[4],
                nomeProjeto=x[5],
            )
            for x in resultado
        ]
        return objetos

    @classmethod
    def obterQtdePaginasAprovar(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM aluno WHERE aprovado = 0 AND idProjeto IS NOT NULL) AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina,)).fetchone()
        return int(resultado[0])

    @classmethod
    def obterQtdeAprovar(cls) -> int:
        sql = "SELECT COUNT(*) FROM aluno WHERE aprovado = 0 AND idProjeto IS NOT NULL"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql).fetchone()
        return int(resultado[0])

    @classmethod
    def obterPorId(cls, id: int) -> Aluno | None:
        sql = "SELECT aluno.id, aluno.nome, aluno.email, aluno.admin, aluno.aprovado, aluno.idProjeto, projeto.nome AS nomeProjeto FROM aluno INNER JOIN projeto ON aluno.idProjeto = projeto.id WHERE aluno.id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (id,)).fetchone()
        if (resultado):
            objeto = Aluno(
                id=resultado[0],
                nome=resultado[1],
                email=resultado[2],
                admin=resultado[3],
                aprovado=resultado[4],
                idProjeto=resultado[5],
                nomeProjeto=resultado[6],
            )
            return objeto
        else: 
            return None

    @classmethod
    def obterUsuarioPorToken(cls, token: str) -> Usuario:
        sql = "SELECT id, nome, email, admin FROM aluno WHERE token=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        # quando se executa fechone em um cursor sem resultado, ele retorna None
        resultado = cursor.execute(sql, (token,)).fetchone()
        if resultado:
            objeto = Usuario(*resultado)
            return objeto
        else:
            return None
