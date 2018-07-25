import psycopg2, psycopg2.extras

from flask import g, session, request, redirect, url_for, render_template

from app import app

from random import randint

@app.before_request
def before_request():
   g.db = psycopg2.connect("dbname=banco_credimaster user=postgres password=rafa123 host=127.0.0.1")

# Disconnect database 
@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/', methods = ['POST', 'GET'])
def index():
	if request.method == 'POST':
		n_conta = request.form['conta']
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM conta WHERE numero = {}".format(n_conta))
		conta = cur.fetchall()
		titular = conta[0][2]
		cur.execute("SELECT * FROM usuario WHERE cpf = '{}'".format(titular))
		titular = cur.fetchall()
		session['cpf'] = n_conta
		if conta[0][4] == request.form['senha']:
			session['cpf'] = conta[0][2]
			return redirect(url_for('cliente'))
		return render_template('index.html', erro = 'Senha incorreta')
		
		
	return render_template('index.html')

@app.route('/abertura-de-conta', methods = ['GET', 'POST'])
def abertura_de_conta():
	if request.method == 'GET':
		return render_template('abrir-conta.html')
	else:
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM usuario")
		usuarios = cur.fetchall()
		aux = 0
		usuario = request.form['cpf']
		for user in usuarios:
			if user['cpf'] == usuario:
				aux = 1
			else:
				pass
		if aux == 1:
			return render_template('abrir-conta.html', error='CPF já cadastrado!')
		else:
			nome = request.form['nome'] 
			cpf = request.form['cpf']
			telefone = request.form['telefone']
			email = request.form['email']
			sexo = request.form['sexo']
			idade = request.form['idade']
			numero = randint(1000, 50000)
			titular = request.form['cpf']
			saldo = 0
			senha = request.form['senha']
			cur.execute("INSERT INTO usuario (nome, cpf, telefone, email, sexo, idade) VALUES ('{}', '{}', '{}', '{}', '{}', {})".format(nome, cpf, telefone, email, sexo, idade))
			cur.execute("INSERT INTO conta (numero, agencia, titular, saldo, senha) VALUES ({}, {}, '{}', {}, '{}')".format(numero, '0001', titular, saldo, senha))
			g.db.commit()
			cur.close()
			session['cpf'] = request.form['cpf']
			return redirect(url_for('cliente'))

def login(titular, conta):
	return render_template('senha.html', titular = titular, conta = conta)

@app.route('/cliente')
def cliente():
	if 'cpf' in session:
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM usuario WHERE cpf = '{}'".format(session['cpf']))
		titular = cur.fetchall()
		cur.execute("SELECT * FROM conta WHERE titular = '{}'".format(session['cpf']))
		conta = cur.fetchall()
		return render_template('cliente.html', titular = titular, conta = conta)
	return redirect(url_for('index'))

@app.route('/sair')
def sair():
	session.pop('cpf')
	return redirect(url_for('index'))

@app.route('/deposito', methods = ['GET', 'POST'])
def deposito():
	cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cur.execute("SELECT * FROM conta WHERE titular = '{}'".format(session['cpf']))
	conta = cur.fetchall()
	cur.execute("SELECT * FROM usuario WHERE cpf = '{}'".format(session['cpf']))
	titular = cur.fetchall()
	if request.method == 'POST':
		saldo = conta[0][3]
		saldo += float(request.form['valor'])
		cur.execute("UPDATE conta SET saldo = {}".format(saldo))
		g.db.commit()
		return redirect(url_for('cliente'))
	return render_template('deposito.html', titular = titular)

@app.route('/saque', methods = ['GET', 'POST'])
def saque():
	cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cur.execute("SELECT * FROM conta WHERE titular = '{}'".format(session['cpf']))
	conta = cur.fetchall()
	cur.execute("SELECT * FROM usuario WHERE cpf = '{}'".format(session['cpf']))
	titular = cur.fetchall()
	if request.method == 'POST':
		saldo = conta[0][3]
		valor = float(request.form['valor'])
		if saldo >= valor:
			print (saldo, valor)
			saldo -= float(request.form['valor'])
			cur.execute("UPDATE conta SET saldo = {}".format(saldo))
			g.db.commit()
			return redirect(url_for('cliente'))
		return render_template('deposito.html', titular = titular, erro = 'Saldo superior ao disponível!')	
	return render_template('deposito.html', titular = titular)

@app.route('/transferencia', methods = ['GET', 'POST'])
def transferencia():
	cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cur.execute("SELECT * FROM conta WHERE titular = '{}'".format(session['cpf']))
	conta = cur.fetchall()
	cur.execute("SELECT * FROM usuario WHERE cpf = '{}'".format(session['cpf']))
	titular = cur.fetchall()
	if request.method == 'POST':
		destino = request.form['conta']
		valor = request.form['valor']
		saldo = conta[0][3]
		if saldo >= float(valor):
			saldo -= float(valor)
			cur.execute("UPDATE conta SET saldo = {}".format(saldo))
			g.db.commit()
			cur.close()
			cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT * FROM conta WHERE numero = {}".format(destino))
			conta_destino = cur.fetchall()
			saldo_destino = conta_destino[0][3]
			saldo_destino += float(valor)
			cur.execute("UPDATE conta SET saldo = {}".format(saldo_destino))
			g.db.commit()
			return redirect(url_for('cliente'))
		return render_template('transferencia.html', titular = titular, erro = 'Saldo superior ao disponível!')	
	return render_template('transferencia.html', titular = titular)

