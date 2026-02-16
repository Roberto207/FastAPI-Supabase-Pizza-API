# 1️⃣ imagem base oficial do Python
FROM python:3.11 

# 2️⃣ cria pasta dentro do container
WORKDIR /app

# 3️⃣ copia apenas o requirements primeiro (melhora cache)
COPY requirements.txt .


# 4️⃣ instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ copia o restante do código
COPY . .

# 6️⃣ comando para iniciar a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

#🧠 Por que 0.0.0.0?Porque o container precisa expor a API para fora. Se usar 127.0.0.1, ninguém de fora do container acessa.

#passo 2 = agora no terminal do projeto rode o comando para criar a imagem:
#docker build -t nome-da-imagem . = build é o comando para criar a imagem, -t é para dar um nome a ela, e o ponto final indica que o Dockerfile está no diretório atual.
#possivel verificar dando docker images = para listar as imagens criadas no seu ambiente.

#passo 3 = para rodar a imagem criada como um container, use o comando:
#docker run -p 8000:8000 nome-da-imagem = run é o comando para rodar a imagem, -p 8000:8000 → conecta porta do seu PC com a porta do container, e nome-da-imagem é o nome da imagem que você criou no passo anterior.

# 🎯 Fluxo mental completo

# Criar Dockerfile

# docker build

# docker run

# acessar localhost