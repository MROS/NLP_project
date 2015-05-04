#! /usr/bin/python3
import jieba.posseg as pseg
import sys
import math


class Sentence:
    def __init__(self, sentence):
        self.sentence = sentence
        self.sentence_with_pos = list(pseg.cut(sentence))

    def set_attr(self, identifier, redundant):
        self.id = identifier
        self.redundant = redundant

    def pos_iter(self, n):
        s_with_pos = self.sentence_with_pos
        for position in range(0, len(s_with_pos)):
            prefix = []
            for shift in range(-n + 1, 0):
                if position + shift < 0:
                    prefix.append(None)
                else:
                    prefix.append(s_with_pos[position + shift].flag)
            prefix = tuple(prefix)
            th = s_with_pos[position].flag
            yield (prefix, th)


# 做有兩種平滑版本
class Ngram:
    def __init__(self, n, sentences):
        self.n = n
        self.POS_KINDS = 39  # 我去數的，不知道對不對
        self.add_k_zero_prob = 0
        self.count = self.count(sentences)
        self.total_gram = sum(self.count.values())
        self.add_k_prob,  self.add_k_zero_prob = self.count_add_k_prob(0.5)
        self.good_turing_prob,  self.good_turing_zero_prob = self.count_good_turing_prob()
        print("ngram 計算結束", file=sys.stderr)

    # 回傳目前的計數
    # 用個dictionary來紀錄
    # None 代表在字首
    def count(self, sentences):
        count = {}
        for sentence in sentences:
            grams = sentence.pos_iter(n)
            for gram in grams:
                try:
                    count[gram] += 1
                except KeyError:
                    count[gram] = 1
        return count

    def count_add_k_prob(self, k):
        original_prob = {}
        for key in self.count:
            original_prob[key] = (self.count[key] + k) / (self.total_gram + k * len(self.count))
        add_k_zero_prob = k / (self.total_gram + k * len(self.count))
        return original_prob, add_k_zero_prob

    def add_k_prob_f(self, gram):
        try:
            ans = self.add_k_prob[gram]
        except KeyError:
            ans = self.add_k_zero_prob
        return ans

    def count_good_turing_prob(self):
        # 超過五以上就不用
        times = {}
        good_turing_prob = {}
        for key in self.count:
            try:
                times[self.count[key]] += 1
            except KeyError:
                times[self.count[key]] = 1
        print(times, file=sys.stderr)
        for key in self.count:
            if self.count[key] <= 5:
                n = self.count[key]
                good_turing_prob[key] = (n + 1) * (times[n + 1] / times[n]) / self.total_gram
            else:
                good_turing_prob[key] = self.count[key] / self.total_gram
        times[0] = self.POS_KINDS**self.n - len(self.count)
        good_turing_zero = times[1] / times[0] / self.total_gram
        return good_turing_prob, good_turing_zero

    def good_turing_prob_f(self, gram):
        try:
            ans = self.good_turing_prob[gram]
        except KeyError:
            ans = self.good_turing_zero_prob
        return ans

    def prob_to_gen(self, sentence, method):
        prob = 0
        for gram in sentence.pos_iter(self.n):
            if method == 'good_turing':
                prob += math.log(self.good_turing_prob_f(gram))
            elif method == 'add_k':
                prob += math.log(self.add_k_prob_f(gram))
        return prob



def get_sentence(train_data):
    f = open(train_data, "r")
    sentences = []
    for line in f:
        redundant = (line.split("\t")[1] == '1')
        sentence = line.split("\t")[2]
        id = int(line.split("\t")[0].split("-")[1])
        s = Sentence(sentence)
        s.set_attr(id, redundant)
        sentences.append(s)
    return sentences

def get_test_sentence(train_data):
    f = open(train_data, "r")
    sentences = []
    for line in f:
        sentence = line.split("\t")[1]
        id = int(line.split("\t")[0].split("-")[1])
        s = Sentence(sentence)
        s.set_attr(id, False)
        sentences.append(s)
    return sentences

def print_result(test_data, fun):
    for s in test_data:
        print("p1test-{0} \t".format(s.id), end="")
        if fun(s):
            print("0")
        else:
            print("1")


# 測試已經知結果的資料，以fun來評估正確的機率
def judge(sentences, fun):
    correct = list(filter(lambda s: not s.redundant, sentences))
    incorrect = list(filter(lambda s: s.redundant, sentences))
    total = 0; shoot = 0
    for s in correct:
        total += 1
        if fun(s):
            shoot += 1
    for s in incorrect:
        total += 1
        if not fun(s):
            shoot += 1
    print("result: {0} / {1} = {2}".format(shoot, total, shoot / total), file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage : redundant.py [input_file] [n].\n", file=sys.stderr)
        print("usage : redundant.py [train_file] [n] [output_file].\n", file=sys.stderr)
        sys.exit(0)
    n = int(sys.argv[2])
    sentences = get_sentence(sys.argv[1])
    length = len(sentences)
    bound = int(length*0.97)
    train_s = sentences[0:bound]
    correct = list(filter(lambda s: not s.redundant, train_s))
    incorrect = list(filter(lambda s: s.redundant, train_s))
    correct_ngram, incorrect_ngram = (Ngram(n, correct), Ngram(n, incorrect))
    if len(sys.argv) == 3:
        test_s = sentences[bound:]
        # test_s = get_sentence(sys.argv[3])
        # test_s = get_test_sentence(sys.argv[3])
        print("all true", file=sys.stderr)
        judge(test_s, lambda s: True)
        print("add-k method", file=sys.stderr)
        judge(test_s, lambda s: correct_ngram.prob_to_gen(s, 'add_k') > incorrect_ngram.prob_to_gen(s, 'add_k'))
        print("good_turing method", file=sys.stderr)
        judge(test_s, lambda s: correct_ngram.prob_to_gen(s, 'good_turing') > incorrect_ngram.prob_to_gen(s, 'good_turing'))
    elif len(sys.argv) == 4:
        test_s = get_test_sentence(sys.argv[3])
        print_result(test_s, lambda s: correct_ngram.prob_to_gen(s, 'add_k') > incorrect_ngram.prob_to_gen(s, 'add_k'))

