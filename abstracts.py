import os
from random import random, choice, shuffle

import nltk
import feedparser
from pattern.en.wordlist import BASIC
from pattern.en import wordnet, conjugate, pluralize, singularize, quantify

from crawl import fetch_arxiv_ids, save_raw_abstracts
nltk.data.path.append('./nltk_data/')

DATADIR = 'data'

def generate(key='q-bio.NC', years=range(2010, 2016), outdir=DATADIR):
    """ src: https://github.com/centrality/arxiv/blob/master/arxiv/crawl.py """
    ids = fetch_arxiv_ids(key, years)
    os.mkdir(outdir)
    save_raw_abstracts(ids, outdir)

def load(indir):
    infile = os.path.join(DATADIR, '0.txt')
    return feedparser.parse(infile)

def clean(entry):
    return ' '.join([x.strip() for x in entry.replace('\n', ' ').split()])
    
def find_replacement(word, pos):
    shuffle(BASIC)
    try:
        w = next(w for w in BASIC if wordnet.synsets(w, pos=pos))
        return (w, True) if random() < 0.3 else (word, False)
    except:
        return word, False

def convert(title, thresh_count=0):
    # print title
    # print '----'
    count = 0
    sentence = nltk.word_tokenize(title)
    tags = nltk.pos_tag(sentence)

    words = []
    new_words = []
    for i, (word, pos) in enumerate(tags):
        cur = ''.join(words)
        next_char = title[title.find(cur)+len(cur)]
        space = ' ' if next_char == ' ' else ''
        words.append(space + word)
        wrap = lambda x: x.title() if word.istitle() else x
        new_word, c = find_replacement(word, pos)
        count += c
        new_words.append(space + wrap(new_word))

    return ''.join(new_words), count >= thresh_count

def justone(atom=None, datadir=DATADIR, pred=None):
    if pred is None:
        pred = lambda x: True
    if atom is None:
        atom = load(datadir)
    success = False
    while not success:
        phrase, success = convert(clean(choice(atom.entries)['title']), 2)
        success = success and pred(phrase)
    return phrase

def main(datadir=DATADIR):
    atom = load(datadir)
    for i in xrange(10):
        print justone(atom=atom)

if __name__ == '__main__':
    main()
