from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, JobPostingViewSet, UserViewSet, job_application

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'jobpostings', JobPostingViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('application/', job_application)
]