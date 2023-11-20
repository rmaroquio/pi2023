# models/Aluno.py
from dataclasses import dataclass


@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    admin: bool = False
