# Dijkstra Visualizado

**Número da Lista**: Lista 2<br>
**Conteúdo da Disciplina**: Algoritmo de Dijkstra<br>

## Alunos

|Matrícula | Aluno |
| -- | -- |
| 17/0039251  |  Lieverton Santos Silva |
| 17/0024121  |  Welison Lucas Almeida Regis |

## Sobre

Para melhor compreensão sobre o algoritmo de Dijkstra, apresentado em sala, decidiu-se fazer uma aplicação para visualizá-lo. Nesse projeto, tem-se dois pontos, A e B, e o objetivo é encontrar o **menor caminho com o algoritmo de Dijkstra**. Para atrapalhar o algoritmo e, também, poder enxergar como ele funciona, é possível ao usuário **desenhar obstáculos** no *grid* do jogo.

## Animação da aplicação

<p align="center">
    <img src="https://media.giphy.com/media/j0poI80Aop2nemnYjK/giphy.gif" alt="Exemplo Dijkstra">
</p>

## Instalação

**Linguagem**: Python 3.7<br>
**Bibliotecas**:
*   Instale o tkinter (Ubuntu): `sudo apt-get install python-tk`.
*   Instale os pré-requisitos do projeto: `pip install -r requirements.txt`.

*   Versão do pip utilizada: 19.0.3.
*   Caso seja necessário, instale manualmente os requirements.

## Uso

*   Tem-se dois pontos, um representa um ponto de início e outro representa um ponto de objetivo final. Pode-se posicionar tais pontos em qualquer local do *grid*, basta clicar e arrastar.
*   Pode-se executar a animação do Algoritmo de Dijkstra ao clicar em **"Go"**.
*   Para limpar a tela e iniciar uma nova animação, clique em **"Clear"**.
*   A aplicação disponibiliza a geração de um labirinto também. Ao clicar em **"Maze"** gera-se um labirinto, e pode-se usar tanto o "Clear" como o "Go".

Execute a aplicação da seguinte forma:
*   Acesse: `cd src`.
*   Com o python 3, execute: `python3 main.py`.
