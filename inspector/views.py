# from django.shortcuts import render, redirect
# from django.contrib import messages
# from mongoengine import DoesNotExist
# from django.contrib.auth.decorators import login_required
# from core.models import Certificate
# from django.views.decorators.http import require_http_methods
# from .models import Post, Reply,Inspector
# from django.utils import timezone
# from django.http import FileResponse, HttpResponseNotFound
# from institute.models import mandatory_dis
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from inspector.models import Feedback
# import io

# def login_view(request):
#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         password = request.POST.get('password')

#         try:
#             # Authenticate the user
#             user = Inspector.objects.get(user_id=user_id, password=password)
#             # Save session data
#             request.session['user_id'] = str(user.user_id)
#             return redirect('view_reports')  # Redirect to dashboard
#         except DoesNotExist:
#             messages.error(request, 'Invalid credentials')
#             return redirect('inspector_login')

#     return render(request, 'inspector/inspector_login.html')

# def inspector_logout(request):
#     request.session.flush()
#     return render(request, 'options.html')



# def view_reports(request):
#     return render(request, 'inspector/view_reports.html')

# # @login_required
# # def discussion_forum(request):
# #     posts = Post.objects.all().order_by('-timestamp')
# #     context = {
# #         'posts': posts,
# #         'user': request.user,
# #     }
# #     return render(request, 'inspector/discussion_forum.html', context)

# # @login_required
# # def view_discussion(request, post_id):
# #     post = Post.objects.get(id=post_id)
# #     replies = Reply.objects.filter(post=post).order_by('timestamp')
# #     context = {
# #         'post': post,
# #         'replies': replies,
# #         'user': request.user,
# #     }
# #     return render(request, 'inspector/discussion.html', context)

# # @login_required
# # def create_post(request):
# #     if request.method == 'POST':
# #         content = request.POST.get('content')
# #         if content.strip():  # Check if content is not just whitespace
# #             Post.objects.create(
# #                 user1=request.user,
# #                 post_content=content,
# #                 # Remove timestamp=timezone.now() as it's handled by auto_now_add
# #             )
# #             messages.success(request, 'Post created successfully!')
# #         else:
# #             messages.error(request, 'Post content cannot be empty!')
# #     return redirect('discussion_forum')

# # @login_required
# # def create_reply(request, post_id):
# #     try:
# #         post = Post.objects.get(id=post_id)
# #         if request.method == 'POST':
# #             content = request.POST.get('content')
# #             if content.strip():
# #                 Reply.objects.create(
# #                     user=request.user,
# #                     post=post,
# #                     reply_content=content,
# #                     # Remove timestamp=timezone.now()
# #                 )
# #                 messages.success(request, 'Reply added successfully!')
# #             else:
# #                 messages.error(request, 'Reply content cannot be empty!')
# #     except Post.DoesNotExist:
# #         messages.error(request, 'Post not found!')
# #     return redirect('view_discussion', post_id=post_id)


# from django.shortcuts import render, redirect
# from django.contrib import messages
# import pymongo
# from inspection_system.settings import db
# from institute.models import certificate
# from django.views.decorators.http import require_http_methods
# from django.http import HttpResponse
# from .models import Inspector,deficiency_report

# from django.shortcuts import get_object_or_404


# def view_certificates(request):
#     """
#     View function for inspectors to view certificates uploaded by institutes
#     """

#     try:
#         # Using MongoEngine to query certificates
#         uploaded_certificates = certificate.objects.all()

#         # Prepare certificate details
#         certificate_details = []
#         for cert in uploaded_certificates:
#             certificate_details.append({
#                 'name': cert.name,
#                 'college_name': cert.college_name,
#                 'id': str(cert.id)
#             })

#         return render(request, 'inspector/view_certificates.html',{'certificates': certificate_details})

#     except Exception as e:
#         # Log the error and show a user-friendly message
#         print(f"Error retrieving certificates: {str(e)}")
#         messages.error(request, "An error occurred while retrieving certificates")
#         return render(request, 'inspector/view_certificates.html')
# from django.http import FileResponse, Http404

# def download_uploaded_certificate(request, certificate_id):
#     """
#     Download function for specific uploaded certificate.
#     """
#     try:
#         # Find the specific certificate by ID
#         cert = certificate.objects.get(id=certificate_id)

