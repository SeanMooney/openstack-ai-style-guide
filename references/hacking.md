---
source_url: https://opendev.org/openstack/hacking/raw/commit/abff65f29b7b00d38bce651a546b05a3eb27b71c/HACKING.rst
conversion_date: 2025-10-25
document_title: OpenStack Style Guidelines
source_type: Style Guide Documentation
commit: abff65f29b7b00d38bce651a546b05a3eb27b71c
---

# OpenStack Style Guidelines

OpenStack has a set of style guidelines for clarity[1]. OpenStack is a very large code base (over 1 Million lines of python), spanning dozens of git trees, with over a thousand developers contributing every 12 months[1]. As such common style helps developers understand code in reviews, move between projects smoothly, and overall make the code more maintainable[1].

## Step 0

- Step 1: Read [PEP 8][pep8][1]
- Step 2: Read [PEP 8][pep8] again[1]
- Step 3: Read on[1]

[pep8]: http://www.python.org/dev/peps/pep-0008/

## General

- **[H903]** Use only UNIX style newlines (`\n`), not Windows style (`\r\n`)[1]
- It is preferred to wrap long lines in parentheses and not a backslash for line continuation[1]
- **[H201]** Do not write `except:`, use `except Exception:` at the very least[1]. When catching an exception you should be as specific so you don't mistakenly catch unexpected exceptions[1].
- **[H101]** Include your name with TODOs as in `# TODO(yourname)`[1]. This makes it easier to find out who the author of the comment was[1].
- **[H105]** Don't use author tags[1]. We use version control instead[1].
- **[H106]** Don't put vim configuration in source files (off by default)[1].
- **[H904]** Delay string interpolations at logging calls (off by default)[1].
- Do not shadow a built-in or reserved word[1]. Shadowing built-in or reserved words makes the code harder to understand[1]. Example:

```python
def list():
    return [1, 2, 3]

mylist = list() # BAD, shadows `list` built-in

class Foo(object):
    def list(self):
        return [1, 2, 3]

mylist = Foo().list() # OKAY, does not shadow built-in
```

## Imports

- Do not import objects, only modules (*)[1]
- **[H301]** Do not import more than one module per line (*)[1]
- **[H303]** Do not use wildcard `*` import (*)[1]
- **[H304]** Do not make relative imports[1]
- **[H306]** Alphabetically order your imports by the full module path[1]. Organize your imports according to the Import order template and Real-world Import Order Examples below[1]. For the purposes of import order, OpenStack projects other than the one to which the file belongs are considered "third party"[1]. Only imports from the same Git repo are considered "project imports"[1].

(*) exceptions are[1]:

- imports from `migrate` package
- imports from `sqlalchemy` package
- function imports from `i18n` module

### Import Order Template

```python
{{stdlib imports in human alphabetical order}}

{{third-party lib imports in human alphabetical order}}

{{project imports in human alphabetical order}}


{{begin your code}}
```

### Real-world Import Order Examples

Example[1]:

```python
import httplib
import logging
import random
import StringIO
import time
import unittest

import eventlet
import webob.exc

import nova.api.ec2
from nova.api import manager
from nova.api import openstack
from nova.auth import users
from nova.endpoint import cloud
import nova.flags
from nova.i18n import _, _LC
from nova import test
```

## Docstrings

- **[H401]** Docstrings should not start with a space[1].
- **[H403]** Multi line docstrings should end on a new line[1].
- **[H404]** Multi line docstrings should start without a leading new line[1].
- **[H405]** Multi line docstrings should start with a one line summary followed by an empty line[1].

Example[1]:

```python
"""A multi line docstring has a one-line summary, less than 80 characters.

Then a new paragraph after a newline that explains in more detail any
general information about the function, class or method. Example usages
are also great to have here if it is a complex class or function.

When writing the docstring for a class, an extra line should be placed
after the closing quotations. For more in-depth explanations for these
decisions see http://www.python.org/dev/peps/pep-0257/

If you are going to describe parameters and return values, use Sphinx, the
appropriate syntax is as follows.

:param foo: the foo parameter
:param bar: the bar parameter
:returns: return_type -- description of the return value
:returns: description of the return value
:raises: AttributeError, KeyError
"""
```

## Dictionaries/Lists

If a dictionary (dict) or list object is longer than 80 characters, its items should be split with newlines[1]. Embedded iterables should have their items indented[1]. Additionally, the last item in the dictionary should have a trailing comma[1]. This increases readability and simplifies future diffs[1].

Example[1]:

```python
my_dictionary = {
    "image": {
        "name": "Just a Snapshot",
        "size": 2749573,
        "properties": {
            "user_id": 12,
            "arch": "x86_64",
        },
        "things": [
            "thing_one",
            "thing_two",
        ],
        "status": "ACTIVE",
    },
}
```

