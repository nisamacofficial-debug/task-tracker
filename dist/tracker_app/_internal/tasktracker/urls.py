"""
URL configuration for tasktracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.urls import path
from login import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path('admin/', admin.site.urls),
    path('menu/', views.menu_view, name='menu'),
    path('manage_issues/', views.manage_issues_view, name='manage_issues'),
    path('add-issue/', views.add_issue_view, name='add_issue'),
    path('update-status/<int:issue_id>/', views.update_status, name='update_status'),
    path("issues/<int:issue_id>/comments/", views.issue_comments, name="issue_comments"),
    path("add-comment/", views.add_comment, name="add_comment"),
    path("add-comment/<int:issue_id>/", views.add_comment, name="add_comment"),
    #path("add-comment/2/", views.add_comment, name="add_comment"),
    path("edit-issue/<int:issue_id>/", views.edit_issue, name="edit_issue"),
    path("delete-issue/<int:issue_id>/", views.delete_issue, name="delete_issue"),
    path('reports/', views.reports_view, name='reports'),
path('logout/', views.logout_view, name='logout'),
path('due-today/', views.due_today_view, name='due_today'),
path("dashboard/closed/", views.dashboard_closed, name="dashboard_closed"),
path("signup/", views.signup_view, name="signup"),   # NEW
path("update-due-date/<int:id>/", views.update_due_date),
path("update-tag/<int:id>/", views.update_tag),
    path("update-field/<int:issue_id>/", views.update_field, name="update_field"),
    path("export_issues_csv/", views.signup_view, name="export_issues_csv"),   # NEW
 path("export_issues_excel/", views.signup_view, name="export_issues_excel"),   # NEW
  path('export/excel/', views.export_issues_excel, name='export_issues_excel'),
    path('export/csv/', views.export_issues_csv, name='export_issues_csv'),
    path("delete-multiple/", views.delete_multiple_issues, name="delete_multiple_issues"),
path("delete-all/", views.delete_all_issues, name="delete_all_issues"),
path("", views.login_view, name="login"),
]