#         # Ensure the file field exists and is accessible
#         if not cert.file:
#             raise ValueError("No file associated with this certificate.")

#         # Create a response with the file
#         response = FileResponse(cert.file, content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{cert.name}.pdf"'
#         return response

#     except certificate.DoesNotExist:
#         messages.error(request, "Certificate not found.")
#         return redirect('view_certificates')
#     except ValueError as e:
#         messages.error(request, str(e))
#         return redirect('view_certificates')
#     except Exception as e:
#         print(f"Error downloading certificate: {str(e)}")
#         messages.error(request, "An error occurred while downloading the certificate.")
#         return redirect('view_certificates')


# def submit_feedback(request):
#     if request.method == 'POST':
#         feedback_text = request.POST.get('feedback')
#         # college_name = request.session.get('college') # Ensure this is passed in the form
#         inspector_name = request.session.get('user_id')  # Get inspector name from session
#         inspector = Inspector.objects.get(user_id=inspector_name)
#         college_name = inspector.college    
#         file = request.FILES['manual_report']

#         if not inspector_name:
#             messages.error(request, "User  not logged in.")
#             return redirect('inspector_login')

#         if not inspector_name or not college_name:
#             messages.error(request, "Inspector or College information is missing!")
#             return redirect('feedback_page')  # Ensure this matches the URL name

#         if not feedback_text.strip():
#             print("Hello")
#             messages.error(request, "Feedback text cannot be empty!")
#             return redirect('feedback_page')
#         print(feedback_text)
#         # Save feedback
#         feedback_entry = Feedback(
#             inspector_name=inspector_name,
#             college_name=college_name,
#             feedback_text=feedback_text,
#             manual_report=file
#         )
#         feedback_entry.save()

#         messages.success(request, "Feedback submitted successfully!")
#         return redirect('feedback_page')  # Ensure this matches the URL name

#     return render(request, 'inspector/feedback.html')  # Render the feedback form for GET requests

# def feedback_page(request):
#     return render(request, 'inspector/feedback.html')  # Adjust the template path as needed

# def view_mandatory(request):
#     try:
#         # Check if user is logged in via session
#         if 'user_id' not in request.session:
#             return redirect('login')

#         # Get college name from session
#         inspector = request.session.get('user_id')

#         if not Inspector:
#             return HttpResponseNotFound("No college associated with this session")

#         inspector_real = Inspector.objects.get(user_id=inspector)
#         # Find the mandatory disclosure file for the specific college
#         mandatory_entry = mandatory_dis.objects.filter(college_name=inspector_real.college).first()

#         if not mandatory_entry or not mandatory_entry.file:
#             return HttpResponseNotFound("Mandatory disclosure file not found")

#         # Create a file-like object from the stored file
#         file_content = io.BytesIO(mandatory_entry.file.read())
        
#         # Prepare the file response
#         response = FileResponse(
#             file_content, 
#             as_attachment=True, 
#             filename=f"{inspector_real.college}_mandatory_disclosure.pdf"
#         )
        
#         return response

#     except Exception as e:
#         print(f"Error downloading mandatory file: {e}")
#         return HttpResponseNotFound("Error downloading file")
    

# from inspector.models import compliancereport

# def view_compliance(request):
#     try:
#         # Check if user is logged in via session
#         if 'user_id' not in request.session:
#             return redirect('inspector_login')

#         # Get college name from session
#         inspector = request.session.get('user_id')

#         if not Inspector:
#             return HttpResponseNotFound("No college associated with this session")

#         inspector_real = Inspector.objects.get(user_id=inspector)
#         # Find the mandatory disclosure file for the specific college
#         college = inspector_real.college

#         if not college:
#             return HttpResponseNotFound("No college associated with this session")

#         # Find the compliance file for the specific college
#         deficiency = compliancereport.objects.filter(college_name=college).first()

#         if not deficiency:
#             return HttpResponseNotFound("Compliance entry not found")

#         if not deficiency.report_file:
#             return HttpResponseNotFound("Compliance file not found")

#         # Create a file-like object from the stored file
#         file_content = io.BytesIO(deficiency.report_file.read())
        
