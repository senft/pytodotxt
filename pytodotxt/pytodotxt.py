#!/usr/bin/env python
# encoding: utf-8

"""
TODO:
    - Rule 2: The date of completion appears directly after the x, separated by
      a space.
    - Ability to keep backups
"""

from datetime import datetime
import logging
from re import findall

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG)


class TodoTxt():
    def __init__(self, filename=None):
        self.entrys = list()
        if filename:
            self.read(filename)

    def read(self, filename):
        """Reads a given todo.txt file."""
        with open(filename, 'r') as f:
            for line in f:
                try:
                    new_entry = self._parse_entry(line)
                    self.entrys.append(new_entry)
                except ValueError:
                    logging.warning('Could not parse line: [{0}]'.format(line))
            logging.info('Read {0} entry(s)'.format(len(self.entrys)))

    def add(self, text, prio='', date=''):
        contexts = [c.replace('@', '') for c in findall(r'@\S+', text)]
        projects = [p.replace('+', '') for p in findall(r'\+\S+', text)]
        new_entry = {'id': len(self.entrys), 'text': text, 'done': False,
                     'prio': prio, 'date': date, 'contexts': contexts,
                     'projects': projects}
        self.entrys.append(new_entry)

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
        for entry in self.entrys:
            if entry['id'] == id:
                self.entrys.remove(entry)

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

    def write(self, filename):
        """Writes all entrys to a given file."""
        with open(filename, 'w') as f:
            for entry in self.entrys:
                f.write(self._entry_to_string(entry) + '\n')
            logging.info('Wrote {0} entrys to file {1}'.format(
                len(self.entrys), filename))

    def _parse_entry(self, line):
        """Parses a line from a todo.txt file into a dict."""
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

        contexts = [c.replace('@', '') for c in findall(r'@\S+', text)]
        projects = [p.replace('+', '') for p in findall(r'\+\S+', text)]

        return {'id': len(self.entrys), 'text': text, 'done': done, 'prio':
                prio, 'date': date, 'contexts': contexts, 'projects': projects}

    def _entry_to_string(self, entry):
        """Creates a string represetation for this entry."""
        result = []
        if entry['done']:
            result.append('x ')

        if entry['prio']:
            result.extend(['(', entry['prio'], ') '])

        if entry['date']:
            result.extend([entry['date'], ' '])

        result.append(entry['text'])
        return ''.join(result).strip()

    def _sort(self, entry):
        """Sorts all entrys, after the following criterea:
            - Done?
            - Date
            - Text
        This is only used when creating a string representation of this object,
        so we don't change order of the entrys.
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
        for entry in sorted(self.entrys, key=self._sort):
            result.append(self._entry_to_string(entry))
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

    #todo.do(2)
    #todo.remove(2)


if __name__ == '__main__':
    main()
