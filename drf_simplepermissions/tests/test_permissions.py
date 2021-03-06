from django.test import TestCase
from django.test import override_settings
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from drf_simplepermissions import SimplePermissions
from drf_simplepermissions import is_demo
from drf_simplepermissions.exceptions import SimpleModeException


class View:
    pass


class Request:
    def __init__(self):
        self.user = None


class TestPermissions(TestCase):
    def setUp(self):
        self.permissions = SimplePermissions()
        self.request = Request()
        self.view = View()

        # Create a user
        user = User.objects.create_user(username='demo', password='demo')
        user.save()
        self.request.user = user

        # Create a content_type to test with
        self.content_type = ContentType(app_label='test_case', model='permissions') # noqa
        self.content_type.save()

    def test_basic_tuple_permission(self):
        permission = Permission.objects.create(codename='test', content_type=self.content_type) # noqa
        self.request.user.user_permissions.add(permission)
        self.view.allowed_permissions = ('test_case.test',)
        self.assertEqual(self.permissions.has_permission(request=self.request, view=self.view), True) # noqa

    def test_incorrect_tuple_permission(self):
        permission = Permission.objects.create(codename='test2', content_type=self.content_type) # noqa
        self.request.user.user_permissions.add(permission)
        self.view.allowed_permissions = ('test_case.test',)
        self.assertEqual(self.permissions.has_permission(request=self.request, view=self.view), False) # noqa

    def test_basic_list_permission(self):
        permission = Permission.objects.create(codename='test', content_type=self.content_type) # noqa
        self.request.user.user_permissions.add(permission)
        self.view.allowed_permissions = ['test_case.test', ]
        self.assertEqual(self.permissions.has_permission(request=self.request, view=self.view), True) # noqa

    def test_incorrect_list_permission(self):
        permission = Permission.objects.create(codename='test2', content_type=self.content_type) # noqa
        self.request.user.user_permissions.add(permission)
        self.view.allowed_permissions = ['test_case.test', ]
        self.assertEqual(self.permissions.has_permission(request=self.request, view=self.view), False) # noqa

    def test_basic_string_permission(self):
        permission = Permission.objects.create(codename='test', content_type=self.content_type) # noqa
        self.request.user.user_permissions.add(permission)
        self.view.allowed_permissions = 'test_case.test'
        self.assertEqual(self.permissions.has_permission(request=self.request, view=self.view), True) # noqa

    def test_incorrect_string_permission(self):
        permission = Permission.objects.create(codename='test2', content_type=self.content_type) # noqa
        self.request.user.user_permissions.add(permission)
        self.view.allowed_permissions = 'test'
        self.assertEqual(self.permissions.has_permission(request=self.request, view=self.view), False) # noqa


class TestIsDemo(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('foo', password='bar')

    def test_demo_default(self):
        self.assertEqual(is_demo(user=self.user), False)

    @override_settings(DEMO=True)
    def test_demo_mode_true(self):
        self.assertEqual(is_demo(user=self.user), True)

    @override_settings(DEMO=False)
    def test_demo_mode_false(self):
        self.assertEqual(is_demo(user=self.user), False)

    def test_demo_group_default_name(self):
        group = Group.objects.create(name='demo')
        group.user_set.add(self.user)
        self.assertEqual(is_demo(user=self.user), True)

    @override_settings(DEMO_GROUPS='foobar')
    def test_demo_group_custom_name(self):
        group = Group.objects.create(name='foobar')
        group.user_set.add(self.user)
        self.assertEqual(is_demo(user=self.user), True)

    @override_settings(DEMO_GROUPS='foobar')
    def test_demo_group_custom_name_with_default_group(self):
        group = Group.objects.create(name='demo')
        group.user_set.add(self.user)
        self.assertEqual(is_demo(user=self.user), False)

    @override_settings(DEMO_GROUPS=['group1', 'group2'])
    def test_demo_multiple_groups_true(self):
        groups = ['group1', 'group2']
        for group_name in groups:
            group = Group.objects.create(name=group_name)
            group.user_set.add(self.user)

        self.assertEqual(is_demo(user=self.user), True)

    @override_settings(DEMO=False)
    def test_demo_mode_for_global_false_but_user_in_demo_group(self):
        group = Group.objects.create(name='demo')
        group.user_set.add(self.user)
        self.assertEqual(is_demo(user=self.user), True)

    @override_settings(DEMO_GROUPS=type('demo_group', (), {})())
    def test_demo_group_unsupported_object(self):
        self.assertEqual(is_demo(user=self.user), False) # noqa

    @override_settings(DEMO='foo')
    def test_demo_group_unsupported_demo_mode(self):
        self.assertRaises(SimpleModeException, is_demo, user=self.user)

    def test_demo_unsupported_user_object(self):
        self.assertEqual(is_demo(user=False), False)