#         # Prepare the file response
#         response = FileResponse(
#             file_content, 
#             as_attachment=True, 
#             filename=f"{college}_compliance_document.pdf"
#         )
        
#         return response

#     except Exception as e:
#         print(f"Error downloading compliance file: {str(e)}")  # Log the error message
#         messages.error(request, "An error occurred while downloading the file.")
#         return HttpResponseNotFound(f"Error downloading file: {str(e)}")
    
# from institute.models import Images 

# def view_category_images(request, category):
#     # Fetch the college name from the session
#     college_name = request.session.get('college_name')

#     # Fetch the images entry for the specific college
#     images_entry = Images.objects(college=college_name).first()

#     if not images_entry:
#         return render(request, 'category_images.html', {'error': 'No images found for the selected category.'})

#     # Map categories to their respective fields
#     category_map = {
#         'classroom': images_entry.classroom,
#         'lab': images_entry.lab,
#         'canteen': images_entry.canteen,
#         'pwd': images_entry.pwd,
#         'parking': images_entry.parking,
#         'washroom': images_entry.washroom,
#     }

#     # Retrieve the data for the specified category
#     category_data = category_map.get(category, [])

#     # Flatten URLs if necessary
#     image_urls = []
#     for item in category_data:
#         image_urls.extend(item.get('url', []))

#     return render(request, 'category_images.html', {'image_urls': image_urls, 'category': category})


# def view_deficiancy(request):   
#     try:
#         # Check if user is logged in via session
#         if 'user_id' not in request.session:
#             return redirect('inspector_login')

#         # Get college name from session
#         inspector = request.session.get('user_id')

#         if not Inspector:
#             return HttpResponseNotFound("No college associated with this session")

#         inspector_real = Inspector.objects.get(user_id=inspector)
#         # Find the mandatory disclosure file for the specific college
#         college = inspector_real.college
#         deficiency = deficiency_report.objects.filter(college=college).first()

#         if not deficiency:
#             return HttpResponseNotFound("Compliance entry not found")

#         if not deficiency.file:
#             return HttpResponseNotFound("Compliance file not found")

#         # Create a file-like object from the stored file
#         file_content = io.BytesIO(deficiency.file.read())
        
#         # Prepare the file response
#         response = FileResponse(
#             file_content, 
#             as_attachment=True, 
#             filename=f"{college}_deficiency_document.pdf"
#         )
        
#         return response

#     except Exception as e:
#         print(f"Error downloading deficiency file: {str(e)}")  # Log the error message
#         messages.error(request, "An error occurred while downloading the file.")
#         return HttpResponseNotFound(f"Error downloading file: {str(e)}")










from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import FileResponse, HttpResponse, HttpResponseNotFound
from mongoengine import DoesNotExist
import io

from institute.models import mandatory_dis 

from .models import Inspector, Feedback, deficiency_report, compliancereport
from institute.models import certificate, mandatory_dis, Images
from core.models import Certificate

import requests

# ---------------- LOGIN ---------------- #

def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')

        try:
            user = Inspector.objects.get(user_id=user_id, password=password)

            # Store session
            request.session['user_id'] = str(user.user_id)

            return redirect('view_reports')

        except DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return redirect('inspector_login')

    return render(request, 'inspector/inspector_login.html')


def inspector_logout(request):
    request.session.flush()
    return render(request, 'options.html')


# ---------------- DASHBOARD ---------------- #

# def view_reports(request):
#     return render(request, 'inspector/view_reports.html')

def view_reports(request):
    show_reports = request.GET.get('reports')

    if show_reports:
        return render(request, 'inspector/view_reports.html', {
            'show_reports': True
        })

    return render(request, 'inspector/view_reports.html')

def view_image(request):
    return render(request, 'inspector/view_image.html')


# ---------------- CERTIFICATES ---------------- #

