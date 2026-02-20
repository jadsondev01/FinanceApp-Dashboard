📌 ESPECIFICAÇÃO TÉCNICA
Sistema de Controle de Gastos Pessoais (Web)
1️⃣ Visão Geral
📍 Nome do Sistema

Sistema Web de Controle de Gastos Pessoais

🎯 Objetivo

Permitir que usuários registrem, acompanhem e analisem seus gastos por categoria e por período, através de gráficos e relatórios visuais.

👥 Público-Alvo

Usuários individuais

Pessoas que desejam controle financeiro pessoal

Pequenos empreendedores

2️⃣ Arquitetura do Sistema
🧱 Arquitetura

Arquitetura baseada em padrão MVT (Model-View-Template) do Django.

🔧 Tecnologias Utilizadas
Camada	Tecnologia
Backend	Python 3
Framework	Django
Banco de Dados	SQLite (padrão)
Frontend	HTML5 + CSS3
Gráficos	Chart.js
Autenticação	Django Auth
3️⃣ Estrutura da Aplicação
📁 Estrutura de Pastas
controle_gastos/
│
├── manage.py
├── controle_gastos/
│   ├── settings.py
│   ├── urls.py
│
├── gastos/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── templates/
│   └── static/

4️⃣ Modelagem de Dados
📌 Model: Gasto
class Gasto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField()
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

📊 Regras do Modelo

Cada gasto pertence a um único usuário.

Valor é armazenado com precisão decimal.

Categoria é padronizada via choices.

Exclusão do usuário remove seus gastos (CASCADE).

5️⃣ Funcionalidades
🔐 Autenticação

Cadastro de usuário

Login

Logout

Validação de senha personalizada

➕ Cadastro de Gastos

Data

Categoria (Select fixo)

Descrição

Valor (com máscara monetária)

📊 Dashboard
Gráficos:

Gastos por Categoria

Tipo: Gráfico de Barras

Cada categoria representa uma barra

Valor exibido é a soma total da categoria

Gastos por Dia (Mensal)

Tipo: Linha

Mostra crescimento acumulado por dia do mês

🧮 Cálculos Realizados

Soma total por categoria

Soma diária

Crescimento acumulado

Total geral do mês

6️⃣ Regras de Negócio

Usuário só visualiza seus próprios dados.

Cada categoria gera uma barra independente no gráfico.

Valores são somados por agrupamento no banco:

Gasto.objects.values('categoria').annotate(total=Sum('valor'))


O gráfico mensal é baseado em agrupamento por data:

Gasto.objects.values('data').annotate(total=Sum('valor'))

7️⃣ Segurança

Autenticação obrigatória (@login_required)

Proteção CSRF em formulários

Hash seguro de senha (Django padrão)

Separação de dados por usuário

8️⃣ Interface do Usuário
🎨 Layout

Formulário horizontal

Inputs estilizados

Botão destacado

Gráficos responsivos

💰 Máscara Monetária

Implementação em JavaScript:

Formatação automática para R$

Conversão posterior para Decimal no backend

9️⃣ Fluxo da Aplicação
Usuário faz login →
Adiciona gasto →
Dados salvos no banco →
View agrega valores →
Dados enviados para template →
Chart.js renderiza gráficos

🔟 Requisitos Funcionais

RF01: Permitir cadastro de usuário

RF02: Permitir login/logout

RF03: Permitir cadastro de gastos

RF04: Exibir gráfico por categoria

RF05: Exibir gráfico mensal acumulado

RF06: Somar valores automaticamente

1️⃣1️⃣ Requisitos Não Funcionais

Interface responsiva

Dados isolados por usuário

Sistema leve

Código organizado em MVT

Fácil escalabilidade futura

1️⃣2️⃣ Possíveis Melhorias Futuras

Exportação para Excel

Filtro por período

Metas financeiras

Gráfico anual

API REST

Deploy em produção (Render/Heroku/AWS)

📌 Conclusão Técnica

A aplicação é um sistema web estruturado em Django que implementa controle financeiro com:

Persistência relacional

Agregação de dados

Visualização gráfica

Autenticação segura

Separação de dados por usuário

Pronto para evoluir para um SaaS financeiro.
