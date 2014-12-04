""" Centralized access to LMS courseware app """
from django.contrib.auth.models import AnonymousUser

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from courseware import courses, module_render
from courseware.model_data import FieldDataCache


def _anonymous_known_flag(user):
    """
    Utility method to force 'known' flag on AnonymousUser users to False
    """
    if isinstance(user, AnonymousUser):
        user.known = False


def get_modulestore():
    """
    Utility method to abstract the call to modulestore()
    """
    return modulestore()


def get_course(request, user, course_id, depth=0, load_content=False):
    """
    Utility method to obtain course components
    """
    _anonymous_known_flag(user)
    course_descriptor = None
    course_content = None
    course_key = get_course_key(course_id)
    if course_key:
        course_descriptor = get_course_descriptor(course_key, depth)
        if course_descriptor and load_content:
            course_content = get_course_content(request, user, course_key, course_descriptor)
    return course_descriptor, course_key, course_content


def get_course_child(request, user, course_key, content_id, load_content=False, depth=None):
    """
    Return a course xmodule/xblock to the caller
    """
    _anonymous_known_flag(user)
    child_descriptor = None
    child_content = None
    child_key = get_course_child_key(content_id)
    if child_key:
        child_descriptor = get_course_child_descriptor(child_key, depth=depth)
        if child_descriptor and load_content:
            child_content = get_course_child_content(request, user, course_key, child_descriptor)
    return child_descriptor, child_key, child_content


def get_course_key(course_id):
    """
    Utility method to create CourseKey values from strings
    """
    return CourseKey.from_string(course_id)


def get_course_descriptor(course_key, depth):
    """
    Utility method to abstract away the work of loading a course descriptor
    """
    try:
        course_descriptor = courses.get_course(course_key, depth)
    except ValueError:
        course_descriptor = None
    return course_descriptor


def get_course_content(request, user, course_key, course_descriptor):
    """
    Utility method to abstract away the work of loading a course content module/object
    """
    field_data_cache = FieldDataCache([course_descriptor], course_key, user)
    course_content = module_render.get_module_for_descriptor(
        user,
        request,
        course_descriptor,
        field_data_cache,
        course_key)
    return course_content


def course_exists(course_id):
    """
    Utility method to test the existence of a course, given a string identifier
    """
    course_key = get_course_key(course_id)
    if not course_key:
        return False
    if not get_modulestore().has_course(course_key):
        return False
    return True


def get_course_child_key(content_id):
    """
    Utility method to generate a Location/Usage key for the specified course content identifier
    """
    try:
        content_key = UsageKey.from_string(content_id)
    except InvalidKeyError:
        content_key = None

    return content_key


def get_course_child_descriptor(child_key, depth=None):
    """
    Utility method to load the descriptor object for the specified course content/module
    """
    try:
        content_descriptor = get_modulestore().get_item(child_key, depth=depth)
    except ItemNotFoundError:
        content_descriptor = None
    return content_descriptor


def get_course_child_content(request, user, course_key, child_descriptor):
    """
    Utility method to load the content object (from modulestore) for the specified course content
    """
    field_data_cache = FieldDataCache([child_descriptor], course_key, user)
    child_content = module_render.get_module_for_descriptor(
        user,
        request,
        child_descriptor,
        field_data_cache,
        course_key)
    return child_content
