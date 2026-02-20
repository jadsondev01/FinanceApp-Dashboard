from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='gastos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('registrar/', views.registrar_usuario, name='registrar'),

    path('adicionar/', views.adicionar_gasto, name='adicionar_gasto'),
    path('importar/', views.importar_excel, name='importar_excel'),
    path('exportar/', views.exportar_excel, name='exportar_excel'),
    path('editar/<int:id>/', views.editar_gasto, name='editar_gasto'),
    path('excluir/<int:id>/', views.excluir_gasto, name='excluir_gasto'),
    path('pdf/', views.gerar_pdf, name='gerar_pdf'),
]
