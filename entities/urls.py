
from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static


app_name = 'entities'
urlpatterns = [
        path('', views.EntityListView.as_view(), name='index'),
        path('<int:pk>/', views.EntityDetailView.as_view(), name ='details'),
        #path('<int:pk>/', views.ProjectDetailView.as_view(), name='details'),
        ##path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category_details'),
        #path('category/', views.category_view, name='category_details'),
        #path('category/<int:category_id>/', views.category_view, name='category_details'),
        #path('<int:project_id>/slides/', views.slides, name='slides'),
        #path('<int:project_id>/slides/<int:image_id>', views.slides, name='slides'),
    ] 

