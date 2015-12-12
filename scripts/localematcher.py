#!/usr/bin/env python
"""
development packages required:
    pip install iso3166
"""
import sys,os
# from iso3166 import countries
import json
from optparse import OptionParser

JSON_PATH = os.environ.get('CONTENT_PATH') + 'countrySynonyms.json'


class LocaleMatcher:

    def __init__(self):
        self.country_dict = {}
        self.country_map = {}

    def compare_list(self, input_list):
        un_matched_list = []
        matched_list = []
        if not input_list:
            raise Exception('Unavailable input list ... ')
        for input_country in input_list:
            if input_country in self.country_map.keys():
                matched_list.append(self.country_map[input_country])
            else:
                un_matched_list.append(input_country)
        return matched_list, un_matched_list

    def do_mapping(self):
        for country_item in self.country_dict.items():
            key = country_item[0]
            values = country_item[1]
            for alias_value in values:
                if isinstance(alias_value, int):
                    continue    # TODO : Marked countries in iso 3166 but not supported by SS
                if alias_value in self.country_map and alias_value != self.country_map[alias_value]:
                    raise Exception('duplicated country synonym names...' + alias_value)
                # normalize all synonym names as same as input file's
                alias_value = LocaleMatcher.normalize_country_name(alias_value)
                self.country_map[alias_value] = key
                self.country_map[key] = key  # make sure the new map has the key value

    def load_source_file(self, validate=False):
        with open(JSON_PATH, 'r+') as f:
            self.country_dict = json.load(f, encoding='utf-8')
        self.do_mapping()
        if validate:
            print 'Load source file .......... good'

    def run_matching(self, input_file, handle_name):
        self.load_source_file()
        input_list = LocaleMatcher.load_input_file(input_file)
        result_list = self.compare_list(input_list)
        matched_list = sorted(result_list[0])
        un_matched_list = result_list[1]
        LocaleMatcher.print_result(matched_list, handle_name)
        LocaleMatcher.print_result(un_matched_list, handle_name, is_match=False)

    @staticmethod
    def decoder(ch):
        return ch.decode('utf-8')

    @staticmethod
    def encoder(ch):
        return ch.encode('utf-8')

    @staticmethod
    def normalize_country_name(input_country):
        if isinstance(input_country, unicode):
            return input_country.lower().title()
        return LocaleMatcher.decoder(input_country).lower().title()

    @staticmethod
    def load_input_file(input_file):
        # load input file with normalizing country names
        with open(input_file, 'r+') as f:
            content_list = [line.rstrip('\n') for line in f]
        return map(LocaleMatcher.normalize_country_name, content_list)

    @staticmethod
    def print_result(result_list, handle, is_match=True):
        if is_match:
            print '\n********* Please copy this list to use *********\n'
            for country in result_list:
                print handle + ',' + country
            print
        elif not is_match and len(result_list) > 0:
            print '\n********* Please correct these names and add to source file *********\n'
            print '\n'.join(result_list)
            print


def run(argv):
    parser = OptionParser(usage='%prog -v -n handle -i input-filename', version='%prog 1.0')
    parser.add_option('-n', '--handle', dest='handle')
    parser.add_option('-i', '--input', dest='input')

    if len(argv) == 0:
        parser.print_usage()
        sys.exit(1)

    locale_matcher = LocaleMatcher()

    if argv[0] != '-v':
        (options, args) = parser.parse_args()
        if options.handle is None:
            parser.error('Please enter handle name !')
        elif options.input is None:
            parser.error('Please enter input file !')
        else:
            handle = options.handle
            input_file = options.input
            locale_matcher.run_matching(input_file, handle)
    else:
        locale_matcher.load_source_file(validate=True)

if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
