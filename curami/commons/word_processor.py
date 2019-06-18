import re
from nltk.corpus import words
import inflection

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

spaces_in_parenthesis_re = re.compile('\\s+(?=[^()]*\\))')
spaces_in_brackets_re = re.compile('\\s+(?=[^\\[\\]]*\\])')
extra_spaces_re = re.compile(r'\s+')

leading_apostrophe_dash = re.compile(r'^[-\']')
dash_followed_by_underscore_re = re.compile(r'([-:=./])(_)')
space_around_slash = re.compile(r' / | /|/ ')
double_quotes_re = re.compile(r'(\"+)(.+?)(\"+)')

abbreviations = {}
metrics = {}
short_words = set()


def main():
    populate_abbreviations()
    populate_metrics()
    populate_short_words()
    test()


def test():
    test1 = 'HelloHow are_you_EBI and WhatHappenEGAToMetadata'


    print(cleanup_string(test1, True))


def normalize_word(word):
    return word.lower().strip()


# should we remove unbalanced parenthesis
def cleanup_string(string_to_clean, convert_to_snake):
    clean_string = string_to_clean
    if convert_to_snake:
        clean_string = camel_to_snake(clean_string)

    # remove white spaces between parenthesis
    clean_string = spaces_in_parenthesis_re.sub('', clean_string)
    clean_string = spaces_in_brackets_re.sub('', clean_string)

    clean_string = leading_apostrophe_dash.sub("", clean_string)
    clean_string = dash_followed_by_underscore_re.sub("-", clean_string)
    clean_string = space_around_slash.sub("/", clean_string)
    clean_string = extra_spaces_re.sub(" ", clean_string)

    # replace backword slashes with forward
    clean_string = clean_string.replace("\"", "")
    clean_string = clean_string.replace("\\", "/")

    # snake to space separated
    clean_string = inflection.humanize(clean_string)

    # to lower case considering the abbreviations
    clean_string = to_lower_case(clean_string)

    # remove all other extra whitespace characters
    clean_string = extra_spaces_re.sub(' ', clean_string).strip()

    return clean_string


def get_metric(metric):
    if metric in metrics:
        return metrics[metric]
    else:
        return ''


def get_abbreviation(abbreviation):
    if abbreviation in abbreviations:
        return abbreviations[abbreviation]
    else:
        return ''


def camel_to_snake(string_to_clean):
    clean_string = string_to_clean
    # clean_string = first_cap_re.sub(r'\1_\2', clean_string)
    # clean_string = all_cap_re.sub(r'\1_\2', clean_string)
    clean_string = inflection.underscore(clean_string)
    clean_string = dash_followed_by_underscore_re.sub(r'\1', clean_string)
    if not words_more_than_two_characters(clean_string):
        clean_string = string_to_clean
    return clean_string


def to_lower_case(string_to_lower):
    lower_cased_string = string_to_lower.lower()
    for word in lower_cased_string.split():
        if word in abbreviations:
            lower_cased_string = lower_cased_string.replace(word, abbreviations[word])

    return lower_cased_string


def words_more_than_two_characters(phrase):
    phrase = phrase.replace("_", " ")
    for word in phrase.split():
        if len(word) < 3 and word.lower() not in short_words:
            return False
    return True


def dictionary_check(phrase):
    for word in phrase.split():
        if word not in words.words():
            return False
    return True


def populate_abbreviations():
    with open("../../resources/known_abbreviation.txt", 'r') as abbreviation_file:
        for abbreviation in abbreviation_file:
            abbreviations[normalize_word(abbreviation)] = abbreviation


def populate_metrics():
    with open("../../resources/known_metrics.txt", 'r') as metric_file:
        for metric in metric_file:
            metrics[normalize_word(metric)] = metric


def populate_short_words():
    with open("../../resources/short_words.txt", 'r') as short_word_file:
        for word in short_word_file:
            short_words.add(normalize_word(word))




main()
