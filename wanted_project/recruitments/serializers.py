from rest_framework import serializers
from .models import Company, JobPosting, User

class CompanySerializer(serializers.ModelSerializer):
    other_jobpostings_of_this_company = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='jobposting_set')

    class Meta:
        model = Company
        fields = '__all__'

class BaseJobPostingSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = JobPosting
        fields = '__all__'

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

    def update(self, instance, validated_data):
        validated_data.pop('company', None)
        return super().update(instance, validated_data)


class JobPostingDetailSerializer(BaseJobPostingSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['other_jobpostings_of_this_company'].remove(representation['id'])
        return representation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'