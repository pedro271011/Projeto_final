from app.controllers.application import Application
from bottle import Bottle, route, run, request, static_file
from bottle import redirect, template, response
import requests


app = Bottle()
ctl = Application()


#-----------------------------------------------------------------------------
# Rotas:

@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./app/static')

@app.route('/helper')
def helper(info= None):
    return ctl.render('helper')


#-----------------------------------------------------------------------------
# Suas rotas aqui:

@app.route('/comentarios')
def helper(info= None):
    return ctl.render('comentarios')


@app.route('/register', method='GET')
def register():
    return template('app/views/html/register', error=None)

@app.route('/register', method='POST')
def action_register():
    username = request.forms.get('username')
    password = request.forms.get('password')
    success = ctl.create_user(username, password)
    
    if success:
        redirect('/portal')
    else:
        return template('app/views/html/register', error="Usuário já existe.")


@app.route('/pagina', methods=['GET'])
@app.route('/pagina/<username>', methods=['GET'])
def action_pagina(username=None):
    if not username:
        return ctl.render('pagina')
    else:
        return ctl.render('pagina',username)

@app.route('/portal', method='GET')
def login():
    return ctl.render('portal')

@app.route('/portal', method='POST')
def action_portal():
    username = request.forms.get('username')
    password = request.forms.get('password')
    session_id, username= ctl.authenticate_user(username, password)
    if session_id:
        response.set_cookie('session_id', session_id, httponly=True, \
        secure=True, max_age=3600)
        redirect(f'/pagina/{username}')
    else:
        return redirect('/portal')

@app.route('/logout', method='POST')
def logout():
      ctl.logout_user()
      response.delete_cookie('session_id')
      redirect('/helper')
      


import requests  # Garante que requests esteja importado

TMDB_API_KEY = "dc1dffa08f0aca6d03c2e75d3c25de0a"

@app.route('/buscar_filme', method='GET')
@app.route('/pagina/<usuario>', methods=['GET'])
def action_pagina(usuario=None):
    # Criação do dicionário de variáveis para o template
    contexto = {
        'usuario_atual': usuario,
        'filme': None
    }
    
    # Retorna o template com as variáveis passadas dentro do dicionário
    return ctl.render('pagina', contexto)

def buscar_filme():
    titulo_filme = request.query.get('movie')  # Nome mais intuitivo
    usuario_atual = ctl.get_current_user()  # Pega o usuário uma única vez

    if titulo_filme:
        url_busca = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={titulo_filme}&language=pt-BR"
        resposta_busca = requests.get(url_busca)
        dados_busca = resposta_busca.json()

        if dados_busca.get("results"):
            id_filme = dados_busca["results"][0].get("id")  # Usa .get() para evitar erro

            url_detalhes = f"https://api.themoviedb.org/3/movie/{id_filme}?api_key={TMDB_API_KEY}&language=pt-BR"
            resposta_detalhes = requests.get(url_detalhes)
            dados_filme = resposta_detalhes.json()

            generos = ", ".join([genero["name"] for genero in dados_filme.get("genres", [])])

            filme = {
                "titulo": dados_filme.get("title", "Título não disponível"),
                "data_lancamento": dados_filme.get("release_date", "Data desconhecida"),
                "generos": generos,
                "descricao": dados_filme.get("overview", "Descrição não disponível"),
                "nota": dados_filme.get("vote_average", "Sem nota"),
                "capa": dados_filme.get("poster_path")
            }

            return template('app/views/html/pagina', usuario_atual=usuario_atual, filme=filme)
        else:
            return template('app/views/html/pagina', usuario_atual=usuario_atual, erro="Filme não encontrado.", filme=None)
    
    return template('app/views/html/pagina', usuario_atual=usuario_atual, erro="Digite o nome de um filme.", filme=None)

#-----------------------------------------------------------------------------


if __name__ == '__main__':

    run(app, host='localhost', port=8080, debug=True)
