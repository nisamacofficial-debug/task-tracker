from django.contrib import admin
from django.urls import path
from login import views

urlpatterns = [
    # Auth
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),

    # Main Menu
    path("menu/", views.menu_view, name="menu"),

    # Issues
    path("manage_issues/", views.manage_issues_view, name="manage_issues"),
    path("add-issue/", views.add_issue_view, name="add_issue"),
    path("edit-issue/<int:issue_id>/", views.edit_issue, name="edit_issue"),
    path("delete-issue/<int:issue_id>/", views.delete_issue, name="delete_issue"),
    path("update-status/<int:issue_id>/", views.update_status, name="update_status"),
    path("update-field/<int:issue_id>/", views.update_field, name="update_field"),
    path("update-due-date/<int:id>/", views.update_due_date),
    path("update-tag/<int:id>/", views.update_tag),

    # Comments (FIXED)
    path("issues/<int:issue_id>/comments/", views.issue_comments, name="issue_comments"),
    path("add-comment/<int:issue_id>/", views.add_comment, name="add_comment"),  # ✔ Correct & only one

    # Bulk delete
    path("delete-multiple/", views.delete_multiple_issues, name="delete_multiple_issues"),
    path("delete-all/", views.delete_all_issues, name="delete_all_issues"),

    # Reports
    path("reports/", views.reports_view, name="reports"),
    path("due-today/", views.due_today_view, name="due_today"),
    path("dashboard/closed/", views.dashboard_closed, name="dashboard_closed"),

    # Exports (FIXED)
    path("export/excel/", views.export_issues_excel, name="export_issues_excel"),
    path("export/csv/", views.export_issues_csv, name="export_issues_csv"),

    # Admin
    path('admin/', admin.site.urls),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)