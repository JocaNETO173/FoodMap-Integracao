# Flash é utilizado para dar alertas ao usuário na tela
from flask import Flask, render_template, request, redirect, flash, session, make_response
import mysql.connector

app = Flask(__name__)
app.secret_key = "sabonete"

# bd_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'escola',
#     'database': 'foodmap',
#     'ssl_disabled': True
# }

bd_config = {
    'host': '127.0.0.1',
    'user': 'flask_user',
    'password': '#Pato26022025',
    'database': 'foodmap'
}


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    senha = request.form.get("senha")
    # baseado no email, ele retornará se a coluna ADM do campo deste email é true ou false

    try:
        conexao = mysql.connector.connect(**bd_config)
        cursor = conexao.cursor(dictionary=True)

        query = "SELECT NOME, EMAIL, ADM FROM usuario WHERE EMAIL = %s AND SENHA = %s"
        cursor.execute(query, (email, senha))
        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

    except mysql.connector.Error as err:
        return f"Erro ao consultar o banco: {err}"

    if not usuario:
        flash("Email ou senha inválidos.")
        return redirect("/login")

    session["usuario_nome"] = usuario["NOME"]
    session["usuario_email"] = usuario["EMAIL"]

    if usuario["ADM"]:
        return redirect("/restaurantes_admin")
    else:
        return redirect("/restaurantes")


@app.route("/cadastro_usuario", methods=["GET", "POST"])
def cadastroUser():
    if request.method == "GET":
        return render_template("cadastro.html")

    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    confirmar_senha = request.form.get("confirm-senha")

    if len(senha) < 8 or len(senha) > 20:
        flash("A senha deve ter entre 8 e 20 caracteres.")
        return redirect('/cadastro_usuario')

    if senha != confirmar_senha:
        flash("As senhas não coincidem.")
        return redirect('/cadastro_usuario')

    try:

        conexao = mysql.connector.connect(**bd_config)
        cursor = conexao.cursor(dictionary=True)

        query = "INSERT INTO usuario (EMAIL, NOME, SENHA, ADM) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (email, nome, senha, False))
        conexao.commit()

        cursor.close()
        conexao.close()
    except mysql.connector.Error as err:
        return f"Erro ao gravar no Banco: {err}"

    flash("Cadastro realizado com sucesso! Faça login para continuar.")
    return redirect("/login")


@app.route("/restaurantes", methods=["GET", "POST"])
def restaurantes():
    termo = request.form.get("termo", "")
    nome = session.get("usuario_nome", "Usuário")
    email = session.get("usuario_email", "email@email.com")
    restaurantes_lista = buscar_restaurantes(termo)
    if nome == "Usuário":
        flash("Você precisa estar logado para acessar esta página.")
        return redirect("/login")
    else:
        return render_template("restaurantes_user.html", restaurantes=restaurantes_lista, termo=termo, nome=nome, email=email)


@app.route("/sairDaConta")
def sairDaConta():
    session.clear()
    flash("Você saiu da conta com sucesso.")
    return redirect("/login")


@app.route("/restaurantes_admin", methods=["GET", "POST"])
def restaurantes_admin():

    termo = request.form.get("termo", "")
    nome = session.get("usuario_nome", "Usuário")
    email = session.get("usuario_email", "email@email.com")
    restaurantes_lista = buscar_restaurantes(termo)
    if nome == "Usuário":
        flash("Você precisa estar logado para acessar esta página.")
        return redirect("/login")
    else:
        return render_template("restaurantes_admin.html", restaurantes=restaurantes_lista, termo=termo, nome=nome, email=email)


def buscar_restaurantes(termo=""):
    conexao = mysql.connector.connect(**bd_config)
    # Retorna os resultados como dicionários
    cursor = conexao.cursor(dictionary=True)

    if termo:
        query = "SELECT * FROM restaurante WHERE nome LIKE %s"
        cursor.execute(query, (f"%{termo}%",))
    else:
        # Se não houver busca, exibe todos (ou deixe vazio se preferir)
        cursor.execute("SELECT * FROM restaurante")

    restaurantes = cursor.fetchall()

    cursor.close()
    conexao.close()
    return restaurantes


@app.route("/cadastro-restaurantes", methods=["GET", "POST"])
def cadastroRestaurantes():
    if request.method == "GET":
        return render_template("restaurante_cadastro.html")

    

    nomeRestaurante = request.form.get("nome-restaurante")
    categoria = request.form.get("categoria")
    descricao = request.form.get("descricao")
    endereco = request.form.get("endereco")
    URLImage = request.form.get("imagem")

    try:
        conexao = mysql.connector.connect(**bd_config)
        cursor = conexao.cursor(dictionary=True)

        query = "INSERT INTO restaurante (NOME, CATEGORIA, DESCRICAO, ENDERECO, IMAGEM) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (nomeRestaurante, categoria,
                       descricao, endereco, URLImage))
        conexao.commit()

        cursor.close()
        conexao.close()
    except mysql.connector.Error as err:
        return f"Erro ao gravar no Banco: {err}"

    return redirect("/restaurantes_admin")


if __name__ == "__main__":
    app.run(debug=True)
