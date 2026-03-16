# Plataforma de Curso e Simulados de Trânsito Online

## Sobre o Projeto

Esta plataforma foi desenvolvida para oferecer **preparação online para provas teóricas de trânsito**, permitindo que alunos estudem conteúdos e realizem **simulados semelhantes aos exames oficiais do DETRAN**.

O sistema permite que usuários se cadastrem, adquiram acesso ao curso, realizem simulados e acompanhem seu desempenho dentro da plataforma.

A aplicação foi construída utilizando **Python**, com **Flask no backend** e **Streamlit na interface**, além de integrações com serviços externos para **pagamentos, envio de emails e autenticação segura**.

🔗 **Acesse a plataforma:**  
https://autoescolaemvideo.com.br

---

# Principais Funcionalidades

## Sistema de Usuários

- Cadastro de usuários
- Login seguro
- Autenticação com tokens
- Recuperação de senha
- Controle de acesso ao curso

---

## Curso de Trânsito Online

- Conteúdos teóricos sobre legislação de trânsito
- Acesso liberado após confirmação de pagamento
- Interface simples e intuitiva
- Aulas e conteúdos digitais acessíveis pela web

---

## Simulados de Prova

- Banco de questões
- Simulados de múltipla escolha
- Correção automática
- Feedback imediato
- Preparação para provas do DETRAN

---

## Integração de Pagamentos

A plataforma possui integração com **Mercado Pago**, permitindo:

- Pagamento online
- Liberação automática de acesso
- Controle de usuários com acesso ao curso

---

## Sistema de Email

Utilizando **SendGrid**, a plataforma envia automaticamente:

- Emails de confirmação de cadastro
- Recuperação de senha
- Notificações do sistema

---

# Segurança

A aplicação utiliza boas práticas de segurança:

- Senhas criptografadas com **bcrypt**
- Autenticação com **JWT**
- Proteção de rotas privadas
- Tokens seguros com **itsdangerous**
- Gerenciamento de variáveis sensíveis via **.env**

---

# Infraestrutura e Deploy

A plataforma está **em produção na AWS (Amazon Web Services)**, garantindo disponibilidade, escalabilidade e confiabilidade para os usuários.

A aplicação é executada utilizando **Gunicorn como servidor WSGI**, com backend em Flask e banco de dados PostgreSQL hospedado via **Supabase**.

Essa arquitetura permite:

- Alta disponibilidade da aplicação
- Escalabilidade da infraestrutura
- Gerenciamento seguro do banco de dados
- Deploy em ambiente de produção estável

---

# Arquitetura do Projeto

O sistema é dividido em duas partes principais.

## Backend

Responsável por:

- API da aplicação
- Autenticação
- Integração com banco de dados
- Integração com pagamentos
- Envio de emails

Tecnologias utilizadas:

- Flask
- PostgreSQL
- Psycopg2
- JWT
- Bcrypt
- Flask-CORS
- Gunicorn

---

## Interface

A interface foi construída com **Streamlit**, permitindo uma aplicação web simples e rápida para interação com os usuários.

---

# Banco de Dados

O projeto utiliza **PostgreSQL**, com conexão realizada via:

- psycopg2
- Supabase

---

# Tecnologias Utilizadas

| Tecnologia | Função |
|---|---|
| Python | Linguagem principal |
| Flask | Backend da aplicação |
| Streamlit | Interface web |
| PostgreSQL | Banco de dados |
| Supabase | Infraestrutura do banco |
| Psycopg2 | Conexão Python/PostgreSQL |
| MercadoPago | Sistema de pagamentos |
| SendGrid | Envio de emails |
| PyJWT | Autenticação |
| Bcrypt | Criptografia de senha |
| Gunicorn | Servidor para produção |
| Flask-CORS | Permissões entre domínios |
| Python-dotenv | Variáveis de ambiente |
| Itsdangerous | Tokens seguros |

---

# Instalação do Projeto

## Clonar o repositório

```bash
git clone https://github.com/andrade044/Curso-WebApp.git
cd Curso-WebApp
