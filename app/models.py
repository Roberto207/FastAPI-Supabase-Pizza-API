#aqui criamos as classes do banco de dados pra dps criar um banco de dados com essas classes
#essse arquivo é o passo a passo q sempre deve ser feito com sql alchemy 
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, ForeignKey, DateTime,Enum
from sqlalchemy.orm import declarative_base,relationship
from datetime import datetime
from sqlalchemy import Numeric
from decimal import Decimal


#from sqlalchemy_utils import ChoiceType 


import alembic #biblioteca usada pra fazer migracoes do banco de dados = adicionar coisas novas ao database,sem ter q apagalo e refazelo
#se rodamos o comando alembic init alembic no terminal,ele cria pastas e um arquivo alembic.ini onde colocamos o link do nosso datavase q é o q esta contido na variavel db = create_engine(link)
#e colocamos esse link no arquivo,na linha 'script location'

#comando pra migracao alembic revision --autogenerate -m "nome_migracao"
#e pra finalizar/atualizar use alembic upgrade head



#cria a conexao com o seu banco 
#db = create_engine('sqlite:///banco.db') #criando o banco de dados sqlite,dentro do parenteses colocamos o link do banco de dados,se estiver
#na nuvem da amazon por exemplo usariamos o link do banco de dados la
#como estamos usando sqlite,que é um banco de dados local,usamos o comando abaixo
#esse comando criara o arquivo local com o banco de dados chamado banco.db

#cria a base de dados para as classes
#base = declarative_base() #criando a base de dados,ou seja,as classes q criarmos dps serao baseadas nessa base

#criar as classes que serao as tabelas do banco de dados,q imaginando uma api de delivery de pizzaria,seriam esses:
#usuarios (teremos usuarios administradores e nao adms,é possivel tambem ter outros niveis de usuarios)




from sqlalchemy import Column, Integer, String
from database import base #importando a base do database pra criar as classes do banco de dados,ou seja, as tabelas do banco de dados
base = base #definindo a base como a base importada do database,ou seja, as classes criadas aqui serao baseadas nessa base de dados

class Usuario(base): #a classe usuario roda na base e é uma subclasse da classe base que na vdd é uma base de dados e o usuario é a tabelka 
    
    __tablename__ = 'usuarios' #definindo o nome da tabela 
    #tudo que quisermos que um usuario tenha,colocamos aqui,cada campo aqui vai ser uma coluna do sqlalchemy e os valores delas sao importados anteriormente (ex: nome é uma string e ativo é booleano)
    
    id = Column('id',Integer,primary_key= True,autoincrement= True) #primeiro passamos o nome que a coluna tera na base de dados e dps os tipos de dados e dps sao os parametros personalizados. o primary key é uma informacao unica que deve ter em toda tabela,normalmente o id e o autoidentificador é o que definira o id de cada novo usuario automaticamente
    nome = Column('nome',String,nullable=False) #nullable = false nao permite valores vazios
    admin = Column('admin',Boolean,default=False) #defalt = false significa q se nada for informado,o parametro padrao é ser falso
    email = Column('email',String)
    senha = Column('senha',String)
    ativo = Column('ativo',Boolean)
    
    pedidos = relationship("Pedido", back_populates="usuario") #relacionamento entre usuario e pedido,ou seja, um usuario pode ter varios pedidos, o back_populates é usado pra criar o relacionamento bidirecional entre as tabelas,ou seja, o usuario tem uma lista de pedidos e cada pedido tem um usuario


    def __init__(self,nome,email,ativo,senha,admin): #funcao que sera inicializada sempre que a classe usuario for ativa,inclusive em outros arquivos,aqui passsamos todos os parametros que devem ser criados qnd o usuario rodar
        #o id nao esta aqui pq ele é a primary key e sera criado automaticamente
        self.nome = nome
        self.email = email
        self.ativo = ativo
        self.senha = senha
        self.admin = admin
        



#pedido

class Pedido(base):
    __tablename__ = 'pedidos'

    


    id = Column('id',Integer,primary_key= True,autoincrement= True)
    #status = Column(Enum(StatusPedido), default=StatusPedido.PENDENTE)
    status = Column('status',String,default='PENDENTE') #status pendente,cancelado ou finalizado
    usuario_id = Column('usuario',ForeignKey('usuarios.id')) #quem fez o pedido, foreign key pq é uma chave estrangeira q referencia a tabela usuarios
    # preco = Column('preco',Float)
    

    preco = Column(Numeric(10,2), default=Decimal("0.00"))

    criado_em = Column("criado_em",DateTime,default=datetime.utcnow)
   
    
    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship(
        "item_pedido",
        back_populates="pedido",
        cascade="all, delete-orphan"
    )




    def __init__(self,usuario_id,status='PENDENTE',preco=0): #qnd se cria um pedido,o valor inicial dele sera 0 e tera status pendente
        self.usuario_id= usuario_id
        self.status = status
        self.preco = preco 
        #self.criado_em = criado_em #a data de criacao do pedido sera a data atual,ou seja, a data q o pedido for criado

    def calcular_preco(self):
        total = Decimal("0.00")
        for item in self.itens:
            total += item.preco_unitario * item.quantidade
        self.preco = total
        #percorrer toda a coluna de itens pra cada pedido e somar os precos de cada item pra dar o preco final do pedio
        #atualizar o campo do preco ate todos os itens forem adicionados 
        

#itens pedidos

class item_pedido(base):
    __tablename__= 'itens_pedidos'

    id = id = Column('id',Integer,primary_key= True,autoincrement= True)
    quantidade = Column('quantidade',Integer)
    sabor = Column('sabor',String) #aqui poderia ser criado uma choice type com os valores pre definidos das pizzas igual foi feito com os status
    tamanho = Column('tamanho',String) #tbm poderia ser choicetype
    preco_unitario =  Column('preco_unitario',Numeric(10,2)) #preco unitario da pizza,ou seja, o preco de cada pizza, o preco total do item sera o preco unitario multiplicado pela quantidade
    #pedido = Column('pedido',ForeignKey('Pedido.id'))

    pedido_id = Column(ForeignKey("pedidos.id"))#isso aqui é so o valor do id do pedido,ou seja, o numero do pedido,mas o relacionamento abaixo é o objeto do tipo pedido,ou seja, o item_pedido tem um atributo chamado pedido que é um objeto do tipo pedido,entao pra acessar o id do pedido a partir do item_pedido,seria item_pedido.pedido.id
    pedido = relationship("Pedido", back_populates="itens") #isso aqui tem o valor de um objeto do tipo pedido,ou seja, o item_pedido tem um atributo chamado pedido que é um objeto do tipo pedido,entao pra acessar o id do pedido a partir do item_pedido,seria item_pedido.pedido.id




    def __init__(self,quantidade,sabor,tamanho,preco_unitario,pedido):
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido

#pra mais funcionalidades,é possivel colocar outras funcionalidades


#executa a criacao dos metadados do seu banco(criando efetivamente todo o conjunto banco de dados)