import os
import argparse
from random import random, choice, shuffle

import nltk
import feedparser
from pattern.en.wordlist import BASIC
from pattern.en import wordnet, conjugate, pluralize, singularize, quantify

from crawl import fetch_arxiv_ids, save_raw_abstracts, get_raw_abstracts
nltk.data.path.append('./nltk_data/')

DATADIR = 'data'
FIELDS = ['cond-mat', 'physics', 'math', 'nlin', 'cs', 'q-bio', 'stat']
ALL_FIELDS = ["astro-ph", "astro-ph.EP", "astro-ph.HE", "astro-ph.CO", "astro-ph.IM", 
    "astro-ph.SR", "astro-ph.GA", "cond-mat", "cond-mat.dis-nn", "cond-mat.soft", 
    "cond-mat.mtrl-sci", "cond-mat.stat-mech", "cond-mat.quant-gas", "cond-mat.supr-con", 
    "cond-mat.str-el", "cond-mat.mes-hall", "cond-mat.other", "gr-qc", "hep-ex", 
    "hep-lat", "hep-ph", "hep-th", "math-ph", "nlin", "nlin.CG", "nlin.CD", 
    "nlin.SI", "nlin.AO", "nlin.PS", "nucl-ex", "nucl-th", "physics", "physics.pop-ph", 
    "physics.space-ph", "physics.data-an", "physics.optics", "physics.soc-ph", 
    "physics.atm-clus", "physics.flu-dyn", "physics.gen-ph", "physics.bio-ph", 
    "physics.hist-ph", "physics.plasm-ph", "physics.atom-ph", "physics.med-ph", 
    "physics.geo-ph", "physics.acc-ph", "physics.class-ph", "physics.ins-det", 
    "physics.comp-ph", "physics.ed-ph", "physics.chem-ph", "physics.ao-ph", 
    "quant-ph", "math", "math.IT", "math.NT", "math.AP", "math.ST", "math.PR", 
    "math.OA", "math.CV", "math.AG", "math.RT", "math.MG", "math.GR", "math.MP", 
    "math.HO", "math.SG", "math.CO", "math.GN", "math.DG", "math.GT", "math.NA", 
    "math.LO", "math.DS", "math.OC", "math.QA", "math.GM", "math.AC", "math.AT", 
    "math.KT", "math.CA", "math.SP", "math.FA", "math.CT", "math.RA", "cs", 
    "cs.ET", "cs.SC", "cs.MA", "cs.GL", "cs.IT", "cs.IR", "cs.CC", "cs.FL", 
    "cs.OS", "cs.SD", "cs.PL", "cs.SI", "cs.CV", "cs.LG", "cs.NE", "cs.DB", 
    "cs.OH", "cs.NA", "cs.SE", "cs.SY", "cs.DC", "cs.MS", "cs.AR", "cs.PF", 
    "cs.DL", "cs.CE", "cs.CR", "cs.AI", "cs.GT", "cs.DM", "cs.HC", "cs.MM", 
    "cs.CL", "cs.CY", "cs.DS", "cs.NI", "cs.LO", "cs.RO", "cs.CG", "cs.GR", 
    "q-bio", "q-bio.BM", "q-bio.GN", "q-bio.TO", "q-bio.CB", "q-bio.SC", 
    "q-bio.PE", "q-bio.NC", "q-bio.MN", "q-bio.QM", "q-bio.OT", "q-fin", 
    "q-fin.TR", "q-fin.CP", "q-fin.PM", "q-fin.PR", "q-fin.GN", "q-fin.RM", 
    "q-fin.EC", "q-fin.MF", "q-fin.ST", "stat", "stat.TH", "stat.ME", 
    "stat.OT", "stat.ML", "stat.CO", "stat.AP"]

def generate(key='q-bio.NC', years=range(2010, 2016), outdir=DATADIR):
    """ src: https://github.com/centrality/arxiv/blob/master/arxiv/crawl.py """
    ids = fetch_arxiv_ids(key, years)
    os.mkdir(outdir)
    save_raw_abstracts(ids, outdir)

def load(indir=DATADIR, load_new=False, key='q-bio.NC', years='new'):
    if load_new:
        ids = fetch_arxiv_ids(key, years)
        xs = get_raw_abstracts(ids)
        return feedparser.parse(''.join(xs[0]))
    else:
        infile = os.path.join(indir, '0.txt')
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

def getsubfield(field=None, subfield=None):
    if subfield is None:
        if field is None:
            field = choice(FIELDS)
        subfield = choice([x for x in ALL_FIELDS if field in x])
    return subfield

def justone(atom=None, pred=None):
    if pred is None:
        pred = lambda x: True
    if atom is None:
        atom = load(load_new=True, key=getsubfield(), years='new')
    success = False
    i = 0
    while not success:
        if i > 100:
            return justone(pred=pred)
        i += 1
        content = clean(choice(atom.entries)['title'])
        phrase, success = convert(content, 2)
        success = success and pred(phrase) and '$' not in phrase
    return phrase.title()

def main(n=1, field=None, subfield=None):
    atom = load(load_new=True, key=getsubfield(field, subfield), years='new')
    for i in xrange(n):
        print justone(atom=atom)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--field', type=str, default=None, help='arxiv field')
    parser.add_argument('--subfield', type=str, default=None, help='arxiv subfield')
    parser.add_argument('-n', '--number', type=int, default=10, help='# of titles to generate')
    args = parser.parse_args()
    main(n=args.number, field=args.field, subfield=args.subfield)
