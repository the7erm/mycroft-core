# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from time import time, sleep
# from mycroft.util import log

import string
import random
import itertools

__author__ = 'the7erm'

# logger = log.getLogger(__name__)

__doc__ = """

"""

dir(string)

genrator_characters = (string.ascii_uppercase + string.digits +
                       string.ascii_lowercase)


def id_generator(size=8, chars=genrator_characters):
    return ''.join(random.choice(chars) for _ in range(size))


class MycroftContextManager(object):

    def __init__(self):
        # The history is a chronological history.  new stuff at top
        self.history = []

    def insert(self, skill, metadata):

        item = {
            "id": id_generator(),
            "metadata": metadata,
            "skill": skill,
            "timestamp": time()
        }

        self.history.insert(0, item)

    def icontains(self, key, value, limit=10, mode="in"):
        key_parts = key.split(".")

        if isinstance(value, (str, unicode)):
            value = value.lower()

        def focus_on(x):
            data = x
            for key in key_parts:
                data = data.get(key, {})

            if isinstance(data, (str, unicode)):
                data = data.lower()

            if mode == "not":
                return value not in data

            return value in data

        return self.recall(limit=limit, filter_by=focus_on)

    def not_icontains(self, key, value, limit=10):
        return self.icontains(key, value, limit=limit, mode="not")

    def callibrate_history(self, focus, forget=False):
        if forget:
            # Forget everything else
            self.history = focus
        else:
            # Prepend the focus so it's first.
            self.history = focus + self.history
            self.uniquify_history()

    def focus(self, key, value, limit=10, forget=False):
        # Re-weigh the entire stack.
        # There is probably a better way to do this.
        focus = [x for x in self.icontains(key, value, limit=None)]
        self.callibrate_history(focus, forget)
        return self.icontains(key, value, limit=limit)

    def blur(self, key, value, limit=10, forget=False):
        # Inverse of focus
        focus = [x for x in self.not_icontains(key, value, limit=None)]
        self.callibrate_history(focus, forget)
        return self.not_icontains(key, value, limit=limit)

    def uniquify_history(self):
        remove_idx = []
        ids = []
        for idx, item in enumerate(self.history):
            if item['id'] in ids:
                remove_idx.append(idx)
            else:
                ids.append(item['id'])

        while remove_idx:
            idx = remove_idx.pop()

    def recall(self, limit=10, filter_by=None):
        """
        """

        if not filter_by:
            # Return True no matter what
            def filter_function(item):
                return True
        elif hasattr(filter_by, '__call__'):
            filter_function = filter_by
        elif isinstance(filter_by, dict):
            def filter_function(item):
                res = False

                for k, v in filter_by.items():
                    if item.get(k) == v:
                        res = True
                        break

                return res

        cnt = 0
        for item in itertools.ifilter(filter_function, self.history):
            cnt += 1
            if limit > 0 and cnt > limit:
                break
            yield item

        self.forget()

    def forget(self):
        now = time()
        remove_items = []

        # TODO figure out when to forget an item.

        while remove_items:
            item = remove_items.pop()
            self.history.remove(item)

        return self

context_manager = MycroftContextManager()

if __name__ == "__main__":
    for i in range(0, 1000):
        metadata = {
            "test": "test value %s" % i
        }
        context_manager.insert("TestSkill%s" % i, metadata)

    for item in context_manager.recall(filter_by={"skill": "TestSkill1"}):
        print "TestSkill1 item:", item

    for item in context_manager.recall(filter_by={"skill": "TestSkill2"}):
        print "TestSkill2 item:", item

    for item in context_manager.icontains("metadata.test", "2"):
        print "icontains:", item

    for item in context_manager.not_icontains("metadata.test", "2"):
        print "not_icontains:", item

    for item in context_manager.history[0:10]:
        print "before:", item

    for item in context_manager.focus("metadata.test", "2"):
        print "focus:", item

    for item in context_manager.history[0:10]:
        print "after focus:", item

    for item in context_manager.blur("metadata.test", "2"):
        print "blur:", item

    for item in context_manager.history[0:10]:
        print "after blur:", item
