#arquivo q tera todas as rotas/ENDPOINTS de comandos/ordens como get,post,delete,put
from fastapi import APIRouter,Depends,HTTPException, Query
from sqlalchemy.orm import Session
from app.models import Pedido,Usuario,item_pedido
from app.scheamas import PedidoSchema,ItemPedidoschema,RespostaPedidoSchema,UsuarioSchema
from app.dependencias import pegar_sessao,verificar_token
from typing import List

order_router = APIRouter(prefix='/orders',tags=['Orders'],dependencies=[Depends(verificar_token)])##criando o roteador de ordens (get,post,etc...),precisamos decifinir o prefixo que ficara 
#no link do navegador,na ordem: dominio/auth(prefixo)/outro caminho definido na rota.
#tags = '' serve para agrupar as rotas na doc automatica do fastapi
#dependencies = adiciona as dependencias em todas as rotas,no caso aq escolhemos a funcao verificar_token para que toda rota de orders exija autentificacao,assim nao precisamos colocar a dependencia em cada rota individualmente
#o ponto negativo de usar as dependencias no roteador é que a resposta dessa funcao nao podera ser usada dentro da funcao,diferentemente de quando colocamos a dependencia dentro da rota como parametro,entao se quisermos usar a resposta da funcao verificar_token,precisamos colocar a dependencia dentro da rota e nao no roteador

#definindo as rotas 
@order_router.get('/') #definindo a rota get para pegar todas as ordens
#sempre que formos criar uma rota,pegamos nosso roteador (order_router),definimos o metodo http(get,post,etc) e o caminho('/') q vira na frente do prefixo

#esse @ é o decorator,ele adiciona funcionalidades a funçoes ja existentes,ou seja estamos adicionando a funcao get(lista) ao prefixo do order_router

async def orders():
    #aqui dentro da funcao podemos colocar tudo q queremos q ela faca,como acessar e pegar x informacao do banco de dados
    #e tambem as mensagens que serao retornadas ao usario 
    #docstring explicando a rota,bom pra apis publicas
    """
    Essa é a rota padrao de pedidos do sistema.Todas as rotas de pedidos precisam de autentificacao 
    """
    return {'mensagem':'voce acessou a rota de pedidos'} #retorna um dicionario pq a fastapi trabalha em json


@order_router.post('/pedido')
async def criar_pedido(pedido_schema : PedidoSchema,session : Session = Depends(pegar_sessao)):
    """
    Rota que cria pedidos,ela verifica se o usuario esta autentificado e commita o novo pedido no sistema.
    Retorna uma mensagem e o id do pedido
    """
    
    
    
    if not session.query(Usuario).filter(Usuario.id == pedido_schema.usuario_id).first():
        raise HTTPException(status_code=400,detail="usuario nao encontrado")
    novo_pedido = Pedido(usuario_id=pedido_schema.usuario_id)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem":f"pedido criado com sucesso. id_pedido = {novo_pedido.id}"}
    
    
@order_router.post("/pedido/cancelar/{id_pedido}") #tudo que for colocado como parametro na rota,tbm tem q ser parametro na funcao. so muda o lugar na fastapi onde fazemos a requisicao
async def cancelar_pedido(id_pedido : int,session : Session = Depends(pegar_sessao),usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400,detail="pedido nao encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=400,detail="voce nao tem autorizacao pra fazer essa modificacao") #
    pedido.status = "CANCELADO"
    session.commit() #salvando a mudanca no banco de dados
    print("bolas")
    return {
        "mensagem": f"pedido de numero {pedido.id} cancelado com sucesso",
        "pedido":pedido
    }




@order_router.get("/listar_pedidos") #
async def listar_pedidos(limite: int = Query(10, ge=1, le=500),usuario : Usuario = Depends(verificar_token),session : Session = Depends(pegar_sessao)):
    """
    Rota que lista todos os pedidos do sistema,so pode ser usada por admins e possui verificacao de autentificacao
    """
    
    
    if usuario.admin == False:
        raise HTTPException(status_code=400,detail="voce nao tem autorizacao pra fazer essa operacao")
    else:
        pedidos = (session.query(Pedido).order_by(Pedido.id.desc()).limit(limite).all())
    return {
        "pedidos": pedidos 
    }





@order_router.post("/pedido/adicionar-item/{id_pedido}") #colocando o parametro na rota,na hora de receber essa inforamcao na API,ele sera tratado como uma header. todo parametro na rota,tem q ser passado tambem na funcao
async def adicionar_item(id_pedido : int,item_pedido_schema : ItemPedidoschema,session : Session = Depends(pegar_sessao),usuario : Usuario = Depends(verificar_token)):
    """
    Adiciona itens ao pedido escolhido,verificando se o pedido existe,se o usuario tem permissao pra isso e se o pedido ja
    nao esta cancelado ou finalizado. Recebe uma informacao no formato item_pedido_schema e 
    retorna uma mensagem, o id do item criado e o preco atualizado do pedido
    """
    
    
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400,detail="pedido nao encontrado")

    if usuario.admin == False and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=400,detail="voce nao tem permissao pra fazer isso")
    if pedido.status == "FINALIZADO":
        raise HTTPException(status_code=400,detail="pedido ja finalizado,nao e possivel fazer modificacoes")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code=400,detail="pedido cancelado,nao e possivel fazer modificacoes")




    item_pedindo = item_pedido(
        sabor=item_pedido_schema.sabor,
        quantidade=item_pedido_schema.quantidade,
        tamanho=item_pedido_schema.tamanho,
        preco_unitario=item_pedido_schema.preco_unitario,
        pedido=pedido#.id
    )
    
    session.add(item_pedindo)
    pedido.calcular_preco()
    session.commit()
    return{
        "mensagem" : f"item criado com sucesso",
        "item_iD" : item_pedindo.id,
        "preco_pedido" : pedido.preco
    }



