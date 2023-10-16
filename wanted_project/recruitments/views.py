from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from .models import Company, JobPosting, User
from .serializers import CompanySerializer, JobPostingSerializer, JobPostingDetailSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['company__company_name', 'company__region', 'company__country', 'position', 'skill']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JobPostingDetailSerializer
        return super().get_serializer_class()

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['POST'])
def job_application(request):
    user_id = request.data.get('user_id')
    jobposting_id = request.data.get('jobposting_id')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        jobposting = JobPosting.objects.get(pk=jobposting_id)
    except JobPosting.DoesNotExist:
        return Response({'error': 'JobPosting not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.jobposting:
        return Response({'error': 'User already applied'}, status=status.HTTP_400_BAD_REQUEST)
    user.jobposting = jobposting
    user.save()

    return Response({'message': 'application completed'}, status=status.HTTP_200_OK)