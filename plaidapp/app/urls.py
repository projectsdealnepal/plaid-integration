from django.urls import path
from django.conf.urls import url, include


from . import views
# from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    # url('', views.login_success),
    # path('', include(tf_urls)),
    url('verify/', views.index, name='index'),
    url('^signin/$', views.signin, name='signin'),
    url('^select/$', views.accounts, name='institution'),
    url('^accounts/$', views.accounts, name='add'),
    url('^signup/', views.register, name='register'),
    # url('bank_login/', views.login, name='login'),
    url('^logout/$', views.logout_view, name='logout'),
    url('transaction/', views.transaction, name='transaction'),
    url('^add_account/$', views.connect, name='add_account'),
    url('^change/$', views.change_password, name='change'),
    url('^profile/$', views.profile, name='profile'),
    # path('', include(tf_urls)),

]