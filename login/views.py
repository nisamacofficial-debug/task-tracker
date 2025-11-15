from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Issue,Comment,IssueDocument
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("Here")
            login(request, user)
            return redirect("reports")   # replace with your dashboard route name
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "logins/login.html")

def menu_view(request):
    return render(request, "logins/menu.html")

@login_required
def manage_issues_view(request):
    issues = Issue.objects.all().order_by('-created_at')
    return render(request, 'manage_issues/manage_issues.html', {'issues': issues})

@login_required
def add_issue_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        status = request.POST.get("status")
        due_date = request.POST.get("due_date")
        tag = request.POST.get("tags", "")
        print(" TAG ", tag)
        Issue.objects.create(
            title=title,
            description=description,
            status=status,
            due_date=due_date if due_date else None,
            created_by=request.user,
            tag=tag
        )
        return redirect("manage_issues")
    return render(request, "manage_issues/add_issue.html")


@csrf_exempt
def update_status(request, issue_id):
    if request.method == "POST":
        data = json.loads(request.body)
        new_status = data.get("status")
        try:
            issue = Issue.objects.get(id=issue_id)
            issue.status = new_status
            issue.save()
            return JsonResponse({"success": True})
        except Issue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Issue not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

@csrf_exempt
def add_comment(request,issue_id):
    if request.method == "POST":
        data = json.loads(request.body)
        #issue_id = data.get("issue_id")
        print("issue id  ", issue_id)
        text = data.get("text", "").strip()
        if not text:
            return JsonResponse({"success": False, "error": "Empty comment"})
        try:
            issue = Issue.objects.get(id=issue_id)
            comment = Comment.objects.create(
                issue=issue, user=request.user, text=text
            )
            return JsonResponse({
                "success": True,
                "comment": {
                    "user": comment.user.username,
                    "text": comment.text,
                    "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
                }
            })
        except Issue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Issue not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

