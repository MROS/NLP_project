import jieba.posseg as pseg
import sys

class Sentence:
    def __init__(self, sentence, redundant):
        self.sentence = sentence
        self.sentence_with_pos = list(pseg.cut(sentence))
        self.redundant = redundant


# 做有兩種平滑版本
class Ngram:
    def __init__(self, n, sentences):
        self.n = n
        self.POS_KINDS = 39 # 我去數的，不知道對不對
        self.add_k_zero_prob = 0
        self.count = self.count(sentences)
        self.total_gram = sum(self.count.values())
        self.add_k_prob,  self.add_k_zero_prob = self.count_add_k_prob(0.5)
        self.good_turing_prob,  self.good_turing_zero_prob = self.count_good_turing_prob()
        print("ngram 計算結束")
        print("共有{0}個gram", self.total_gram)

    # 回傳目前的計數
    # 用個dictionary來紀錄
    # None 代表在字首
    def count(self, sentences):
        count = {}
        for sentence in sentences:
            s_with_pos = sentence.sentence_with_pos
            for position in range(0, len(s_with_pos)):
                prefix = []
                for shift in range(-self.n + 1, 0):
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
        print(times)
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

    def prob_to_gen(self, sentence):
        pass



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
    return Ngram(n, correct), Ngram(n, incorrect)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage : test.py [input_file] [n].\n")
        sys.exit(0)
    n = int(sys.argv[2])
    correct_ngram, incorrect_ngram = get_ngram(n, sys.argv[1])
