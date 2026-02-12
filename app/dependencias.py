from models import Usuario #usaremos a tabela do usuario pra buscas e pra isso precisamos do db pra sessoes
from sqlalchemy.orm import sessionmaker,Session
from fastapi import Depends,HTTPException 
from jose import jwt,JWTError #pra decodificacao na  funcao de verificar token 
from main import SECRET_KEY,ALGORITMH,oauth2_schema
import logging
from database import SessionLocal
#IMPORTANTE = DEPENDENCIAS TEM Q SER USADAS COMO PARAMETROS DE FUNCOES E NAO PODEM SER USADAS DENTRO DELAS  

def pegar_sessao(): #funcao que permite fazer alteracoes no banco de dados,toda rota que for fazer uma adicao,mudanca ou remocao no database,precisa dessa funcao como parametro
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




#funcao que restringe o uso dos endpoints a usuarios autentificados 
#toda funcao de endpoint das rotas que tiver como parametro a Depends(verificar_token) sera restrita a usuarios autentificados com token ativo
def verificar_token(token: str = Depends(oauth2_schema),session: Session = Depends(pegar_sessao)):

    try:
        dict_info = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITMH])
        

        id_usuario = int(dict_info.get("sub"))
        if not id_usuario:
            raise HTTPException(status_code=401, detail="Token sem sub = ids")
    except JWTError as erro:
        print(erro)
        raise HTTPException(status_code=401,detail="acesso negado,verifique a validade do token")
        

    #verificar se o token é valido
    #extrair o id do usuario do token 
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401,detail="acesso invalido")
    return usuario