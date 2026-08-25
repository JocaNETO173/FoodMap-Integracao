# Flash é utilizado para dar alertas ao usuário na tela
from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "sabonete"

bd_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'escola',
    'database': 'foodmap',
    'ssl_disabled': True
}


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
    return render_template("restaurantes_user.html", restaurantes=restaurantes_lista, termo=termo, nome=nome, email=email)

@app.route("/restaurantes_admin", methods=["GET", "POST"])
def restaurantes_admin():
    termo = request.form.get("termo", "")
    restaurantes_lista = buscar_restaurantes(termo)
    return render_template("restaurantes_admin.html", restaurantes=restaurantes_lista, termo=termo)

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

@app.route("/cadastro-restaurantes", methods = "GET, POST")
def cadastroRestaurantes():
    nomeRestaurante = request.form.get("")
    descricao = request.form.get("") 
    endereco = request.form.get("") 
    URLImage = request.form.get("") 

    try:

        conexao = mysql.connector.connect(**bd_config)
        cursor = conexao.cursor(dictionary=True)

        query = "INSERT INTO restaurantes (NOME, CATEGORIA, ENDERECO, IMAGEM) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nomeRestaurante, descricao, endereco, URLImage))
        conexao.commit()

        cursor.close()
        conexao.close()
    except mysql.connector.Error as err:
        return f"Erro ao gravar no Banco: {err}"
    
    return render_template("restaurante_cadastro.html")

if __name__ == "__main__":
    app.run(debug=True)
