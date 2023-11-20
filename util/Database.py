# util/Database.py
import sqlite3

class Database:
    @classmethod
    def criarConexao(cls):
        conexao = sqlite3.connect("dados.db")
        return conexao