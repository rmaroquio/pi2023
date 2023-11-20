# repositories/ProjetoRepo.py
from typing import List
from models.Projeto import Projeto
from util.Database import Database

class ProjetoRepo:
    @classmethod
    def criarTabela(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS projeto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL)
        """
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        tableCreated = (cursor.execute(sql).rowcount > 0)
        conexao.commit()
        conexao.close()
        return tableCreated
    
    @classmethod
    def inserir(cls, projeto: Projeto) -> Projeto:        
        sql = "INSERT INTO projeto (nome, descricao) VALUES (?, ?)"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (projeto.nome, projeto.descricao))
        if (resultado.rowcount > 0):            
            projeto.id = resultado.lastrowid
        conexao.commit()
        conexao.close()
        return projeto
    
    @classmethod
    def alterar(cls, projeto: Projeto) -> Projeto:
        sql = "UPDATE projeto SET nome=?, descricao=? WHERE id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (projeto.nome, projeto.descricao, projeto.id))
        if (resultado.rowcount > 0):            
            conexao.commit()
            conexao.close()
            return projeto
        else: 
            conexao.close()
            return None
        
    @classmethod
    def excluir(cls, id: int) -> bool:
        sql = "DELETE FROM projeto WHERE id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (id, ))
        if (resultado.rowcount > 0):
            conexao.commit()
            conexao.close()
            return True
        else: 
            conexao.close()
            return False
        
    @classmethod
    def obterTodos(cls) -> List[Projeto]:
        sql = "SELECT id, nome, descricao FROM projeto ORDER BY nome"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql).fetchall()
        objetos = [Projeto(*x) for x in resultado]
        return objetos
    
    @classmethod
    def obterTodosParaSelect(cls) -> List[Projeto]:
        sql = "SELECT id, nome FROM projeto ORDER BY nome"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql).fetchall()
        objetos = [Projeto(id=x[0], nome=x[1]) for x in resultado]
        return objetos
    
    @classmethod
    def obterPagina(cls, pagina: int, tamanhoPagina: int) -> List[Projeto]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT id, nome, descricao FROM projeto ORDER BY nome LIMIT ?, ?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [Projeto(*x) for x in resultado]
        return objetos
    
    @classmethod
    def obterQtdePaginas(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM projeto) AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina, )).fetchone()
        return int(resultado[0])
    
    @classmethod
    def obterPorId(cls, id: int) -> Projeto:
        sql = "SELECT id, nome, descricao FROM projeto WHERE id=?"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (id, )).fetchone()
        objeto = Projeto(*resultado)
        return objeto
        
    @classmethod
    def obterIntegrantes(cls, id: int) -> List[str]:
        sql = "SELECT nome FROM aluno WHERE idProjeto=? and aprovado=1 ORDER BY nome"
        conexao = Database.criarConexao()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (id, )).fetchall()        
        if resultado:            
            return [x[0] for x in resultado]
        else:
            return []            