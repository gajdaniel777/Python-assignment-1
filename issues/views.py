import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

def getIssuesById(request: Request) -> Response:
    issue_id = int(request.GET.get('id'))

    with open('issues.json', 'r') as f:
        issues = json.load(f)  
    for issue in issues:
        if issue['id'] == issue_id:
            return Response({
                "issue": issue
            })

    return JsonResponse({'error': 'Issue not found'}, status=404)

def getIssuesByStatus(request: Request) -> Response:
    issue_status = request.GET.get('status')

    with open('issues.json', 'r') as f:
        issues = json.load(f)

    li = []
    for issue in issues:
        if issue['status'] == issue_status:
            li.append(issue)

    return Response({
        "issues": li
    })

    


def getIssues(request: Request) -> Response:

    with open('issues.json', 'r') as f:
        issues = json.load(f)  

    return Response({
        "issues": issues
    })


def getIss(request: Request) -> Response:
    if request.GET.get('id') is not None:
        return getIssuesById(request)
    elif request.GET.get('status') is not None:
        return getIssuesByStatus(request)    
    return getIssues(request)


def createIssue(request: Request):
    data = request.data

    with open('issues.json','r') as f:
        issues = json.load(f)

    new_issue = {
        "id": data["id"],
        "title": data["title"],
        "description": data["description"],
        "status": data["status"],
        "priority": data["priority"],
        "reporter_id": data["reporter_id"],
        "created_at": data["created_at"]
    }

    issues.append(new_issue)

    with open('issues.json','w') as f:
        json.dump(issues,f,indent=2)

    return Response({
        "new_issue": new_issue
    })

#Here I wrote this with the help of AI to call get and post method with same endpoint.
@api_view(['GET', 'POST'])
def issues(request: Request) -> Response:
    if request.method == 'GET':
        return getIss(request)    
    return createIssue(request)