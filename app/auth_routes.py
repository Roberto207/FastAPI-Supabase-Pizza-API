#arquivo q tera todas as rotas/ENDPOINTS de autenticação
from fastapi import APIRouter,Depends, HTTPException #criador de roteadores q gerenciam as rotas e o gerenciador de dependencias E o http pra mensagens de erro
from app.models import Usuario#usaremos a tabela do usuario pra buscas e pra isso precisamos do db pra sessoes
from app.dependencias import pegar_sessao,verificar_token #funcao que utiliza das sessoes pra mexer no database e dps fechar a sessao automatica
from app.main import bcrypt_context #importando o contexto de criptografia do main.py
from app.scheamas import UsuarioSchema,LoginSchema,DeleteSchema 
from sqlalchemy.orm import Session #importando o formato sessao usado pra interagir com o database 
from sqlalchemy import delete #deletar coisas da database
from sqlalchemy import select #selecionar coisas da database 
from jose import jwt,JWTError #usado pra criacao de jwts 
from datetime import datetime,timedelta, timezone #usado pra definir tempo de expiracao do token jwt
from app.main import ALGORITMH,ACCESS_TOKEN_EXPIRE_MINUTES,SECRET_KEY
from fastapi.security import OAuth2PasswordRequestForm



auth_router = APIRouter(prefix="/auth",tags=['Authentication']) #criando o roteador de autenticação,precisamos decifinir o prefixo que ficara 
#no link do navegador,na ordem: dominio/auth(prefixo)/outro caminho definido na rota.
#tags = '' serve para agrupar as rotas na doc automatica do fastapi

#funcoes uteis abaixo s


#login --> email e senha --> JWT  
#login é o processo onde alguem ja cadastrado gera um token JWT pra usar o sistema 

def criar_token(usuario_id,duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token # data_expiracao = momento em q o token foi criado + tempo definido na variavel acess token...
    
    dicionario_infos = {"sub" : str(usuario_id),"expiration_date":data_expiracao.timestamp()} #dicionario q fala quais informacoes estarao presentes no jwt,nesse caso id e data_exp 
    
    jwt_codificado = jwt.encode(dicionario_infos,SECRET_KEY,algorithm=ALGORITMH) #a funcao q cria jwts,pede o dicionario com o q sera codificado,a chave de codificacao (secret_key) e o algoritmo de codificacao. tudo isso ja foi criado no env e armazenado no arquivo main
    return jwt_codificado
    




def autentificar_usuario(email,senha,session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first() #vendo se o email inserido pelo usuario esta na database
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha,usuario.senha): #verifica se a senha colocada no login é igual a senha descriptografada presente na database
        return False #se as senhas n coincidirem retorna falso 

    return usuario #so retorna user se passar por tdos os ifs


#rotas abaixo


@auth_router.get('/')  #oq vem no parentesis,sera colocado na frente do prefixo
async def autentificar():
    #docstring explicando a rota,bom pra apis publicas
    """
    Essa é a rota padrao de pedidos do sistema.Todas as rotas de pedidos precisam de autentificacao 
    """
    return {'mensagem' : 'voce acessou a rota padrao de autentificacao','autentificado' : True} #é possivel passar mais de uma informacao no dicionario,aqui mandamos o true q o usuario esta autentificado,claro q nao foi autentificado de vdd mas por enquanto deixamos assim 




#criando rota de criacao de usuario. post no database
@auth_router.post('/criar_conta') #definindo a rota post para registrar/criar usuario
async def criar_conta(usuario_schema: UsuarioSchema,session: Session = Depends(pegar_sessao)): #a funcao recebera email,nome e  senha pra criacao do user. o comando depends fala pro codigo que o parametro session vira das dependencias e nao do usuario como os outros parametros
    # session = sessionmaker(bind=db) #configurando
    # session = session() #abrindo a sessao 
    #esse é o jeito de criar uma sessao sem usar o dependencia.py
    #session.query pra buscar inforamcoes no banco de dados,como na linha abaixo q buscamos pra ver se o email ja existe

    """
    Essa rota é usada para criar um novo usuario no sistema,ela recebe um objeto do tipo UsuarioSchema com as informacoes 
    do usuario a ser criado,verifica se o email ja esta cadastrado e se n estiver,criptografa a senha e salva o novo 
    usuario no database
    """
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first() #vendo se o email ja foi cadastrado
    if usuario:  #se ja existir um usuario com o email
        raise HTTPException(status_code=400,detail="Email ja cadastrado no sistema") #retorna erro 400 de bad request
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha) #criptografando a senha usando o bcrypt_context definido no main.py
        novo_usuario = Usuario(nome=usuario_schema.nome,email=usuario_schema.email,senha=senha_criptografada,ativo=usuario_schema.ativo,admin=usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usuario cadastrado com sucesso {novo_usuario.email}"}





@auth_router.post('/login')
#versao login sem dados formulario que é algo opcional pra termos permissao nas docs do fastapi mas o frontend funciona perfeitamente sem o parametro dados_formulario
async def login(loginschema : LoginSchema ,session: Session = Depends(pegar_sessao)):
    """
    Essa rota é usada para autentificar um usuario ja cadastrado no sistema,ela recebe um objeto do tipo LoginSchema com o
    email e senha do usuario,verifica se as credenciais estao corretas e se estiverem,gera um token JWT de acesso e um 
    token de refresh (opcional) e retorna ambos os tokens para o usuario
    """
    
    
    usuario = autentificar_usuario(email=loginschema.email,senha=loginschema.senha,session=session) #aplicando a funcao 
    
    if not usuario:
        raise HTTPException(status_code=400,detail="email nao encontrado no sistema ou credenciais invalidas")
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id,duracao_token= timedelta(days=7)) #token secundario usado qnd o access token expira pra dar mais tempo ao usaurio e ele n preicsar fazer o login novamente. esse token é opcional
        return {
            "access_token ": access_token,
            "refresh_token":refresh_token,
            "token_type" : "Bearer"
        }


