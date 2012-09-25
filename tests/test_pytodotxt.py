#!/usr/bin/env python
# encoding: utf-8

import unittest
from pytodotxt.pytodotxt import TodoTxt


class Test(unittest.TestCase):
    def setUp(self):
        self.filename = 'tests/todo.test.txt'
        self.todo = TodoTxt(self.filename)

    def test_num_entries(self):
        self.assertEquals(9, len(self.todo.entrys))

    def test_get_filterd(self):
        one_keyword = self.todo.get(keywords=['Handy'])
        self.assertEquals(2, len(one_keyword))

        two_projects = self.todo.get(projects=['aa', 'server'])
        self.assertEquals(1, len(two_projects))

    def test_add(self):
        self.todo.add(text='A test @dev')
        self.assertEquals(10, len(self.todo.entrys))

    def test_write(self):
        """Adds one entry and writes all entrys to a new file. Then checks if
        all entrys have been correctly written to the file."""

        new_filename = 'tests/todo.write.txt'
        self.todo.add(text='A test @dev')
        self.assertEquals(10, len(self.todo.entrys))

        # Write to another file
        self.todo.write(new_filename)

        lines = []
        with open(new_filename, 'r') as f:
            for line in f.readlines():
                lines.append(line.strip())

        for entry in self.todo.entrys:
            self.assertTrue(str(entry in lines))


class TestStr(unittest.TestCase):
    """Reads a well formated todo.txt and checks if the internal string
    representation is the same as the respective line in the file."""

    def setUp(self):
        self.filename = 'tests/todo.wellformatted.txt'
        self.todo = TodoTxt(self.filename)

    def test_str(self):
        lines = []
        with open(self.filename, 'r') as f:
            for line in f.readlines():
                lines.append(line.strip())

        for entry in self.todo.entrys:
            self.assertTrue(str(entry) in lines)


class TestNoFile(unittest.TestCase):
    def test_no_file(self):
        with self.assertRaises(IOError):
            TodoTxt('filenotfound.txt')
