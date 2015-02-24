import os
import unittest

here = os.path.abspath(os.path.dirname(__file__))


class TestCallerPath(unittest.TestCase):
    def tearDown(self):
        from dotted_name_resolver.tests import test_dotted_name_resolver
        if hasattr(test_dotted_name_resolver, '__abspath__'):
            del test_dotted_name_resolver.__abspath__

    def _callFUT(self, path, level=2):
        from dotted_name_resolver import caller_path
        return caller_path(path, level)

    def test_isabs(self):
        result = self._callFUT('/a/b/c')
        self.assertEqual(result, '/a/b/c')

    def test_pkgrelative(self):
        import os
        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join(here, 'a/b/c'))

    def test_memoization_has_abspath(self):
        import os
        from dotted_name_resolver.tests import test_dotted_name_resolver
        test_dotted_name_resolver.__abspath__ = '/foo/bar'
        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join('/foo/bar', 'a/b/c'))

    def test_memoization_success(self):
        import os
        from dotted_name_resolver.tests import test_dotted_name_resolver
        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join(here, 'a/b/c'))
        self.assertEqual(test_dotted_name_resolver.__abspath__, here)


class TestCallerModule(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from dotted_name_resolver import caller_module
        return caller_module(*arg, **kw)

    def test_it_level_1(self):
        from dotted_name_resolver.tests import test_dotted_name_resolver
        result = self._callFUT(1)
        self.assertEqual(result, test_dotted_name_resolver)

    def test_it_level_2(self):
        from dotted_name_resolver.tests import test_dotted_name_resolver
        result = self._callFUT(2)
        self.assertEqual(result, test_dotted_name_resolver)

    def test_it_level_3(self):
        from dotted_name_resolver.tests import test_dotted_name_resolver
        result = self._callFUT(3)
        self.assertNotEqual(result, test_dotted_name_resolver)

    def test_it_no___name__(self):
        class DummyFrame(object):
            f_globals = {}

        class DummySys(object):
            def _getframe(self, level):
                return DummyFrame()
            modules = {'__main__': 'main'}

        dummy_sys = DummySys()
        result = self._callFUT(3, sys=dummy_sys)
        self.assertEqual(result, 'main')


class TestCallerPackage(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from dotted_name_resolver import caller_package
        return caller_package(*arg, **kw)

    def test_it_level_1(self):
        from dotted_name_resolver import tests
        result = self._callFUT(1)
        self.assertEqual(result, tests)

    def test_it_level_2(self):
        from dotted_name_resolver import tests
        result = self._callFUT(2)
        self.assertEqual(result, tests)

    def test_it_level_3(self):
        import unittest
        result = self._callFUT(3)
        self.assertEqual(result, unittest)

    def test_it_package(self):
        import dotted_name_resolver.tests

        def dummy_caller_module(*arg):
            return dotted_name_resolver.tests

        result = self._callFUT(1, caller_module=dummy_caller_module)
        self.assertEqual(result, dotted_name_resolver.tests)


class TestPackagePath(unittest.TestCase):
    def _callFUT(self, package):
        from dotted_name_resolver import package_path
        return package_path(package)

    def test_it_package(self):
        from dotted_name_resolver import tests
        package = DummyPackageOrModule(tests)
        result = self._callFUT(package)
        self.assertEqual(result, package.package_path)

    def test_it_module(self):
        from dotted_name_resolver.tests import test_dotted_name_resolver
        module = DummyPackageOrModule(test_dotted_name_resolver)
        result = self._callFUT(module)
        self.assertEqual(result, module.package_path)

    def test_memoization_success(self):
        from dotted_name_resolver.tests import test_dotted_name_resolver
        module = DummyPackageOrModule(test_dotted_name_resolver)
        self._callFUT(module)
        self.assertEqual(module.__abspath__, module.package_path)

    def test_memoization_fail(self):
        from dotted_name_resolver.tests import test_dotted_name_resolver
        module = DummyPackageOrModule(
            test_dotted_name_resolver,
            raise_exc=TypeError
        )
        result = self._callFUT(module)
        self.assertFalse(hasattr(module, '__abspath__'))
        self.assertEqual(result, module.package_path)


class TestPackageOf(unittest.TestCase):
    def _callFUT(self, package):
        from dotted_name_resolver import package_of
        return package_of(package)

    def test_it_package(self):
        from dotted_name_resolver import tests
        package = DummyPackageOrModule(tests)
        result = self._callFUT(package)
        self.assertEqual(result, tests)

    def test_it_module(self):
        import dotted_name_resolver.tests.test_dotted_name_resolver
        from dotted_name_resolver import tests
        package = DummyPackageOrModule(
            dotted_name_resolver.tests.test_dotted_name_resolver
        )
        result = self._callFUT(package)
        self.assertEqual(result, tests)


class TestPackageName(unittest.TestCase):
    def _callFUT(self, package):
        from dotted_name_resolver import package_name
        return package_name(package)

    def test_it_package(self):
        from dotted_name_resolver import tests
        package = DummyPackageOrModule(tests)
        result = self._callFUT(package)
        self.assertEqual(result, 'dotted_name_resolver.tests')

    def test_it_namespace_package(self):
        from dotted_name_resolver import tests
        package = DummyNamespacePackage(tests)
        result = self._callFUT(package)
        self.assertEqual(result, 'dotted_name_resolver.tests')

    def test_it_module(self):
        from dotted_name_resolver.tests import test_dotted_name_resolver
        module = DummyPackageOrModule(test_dotted_name_resolver)
        result = self._callFUT(module)
        self.assertEqual(result, 'dotted_name_resolver.tests')

    def test_it_None(self):
        result = self._callFUT(None)
        self.assertEqual(result, '__main__')

    def test_it_main(self):
        import __main__
        result = self._callFUT(__main__)
        self.assertEqual(result, '__main__')


class TestResolver(unittest.TestCase):
    def _getTargetClass(self):
        from dotted_name_resolver import Resolver
        return Resolver

    def _makeOne(self, package):
        return self._getTargetClass()(package)

    def test_get_package_caller_package(self):
        import dotted_name_resolver.tests
        from dotted_name_resolver import CALLER_PACKAGE
        self.assertEqual(
            self._makeOne(CALLER_PACKAGE).get_package(),
            dotted_name_resolver.tests
        )

    def test_get_package_name_caller_package(self):
        from dotted_name_resolver import CALLER_PACKAGE
        self.assertEqual(
            self._makeOne(CALLER_PACKAGE).get_package_name(),
            'dotted_name_resolver.tests'
        )

    def test_get_package_string(self):
        import dotted_name_resolver.tests
        self.assertEqual(
            self._makeOne('dotted_name_resolver.tests').get_package(),
            dotted_name_resolver.tests
        )

    def test_get_package_name_string(self):
        self.assertEqual(
            self._makeOne('dotted_name_resolver.tests').get_package_name(),
            'dotted_name_resolver.tests'
        )


class TestDottedNameResolver(unittest.TestCase):
    def _makeOne(self, package=None):
        from dotted_name_resolver import DottedNameResolver
        return DottedNameResolver(package)

    def config_exc(self, func, *arg, **kw):
        try:
            func(*arg, **kw)
        except ValueError as e:
            return e
        else:
            raise AssertionError('Invalid not raised')  # pragma: no cover

    def test_zope_dottedname_style_resolve_builtin(self):
        typ = self._makeOne()
        result = typ._zope_dottedname_style('__builtin__.str', None)
        self.assertEqual(result, str)

    def test_zope_dottedname_style_resolve_absolute(self):
        typ = self._makeOne()
        pkg = 'dotted_name_resolver'
        result = typ._zope_dottedname_style(
            pkg + '.tests.test_dotted_name_resolver.TestDottedNameResolver',
            None
        )
        self.assertEqual(result, self.__class__)

    def test_zope_dottedname_style_irrresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(
            ImportError,
            typ._zope_dottedname_style,
            'dotted_name_resolver.test_dotted_name_resolver.nonexisting_name',
            None
        )

    def test__zope_dottedname_style_resolve_relative(self):
        import dotted_name_resolver.tests
        typ = self._makeOne()
        result = typ._zope_dottedname_style(
            '.test_dotted_name_resolver.TestDottedNameResolver',
            dotted_name_resolver.tests
        )
        self.assertEqual(result, self.__class__)

    def test__zope_dottedname_style_resolve_relative_leading_dots(self):
        import dotted_name_resolver.tests.test_dotted_name_resolver
        typ = self._makeOne()
        result = typ._zope_dottedname_style(
            '..tests.test_dotted_name_resolver.TestDottedNameResolver',
            dotted_name_resolver.tests
        )
        self.assertEqual(result, self.__class__)

    def test__zope_dottedname_style_resolve_relative_is_dot(self):
        import dotted_name_resolver.tests
        typ = self._makeOne()
        result = typ._zope_dottedname_style('.', dotted_name_resolver.tests)
        self.assertEqual(result, dotted_name_resolver.tests)

    def test__zope_dottedname_style_irresolveable_relative_is_dot(self):
        typ = self._makeOne()
        e = self.config_exc(typ._zope_dottedname_style, '.', None)
        self.assertEqual(
            e.args[0],
            "relative name '.' irresolveable without package")

    def test_zope_dottedname_style_resolve_relative_nocurrentpackage(self):
        typ = self._makeOne()
        e = self.config_exc(typ._zope_dottedname_style, '.whatever', None)
        self.assertEqual(
            e.args[0],
            "relative name '.whatever' irresolveable without package")

    def test_zope_dottedname_style_irrresolveable_relative(self):
        import dotted_name_resolver.tests
        typ = self._makeOne()
        self.assertRaises(
            ImportError,
            typ._zope_dottedname_style,
            '.notexisting',
            dotted_name_resolver.tests
        )

    def test__zope_dottedname_style_resolveable_relative(self):
        import dotted_name_resolver
        typ = self._makeOne()
        result = typ._zope_dottedname_style('.tests', dotted_name_resolver)
        from dotted_name_resolver import tests
        self.assertEqual(result, tests)

    def test__zope_dottedname_style_irresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(
            ImportError,
            typ._zope_dottedname_style, 'dotted_name_resolver.fudge.bar',
            None
        )

    def test__zope_dottedname_style_resolveable_absolute(self):
        typ = self._makeOne()
        pkg = 'dotted_name_resolver.tests'
        result = typ._zope_dottedname_style(
            pkg + '.test_dotted_name_resolver.TestDottedNameResolver',
            None
        )
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_resolve_absolute(self):
        typ = self._makeOne()
        pkg = 'dotted_name_resolver.tests'
        result = typ._pkg_resources_style(
            pkg + '.test_dotted_name_resolver:TestDottedNameResolver',
            None
        )
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_irrresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(
            ImportError,
            typ._pkg_resources_style,
            'dotted_name_resolver.tests:nonexisting',
            None
        )

    def test__pkg_resources_style_resolve_relative(self):
        import dotted_name_resolver.tests
        typ = self._makeOne()
        result = typ._pkg_resources_style(
            '.test_dotted_name_resolver:TestDottedNameResolver',
            dotted_name_resolver.tests
        )
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_resolve_relative_is_dot(self):
        import dotted_name_resolver.tests
        typ = self._makeOne()
        result = typ._pkg_resources_style('.', dotted_name_resolver.tests)
        self.assertEqual(result, dotted_name_resolver.tests)

    def test__pkg_resources_style_resolve_relative_nocurrentpackage(self):
        typ = self._makeOne()
        self.assertRaises(ValueError, typ._pkg_resources_style,
                          '.whatever', None)

    def test__pkg_resources_style_irrresolveable_relative(self):
        import dotted_name_resolver
        typ = self._makeOne()
        self.assertRaises(
            ImportError,
            typ._pkg_resources_style,
            ':notexisting',
            dotted_name_resolver
        )

    def test_resolve_not_a_string(self):
        typ = self._makeOne()
        e = self.config_exc(typ.resolve, None)
        self.assertEqual(e.args[0], 'None is not a string')

    def test_resolve_using_pkgresources_style(self):
        typ = self._makeOne()
        pkg = 'dotted_name_resolver.tests'
        result = typ.resolve(
            pkg + '.test_dotted_name_resolver:TestDottedNameResolver'
        )
        self.assertEqual(result, self.__class__)

    def test_resolve_using_zope_dottedname_style(self):
        typ = self._makeOne()
        pkg = 'dotted_name_resolver.tests'
        result = typ.resolve(
            pkg + '.test_dotted_name_resolver:TestDottedNameResolver'
        )
        self.assertEqual(result, self.__class__)

    def test_resolve_missing_raises(self):
        typ = self._makeOne()
        self.assertRaises(ImportError, typ.resolve, 'cant.be.found')

    def test_resolve_caller_package(self):
        from dotted_name_resolver import CALLER_PACKAGE
        typ = self._makeOne(CALLER_PACKAGE)
        self.assertEqual(
            typ.resolve('.test_dotted_name_resolver.TestDottedNameResolver'),
            self.__class__
        )

    def test_maybe_resolve_caller_package(self):
        from dotted_name_resolver import CALLER_PACKAGE
        typ = self._makeOne(CALLER_PACKAGE)
        self.assertEqual(
            typ.maybe_resolve(
                '.test_dotted_name_resolver.TestDottedNameResolver'
            ),
            self.__class__
        )

    def test_ctor_string_module_resolveable(self):
        import dotted_name_resolver.tests
        typ = self._makeOne(
            'dotted_name_resolver.tests.test_dotted_name_resolver'
        )
        self.assertEqual(typ.package, dotted_name_resolver.tests)

    def test_ctor_string_package_resolveable(self):
        import dotted_name_resolver.tests
        typ = self._makeOne('dotted_name_resolver.tests')
        self.assertEqual(typ.package, dotted_name_resolver.tests)

    def test_ctor_string_irresolveable(self):
        self.assertRaises(ValueError, self._makeOne, 'cant.be.found')

    def test_ctor_module(self):
        import dotted_name_resolver.tests
        import dotted_name_resolver.tests.test_dotted_name_resolver
        typ = self._makeOne(
            dotted_name_resolver.tests.test_dotted_name_resolver
        )
        self.assertEqual(typ.package, dotted_name_resolver.tests)

    def test_ctor_package(self):
        import dotted_name_resolver.tests
        typ = self._makeOne(dotted_name_resolver.tests)
        self.assertEqual(typ.package, dotted_name_resolver.tests)

    def test_ctor_None(self):
        typ = self._makeOne(None)
        self.assertEqual(typ.package, None)


class DummyPkgResource(object):
    pass


class DummyPackageOrModule:
    def __init__(self, real_package_or_module, raise_exc=None):
        self.__dict__['raise_exc'] = raise_exc
        self.__dict__['__name__'] = real_package_or_module.__name__
        import os
        self.__dict__['package_path'] = os.path.dirname(
            os.path.abspath(real_package_or_module.__file__))
        self.__dict__['__file__'] = real_package_or_module.__file__

    def __setattr__(self, key, val):
        if self.raise_exc is not None:
            raise self.raise_exc
        self.__dict__[key] = val


class DummyNamespacePackage:
    """Has no __file__ attribute.
    """

    def __init__(self, real_package_or_module):
        self.__name__ = real_package_or_module.__name__
        import os
        self.package_path = os.path.dirname(
            os.path.abspath(real_package_or_module.__file__))
