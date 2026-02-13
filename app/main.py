from fastapi import FastAPI
from passlib.context import CryptContext #cryptografia de senhas
from dotenv import load_dotenv #isso é pra importar a variavel de ambiente do arquivo .env  q tem a secret key da criptografia
import os
from fastapi.security import OAuth2PasswordBearer
from app.database import base, engine


#comando pra rodar o servidor: uvicorn main:app --reload (rodar no terminal)(roda a variavel app do arquivo 
# main(nome do arquvio onde criamoso projeto,pode ser outro)) num servidor uvicorn
#usuario de teste : email:"boludo@gmail.com", "senha": "123456"
 

load_dotenv() #carregando as variaveis de ambiente do arquivo .env

SECRET_KEY = os.getenv("SECRET_KEY") #pegando a secret key do .env pra usar na criptografia
ALGORITMH = os.getenv("ALGORITMH") 
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


app = FastAPI() #so esse comando ja cria uma aba fastapi mas vazia 
#so importar as rotas dps de criar o app 

base.metadata.create_all(bind=engine) #criando as tabelas do banco de dados,ou seja, criando a estrutura do banco de dados,com base nas classes criadas no models.py,ou seja, as tabelas do banco de dados serao criadas com base nessas classes



bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #configurando o esquema de criptografia.
#definimos o esquema de cryptografia como bcrypt e deprecated auto pra n usar esquemas antigos

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login_formula")


from app.auth_routes import auth_router #router = roteador
from app.orders_routes import order_router

app.include_router(auth_router) #incluindo as rotas de autenticação no app fastapi
app.include_router(order_router) #incluindo as rotas de ordens no app fast

#para olhar as rotas na pagina do app,é preciso usar o comadno uvicorn no terminal pra criar o servidor
#e depois ir no navegador no link e colocar /docs no final do link 
