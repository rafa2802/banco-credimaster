CREATE DATABASE BANCO_CREDIMASTER;

CREATE TABLE USUARIO(
	nome varchar(255),
	telefone varchar(255),
	email varchar(255),
	cpf varchar(11),
	sexo varchar(1),
	idade integer,
	primary key (cpf)
);

CREATE TABLE CONTA(
	numero integer,
	agencia integer,
	titular varchar(11),
	saldo integer,
	primary key(numero),
	foreign key(titular) references USUARIO (cpf)
);
