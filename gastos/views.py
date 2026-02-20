from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError

from .models import Gasto, MetaFinanceira
from .forms import GastoForm, CustomUserCreationForm

import pandas as pd
import calendar
from datetime import datetime

# REPORTLAB
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import TableStyle
from reportlab.lib.units import inch

from django.contrib.auth.forms import AuthenticationForm

# ================= LOGIN =================
def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'gastos/login.html', {'form': form})

# ================= LOGOUT =================
@login_required
def logout_usuario(request):
    logout(request)
    return redirect('login')

# ================= REGISTRO =================
def registrar_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Usuário criado com sucesso!")
            return redirect('dashboard')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, 'gastos/registrar.html', {'form': form})

# ================= DASHBOARD =================
@login_required
def dashboard(request):
    # Filtra os gastos do usuário
    gastos = Gasto.objects.filter(usuario=request.user)

    # Filtro por datas
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')
    if inicio and fim:
        gastos = gastos.filter(data__range=[inicio, fim])

    # Totais gerais
    total = gastos.aggregate(Sum('valor'))['valor__sum'] or 0

    hoje = timezone.now()

    # Mês atual
    mes_atual = gastos.filter(
        data__year=hoje.year,
        data__month=hoje.month
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    # Mês passado
    mes_passado_num = hoje.month - 1 if hoje.month > 1 else 12
    ano_mes_passado = hoje.year if hoje.month > 1 else hoje.year - 1
    mes_passado = gastos.filter(
        data__year=ano_mes_passado,
        data__month=mes_passado_num
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    # Meta e progresso
    meta = MetaFinanceira.objects.filter(usuario=request.user).first()
    progresso = 0
    if meta and meta.valor_meta > 0:
        progresso = (mes_atual / meta.valor_meta) * 100
        if progresso > 100:
            progresso = 100

    # ---------------- GASTOS POR CATEGORIA ----------------
    categorias_qs = gastos.values('categoria').annotate(total=Sum('valor')).order_by('categoria')
    categorias = [c['categoria'] for c in categorias_qs]
    totais_categorias = [float(c['total']) for c in categorias_qs]  # JS puro

    # ---------------- GASTOS DIÁRIOS (para gráfico de linha) ----------------
    # Agrupa gastos por dia e ordena
    gastos_por_dia_qs = gastos.values('data').annotate(total=Sum('valor')).order_by('data')
    dias = [g['data'].strftime("%d/%m/%Y") for g in gastos_por_dia_qs]
    totais_dias = [float(g['total']) for g in gastos_por_dia_qs]

    # Calcula soma acumulada diária
    totais_dias_acumulados = []
    acumulado = 0
    for valor in totais_dias:
        acumulado += valor
        totais_dias_acumulados.append(acumulado)

    # Formulário para adicionar gasto
    form = GastoForm()

    return render(request, 'gastos/dashboard.html', {
        'gastos': gastos,
        'total': total,
        'mes_atual': mes_atual,
        'mes_passado': mes_passado,
        'meta': meta,
        'progresso': progresso,
        'categorias': categorias,
        'totais_categorias': totais_categorias,
        'dias': dias,
        'totais_dias_acumulados': totais_dias_acumulados,
        'form': form
    })

# ================= ADICIONAR =================
@login_required
def adicionar_gasto(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.usuario = request.user
            gasto.save()
    return redirect('dashboard')

# ================= EDITAR =================
@login_required
def editar_gasto(request, id):
    gasto = get_object_or_404(Gasto, id=id, usuario=request.user)
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = GastoForm(instance=gasto)
    return render(request, 'gastos/editar.html', {'form': form})

# ================= EXCLUIR =================
@login_required
def excluir_gasto(request, id):
    gasto = get_object_or_404(Gasto, id=id, usuario=request.user)
    gasto.delete()
    return redirect('dashboard')

# ================= EXPORTAR EXCEL =================
@login_required
def exportar_excel(request):
    gastos = Gasto.objects.filter(usuario=request.user).values()
    df = pd.DataFrame(gastos)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="gastos.xlsx"'
    df.to_excel(response, index=False)
    return response

# ================= IMPORTAR EXCEL =================
@login_required
def importar_excel(request):
    if request.method == 'POST' and request.FILES.get('arquivo'):
        arquivo = request.FILES['arquivo']
        try:
            df = pd.read_excel(arquivo)
            obrigatorios = ['data', 'categoria', 'descricao', 'valor']
            if not all(col in df.columns for col in obrigatorios):
                messages.error(request, 'O arquivo deve conter as colunas: Data, Categoria, Descrição, Valor')
                return redirect('dashboard')

            for _, row in df.iterrows():
                if pd.isna(row['data']) or pd.isna(row['categoria']) or pd.isna(row['descricao']) or pd.isna(row['valor']):
                    continue
                Gasto.objects.create(
                    usuario=request.user,
                    data=row['data'] if isinstance(row['data'], datetime) else pd.to_datetime(row['data']),
                    categoria=row['categoria'],
                    descricao=row['descricao'],
                    valor=float(row['valor'])
                )

            messages.success(request, 'Gastos importados com sucesso!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Erro ao importar Excel: {str(e)}')
            return redirect('dashboard')
    return redirect('dashboard')

# ================= GERAR PDF =================
@login_required
def gerar_pdf(request):
    gastos = Gasto.objects.filter(usuario=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_gastos.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elementos = []

    styles = getSampleStyleSheet()
    elementos.append(Paragraph("<b>Relatório de Gastos</b>", styles['Title']))
    elementos.append(Spacer(1, 0.5 * inch))

    dados = [["Data", "Categoria", "Descrição", "Valor"]]
    total = 0

    for gasto in gastos:
        dados.append([
            gasto.data.strftime("%d/%m/%Y"),
            gasto.categoria,
            gasto.descricao,
            f"R$ {gasto.valor}"
        ])
        total += gasto.valor

    dados.append(["", "", "Total", f"R$ {total}"])

    tabela = Table(dados)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
    ]))

    elementos.append(tabela)
    doc.build(elementos)

    return response
