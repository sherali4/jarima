from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.views.generic import TemplateView


urlpatterns = [
    
    path('logout/', views.logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('signup/', views.signup_view, name='signup'),  # ro‘yxatdan o‘tish
    path('topshiriq/create/', views.topshiriq_create_view, name='topshiriq_create'),  # topshiriq yaratish
    path('auth/', include('social_django.urls', namespace='social')),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('jarima/', views.upload_excel, name='upload_excel'),  # jarima sahifasi
    path('ajax/load-hisobot-davri/', views.load_hisobot_davri, name='ajax_load_hisobot_davri'),
    path('jarima/excel/list/', views.excelupload_list, name='excelupload_list'),
    path('jarima/dalolatnoma/list/', views.dalolatnoma_list, name='dalolatnoma_list'),
    path('jarima/kiritish/<int:pk>/', views.KorxonaUpdateView.as_view(), name='item_detail'),
    path('jarima/jarima_qilinmagan/', views.JarimaQilinmagan, name='jarima_qilinmagan'),
    path('jarima/excel/download/', views.Exceluploadtoexcel, name='excel_download'),
    path('jarima/dalolatnoma/<int:pk>/', views.DalolatnomaUpdateView.as_view(), name='dalolatnoma_update'),
    path('jarima/dalolatnoma/from-excel/<int:excel_id>/', views.dalolatnoma_from_excelupload, name='dalolatnoma_from_excel'),
    path('tools/parse_pdf/', views.parse_pdf, name='parse_pdf'),

    




    path('', views.index, name='index'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)