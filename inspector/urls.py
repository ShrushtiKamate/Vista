
# from django.urls import path
# from . import views

# urlpatterns = [

#     path('login/', views.login_view, name='inspector_login'),
#     path('view-reports/', views.view_reports, name='view_reports'),
    
#     # path('discussion-forum/', views.discussion_forum, name='discussion_forum'),
#     # path('discussion/<int:post_id>/', views.view_discussion, name='view_discussion'),
#     # path('create-post/', views.create_post, name='create_post'),
#     # path('create-reply/<int:post_id>/', views.create_reply, name='create_reply'),
    
#     path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
#     path('feedback-page/', views.feedback_page, name='feedback_page'),
#     path('inspector/view-uploaded-certificates/', views.view_certificates, name='view_certificates'),
#     path('inspector/download-uploaded-certificate/<str:certificate_id>/', views.download_uploaded_certificate, name='download_uploaded_certificate'),
#     path('view_images/<str:category>/', views.view_category_images, name='view_category_images'),
  
# ]


from django.urls import path
from . import views

urlpatterns = [

    # Auth
    path('login/', views.login_view, name='inspector_login'),
    path('logout/', views.inspector_logout, name='inspector_logout'),

    # Dashboard
    path('view-reports/', views.view_reports, name='view_reports'),

    # Feedback
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback-page/', views.feedback_page, name='feedback_page'),

    # Certificates
    path('view-certificates/', views.view_certificates, name='view_certificates'),
    path('download-certificate/<str:certificate_id>/', views.download_uploaded_certificate, name='download_uploaded_certificate'),

    # Images
    path('view_images/<str:category>/', views.view_category_images, name='view_category_images'),

    # Documents (FIXED)
    path('view_mandatory/', views.view_mandatory, name='view_mandatory'),
    path('view_compliance/', views.view_compliance, name='view_compliance'),
    path('view_deficiency/', views.view_deficiency, name='view_deficiency'),
]