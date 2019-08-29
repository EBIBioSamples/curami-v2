import re

import inflection
from nltk.corpus import words

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

spaces_in_parenthesis_re = re.compile('([([])\s+(.*)\s+([\\)\\]])')
extra_spaces_re = re.compile(r'\s+')

leading_apostrophe_dash = re.compile(r'^[-\']')
dash_followed_by_underscore_re = re.compile(r'([-:=./])(_)')
space_around_slash = re.compile(r' / | /|/ ')
double_quotes_re = re.compile(r'(\"+)(.+?)(\"+)')

abbreviations = {}
metrics = {}
short_words = set()


class WordProcessor:

    def __init__(self):
        self.populate_abbreviations()
        self.populate_metrics()
        self.populate_short_words()

    @staticmethod
    def normalize_word(word):
        return word.lower().strip()

    @staticmethod
    def dictionary_check(phrase):
        for word in phrase.split():
            if word not in words.words():
                return False
        return True

    # should we remove unbalanced parenthesis
    def cleanup_string(self, string_to_clean, convert_to_snake):
        clean_string = string_to_clean
        if convert_to_snake:
            clean_string = self.camel_to_snake(clean_string)

        # remove white spaces between parenthesis
        clean_string = spaces_in_parenthesis_re.sub(r'\1\2\3', clean_string)

        clean_string = leading_apostrophe_dash.sub("", clean_string)
        clean_string = dash_followed_by_underscore_re.sub("-", clean_string)
        clean_string = space_around_slash.sub("/", clean_string)
        clean_string = extra_spaces_re.sub(" ", clean_string)

        # replace backword slashes with forward
        clean_string = clean_string.replace("\"", "")
        clean_string = clean_string.replace("\\", "/")

        # snake to space separated
        # clean_string = inflection.humanize(clean_string) # removes _id from string
        clean_string = clean_string.replace('_', ' ')

        # to lower case considering the abbreviations
        clean_string = self.to_lower_case(clean_string)

        # remove all other extra whitespace characters
        clean_string = extra_spaces_re.sub(' ', clean_string).strip()

        return clean_string

    def get_metric(self, metric):
        if metric in metrics:
            return metrics[metric]
        else:
            return ''

    def get_abbreviation(self, abbreviation):
        if abbreviation in abbreviations:
            return abbreviations[abbreviation]
        else:
            return ''

    def camel_to_snake(self, string_to_clean):
        clean_string = string_to_clean
        # clean_string = first_cap_re.sub(r'\1_\2', clean_string)
        # clean_string = all_cap_re.sub(r'\1_\2', clean_string)
        clean_string = inflection.underscore(clean_string)
        clean_string = dash_followed_by_underscore_re.sub(r'\1', clean_string)
        if not self.words_more_than_two_characters(clean_string):
            clean_string = string_to_clean
        return clean_string

    def to_lower_case(self, string_to_lower):
        lower_cased_string = string_to_lower.lower()
        for word in lower_cased_string.split():
            if word in abbreviations:
                lower_cased_string = lower_cased_string.replace(word, abbreviations[word])

        return lower_cased_string

    def words_more_than_two_characters(self, phrase):
        phrase = phrase.replace("_", " ")
        for word in phrase.split():
            if len(word) < 3 and word.lower() not in short_words:
                return False
        return True

    def populate_abbreviations(self):
        with open("../../resources/known_abbreviation.txt", 'r') as abbreviation_file:
            for abbreviation in abbreviation_file:
                abbreviations[WordProcessor.normalize_word(abbreviation)] = abbreviation

    def populate_metrics(self):
        with open("../../resources/known_metrics.txt", 'r') as metric_file:
            for metric in metric_file:
                metrics[WordProcessor.normalize_word(metric)] = metric

    def populate_short_words(self):
        with open("../../resources/short_words.txt", 'r') as short_word_file:
            for word in short_word_file:
                short_words.add(WordProcessor.normalize_word(word))

# main()
