import jieba.posseg as pseg


f = open("train.txt", "r")
out = open("POS.txt", "w")
q = None
q2 = None
for line in f:
    q = line.split("\t")
    out.write(q[1] + "/")
    q2 = pseg.cut(q[2])
    for w in q2:
        out.write(w.flag + "/")
    out.write("\n")

print "Done~\n"
