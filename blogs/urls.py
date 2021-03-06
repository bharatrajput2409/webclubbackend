from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('searchBlogWithTag',views.searchBlogWithTag),
    path('getblogs',views.loadBlogs),
    path('getblogs/<id>',views.loadBlog),
    path('addblog',views.postBlog),
    path('googlelogin',views.validate_google_login_token, name='google_login'),
    # path('create_club_member_data',views.create_club_member_data)
    path('deleteblog',views.deleteblog,name='delete_blog')
]