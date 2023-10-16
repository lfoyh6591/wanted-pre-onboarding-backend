# wanted-pre-onboarding-backend

# Models

```python
class Company(models.Model):
    company_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

class JobPosting(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    reward = models.IntegerField()
    content = models.TextField()
    skill = models.CharField(max_length=100)

class User(models.Model):
    name = models.CharField(max_length=100)
    jobposting = models.ForeignKey(JobPosting, on_delete=models.SET_NULL, null=True, blank=True)
```

요구사항 6에 User가 1회만 지원 가능하다는 조건이 있어서 JobPosting과 Many-to-one 관계로 구현하였고 nullable로 해주었다.

나머지는 예시와 동일하다.

기본적인 api들은 DRF의 serializer와 viewset을 통해 구현하였다.

각각의 viewset은 defaultrouter로 등록해주었고 app의 url은 project의 ‘api/’ url로 등록해주었다.

# 요구사항 1

### POST api/jobpostings/

JobPosting model은 Company model과 Many-to-one 관계이다.

POST 시에 company의 id만으로 company와 연결해줄 수 있어야 한다.

jobposting의 serializer에서 다음과 같이 구현하였다.

```python
company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
```

# 요구사항2

### PUT api/jobpostings/{id}/

일반적인 update에서 company의 변경사항은 무시되어야 한다.

jobposting의 serializer에서 update 메소드를 오버라이딩 하여 company의 변경사항을 무시할 수 있도록 구현하였다.

```python
def update(self, instance, validated_data):
        validated_data.pop('company', None)
        return super().update(instance, validated_data)
```

# 요구사항3

### DELETE api/jobpostings/{id}/

기본적인 serializer와 viewset에 의해 구현되었다.

# 요구사항4

## 요구사항 4-1

### GET api/jobpostings/

다음 요구사항에 있을 detail한 항목들을 get 할 때와 구별해주기 위해 BaseJobPostingSerializer를 상속하는 방식으로 구현하였다.

company의 항목들을 맨 위로 올리기 위해서 to_representation 메소드를 오버라이딩 해주었다.

JobPostingSerializer는 BaseJobPostingSerializer를 상속하고 상세페이지에만 나타나는 ‘채용내용’, ‘회사가 올린 다른 공고’ 에 대한 항목들을 빼주었다.

```python
# BaseJobPostingSerializer class
def to_representation(self, instance):
        representation = super().to_representation(instance)
        company_representation = CompanySerializer(instance.company).data

        for key, value in company_representation.items():
            if key == "id":
                continue
            representation[f'{key}'] = value
        
        representation.pop('company', None)
        return representation

class JobPostingSerializer(BaseJobPostingSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('content')
        representation.pop('other_jobpostings_of_this_company')
        return representation
```

## 요구사항 4-2

### GET api/jobpostings/?search={}

DRF의 filters를 사용해서 구현해주었다.

search field는 텍스트가 들어가는 항목으로 제한하였다.

```python
from rest_framework import filters

class JobPostingViewSet(viewsets.ModelViewSet):
    #기존 코드
    filter_backends = [filters.SearchFilter]
    search_fields = ['company__company_name', 'company__region', 'company__country', 'position', 'skill']
```

# 요구사항 5

### GET api/jobpostings/{id}

JobPostingDetailSerializer는 BaseJobPostingSerializer를 상속하고 ‘회사가 올린 다른 채용공고’에는 현재 채용공고의 id를 빼주었다.

‘회사가 올린 다른 채용공고’는 CompanySerializer에서 jobposting 역참조를 통해 받아온다.

```python
class CompanySerializer(serializers.ModelSerializer):
    other_jobpostings_of_this_company = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='jobposting_set')
		#기존 코드
```

```python
class JobPostingDetailSerializer(BaseJobPostingSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['other_jobpostings_of_this_company'].remove(representation['id'])
        return representation
```

# 요구사항 6

### POST api/application/

viewset이 아닌 함수형 view를 통해 구현하였다.

user_id, jobposting_id를 받아서 user의 jobposting에 넣어주었다.

이 때, jobposting이 null인 아닌 경우는 이미 지원을 완료한 경우로 에러처리를 해주었다.

이 외에 user, jobposting이 각각 id로 발견되지 않았을 경우도 에러처리를 해주었다.

```python
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
```