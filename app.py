# Flash é utilizado para dar alertas ao usuário na tela
from flask import Flask, render_template, request, redirect, flash
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


@app.route("/login")
def login():
    return render_template("login.html")


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
    restaurantes = []
    termo = request.form.get("termo", "")  # Pega o que o usuário digitou

    conexao = mysql.connector.connect(**bd_config)
    # Retorna os resultados como dicionários
    cursor = conexao.cursor(dictionary=True)

    if termo:
        query = "SELECT * FROM restaurantes WHERE nome LIKE %s"
        cursor.execute(query, (f"%{termo}%",))
    else:
        # Se não houver busca, exibe todos (ou deixe vazio se preferir)
        cursor.execute("SELECT * FROM restaurantes")

    restaurantes = cursor.fetchall()

    cursor.close()
    conexao.close()
    return render_template("restaurantes_user.html", restaurantes=restaurantes, termo=termo)
    # if (usuario == user):
    #
    # elif (usuario == admin):
    #     return render_template("restaurantes_admin.html", restaurantes=restaurantes, termo=termo)


if __name__ == "__main__":
    app.run(debug=True)
