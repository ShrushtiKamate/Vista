# # core/views.py
# from django.shortcuts import render, redirect
# from .models import Certificate
# from django.contrib import messages
# from inspector.models import Feedback

# from inspector.models import Feedback

# from django.http import JsonResponse

# from django.views.decorators.csrf import csrf_exempt   # ✅ ADD THIS

# #common
# def homepage(request):
#     return render(request, 'homepage.html')

# def options(request):
#     return render(request, 'options.html')



# #aicte
# def aicte_login(request):
#     return render(request, 'aicte/aicte_login.html')

# def aictemain(request):
#     aicte = request.GET.get('aicte', 'Guest')
#     return render(request, 'aicte/aictemain.html',{'aicte': aicte})

# def aicte_institutes(request):
#     return render(request, 'aicte/aicte_institutes.html')


# def aicte_inspector(request):
#     return render(request, 'aicte/aicte_inspector.html')


# def aicte_annexure(request):
#     return render(request, 'aicte/aicte_annexure.html')


# def regionmap(request):
#     return render(request, 'aicte/regionmap.html')


# def region2(request):
#     return render(request, 'aicte/region2.html')


# def anamoly(request):
#     return render(request, 'inspector/anamoly.html')




# #college

# def college_login(request):
#     return render(request, 'institute/college_login.html')


# def index(request):
#     return render(request, 'institute/index.html')

# def signup(request):
#     return render(request, 'institute/signup.html')

# def upload_certificate(request):
#     return render(request,'institute/upload_certificate.html')


# def annexure(request):
#     return render(request,'institute/annexure.html')

# def upload_image(request):
#     return render(request,'institute/upload_image.html')

# def upload_excel(request):
#     return render(request,'institute/upload_excel.html')

# def classroom_upload(request):
#     return render(request,'institute/classroom_upload.html')

# def canteen_upload(request):
#     return render(request,'institute/canteen_upload.html')

# def report3(request):
#     return render(request,'institute/report3.html')








# #inspector

# def view_reports(request):
#     user_id = request.GET.get('user_id', 'Guest')
#     return render(request, 'inspector/view_reports.html',{'user_id': user_id})


# def discussion_forum(request):
#     return render(request, 'inspector/discussion_forum.html')

# def view_feedback(request):
#     college_name = request.session.get('college_name')  # Get college name from session
#     if not college_name:
#         messages.error(request, "College information is missing!")
#         return redirect('college_login')  # Redirect to a default page if college name is not found

#     # Retrieve feedback entries for the specific college
#     feedback_entry = Feedback.objects(college_name=college_name)
    
#     for feedback in feedback_entry:
#             print(f"Inspector Name: {feedback.inspector_name}, College Name: {feedback.college_name}, Feedback: {feedback.feedback_text}")

#     context = {
#         'feedback_entry': feedback_entry,
#         'college_name': college_name  # Pass college name to the template
#     }
#     return render(request, 'feedback_view.html', context)  # Updated template name

# def inspector_login(request):
#     return render(request, 'inspector/inspector_login.html')

# def view_image(request):
#     return render(request, 'inspector/view_image.html')

# def annexure(request):
#     return render(request,'inspector/annexure.html')

# def report2(request):
#     return render(request,'inspector/report2.html')


# def feedback(request):
#     return render(request,'inspector/feedback.html')


# def pattern_pred(request):
#     return render(request,'inspector/pattern_pred.html')



# def view_classroom(request):
#     return render(request,'inspector/view_classroom.html')


# def view_lab(request):
#     return render(request,'inspector/view_lab.html')


# def view_washroom(request):
#     return render(request,'inspector/view_washroom.html')


# def view_parking(request):
#     return render(request,'inspector/view_parking.html')


# def view_pwd(request):
#     return render(request,'inspector/view_pwd.html')


# def view_canteen(request):
#     return render(request,'inspector/view_canteen.html')

# def lab_upload(request):
#     return render(request,'institute/lab_upload.html')

# def pwd_upload(request):
#     return render(request,'institute/pwd_upload.html')

# def parking_upload(request):
#     return render(request,'institute/parking_upload.html')

# def washroom_upload(request):
#     return render(request,'institute/washroom_upload.html')

# def report3(request):
#     # Fetch all feedback entries or filter as needed
#     feedback_entries = Feedback.objects.all()

#     # Pass data to the template
#     context = {'feedback_entries': feedback_entries}
#     return render(request, 'institute/report3.html', context)


# @csrf_exempt 
# def generate_report(request):
#     print("Generate report API called")

#     return JsonResponse({
#         "status": "success",
#         "message": "Report generated successfully"
#     })






from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from inspector.models import Feedback
from institute.models import Images
import requests
import os
from django.http import FileResponse, HttpResponseNotFound

# =========================
# COMMON
# =========================
def homepage(request):
    return render(request, 'homepage.html')

def options(request):
    return render(request, 'options.html')


# =========================
# AICTE
# =========================
def aicte_login(request):
    return render(request, 'aicte/aicte_login.html')

def aictemain(request):
    aicte = request.GET.get('aicte', 'Guest')
    return render(request, 'aicte/aictemain.html', {'aicte': aicte})

def aicte_institutes(request):
    return render(request, 'aicte/aicte_institutes.html')

def aicte_inspector(request):
    return render(request, 'aicte/aicte_inspector.html')

def aicte_annexure(request):
    return render(request, 'aicte/aicte_annexure.html')

