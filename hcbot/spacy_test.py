# -*- coding:utf-8 -*-


def test_zh():
    import zh_core_web_sm
    nlp = zh_core_web_sm.load()
    doc = nlp("我去食堂吃饭")

    print(">>tokens")
    for token in doc:
        print(token)

    print(">>sents")
    print(list(doc.sents))

    print(">>tags")
    for w in doc:
        print(w.pos, w.pos_)

    print(">>ents")
    print(list(doc.ents))


def test_en():
    print("importing spacy")
    import spacy
    print("load en dict")
    nlp = spacy.load('zh')
    print("doing nlp")
    doc = nlp('我是中国人')
    print(">>tokens")
    for token in doc:
        print(token)

    print(">>sents")
    print(list(doc.sents))

    print(">>tags")
    for w in doc:
        print(w.pos, w.pos_)

    print(">>ents")
    print(list(doc.ents))

if __name__ == '__main__':
    test_en()