@order_router.post("/pedido/remover-item/{id_item_pedido}") #parametro na rota ja foi explicado acima
async def remover_item(id_item_pedido : int,session : Session = Depends(pegar_sessao),usuario : Usuario = Depends(verificar_token)):
    """
    Rota de remocao do item,com base no id do item pedido e com as mesmas verificacoes de permissao e status do pedido da 
    rota de adicao de item,ela remove o item do pedido e retorna uma mensagem, a quantidade de itens restantes no pedido 
    e um resumo do pedido atualizado
    """
    
    
    item_pedindo = session.query(item_pedido).filter(item_pedido.id == id_item_pedido).first()
    
    if not item_pedindo:
        raise HTTPException(status_code=400,detail="item de pedido nao encontrado")
    pedido = session.query(Pedido).filter(Pedido.id == item_pedindo.pedido_id).first()
    if pedido.status == "FINALIZADO":
        raise HTTPException(status_code=400,detail="pedido ja finalizado,nao e possivel fazer modificacoes")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code=400,detail="pedido cancelado,nao e possivel fazer modificacoes")

    
    if usuario.admin == False and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=400,detail="voce nao tem permissao pra fazer isso")

    
    session.delete(item_pedindo)
    pedido.calcular_preco()
    session.commit()
    return{
        "mensagem" : f"item removido com sucesso",
        "quantidade_itens_pedido" : len(pedido.itens),
        "resumo do pedido" : pedido
    }


#finalizar pedido 

@order_router.post("/pedido/finalizar/{id_pedido}") #
async def finalizar_pedido(id_pedido : int,session : Session = Depends(pegar_sessao),usuario : Usuario = Depends(verificar_token)):
    """
    Rota de finalizacao do pedido,ela verifica se o pedido existe,se o usuario tem permissao pra isso e se o pedido ja nao
    esta cancelado ou finalizado. Se tudo estiver ok,ela muda o status do pedido para "FINALIZADO" e retorna uma mensagem 
    de confirmacao junto com um resumo do pedido finalizado.
    """
    
    
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400,detail="pedido nao encontrado")

    if usuario.admin == False and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=400,detail="voce nao tem permissao pra fazer isso")
    if pedido.status == "FINALIZADO":
        raise HTTPException(status_code=400,detail="pedido ja finalizado,nao e possivel fazer modificacoes")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code=400,detail="pedido cancelado,nao e possivel fazer modificacoes")



    pedido.status = "FINALIZADO"
    session.commit()
    
    return{
        "mensagem" : f"pedido numero {pedido.id} finalizado com sucesso",
        "pedido" : pedido
    }

#visualizar detalhes do pedido
@order_router.get("/pedido/detalhes/{id_pedido}",response_model=RespostaPedidoSchema) #response model pra padronizar a resposta da api,isso possibilita o return simplificado la embaixo
async def detalhes_pedido(id_pedido : int,session : Session = Depends(pegar_sessao),usuario : Usuario = Depends(verificar_token)):
    """
    Rota pra visualizacao de detalhes de um peddido especifico. Verificacao de autentificacao,verifica se o pedido existe 
    e entao retorna o pedido no formato definido no schema RespostaPedidoSchema.
    """
    
    
    
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400,detail="pedido nao encontrado")

    if usuario.admin == False and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=400,detail="voce nao tem permissao pra fazer isso")

    # return{
    #     "pedido" : pedido,
    #     "quantidade_itens" : len(pedido.itens),
    #     "itens" : pedido.itens
    # }
    return pedido #como a resposta da rota foi padronizada com o schema RespostaPedidoSchema,entao a fastapi vai converter automaticamente o pedido para o formato definido no schema,ou seja, ela vai pegar os atributos do pedido e colocar no formato definido no schema,entao nao precisamos montar manualmente a resposta como fizemos antes,ela ja vai ser montada automaticamente com base no schema



#visualizar todos os pedidos de um usuario
@order_router.get("/pedido/meus-pedidos/{id_usuario}",response_model=List[RespostaPedidoSchema])
async def visualizar_pedidos(id_usuario: int,session : Session = Depends(pegar_sessao),usuario : Usuario = Depends(verificar_token),limite: int = Query(10, ge=1, le=500)): #
    """
    Rota de visualizacao de todos os pedidos de um usuario especifico. Verificacao de autentificacao,verifica se o 
    usuario existe e retorna uma lista de pedidos do usuario no formato definido no schema RespostaPedidoSchema em ordem 
    de ultimos pedidos feitos. 
    """
    
    
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=400,detail="usuario nao existe")

    if usuario.admin == False and usuario.id != usuario.id:
        raise HTTPException(status_code=400,detail="voce nao tem permissao pra fazer isso")
    
    else:
        pedidos = (session.query(Pedido).filter(Pedido.usuario_id == usuario.id).order_by(Pedido.id.desc()).limit(limite).all())
    return pedidos #como a resposta da rota foi padronizada com o schema RespostaPedidoSchema,entao a fastapi vai converter automaticamente os pedidos para o formato definido no schema,ou seja, ela vai pegar os atributos dos pedidos e colocar no formato definido no schema,entao nao precisamos montar manualmente a resposta como fizemos antes,ela ja vai ser montada automaticamente com base no schema
