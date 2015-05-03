import jieba.posseg as pseg
import sys


class Sentence:
    def __init__(self, sentence, redundant):
        self.sentence = sentence
        self.sentence_with_pos = list(pseg.cut(sentence))
        self.redundant = redundant
        print("redundant: {0}, pos: {1}".format(self.redundant, list(map(lambda a: a.flag, self.sentence_with_pos))))


# 做有平滑跟無平滑版本
class Ngram:
    def __init__(self, n, sentences):
        self.n = n
        self.count(sentences)

    # 回傳目前的計數
    # 用個dictionary來紀錄
    # None 代表在字首
    def count(self, sentences):
        count = {}
        for sentence in sentences:
            s_with_pos = sentence.sentence_with_pos
            for position in range(0, len(s_with_pos)):
                prefix = []
                for shift in range(-self.n, 0):
                    if position + shift < 0:
                        prefix.append(None)
                    else:
                        prefix.append(s_with_pos[position + shift].flag)
                prefix = tuple(prefix)
                th = s_with_pos[position].flag
                try:
                    count[(prefix, th)] += 1
                except KeyError:
                    count[(prefix, th)] = 1
        print(count)


def get_ngram(n, train_data):
    f = open(train_data, "r")
    correct = []
    incorrect = []
    for line in f:
        redundant = (line.split("\t")[1] == '1')
        sentence = line.split("\t")[2]
        if redundant:
            incorrect.append(Sentence(sentence, redundant))
        else:
            correct.append(Sentence(sentence, redundant))
    print("詞性分析結束\n")
    return (Ngram(n, correct), Ngram(n, incorrect))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage : test.py [input_file] [n].\n")
        sys.exit(0)
    n = int(sys.argv[2])
    a = get_ngram(n, sys.argv[1])
