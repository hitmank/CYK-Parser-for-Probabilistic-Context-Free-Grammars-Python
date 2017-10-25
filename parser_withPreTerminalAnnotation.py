#!/usr/bin/env python
import sys, fileinput
import collections
import tree
from sets import Set
import math
import bigfloat

rules = collections.defaultdict(int)
rules_probability = collections.defaultdict(float)
non_terminals = collections.defaultdict(int)
terminals = Set()

trees = []

trainfile = open(sys.argv[1],"r")
test =  open(sys.argv[2],"r")
outfile = open(sys.argv[3],"w")

for line in trainfile.readlines():
    t = tree.Tree.from_str(line)
    for node in t.bottomup():
        if node.children.__len__() > 0:
            #vertical markovization
            label = node.label
            # if node.parent != None:
            #     label = label + "[" + node.parent.label + "]"
            # if node.label == "IN":
            #     if node.parent is not None:
            #         label = label + "^" + node.parent.label
            if node.children.__len__() == 1 and node.parent is not None:
                label = label + "^" + node.parent.label
            non_terminals[label] += 1
            current_rule = label


            for child in node.children:
                childlabel = child.label
                # if childlabel == "NP":
                #     does_contain_np = True
                # if child.children.__len__() > 0 and child.parent != None:
                #     childlabel = childlabel + "[" + child.parent.label + "]"
                # if childlabel == "IN" and child.parent is not None:
                #     childlabel = childlabel + "^" + child.parent.label
                if child.children.__len__() == 1 and child.parent is not None:
                    childlabel = childlabel + "^" + child.parent.label
                current_rule = current_rule + "-" + childlabel

            rules[current_rule] += 1
        else:
            terminals.add(node.label)

#Calculate maximum likely hood parameter:
most_frequent_rule = ""
most_frequent_rule_count = 0

for rule in rules.keys():
    count_rule = rules[rule]
    split_rule = rule.split("-")
    rule_lhs = split_rule[0]
    count_lhs = non_terminals[rule_lhs]
    max_likely_hood = bigfloat.bigfloat(count_rule) / bigfloat.bigfloat(count_lhs)
    rules_probability[rule] = max_likely_hood
    if count_rule > most_frequent_rule_count:
        most_frequent_rule_count = count_rule
        most_frequent_rule = rule




def CYK(sentence):
    sentenceArray = sentence.rstrip().split(" ")
    lengthOfSentence = sentenceArray.__len__()
    dynamicArray = []
    backArray = []

    for i in range(0,lengthOfSentence+1):
        dynamicArray.append([])
        backArray.append([])
        for j in range(0,lengthOfSentence+1):
            dynamicArray[i].append({})
            backArray[i].append({})

    for i in range(0, lengthOfSentence):
        j = i + 1
        current_word = sentenceArray[i]
        dict = {}
        if not terminals.__contains__(current_word):
            current_word = "<unk>"

        for eachRule in rules_probability.keys():
            split_rule = eachRule.split("-")
            if current_word == split_rule[1]:
                the_nonTerminal = split_rule[0]
                dict[the_nonTerminal] = rules_probability[eachRule]
                backArray[i][j][the_nonTerminal] = (0, current_word, 0)
        dynamicArray[i][j] = dict



    for span in range(2,lengthOfSentence+1):
        for begin in range(0, lengthOfSentence-span+1):
            end = begin + span
            for split in xrange(begin+1,end):
                for rule in rules_probability.keys():
                    split_rule = rule.split("-")
                    if split_rule.__len__() == 3:
                        A = split_rule[0]
                        B = split_rule[1]
                        C = split_rule[2]
                        #A->BC
                        calc_prob = bigfloat.bigfloat(0)
                        if dynamicArray[begin][split].has_key(B):
                            if dynamicArray[split][end].has_key(C):
                                calc_prob = dynamicArray[begin][split][B]*dynamicArray[split][end][C]*rules_probability[rule]
                        if bigfloat.bigfloat.__cmp__(calc_prob, 0) > 0:
                            if not dynamicArray[begin][end].has_key(A):
                                dynamicArray[begin][end][A] = calc_prob
                                backArray[begin][end][A] = (split, B, C)
                            elif bigfloat.bigfloat.__cmp__(calc_prob,dynamicArray[begin][end][A]) > 0:
                                dynamicArray[begin][end][A] = calc_prob
                                backArray[begin][end][A] = (split, B, C)

    #use backArray to get the parse tree
    i = 0
    j = lengthOfSentence
    current_node = "TOP"
    numberOfLeavesFound = 0

    def theRecursiveFinder(current_node,i,j,bp_array,parent):

        if current_node in bp_array[i][j]:
            split,leftChild,rightChild = bp_array[i][j][current_node]
            if split == 0:
                only_child = tree.Node(leftChild,[])
                parent.append_child(only_child)
            else:
                #vertical markovization - removing parent link
                # leftChild_withoutParent = leftChild.split("[")[0]
                # rightChild_withoutParent = rightChild.split("[")[0]
                leftChild_withoutINAnnotation = leftChild.split("^")[0]
                rightChild_withoutINAnnotation = rightChild.split("^")[0]
                leftNode = tree.Node(leftChild_withoutINAnnotation,[])
                rightNode = tree.Node(rightChild_withoutINAnnotation,[])
                parent.append_child(leftNode)
                parent.append_child(rightNode)
                theRecursiveFinder(leftChild,i,split,bp_array,leftNode)
                theRecursiveFinder(rightChild,split,j,bp_array,rightNode)

    par = tree.Node("TOP",[])
    if "TOP" not in backArray[0][lengthOfSentence]:
        outfile.writelines("\n")
    else:
        theRecursiveFinder(current_node, 0, lengthOfSentence, backArray,par)
        outfile.write(par._subtree_str())
        outfile.write("\n")

# def wrapper(func, *args, **kwargs):
#      def wrapped():
#          return func(*args, **kwargs)
#      return wrapped

lenArr = []
timeArr = []
for eachLine in test.readlines():
   # wr = wrapper(CYK,eachLine)
   # ft = timeit.timeit(wr,number=1)
   # lenArr.append(math.log10(eachLine.rstrip().split(" ").__len__()))
   # timeArr.append(math.log10(ft))

    CYK(eachLine)

# plt.plot(lenArr, timeArr, "ro")
# plt.show()

for x in range(0,timeArr.__len__()):
    print str(lenArr[x]) + "," + str(timeArr[x])