def issue_comments(request, issue_id):
    try:
        issue = Issue.objects.get(id=issue_id)
        comments = issue.comments.all().order_by("-created_at")
        for comment in comments:
            print("Here", issue_id)
            print(comment)
        data = [
            {
                "user": comment.user.username,
                "text": comment.text,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for comment in comments
        ]

        return JsonResponse({"success": True, "comments": data})
    except Issue.DoesNotExist:
        return JsonResponse({"success": False, "error": "Issue not found"})

def edit_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == "POST":
        issue.title = request.POST.get("title")
        issue.description = request.POST.get("description")
        issue.status = request.POST.get("status")
        issue.due_date = request.POST.get("due_date") or None
        issue.tags = request.POST.get("tags")
        issue.save()
        # 🔥 SAVE UPLOADED FILES
        if request.FILES.getlist("documents"):
            for f in request.FILES.getlist("documents"):
                IssueDocument.objects.create(issue=issue, file=f)
                
        return redirect("manage_issues")
    return render(request, "manage_issues/edit_issue.html", {"issue": issue})

@csrf_exempt  # (Optional if using JS CSRF token correctly)
def delete_issue(request, issue_id):
    if request.method == "POST":
        try:
            issue = Issue.objects.get(id=issue_id)
            issue.delete()
            return JsonResponse({"success": True})
        except Issue.DoesNotExist:
            return JsonResponse({"success": False, "error": "Issue not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

def reports_view(request):
    qs = Issue.objects.all().values('id','status','created_at','tag')
    # convert datetimes to ISO strings
    issues_list = []
    print("hERE")
    from collections import defaultdict
    tag_counts = defaultdict(int)
    for issue in qs:
        if issue['tag']:
            # Split multiple tags like: "UI, Backend, Bug"
            for tag in issue['tag'].split(","):
                t = tag.strip()
                if t:
                    tag_counts[t] += 1

    # Convert dict to normal JSON-serializable form
    tag_counts = dict(tag_counts)
    for i in qs:
        issues_list.append({
            'id': i['id'],
            'status': i['status'],
            'created_at': i['created_at'].isoformat() if i['created_at'] else None,
             "tag_counts_json": json.dumps(tag_counts),
        })
    context = {'issues_json': json.dumps(issues_list)}
    return render(request, 'Reports/reports.html', context)




from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)  # This clears the session and logs out the user
    return redirect('/login')  # Redirect to login page after logout

from datetime import date, timedelta
def due_today_view(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    due_today_issues = Issue.objects.filter(due_date=today).order_by('due_date','created_at')
    count_due_today = due_today_issues.count()
    tagCounts =  Issue.objects.count()
    count_due_tomorrow = Issue.objects.filter(due_date=tomorrow).count()
    all_due_issues = Issue.objects.filter(due_date__lte=today).order_by('due_date')
    count_due_all = Issue.objects.filter(due_date__lte=today).count()
    
    context = {
        'count_due_all': count_due_all,
        'due_today_issues': due_today_issues,
        'count_due_today': count_due_today,
        "all_due_issues": all_due_issues,
        'count_due_tomorrow': count_due_tomorrow,
    }
    return render(request, 'logins/due_today.html', context)


def dashboard_closed(request):
    closed_issues = Issue.objects.filter(status="closed")
    total_closed = Issue.objects.filter(status="closed").count()
    total_open = Issue.objects.filter(status="Open").count()
    total_in_progress = Issue.objects.filter(status="In Progress").count()

    context = {
        "closed_issues": closed_issues,
        "total_closed": total_closed,
        "total_open": total_open,
        "total_in_progress": total_in_progress,
    }
    return render(request, "logins/dashboard_closed.html", context)


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        # Create user
        user = User.objects.create_user(username=username, password=password)

        # Auto-login user
        login(request, user)

        return redirect("menu")  # Redirect to dashboard

    return render(request, "logins/signup.html")

def update_due_date(request, id):
    issue = Issue.objects.get(id=id)
    issue.due_date = request.POST.get("value") or None
    issue.save()
    return JsonResponse({"success": True})

def update_tag(request, id):
    issue = Issue.objects.get(id=id)
    issue.tag = request.POST.get("value")
    issue.save()
    return JsonResponse({"success": True})

@login_required
@require_POST
def update_field(request, issue_id):
    """
    Updates a single field of Issue model.
    Expects: { "field": "title", "value": "New title" }
    """
    print("Hellllo")
    issue = get_object_or_404(Issue, id=issue_id)
    data = json.loads(request.body)
    field = data.get("field")
    value = data.get("value")
    print("Hello ", value)

    if field not in ["title", "description", "status", "due_date", "tag"]:
        return JsonResponse({"error": "Invalid field"}, status=400)

    # Special handling for tags (comma separated)
    if field == "tags":
        issue.tags = value  # save comma-separated
    else:
        setattr(issue, field, value)

    issue.save()

    return JsonResponse({"success": True, "field": field, "value": value})


from openpyxl import Workbook
from django.utils.timezone import localtime
def export_issues_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Issues"

    # Header
    ws.append([
        "ID", "Title", "Description", "Status", "Tag", "Due Date", "Created At"
    ])

    for issue in Issue.objects.all().order_by('-created_at'):
        ws.append([
            issue.id,
            issue.title,
            issue.description,
            issue.status,
            issue.tag,
            issue.due_date.strftime("%Y-%m-%d") if issue.due_date else "",
            localtime(issue.created_at).strftime("%Y-%m-%d %H:%M"),
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="issues.xlsx"'
    wb.save(response)
    return response

import csv
from django.http import HttpResponse

def export_issues_csv(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="issues.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "ID", "Title", "Description", "Status", "Tag", "Due Date", "Created At"
    ])

    for issue in Issue.objects.all().order_by('-created_at'):
        writer.writerow([
            issue.id,
            issue.title,
            issue.description,
            issue.status,
            issue.tag,
            issue.due_date.strftime("%Y-%m-%d") if issue.due_date else "",
            localtime(issue.created_at).strftime("%Y-%m-%d %H:%M"),
        ])

    return response

@login_required
def delete_multiple_issues(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        ids = data.get("ids", [])

        Issue.objects.filter(id__in=ids).delete()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

@login_required
def delete_all_issues(request):
    if request.method == "POST":
        Issue.objects.all().delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


@login_required
def add_issue_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        status = request.POST.get("status")
        due_date = request.POST.get("due_date")
        tags = request.POST.get("tags", "")

        issue = Issue.objects.create(
            title=title,
            description=description,
            status=status,
            due_date=due_date if due_date else None,
            created_by=request.user,
            tag=tags
        )

        # Save uploaded documents
        for uploaded_file in request.FILES.getlist("documents"):
            IssueDocument.objects.create(issue=issue, file=uploaded_file)

        return redirect("manage_issues")

    return render(request, "manage_issues/add_issue.html")

