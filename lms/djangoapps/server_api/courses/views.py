""" API implementation for course-oriented interactions. """

import logging

from django.core.urlresolvers import reverse
from rest_framework import status

from rest_framework.response import Response

from courseware.courses import course_image_url
from server_api.util.courseware_access import get_course, get_course_child, get_course_key, get_modulestore, \
    get_course_descriptor
from server_api.util.permissions import SecureAPIView, SecureListAPIView
from server_api.courses.serializers import CourseSerializer


log = logging.getLogger(__name__)


def _get_content_children(content, category=None):
    """
    Parses the provided content object looking for children.
    Matches on child content type (category) when specified.
    """
    children = []
    if content.has_children:
        child_content = content.get_children()
        for child in child_content:
            if category:
                if getattr(child, 'category') == category:
                    children.append(child)
            else:
                children.append(child)
    return children


def _serialize_content(request, course_key, content_descriptor):
    """
    Loads the specified content object into the response dict
    This should probably evolve to use DRF serializers
    """

    data = {}

    if hasattr(content_descriptor, 'display_name'):
        data['name'] = content_descriptor.display_name

    if hasattr(content_descriptor, 'due'):
        data['due'] = content_descriptor.due

    data['start'] = getattr(content_descriptor, 'start', None)
    data['end'] = getattr(content_descriptor, 'end', None)

    data['category'] = content_descriptor.location.category

    # Some things we only do if the content object is a course
    if hasattr(content_descriptor, 'category') and content_descriptor.category == 'course':
        content_id = unicode(content_descriptor.id)
        content_uri = request.build_absolute_uri(reverse('server_api:courses:detail', kwargs={'course_id': content_id}))
        data['course'] = content_descriptor.location.course
        data['org'] = content_descriptor.location.org
        data['run'] = content_descriptor.location.run

    # Other things we do only if the content object is not a course
    else:
        content_id = unicode(content_descriptor.location)
        # Need to use the CourseKey here, which will possibly result in a different (but valid)
        # URI due to the change in key formats during the "opaque keys" transition
        content_uri = request.build_absolute_uri(reverse('server_api:courses:content_detail',
                                                         kwargs={'course_id': unicode(course_key),
                                                                 'content_id': content_id}))

    data['id'] = unicode(content_id)
    data['uri'] = content_uri

    # Include any additional fields requested by the caller
    include_fields = request.QUERY_PARAMS.get('include_fields', None)
    if include_fields:
        include_fields = include_fields.split(',')
        for field in include_fields:
            data[field] = getattr(content_descriptor, field, None)

    return data


def _serialize_content_children(request, course_key, children):
    """
    Loads the specified content child data into the response dict
    This should probably evolve to use DRF serializers
    """
    data = []
    if children:
        for child in children:
            child_data = _serialize_content(
                request,
                course_key,
                child
            )
            data.append(child_data)
    return data


def _serialize_content_with_children(request, course_key, descriptor, depth):  # pylint: disable=invalid-name
    """
    Serializes course content and then dives into the content tree,
    serializing each child module until specified depth limit is hit
    """
    data = _serialize_content(
        request,
        course_key,
        descriptor
    )

    if depth > 0:
        data['children'] = []
        for child in descriptor.get_children():
            data['children'].append(_serialize_content_with_children(request, course_key, child, depth - 1))
    return data


def _get_course_data(request, course_key, course_descriptor, depth=0):
    """
    creates a dict of course attributes
    """

    if depth > 0:
        data = _serialize_content_with_children(
            request,
            course_key,
            course_descriptor,  # Primer for recursive function
            depth
        )
        data['content'] = data['children']
        data.pop('children')
    else:
        data = _serialize_content(
            request,
            course_key,
            course_descriptor
        )

    data['course_image_url'] = ''
    if getattr(course_descriptor, 'course_image'):
        data['course_image_url'] = course_image_url(course_descriptor)

    data['resources'] = []
    resources = ['content_list']
    for resource in resources:
        data['resources'].append({'uri': request.build_absolute_uri(
            reverse('server_api:courses:{}'.format(resource), kwargs={'course_id': unicode(course_key)}))})

    return data


class CourseContentList(SecureAPIView):
    """
    **Use Case**

        CourseContentList gets a collection of content for a given
        course. You can use the **uri** value in
        the response to get details for that content entity.

        CourseContentList has an optional category parameter that allows you to
        filter the response by content category. The value of the category parameter
        matches the category value in the response. Valid values for the category
        parameter include (but may not be limited to):

        * chapter
        * sequential
        * vertical
        * html
        * problem
        * discussion
        * video

    **Example requests**:

        GET /api/courses/{course_id}/content/

        GET /api/courses/{course_id}/content/?category=video

        GET /api/courses/{course_id}/content/{content_id}/children/

    **Response Values**

        * category: The type of content.

        * due: The due date.

        * uri: The URI to use to get details of the content entity.

        * id: The unique identifier for the content entity.

        * name: The name of the course.
    """

    def get(self, request, course_id, content_id=None):
        """
        GET /api/courses/{course_id}/content/
        GET /api/courses/{course_id}/content/{content_id}/children/
        """
        user = request.user
        course_descriptor, course_key, _course_content = get_course(request, user, course_id)
        if not course_descriptor:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        if content_id is None:
            content_id = course_id
        response_data = []
        category = request.QUERY_PARAMS.get('category', None)
        depth = int(request.QUERY_PARAMS.get('depth', 1))
        if course_id != content_id:
            _content_descriptor, _content_key, content = get_course_child(request, user, course_key, content_id,
                                                                          load_content=True, depth=depth)
        else:
            content = course_descriptor
        if content:
            children = _get_content_children(content, category)
            response_data = _serialize_content_children(
                request,
                course_key,
                children
            )
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_404_NOT_FOUND
        return Response(response_data, status=status_code)