def regionmap(request):
    return render(request, 'aicte/regionmap.html')

def region2(request):
    return render(request, 'aicte/region2.html')

def anamoly(request):
    return render(request, 'inspector/anamoly.html')


# =========================
# COLLEGE
# =========================
def college_login(request):
    return render(request, 'institute/college_login.html')

def index(request):
    return render(request, 'institute/index.html')

def signup(request):
    return render(request, 'institute/signup.html')

def upload_certificate(request):
    return render(request, 'institute/upload_certificate.html')

def annexure(request):
    return render(request, 'institute/annexure.html')

def upload_image(request):
    return render(request, 'institute/upload_image.html')

def upload_excel(request):
    return render(request, 'institute/upload_excel.html')

def classroom_upload(request):
    return render(request, 'institute/classroom_upload.html')

def canteen_upload(request):
    return render(request, 'institute/canteen_upload.html')

def lab_upload(request):
    return render(request, 'institute/lab_upload.html')

def pwd_upload(request):
    return render(request, 'institute/pwd_upload.html')

def parking_upload(request):
    return render(request, 'institute/parking_upload.html')

def washroom_upload(request):
    return render(request, 'institute/washroom_upload.html')

def report3(request):
    return render(request, 'institute/report3.html')


# =========================
# INSPECTOR
# =========================
def inspector_login(request):
    return render(request, 'inspector/inspector_login.html')

def view_reports(request):
    user_id = request.GET.get('user_id', 'Guest')
    return render(request, 'inspector/view_reports.html', {'user_id': user_id})

def discussion_forum(request):
    return render(request, 'inspector/discussion_forum.html')


def view_feedback(request):
    college_name = request.session.get('college_name')

    if not college_name:
        messages.error(request, "College information is missing!")
        return redirect('college_login')

    feedback_entry = Feedback.objects(college_name=college_name)

    context = {
        'feedback_entry': feedback_entry,
        'college_name': college_name
    }
    return render(request, 'inspector/feedback_view.html', context)


# =========================
# 🔥 IMAGE VIEW LOGIC (FIXED)
# =========================
def view_classroom(request):
    college_name = request.session.get('college_name')

    record = Images.objects(college=college_name).first()

    images = []

    if record and record.classroom:
        for item in record.classroom:
            images.extend(item.get('url', []))  # flatten

    return render(request, 'inspector/view_classroom.html', {
        'images': images
    })


# def view_classroom(request):
#     college_name = request.session.get('college_name')

#     print("College Name:", college_name)

#     record = Images.objects(college=college_name).first()

#     print("Record:", record)

#     images = []

#     if record and record.classroom:
#         print("Classroom Data:", record.classroom)

#         for item in record.classroom:
#             print("Item:", item)
#             images.extend(item.get('url', []))

#     print("Final Images:", images)

#     return render(request, 'inspector/view_classroom.html', {
#         'images': images
#     })


def view_lab(request):
    college_name = request.session.get('college_name')

    record = Images.objects(college=college_name).first()

    images = []

    if record and record.lab:
        for item in record.lab:
            images.extend(item.get('url', []))

    return render(request, 'inspector/view_lab.html', {
        'images': images
    })


def view_washroom(request):
    college_name = request.session.get('college_name')

    record = Images.objects(college=college_name).first()
    images = record.washroom if record else []

    return render(request, 'inspector/view_washroom.html', {
        'images': images
    })


def view_parking(request):
    college_name = request.session.get('college_name')

    record = Images.objects(college=college_name).first()
    images = record.parking if record else []

    return render(request, 'inspector/view_parking.html', {
        'images': images
    })


def view_pwd(request):
    college_name = request.session.get('college_name')

    record = Images.objects(college=college_name).first()
    images = record.pwd if record else []

    return render(request, 'inspector/view_pwd.html', {
        'images': images
    })


def view_canteen(request):
    college_name = request.session.get('college_name')

    record = Images.objects(college=college_name).first()
    images = record.canteen if record else []

    return render(request, 'inspector/view_canteen.html', {
        'images': images
    })


def view_image(request):
    return render(request, 'inspector/view_image.html')


def report2(request):
    return render(request, 'inspector/report2.html')

def feedback(request):
    return render(request, 'inspector/feedback.html')

# def pattern_pred(request, filename):
#     file_path = os.path.join("media", "docs", filename)


def pattern_pred(request, filename):
    import os
    import requests
    from django.http import FileResponse, HttpResponseNotFound

    print("📄 Requested file:", filename)

    # 🔥 STEP 1: CALL FASTAPI (GENERATE REPORT)
    try:
        response = requests.post(
            "http://127.0.0.1:8001/generate-pattern-report/",
            json={"filename": filename}
        )
        print("FastAPI response:", response.status_code)
    except Exception as e:
        print("❌ FastAPI call failed:", e)

    # 🔥 STEP 2: OPEN GENERATED FILE (NOT ORIGINAL)
    file_path = os.path.join("media", "docs", f"ANALYSIS_{filename}")

    print("📂 Opening file:", file_path)

    if not os.path.exists(file_path):
        return HttpResponseNotFound("Generated file not found")

    return FileResponse(open(file_path, "rb"), content_type="application/pdf")


# =========================
# API (FIXED)
# =========================
@csrf_exempt
def generate_report(request):
    print("Generate report API called")

    return JsonResponse({
        "status": "success",
        "message": "Report generated successfully"
    })

