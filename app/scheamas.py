#arquvio pra estruturas,muito parecido com oq temos no modelo,os schemas servem pra definir / padronizar como os dados serao enviados e recebidos pela API
#os parametros usados nas rotas vao ser validados com base nesses schemas
from pydantic import BaseModel,validator
from typing import Optional
from sqlalchemy import DateTime
from datetime import datetime
from enum import Enum #pra "choicetype"
from decimal import Decimal # pra dinheiro 

class UsuarioSchema(BaseModel):
    email: str #os dois pontos : sao usados pra definir o tipo e nao atribuir valores 
    senha: str
    nome: str
    ativo: Optional[bool] = True
    admin: Optional[bool] = False

    class Config:
        from_attributes = True #pra converter automaticamente os modelos do sqlalchemy em pydantic modelos

class PedidoSchema(BaseModel): # so passar aqui dentro oq for fornecido pelo usuario
    usuario_id : int 
    
    


    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email : str
    senha : str

    class Config:
        from_attributes = True

class DeleteSchema(BaseModel):
    email: str

    class Config:
        from_attributes = True


class TamanhoItemSchema(str,Enum):
    P = "P"
    M = "M"
    G = "G"
    GG = "GG"

class SaborItemSchema(str,Enum):
    CALABRESA = "CALABRESA"
    MARGUERITA = "MARGUERITA"
    PORTUGUESA = "PORTUGUESA"
    FRANGO = "FRANGO"
    ATUM = "ATUM"
    VEGETARIANA = "VEGETARIANA"



class ItemPedidoschema(BaseModel):
    quantidade : int
    sabor: SaborItemSchema
    tamanho : TamanhoItemSchema
    preco_unitario : Decimal

    @validator('sabor', pre=True)
    def upper_sabor(cls, v):
        return v.upper()

    @validator('tamanho', pre=True)
    def upper_tamanho(cls, v):
        return v.upper()

    class Config:
        from_attributes = True




# class StatusPedido(str,Enum):
#     PENDENTE = "PENDENTE"
#     CANCELADO = "CANCELADO"
#     FINALIZADO = "FINALIZADO"




#antes so fizemos schemas pra usuarios inserirem os dados,agora vamos criar um schema pra resposta da API,ou seja, a padronizacao em que a API vai retornar para o cliente apos uma requisição,nesse caso,quando o cliente fizer um pedido,ele vai receber uma resposta com os detalhes do pedido,como os itens e o valor total
class RespostaPedidoSchema(BaseModel):
    id : int
    usuario_id : int
    status : str
    #preco : float
    preco : Decimal
    itens : list[ItemPedidoschema]
    #criado_em : datetime = None

    class Config:
        from_attributes = True
    
    