class CourseContentDetail(SecureAPIView):
    """
    **Use Case**

        CourseContentDetail returns a JSON collection for a specified
        CourseContent entity. If the specified CourseContent is the Course, the
        course representation is returned. You can use the uri values in the
        children collection in the JSON response to get details for that content
        entity.

        CourseContentDetail has an optional category parameter that allows you to
        filter the response by content category. The value of the category parameter
        matches the category value in the response. Valid values for the category
        parameter are:

        * chapter
        * sequential
        * vertical
        * html
        * problem
        * discussion
        * video
        * [CONFIRM]

    **Example Request**

          GET /api/courses/{course_id}/content/{content_id}/

    **Response Values**

        * category: The type of content.

        * name: The name of the content entity.

        * due:  The due date.

        * uri: The URI of the content entity.

        * id: The unique identifier for the course.

        * children: Content entities that this content entity contains.
    """

    def get(self, request, course_id, content_id):
        """
        GET /api/courses/{course_id}/content/{content_id}/
        """
        depth = int(request.QUERY_PARAMS.get('depth', 0))
        _course_descriptor, course_key, _course_content = get_course(request, request.user, course_id)

        # TODO Add category filtering
        content_descriptor, _content_key, _content = get_course_child(request, request.user, course_key, content_id,
                                                                      load_content=True)
        response_data = _serialize_content_with_children(request, course_key, content_descriptor, depth)
        return Response(response_data, status=status.HTTP_200_OK)


class CourseList(SecureListAPIView):
    """
    **Use Case**

        CourseList returns paginated list of courses in the edX Platform. You can
        use the uri value in the response to get details of the course. course list can be
        filtered by course_id

    **Example Request**

          GET /api/courses/
          GET /api/courses/?course_id={course_id1},{course_id2}

    **Response Values**

        * category: The type of content. In this case, the value is always "course".

        * name: The name of the course.

        * uri: The URI to use to get details of the course.

        * course: The course number.

        * due:  The due date. For courses, the value is always null.

        * org: The organization specified for the course.

        * id: The unique identifier for the course.
    """
    serializer_class = CourseSerializer

    def get_queryset(self):
        course_ids = self.request.QUERY_PARAMS.get('course_id', None)
        depth = self.request.QUERY_PARAMS.get('depth', 0)
        course_descriptors = []
        if course_ids:
            course_ids = course_ids.split(',')
            for course_id in course_ids:
                course_key = get_course_key(course_id)
                course_descriptor = get_course_descriptor(course_key, 0)
                course_descriptors.append(course_descriptor)
        else:
            course_descriptors = get_modulestore().get_courses()

        results = [_get_course_data(self.request, descriptor.id, descriptor, depth)
                   for descriptor in course_descriptors]
        return results


class CourseDetail(SecureAPIView):
    """
    **Use Case**

        CourseDetail returns details for a course. You can use the uri values
        in the resources collection in the response to get more course
        information for:

        * Course Overview (/api/courses/{course_id}/overview/)
        * Course Updates (/api/courses/{course_id}/updates/)
        * Course Pages (/api/courses/{course_id}/static_tabs/)

        CoursesDetail has an optional **depth** parameter that allows you to
        get course content children to the specified tree level.

    **Example requests**:

        GET /api/courses/{course_id}/

        GET /api/courses/{course_id}/?depth=2

    **Response Values**

        * category: The type of content.

        * name: The name of the course.

        * uri: The URI to use to get details of the course.

        * course: The course number.

        * content: When the depth parameter is used, a collection of child
          course content entities, such as chapters, sequentials, and
          components.

        * due:  The due date. For courses, the value is always null.

        * org: The organization specified for the course.

        * id: The unique identifier for the course.

        * resources: A collection of URIs to use to get more information about
          the course.
    """

    def get(self, request, course_id):
        """
        GET /api/courses/{course_id}/
        """
        depth = int(request.QUERY_PARAMS.get('depth', 0))
        # get_course_by_id raises an Http404 if the requested course is invalid
        # Rather than catching it, we just let it bubble up
        course_descriptor, course_key, _course_content = get_course(request, request.user, course_id, depth=depth)
        if not course_descriptor:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        response_data = _get_course_data(request, course_key, course_descriptor, depth)
        return Response(response_data, status=status.HTTP_200_OK)
