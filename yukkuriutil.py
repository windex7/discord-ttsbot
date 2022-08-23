import MeCab
import unicodedata
import string

def format_text(text):
    text = unicodedata.normalize("NFKC", text)
    table = str.maketrans("", "", string.punctuation + "「」、。・")
    text = text.translate(table)
    return text

m = MeCab.Tagger()

"""
mecab.parse('')
node = mecab.parseToNode(text)
while node:
    word = node.surface
    pos = node.feature.split(",")[1]
    print('{0},{1}'.format(word, pos))
    node = node.next
"""

def get_pron(text):
    m_result = m.parse(text).splitlines()
    m_result = m_result[:-1]

    pro = ''
    for v in m_result:
        if '\t' not in v: continue
        surface = v.split('\t')[0]
        p = v.split('\t')[1].split(',')[-1]
        if p == '*' : p = surface
        pro += p

    pro = format_text(pro)

    return pro
