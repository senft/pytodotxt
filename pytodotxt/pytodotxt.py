#!/usr/bin/env python
# encoding: utf-8

"""
TODO:
    - It's bad that we rewrite the entrys sorted.. The order should not be
      altered
    - Rule 2: The date of completion appears directly after the x, separated by
      a space.
    - Ability to keep backups
"""

from datetime import datetime
import logging
import re

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG)


class Entry(dict):
    def __init__(self, idn=0, done=False, date='', prio='', text=''):
        dict.__init__(self)
        self['id'] = idn
        self['done'] = done
        self['prio'] = prio
        self['date'] = date
        self['text'] = text
        self['contexts'] = [c.replace('@', '') for c in re.findall(r'@\S+',
                                                                   text)]
        self['projects'] = [p.replace('+', '') for p in re.findall(r'\+\S+',
                                                                   text)]

    def __str__(self):
        """Creates a string represetation for this entry."""
        result = []
        if self['done']:
            result.append('x ')

        if self['prio']:
            result.extend(['(', self['prio'], ') '])

        if self['date']:
            result.extend([self['date'], ' '])

        result.append(self['text'])
        return ''.join(result)


class TodoTxt():
    def __init__(self, filename=None):
        self.entrys = list()
        if filename:
            self.read(filename)

    def read(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                try:
                    new_entry = self._parse_entry(line)
                    self.entrys.append(new_entry)
                except ValueError:
                    logging.warning('Could not parse line: [{0}]'.format(line))
            self.entrys.sort(key=self._sort)
            logging.info('Read {0} entry(s)'.format(len(self.entrys)))

    def add(self, text, prio='', date=''):
        new_entry = Entry(text=text, prio=prio, date=date)
        self.entrys.append(new_entry)
        self.entrys.sort(key=self._sort)

    def do(self, id, add_date=False):
        """Marks the entry with the given ID as 'done'. Returns true if the
        state was changed, else False."""
        for entry in self.entrys:
            if entry['id'] == id:
                already_done = entry['done']
                entry['done'] = True
                return not already_done
        raise False

    def remove(self, id):
        """Removes the entry with the given ID from the list of entrys."""
        pass

    def get(self, keywords=[], projects=[], contexts=[], sorted=True):
        """Returns the entrys that contain all of the given fields.
        An entry has to contain all elements of the the lists.
        Note: The projects and contexts can but do not have to be preceeded by
        a '+' or '@'.

        Keyword arguments:
        keywords -- the list of keywords
        projects -- the list of projects (e.g. ['+proj1', 'proj2'])
        contexts -- the list of contexts (e.g. ['@job', 'rl'])
        """
        return [entry for entry in self.entrys
                if all([keyword in entry['text'] for keyword in keywords])
                and all([project in entry['projects'] for project in projects])
                and all([context in entry['contexts'] for context in contexts])
                ]

    def _parse_entry(self, line):
        if not line.strip():
            # Catches empty lines
            raise ValueError

        done = line[0] == 'x'
        if done:
            line = line[2:].strip()

        if line and line[0] == '(':
            # line is not empty and we have a priority to parse
            prio = line[1]
            line = line[3:].strip()
        else:
            prio = ''

        try:
            date = line[0:10]
            (datetime.strptime(date, '%Y-%m-%d'))
            line = line[11:].strip()
        except ValueError:
            # No date could be parsed
            date = ''

        text = line.strip()
        return Entry(idn=len(self.entrys), text=text, done=done, prio=prio,
                     date=date)

    def write(self, filename):
        """Writes all entrys to the file they have been read from."""
        with open(filename, 'w') as f:
            for entry in self.entrys:
                f.write(str(entry) + '\n')
            logging.info('Wrote {0} entrys to file {1}'.format(
                len(self.entrys), filename))

    def _sort(self, entry):
        """Sorts all entrys, after the following criterea:
             - Done?
             - Date
             - Text
        """
        if entry['done']:
            return ''.join(['Z', entry['prio'], entry['date'], entry['text']])
        elif entry['date']:
            return ''.join(['A', entry['prio'], entry['date'], entry['text']])
        else:
            return ''.join(['A', entry['prio'], entry['text']])

    def __str__(self):
        """Creates a string represetation for this entry."""
        result = []
        for entry in self.entrys:
            result.append(str(entry))
        return '\n'.join(result)


def main():
    FILE = 'todo.txt'

    try:
        todo = TodoTxt(FILE)
    except IOError:
        logging.error('Could not open file ({0})'.format(FILE))
        import sys
        sys.exit(1)

    print(todo)

    todo.do(2)

    print(todo)


if __name__ == '__main__':
    main()