- **[H501]** Do not use `locals()` or `self.__dict__` for formatting strings[1], it is not clear as using explicit dictionaries and can hide errors during refactoring[1].

## Calling Methods

Calls to methods 80 characters or longer should format each argument with newlines[1]. This is not a requirement, but a guideline[1]:

```python
unnecessarily_long_function_name('string one',
                                 'string two',
                                 kwarg1=constants.ACTIVE,
                                 kwarg2=['a', 'b', 'c'])
```

Rather than constructing parameters inline, it is better to break things up[1]:

```python
list_of_strings = [
    'what_a_long_string',
    'not as long',
]

dict_of_numbers = {
    'one': 1,
    'two': 2,
    'twenty four': 24,
}

object_one.call_a_method('string three',
                         'string four',
                         kwarg1=list_of_strings,
                         kwarg2=dict_of_numbers)
```

## Internationalization (i18n) Strings

In order to support multiple languages, we have a mechanism to support automatic translations of exception and log strings[1].

Example[1]:

```python
msg = _("An error occurred")
raise HTTPBadRequest(explanation=msg)
```

- **[H702]** If you have a variable to place within the string, first internationalize the template string then do the replacement[1].

  Example[1]:

  ```python
  msg = _LE("Missing parameter: %s")
  LOG.error(msg, "flavor")
  ```

- **[H703]** If you have multiple variables to place in the string, use keyword parameters[1]. This helps our translators reorder parameters when needed[1].

  Example[1]:

  ```python
  msg = _LE("The server with id %(s_id)s has no key %(m_key)s")
  LOG.error(msg, {"s_id": "1234", "m_key": "imageId"})
  ```

See also:

- [oslo.i18n Guidelines](https://docs.openstack.org/oslo.i18n/latest/user/guidelines.html)[1]

## Python 3.x Compatibility

OpenStack code should become Python 3.x compatible[1]. That means all Python 2.x-only constructs or dependencies should be avoided[1]. In order to start making code Python 3.x compatible before it can be fully Python 3.x compatible, we have checks for Python 2.x-only constructs[1]:

- **[H231]** `except`. Instead of[1]:

  ```python
  except x,y:
  ```

  Use[1]:

  ```python
  except x as y:
  ```

- **[H232]** Python 3.x has become more strict regarding octal string literals[1]. Use `0o755` instead of `0755`[1]. Similarly, explicit use of long literals (`01234L`) should be avoided[1].

- **[H233]** The `print` operator can be avoided by using[1]:

  ```python
  from __future__ import print_function
  ```

  at the top of your module[1].

- **[H234]** `assertEquals()` logs a DeprecationWarning in Python 3.x, use `assertEqual()` instead[1]. The same goes for `assertNotEquals()`[1].

- **[H235]** `assert_()` is deprecated in Python 3.x, use `assertTrue()` instead[1].

- **[H236]** Use `six.add_metaclass` instead of `__metaclass__`[1].

  Example[1]:

  ```python
  import six

  @six.add_metaclass(Meta)
  class YourClass():
  ```

- **[H237]** Don't use modules that were removed in Python 3[1]. Removed module list: http://python3porting.com/stdlib.html#removed-modules[1]

- **[H238]** Old style classes are deprecated and no longer available in Python 3 (they are converted to new style classes)[1]. In order to avoid any unwanted side effects all classes should be declared using new style[1]. See [the new-style class documentation](https://www.python.org/doc/newstyle/) for reference on the differences[1].

  Example[1]:

  ```python
  class Foo(object):
      pass
  ```

## Creating Unit Tests

For every new feature, unit tests should be created that both test and (implicitly) document the usage of said feature[1]. If submitting a patch for a bug that had no unit test, a new passing unit test should be added[1]. If a submitted bug fix does have a unit test, be sure to add a new one that fails without the patch and passes with the patch[1].

## Unit Tests and assertRaises

A properly written test asserts that particular behavior occurs[1]. This can be a success condition or a failure condition, including an exception[1]. When asserting that a particular exception is raised, the most specific exception possible should be used[1].

- **[H202]** Testing for `Exception` being raised is almost always a mistake since it will match (almost) every exception, even those unrelated to the exception intended to be tested[1].

  This applies to catching exceptions manually with a try/except block, or using `assertRaises()`[1].

  Example[1]:

  ```python
  with self.assertRaises(exception.InstanceNotFound):
      db.instance_get_by_uuid(elevated, instance_uuid)
  ```

- **[H203]** Use assertIs(Not)None to check for None (off by default)[1]. Unit test assertions tend to give better messages for more specific assertions[1]. As a result, `assertIsNone(...)` is preferred over `assertEqual(None, ...)` and `assertIs(None, ...)`, and `assertIsNotNone(...)` is preferred over `assertNotEqual(None, ...)` and `assertIsNot(None, ...)`[1]. Off by default[1].

- **[H204]** Use assert(Not)Equal to check for equality[1]. Unit test assertions tend to give better messages for more specific assertions[1]. As a result, `assertEqual(...)` is preferred over `assertTrue(... == ...)`, and `assertNotEqual(...)` is preferred over `assertFalse(... == ...)`[1]. Off by default[1].

- **[H205]** Use assert(Greater|Less)(Equal) for comparison[1]. Unit test assertions tend to give better messages for more specific assertions[1]. As a result, `assertGreater(Equal)(...)` is preferred over `assertTrue(... >(=) ...)`, and `assertLess(Equal)(...)` is preferred over `assertTrue(... <(=) ...)`[1]. Off by default[1].

- **[H210]** Require `autospec`, `spec`, or `spec_set` in `mock.patch()` or `mock.patch.object()` calls (off by default)[1].

  Users of `mock.patch()` or `mock.patch.object()` may think they are doing a correct assertion for example[1]:

  ```python
  my_mock_obj.called_once_with()
  ```

  When the correct call is[1]:

  ```python
  my_mock_obj.assert_called_once_with()
  ```

  By using `autospec=True` those kind of errors can be caught[1]. This test does not force them to use `autospec=True`, but requires that they define some value for `autospec`, `spec`, or `spec_set`[1]. It could be `autospec=False`[1]. We just want them to make a conscious decision on using or not using `autospec`[1]. If any of the following are used then `autospec` will not be required: `new`, `new_callable`, `spec`, `spec_set`, `wraps`[1].

- **[H211]** Change assertTrue(isinstance(A, B)) by optimal assert like assertIsInstance(A, B)[1].

- **[H212]** Change assertEqual(type(A), B) by optimal assert like assertIsInstance(A, B)[1].

- **[H213]** Check for usage of deprecated assertRaisesRegexp[1].

- **[H214]** Change assertTrue/False(A in/not in B, message) to the more specific assertIn/NotIn(A, B, message)[1].

- **[H215]** Change assertEqual(A in B, True), assertEqual(True, A in B), assertEqual(A in B, False) or assertEqual(False, A in B) to the more specific assertIn/NotIn(A, B)[1].

- **[H216]** Make sure unittest.mock is used instead of the third party mock library[1]. On by default[1].

  Starting with Python 3.3 and later, the mock module was added under unittest[1]. Previously, this functionality was only available by using the third party `mock` library[1].

  Most users are not aware of this subtle distinction[1]. This results in issues where the project does not declare the `mock` library in its requirements file, but the code does an `import mock` assuming that the module is present[1]. This may work initially if one of the project's dependencies ends up pulling that dependency in indirectly, but then can cause things to suddenly break if that transitive dependency goes away[1].

  Since this third party library usage is done without being aware of it, this check is enabled by default to make sure those projects that actually do intend to use the `mock` library are doing so explicitly[1].

## OpenStack Trademark

OpenStack is a registered trademark of the OpenStack Foundation, and uses the following capitalization[1]:

```
OpenStack
```

## OpenStack Licensing

- **[H102 H103]** Newly contributed Source Code should be licensed under the Apache 2.0 license[1]. All source files should have the following header[1]:

  ```python
  #  Licensed under the Apache License, Version 2.0 (the "License"); you may
  #  not use this file except in compliance with the License. You may obtain
  #  a copy of the License at
  #
  #       http://www.apache.org/licenses/LICENSE-2.0
  #
  #  Unless required by applicable law or agreed to in writing, software
  #  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
  #  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
  #  License for the specific language governing permissions and limitations
  #  under the License.
  ```

  Alternately also check for the [SPDX license header](https://spdx.org/licenses/Apache-2.0.html) for Apache 2.0[1]:

  ```python
  # SPDX-License-Identifier: Apache-2.0
  ```

- **[H104]** Files with no code shouldn't contain any license header nor comments, and must be left completely empty[1].

## Commit Messages

Using a common format for commit messages will help keep our git history readable[1].

For further information on constructing high quality commit messages, and how to split up commits into a series of changes, consult the project wiki: https://wiki.openstack.org/GitCommitMessages[1]

## References

[1] https://opendev.org/openstack/hacking/raw/commit/abff65f29b7b00d38bce651a546b05a3eb27b71c/HACKING.rst
    - Full document conversion
    - Retrieved: 2025-10-25