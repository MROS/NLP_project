import jieba.posseg as pseg
import sys
def getPOSfile(inputfile):
    f = open(inputfile, "r")
    q = None
    q2 = None
    for line in f:
        q = line.split("\t")
        q2 = q2 + pseg.cut(q[2])

    print("Done~\n")
    return q2

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage : test.py [inputfile].\n")
        sys.exit(0)
    A = getPOSfile(sys.argv[1])
    for l in A:
        for w in l:
            print(w.flag + "\n")
        print("\n")
