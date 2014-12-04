""" Django REST Framework Serializers """

from rest_framework import serializers

from server_api.util.utils import generate_base_uri


class CourseSerializer(serializers.Serializer):
    """ Serializer for Courses """
    id = serializers.CharField(source='id')
    name = serializers.CharField(source='name')
    category = serializers.CharField(source='category')
    course = serializers.CharField(source='course')
    org = serializers.CharField(source='org')
    run = serializers.CharField(source='run')
    uri = serializers.CharField(source='uri')
    course_image_url = serializers.CharField(source='course_image_url')
    resources = serializers.CharField(source='resources')
    due = serializers.DateTimeField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def get_uri(self, course):
        """
        Builds course detail uri
        """
        return "{}/{}".format(generate_base_uri(self.context['request']), course.id)  # pylint: disable=E1101