def view_certificates(request):
    try:
        uploaded_certificates = certificate.objects.all()

        certificate_details = []
        for cert in uploaded_certificates:
            certificate_details.append({
                'name': cert.name,
                'college_name': cert.college_name,
                'id': str(cert.id)
            })

        return render(request, 'inspector/view_certificates.html', {
            'certificates': certificate_details
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, "Error retrieving certificates")
        return render(request, 'inspector/view_certificates.html')


def download_uploaded_certificate(request, certificate_id):
    try:
        cert = certificate.objects.get(id=certificate_id)

        if not cert.file:
            raise ValueError("No file found")

        response = FileResponse(cert.file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{cert.name}.pdf"'
        return response

    except certificate.DoesNotExist:
        messages.error(request, "Certificate not found")
        return redirect('view_certificates')

    except Exception as e:
        print(str(e))
        messages.error(request, "Error downloading file")
        return redirect('view_certificates')


# ---------------- FEEDBACK ---------------- #

def submit_feedback(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        inspector_id = request.session.get('user_id')

        if not inspector_id:
            messages.error(request, "Not logged in")
            return redirect('inspector_login')

        inspector = Inspector.objects.get(user_id=inspector_id)
        college_name = inspector.college

        file = request.FILES.get('manual_report')

        if not feedback_text.strip():
            messages.error(request, "Feedback cannot be empty")
            return redirect('feedback_page')

        Feedback.objects.create(
            inspector_name=inspector_id,
            college_name=college_name,
            feedback_text=feedback_text,
            manual_report=file
        )

        messages.success(request, "Feedback submitted successfully")
        return redirect('feedback_page')

    return render(request, 'inspector/feedback.html')


def feedback_page(request):
    return render(request, 'inspector/feedback.html')


# ---------------- MANDATORY FILE ---------------- #

def view_mandatory(request):
    try:
        inspector_id = request.session.get('user_id')

        if not inspector_id:
            return redirect('inspector_login')

        inspector = Inspector.objects.get(user_id=inspector_id)

        print("Inspector College:", inspector.college)

        mandatory_entry = mandatory_dis.objects.filter(
            college_name=inspector.college
        ).first()

        print("Mandatory Entry:", mandatory_entry)


        # if mandatory_entry:
        #     print("File exists:", mandatory_entry.file)
        # else:
        #     print("No record found in DB ❌")

        if not mandatory_entry or not mandatory_entry.file:
            return HttpResponseNotFound("File not found")

        file_content = io.BytesIO(mandatory_entry.file.read())

        return FileResponse(
            file_content,
            as_attachment=True,
            filename=f"{inspector.college}_mandatory.pdf"
        )

    except Exception as e:
        print(e)
        return HttpResponseNotFound("Error downloading file")


# ---------------- COMPLIANCE ---------------- #

# def view_compliance(request):
#     try:
#         inspector_id = request.session.get('user_id')

#         if not inspector_id:
#             return redirect('inspector_login')

#         inspector = Inspector.objects.get(user_id=inspector_id)

#         compliance = compliancereport.objects.filter(
#             college_name=inspector.college
#         ).first()

#         if not compliance or not compliance.report_file:
#             return HttpResponseNotFound("File not found")

#         file_content = io.BytesIO(compliance.report_file.read())

#         return FileResponse(
#             file_content,
#             as_attachment=True,
#             filename=f"{inspector.college}_compliance.pdf"
#         )

#     except Exception as e:
#         print(e)
#         return HttpResponseNotFound("Error downloading file")


# def view_compliance(request):
#     try:
#         inspector_id = request.session.get('user_id')

#         if not inspector_id:
#             return redirect('inspector_login')

#         inspector = Inspector.objects.get(user_id=inspector_id)

#         # ✅ STEP 1: GET INTAKE FROM mandatory_dis
#         from institute.models import mandatory_dis

#         mandatory = mandatory_dis.objects(
#             college_name=inspector.college
#         ).first()

#         if not mandatory:
#             return HttpResponseNotFound("Mandatory data not found")

#         intake = mandatory.college_intake

#         # ✅ STEP 2: CALL FASTAPI TO GENERATE REPORT
#         response = requests.post(
#             "http://127.0.0.1:8001/create-compliance-report/",
#             json={
#                 "college_name": inspector.college,
#                 "intake": intake
#             }
#         )

#         print("FastAPI response:", response.status_code)

#         # ✅ STEP 3: FETCH REPORT FROM DB
#         compliance = compliancereport.objects.filter(
#             college_name=inspector.college
#         ).first()

#         if not compliance or not compliance.report_file:
#             return HttpResponseNotFound("Report not found")

#         # ✅ STEP 4: RETURN FILE
#         file_content = io.BytesIO(compliance.report_file.read())

#         return FileResponse(
#             file_content,
#             as_attachment=True,
#             filename=f"{inspector.college}_compliance.pdf"
#         )

#     except Exception as e:
#         print(e)
#         return HttpResponseNotFound("Error downloading file")
    
    

def view_compliance(request):
    try:
        inspector_id = request.session.get('user_id')

        if not inspector_id:
            return redirect('inspector_login')

        inspector = Inspector.objects.get(user_id=inspector_id)

        # 🔍 Step 1: Check if report exists
        compliance = compliancereport.objects.filter(
            college_name=inspector.college
            
        ).first()

        # 🚨 Step 2: If report not found → CALL FASTAPI
        if not compliance:
            print("⚡ Report not found → generating now...")

            # ✅ FETCH INTAKE DYNAMICALLY
            mandatory = mandatory_dis.objects(
                # college_name=inspector.college   # or college_id if your DB uses that
                # college_id=inspector.college
                college_name=inspector.college

            ).first()

            if not mandatory:
                return HttpResponseNotFound("Mandatory data not found")

            intake = mandatory.college_intake
            print("INTAKE SENT:", intake)

            response = requests.post(
                "http://127.0.0.1:8001/process-mandatory-disclosure/",
                json={
                    "college_id": inspector.college,
                    "intake": intake   # ✅ FIXED
                }
            )

            print("FastAPI response:", response.status_code)

            if response.status_code != 200:
                return HttpResponseNotFound("Error generating report")

            # 🔁 Step 3: Fetch again after generation
            # compliance = compliancereport.objects.filter(
            #     college_name=inspector.college
            # ).first()

            compliance = compliancereport.objects.filter(
                college_id=inspector.college
            ).order_by('-id').first()

        # ❌ still not found
        if not compliance or not compliance.report_file:
            return HttpResponseNotFound("File not found")

        # ✅ Step 4: Return PDF
        # file_content = io.BytesIO(compliance.report_file.read())

        # return FileResponse(
        #     file_content,
        #     as_attachment=True,
        #     filename=f"{inspector.college}_compliance.pdf"
        # )

        pdf_data = compliance.report_file.read()

        response = HttpResponse(
            pdf_data,
            content_type='application/pdf'
        )

        response['Content-Disposition'] = (
            f'inline; filename="{inspector.college}_compliance.pdf"'
        )

        return response

    except Exception as e:
        print("❌ ERROR:", e)
        return HttpResponseNotFound("Error downloading file")
    

    
# ---------------- CATEGORY IMAGES (FIXED 🔥) ---------------- #

def view_category_images(request, category):
    try:
        inspector_id = request.session.get('user_id')

        if not inspector_id:
            return redirect('inspector_login')

        inspector = Inspector.objects.get(user_id=inspector_id)
        # college_name = inspector.college
        college_id = inspector.college   # assuming this stores ID
        print("Inspector College ID:", college_id) 

        images_entry = Images.objects(college=college_id).first()
        print("Images Entry:", images_entry) 

        if not images_entry:
            return render(request, 'inspector/category_images.html', {
                'error': 'No images found'
            })

        category_map = {
            'classroom': images_entry.classroom,
            'lab': images_entry.lab,
            'canteen': images_entry.canteen,
            'pwd': images_entry.pwd,
            'parking': images_entry.parking,
            'washroom': images_entry.washroom,
        }

        category_data = category_map.get(category, [])

        image_urls = []
        for item in category_data:
            image_urls.extend(item.get('url', []))

        return render(request, 'inspector/category_images.html', {
            'image_urls': image_urls,
            'category': category
        })

    except Exception as e:
        print(e)
        return render(request, 'inspector/category_images.html', {
            'error': 'Something went wrong'
        })


# ---------------- DEFICIENCY ---------------- #

# def view_deficiency(request):
#     try:
#         inspector_id = request.session.get('user_id')

#         if not inspector_id:
#             return redirect('inspector_login')

#         inspector = Inspector.objects.get(user_id=inspector_id)

#         print("Inspector College:", inspector.college)

#         deficiency = deficiency_report.objects.filter(
#             college=inspector.college
#         ).first()

#         print("Deficiency Object:", deficiency)

#         if not deficiency or not deficiency.file:
            
#             return HttpResponseNotFound("File not found")

#         file_content = io.BytesIO(deficiency.file.read())

#         return FileResponse(
#             file_content,
#             as_attachment=True,
#             filename=f"{inspector.college}_deficiency.pdf"
#         )

#     except Exception as e:
#         print(e)
#         return HttpResponseNotFound("Error downloading file")




def view_deficiency(request):
    try:
        inspector_id = request.session.get('user_id')

        if not inspector_id:
            return redirect('inspector_login')

        inspector = Inspector.objects.get(user_id=inspector_id)

        print("Inspector College:", inspector.college)

        # 🔍 Step 1: Check if deficiency report exists
        deficiency = deficiency_report.objects.filter(
            college=inspector.college
        ).first()

        print("Deficiency Object BEFORE:", deficiency)

        # 🚨 Step 2: If NOT FOUND → CALL FASTAPI
        if not deficiency:
            print("⚡ Generating deficiency report via FastAPI...")

            response = requests.post(
                "http://127.0.0.1:8001/generate-deficiency-report/",
                json={
                    "college_id": inspector.college,
                    "intake": "100"   # you can make this dynamic later
                }
            )

            print("FastAPI response:", response.status_code)

            if response.status_code != 200:
                return HttpResponseNotFound("Error generating deficiency report")

            # 🔁 Step 3: Fetch again after generation
            deficiency = deficiency_report.objects.filter(
                college=inspector.college
            ).first()

            print("Deficiency Object AFTER:", deficiency)

        # ❌ Still not found
        if not deficiency or not deficiency.file:
            return HttpResponseNotFound("File not found")

        # ✅ Step 4: Return PDF
        file_content = io.BytesIO(deficiency.file.read())

        return FileResponse(
            file_content,
            as_attachment=True,
            filename=f"{inspector.college}_deficiency.pdf"
        )

    except Exception as e:
        print("❌ ERROR:", e)
        return HttpResponseNotFound("Error downloading file")
# def generate_report(request):
#     try:
#         inspector_id = request.session.get('user_id')

#         if not inspector_id:
#             return redirect('inspector_login')

#         inspector = Inspector.objects.get(user_id=inspector_id)

#         print("Calling ML for college:", inspector.college)

#         response = requests.post(
#             "http://127.0.0.1:8001/create-compliance-report/",
#             json={
#                 "college_name": inspector.college,
#                 "intake": "100"
#             }
#         )

#         print("Status Code:", response.status_code)

#         data = response.json()

#         return render(request, 'inspector/view_reports.html', {
#             'report': data
#         })

#     except Exception as e:
#         print("Error:", e)
#         return render(request, 'inspector/view_reports.html', {
#             'error': str(e)
#         })


  

def generate_report(request):
    try:
        inspector_id = request.session.get('user_id')

        if not inspector_id:
            return redirect('inspector_login')

        inspector = Inspector.objects.get(user_id=inspector_id)

        print("Calling ML for college:", inspector.college)

        # ✅ STEP 1: Fetch intake dynamically
        mandatory = mandatory_dis.objects(
            # college_name=inspector.college
            college_id=inspector.college
        ).first()

        if not mandatory:
            return render(request, 'inspector/view_reports.html', {
                'error': 'Mandatory data not found'
            })

        intake = mandatory.college_intake

        print("INTAKE SENT:", intake)   # ✅ debug

        # ✅ STEP 2: Send dynamic intake
        # response = requests.post(
        #     "http://127.0.0.1:8001/create-compliance-report/",
        #     json={
        #         "college_name": inspector.college,
        #         "intake": intake
        #     }
        # )

        response = requests.post(
            "http://127.0.0.1:8001/process-mandatory-disclosure/",
            json={
            "college_id": inspector.college,
            "intake": intake
            }
        )

        print("Status Code:", response.status_code)

        data = response.json()

        return render(request, 'inspector/view_reports.html', {
            'report': data
        })

    except Exception as e:
        print("Error:", e)
        return render(request, 'inspector/view_reports.html', {
            'error': str(e)
        })