#versao login do formulario q é opcional,frontend funciona sem isso aq,so a de cima 
@auth_router.post('/login_formula')
async def login_formula(dados_formulario : OAuth2PasswordRequestForm = Depends(),session: Session = Depends(pegar_sessao)):
    
    """
    Autentica um usuário já cadastrado utilizando OAuth2PasswordRequestForm.
    Valida email e senha e, se corretos, retorna um token JWT de acesso
    (e opcionalmente um refresh token).

    Essa rota é opcional e existe para facilitar a autenticação via
    documentação automática do FastAPI, funcionando como alternativa
    à rota de login tradicional que utiliza LoginSchema.
    """
    
    
    usuario = autentificar_usuario(dados_formulario.username,dados_formulario.password,session=session) #aplicando a funcao 
    
    if not usuario:
        raise HTTPException(status_code=400,detail="email nao encontrado no sistema ou credenciais invalidas")
    else:
        access_token = criar_token(usuario.id)
        #refresh_token = criar_token(usuario.id,duracao_token= timedelta(days=7)) #token secundario usado qnd o access token expira pra dar mais tempo ao usaurio e ele n preicsar fazer o login novamente. esse token é opcional
        return {
            "access_token": access_token,
            "token_type" : "Bearer"
        }


        
    
    
    
@auth_router.get("/refresh_token")
#toda funcao de endpoint das rotas que tiver como parametro a Depends(verificar_token) sera restrita a usuarios autentificados com token ativo
async def usar_refresh_token(usuario: Usuario = Depends(verificar_token)): #funcao pra usar o refresh token qnd o acess token expira parametros = o parametro usuario tem valor do tipo database Usuario e o seu valor padrao vem da funcao verificar(token) q é uma dependencia
    """
    Rota pra gerar refresh token,ela é acessada quando o access token expira,ela recebe o usuario autenticado atraves do 
    token expirado e gera um novo access token pra ele. O refresh token é opcional e pode ser implementado de acordo com 
    as necessidades do sistema,mas a ideia geral é que ele tenha um tempo de expiração mais longo que o access token e s
    eja usado para gerar novos access tokens sem precisar que o usuário faça login novamente.
    """



    #criando novo token
    access_token = criar_token(usuario.id)
    return {
            "access_token ": access_token,
            "token_type" : "Bearer"
        }






@auth_router.delete("/deletar_usuario")
async def deletar_usuario(
    dados: DeleteSchema,
    db: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    """
    Rota para deletar um usuário do sistema. Ela recebe um objeto do tipo DeleteSchema com o email do usuário a ser deletado,
    uma sessão do banco de dados e o usuário autenticado através do token JWT. A função verifica o nivel de acesso do 
    usuario e executa a funcao
    """
    
    
    
    
    if usuario.admin == False and usuario.email != dados.email:
        raise HTTPException(403, "Voce nao tem permissao para deletar esse usuario")
    stmt = select(Usuario).where(Usuario.email == dados.email)
    usuario = db.execute(stmt).scalar_one_or_none()

    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")

    db.delete(usuario)
    db.commit()

    return {"msg": f"Usuário {dados.email} deletado com sucesso"}
    print('bolas')
