## Acervo digital de livros
Plataforma para gerenciamento de livros e romancistas


## Instalação
#### Pré requisitos
- `python >= 3.11`
- `poetry >= 2.1`
- `docker & docker-compose`

1. No diretório do projeto execute o comando `poetry install` para instalação de todas
as dependências de produção de desenvolvimento.

2. Ainda no diretório do projeto, execute `docker-compose up` ou caso tenha instalado o Docker Desktop, execute `docker compose up`, será feito o pull das imagens do PostgresSQL, e do Python, bem como a criação da imagem da aplicação de acervo digital.

...
