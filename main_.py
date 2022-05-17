import re

# from os import SF_MNOWAIT, WCONTINUED
from probability import entropyOfList
from sequence import genSubstr,genSubparts_forspace,genSubparts





class WordInfo_for_space(object):
    """
    Store information of each word, including its freqency, left neighbors and right neighbors
    """
    def __init__(self, text):
        super(WordInfo_for_space, self).__init__()
        self.text = text
        self.freq = 0.0
        self.left = []
        self.right = []

        self.aggregation = 0

    def update(self, left, right):
        """
        Increase frequency of this word, then append left/right neighbors
        @param left a single character on the left side of this word
        @param right as left is, but on the right side
        """
        self.freq += 1
        if left: self.left.append(left)
        if right: self.right.append(right)

    def compute(self, length):
        """
        Compute frequency and entropy of this word
        @param length length of the document for training to get words
        """

        # print('compute text:',self.text,self.freq,length,self.freq/length)
        self.freq /= length
        # print('text:',self.text,)
        self.left = entropyOfList(self.left)
        self.right = entropyOfList(self.right)

    def computeAggregation(self, words_dict):
        """
        Compute aggregation of this word
        @param words_dict frequency dict of all candidate words
        """
        parts = genSubparts_forspace(self.text)
        if len(parts) > 0:
            self.aggregation = min([self.freq/words_dict[p1_p2[0]].freq/words_dict[p1_p2[1]].freq for p1_p2 in parts])


def indexOfSortedSuffix(doc, max_word_len):
    """
    Treat a suffix as an index where the suffix begins.
    Then sort these indexes by the suffixes.
    """
    indexes = []
    length = len(doc)
    for i in range(0, length):
        for j in range(i + 1, min(i + 1 + max_word_len, length + 1)):
            indexes.append((i, j))
    # return sorted(indexes, key=lambda i_j: doc[i_j[0]:i_j[1]])
    return indexes

class WordSegment_all_space(object):


    def __init__(self, doc, max_word_len=5, min_freq=0.00005, min_entropy=2.0, min_aggregation=50):
        super(WordSegment_all_space, self).__init__()
        self.max_word_len = max_word_len
        self.min_freq = min_freq
        self.min_entropy = min_entropy
        self.min_aggregation = min_aggregation
        ''
        self.word_infos = self.genWords(doc)
        # for i in self.word_infos:
        #     print('this is word info',i.text,i.freq,i.aggregation,i.left,i.right)
        # print(self.word_infos)

        # Result infomations, i.e., average data of all words
        word_count = float(len(self.word_infos))
        self.avg_len = sum([len(w.text) for w in self.word_infos])/word_count
        self.avg_freq = sum([w.freq for w in self.word_infos])/word_count
        self.avg_left_entropy = sum([w.left for w in self.word_infos])/word_count
        self.avg_right_entropy = sum([w.right for w in self.word_infos])/word_count
        self.avg_aggregation = sum([w.aggregation for w in self.word_infos])/word_count
        self.mid_freq = sorted([w.freq for w in self.word_infos])[int(len(doc)/2)]
        self.mid_left_entropy = sorted([w.left for w in self.word_infos])[int(len(doc)/2)]
        self.mid_right_entropy = sorted([w.right for w in self.word_infos])[int(len(doc)/2)]
        self.mid_aggregation = sorted([w.aggregation for w in self.word_infos])[int(len(doc)/2)]
        filter_func = lambda v: len(v.text) > 1 and v.aggregation > self.min_aggregation and\
                    v.freq > self.min_freq and v.left > self.min_entropy and v.right > self.min_entropy
        self.word_with_freq = [(w.text, w.freq) for w in list(filter(filter_func, self.word_infos))]
        self.words = [w[0] for w in self.word_with_freq]
    

    def list_word_cands(self,doc,len1,len2):
        # if(len1)
        len1 = max(0,len1)
        len2 = min(len2,len(doc))
        word = ''
        for word_index in range(len1,len2):
            word += doc[word_index]+' '
        word = word[0:-1]

        return word

    def genWords(self, doc):
        
        suffix_indexes = indexOfSortedSuffix(doc, self.max_word_len)
        word_cands = {}
        # compute frequency and neighbors
        for suf in suffix_indexes:
            word = self.list_word_cands(doc,suf[0],suf[1])
            # word = doc[suf[0]:suf[1]]
            if word not in word_cands:
                word_cands[word] = WordInfo_for_space(word)
            # word_cands[word].update(doc[suf[0] - 1:suf[0]], doc[suf[1]:suf[1] + 1])
            word_cands[word].update(self.list_word_cands(doc,suf[0] - 1,suf[0]), self.list_word_cands(doc,suf[1],suf[1]+1))
        # compute probability and entropy
        # print('word_cands',word_cands.keys(),word_cands.values())
        # for i in word_cands.values():
        #     print('this is cands',i.text,i.freq,i.left,i.right)

        length = len(doc)

        for k in word_cands:
            word_cands[k].compute(length)
        
        # for k in word_cands:
        #     print('this is new calculate ',word_cands[k].text,word_cands[k].freq)
        
        # compute aggregation of words whose length > 1
        values = sorted(list(word_cands.values()), key=lambda x: len(x.text))
        # valuse1 = sorted(values, key=lambda v: v.freq, reverse=True)
        # for v in valuse1:
        #     print('this is v',v.text,v.freq)
        #     if(v.freq>1):
        #         print('*********************')
        # values = word_cands
        for v in values:
            if len(v.text.replace(' ','')) <= 1: continue
            v.computeAggregation(word_cands)
        # values2 = sorted(values, key=lambda v: v.freq, reverse=True)
        # for v in values2:
        #     print('this is v',v.text,v.freq)
        #     if(v.freq>1):
        #         print('*********************')


        return sorted(values, key=lambda v: v.freq, reverse=True)













class WordInfo(object):
    """
    Store information of each word, including its freqency, left neighbors and right neighbors
    """
    def __init__(self, text):
        super(WordInfo, self).__init__()
        self.text = text
        self.freq = 0.0
        self.left = []
        self.right = []
        self.aggregation = 0

    def update(self, left, right):
        """
        Increase frequency of this word, then append left/right neighbors
        @param left a single character on the left side of this word
        @param right as left is, but on the right side
        """
        self.freq += 1
        if left: self.left.append(left)
        if right: self.right.append(right)

    def compute(self, length):
        """
        Compute frequency and entropy of this word
        @param length length of the document for training to get words
        """
        self.freq /= length
        self.left = entropyOfList(self.left)
        self.right = entropyOfList(self.right)

    def computeAggregation(self, words_dict):
        """
        Compute aggregation of this word
        @param words_dict frequency dict of all candidate words
        """
        parts = genSubparts(self.text)
        if len(parts) > 0:
            self.aggregation = min([self.freq/words_dict[p1_p2[0]].freq/words_dict[p1_p2[1]].freq for p1_p2 in parts])



class WordSegment(object):

    """
    Main class for Chinese word segmentation
    1. Generate words from a long enough document
    2. Do the segmentation work with the document
    """

    # if a word is combination of other shorter words, then treat it as a long word
    L = 0
    # if a word is combination of other shorter words, then treat it as the set of shortest words
    S = 1
    # if a word contains other shorter words, then return all possible results
    ALL = 2

    def __init__(self, doc, max_word_len=5, min_freq=0.00005, min_entropy=2.0, min_aggregation=50):
        super(WordSegment, self).__init__()
        self.max_word_len = max_word_len
        self.min_freq = min_freq
        self.min_entropy = min_entropy
        self.min_aggregation = min_aggregation
        ''
        self.word_infos = self.genWords(doc)
        
        # Result infomations, i.e., average data of all words
        word_count = float(len(self.word_infos))
        self.avg_len = sum([len(w.text) for w in self.word_infos])/word_count
        self.avg_freq = sum([w.freq for w in self.word_infos])/word_count
        self.avg_left_entropy = sum([w.left for w in self.word_infos])/word_count
        self.avg_right_entropy = sum([w.right for w in self.word_infos])/word_count
        self.avg_aggregation = sum([w.aggregation for w in self.word_infos])/word_count
        self.mid_freq = sorted([w.freq for w in self.word_infos])[int(len(doc)/2)]
        self.mid_left_entropy = sorted([w.left for w in self.word_infos])[int(len(doc)/2)]
        self.mid_right_entropy = sorted([w.right for w in self.word_infos])[int(len(doc)/2)]
        self.mid_aggregation = sorted([w.aggregation for w in self.word_infos])[int(len(doc)/2)]
        # Filter out the results satisfy all the requirements
        filter_func = lambda v: len(v.text) > 1 and v.aggregation > self.min_aggregation and\
                    v.freq > self.min_freq and v.left > self.min_entropy and v.right > self.min_entropy
        self.word_with_freq = [(w.text, w.freq) for w in list(filter(filter_func, self.word_infos))]
        self.words = [w[0] for w in self.word_with_freq]

    def genWords(self, doc):
        """
        Generate all candidate words with their frequency/entropy/aggregation informations
        @param doc the document used for words generation
        """
        pattern = re.compile('[\\s\\d,.<>/?:;\'\"[\\]{}()\\|~!@#$%^&*\\-_=+a-zA-Z，。《》、？：；“”‘’｛｝【】（）…￥！—┄－]+')
        doc = re.sub(pattern, ' ', doc)
        suffix_indexes = indexOfSortedSuffix(doc, self.max_word_len)
        word_cands = {}
        # compute frequency and neighbors
        for suf in suffix_indexes:
            word = doc[suf[0]:suf[1]]
            if word not in word_cands:
                word_cands[word] = WordInfo(word)
            word_cands[word].update(doc[suf[0] - 1:suf[0]], doc[suf[1]:suf[1] + 1])
        # compute probability and entropy
        # print('word_cands',word_cands.keys())
        length = len(doc)
        for k in word_cands:
            word_cands[k].compute(length)
        # compute aggregation of words whose length > 1
        values = sorted(list(word_cands.values()), key=lambda x: len(x.text))
        for v in values:
            if len(v.text) == 1: continue
            v.computeAggregation(word_cands)
        return sorted(values, key=lambda v: v.freq, reverse=True)

    def segSentence(self, sentence, method=ALL):
        """
        Segment a sentence with the words generated from a document
        @param sentence the sentence to be handled
        @param method segmentation method
        """
        i = 0
        res = []
        while i < len(sentence):
            if method == self.L or method == self.S:
                j_range = list(range(self.max_word_len, 0, -1)) if method == self.L else list(range(2, self.max_word_len + 1)) + [1]
                for j in j_range:
                    if j == 1 or sentence[i:i + j] in self.words:
                        res.append(sentence[i:i + j])
                        i += j
                        break
            else:
                to_inc = 1
                for j in range(2, self.max_word_len + 1):
                    if i + j <= len(sentence) and sentence[i:i + j] in self.words:
                        res.append(sentence[i:i + j])
                        if to_inc == 1: to_inc = j
                if to_inc == 1: res.append(sentence[i])
                i += to_inc
        return res












def en_seg(doc):
    # doc = ''
    # f1 = open(filename,'r',encoding='utf-8')
    # for i in f1.readlines():
    #     doc += i.strip('\n')
    pattern = re.compile('[\\s\\d,.<>/?:;\'\"[\\]{}()\\|~!@#$%^&*\\=+，。《》、？：；“”‘’｛｝【】（）…￥！—┄－]+')
    doc = re.sub(pattern, ' ', doc)
    doc = doc.replace('  ',' ')
    list1 = doc.split(' ')
    ws = WordSegment_all_space(list1, max_word_len=5, min_aggregation=9, min_entropy=0)

    return ws
    # for w in ws.word_infos:
    #     print(w.text,w.freq)



def ch_seg(doc):
    # doc = '据悉，中国的三名航天员已经成功地完成了两次出舱任务。而保管好这个出舱航天服就是们需要进行的第一个准备。这个出舱航天服不同于一般的航天服，它们是用于出舱也就是不在空间站舱内会用的航天服，这个出舱航天服不是一次性的，可以多次使用，所以使用过后需要报管好。保管好之前需要对这个出舱航天服干燥，这样才能确保下一次上来的航天员能够更快地熟悉适应。'
    # doc = '我对这家酒店印象非常好，这是我第一家便宜的酒店，但我很喜欢。'
    ws = WordSegment(doc, max_word_len=5, min_aggregation=9, min_entropy=0)
    return ws







def seg_for_alllanguage(doc):
    # prin
    space_number = doc.count(' ')
    words_doc = len(doc.split(' '))
    if(space_number == words_doc-1 and space_number>0):
        print('en')
        ws = en_seg(doc)

        filter_func = lambda v: len(v.text) > 1 and v.aggregation > ws.min_aggregation and\
                        v.freq > ws.min_freq and v.left > ws.min_entropy and v.right > ws.min_entropy
        word_with_freq = [(w.text, w.freq) for w in list(filter(filter_func, ws.word_infos))]

        print(word_with_freq)

        word_list = []
        for i,_ in word_with_freq:
            word_list.append(i)
        pattern = re.compile('[\\s\\d,.<>/?:;\'\"[\\]{}()\\|~!@#$%^&*\\=+，。《》、？：；“”‘’｛｝【】（）…￥！—┄－]+')
        doc = re.sub(pattern, ' ', doc)
        doc = doc.replace('  ',' ')
        list1 = doc.split(' ')
        
        res = seg_sentence_en(list1,word_list,0)
        print(res)



    else:
        print('ch')
        ws = ch_seg(doc)

    
        filter_func = lambda v: len(v.text) > 1 and v.aggregation > ws.min_aggregation and\
                        v.freq > ws.min_freq and v.left > ws.min_entropy and v.right > ws.min_entropy
        word_with_freq = [(w.text, w.freq) for w in list(filter(filter_func, ws.word_infos))]

        print(word_with_freq)
        word_list = []
        for i,_ in word_with_freq:
            word_list.append(i)             
        
        res = seg_sentence_ch(doc,word_list,0)
        print(res)

    
    
    # for w in ws.word_infos:
    #     print(w.text,w.freq)

    

def seg_sentence_ch(sentence,wordlist,model,max_word_len=5):
    """
    model= 1 为正向，0为逆向
    """
    i = 0
    res = []
    while i < len(sentence):
        # if method == self.L or method == self.S:
        j_range = list(range(max_word_len, 0, -1)) if model == 0 else list(range(2, max_word_len + 1)) + [1]
        for j in j_range:
            if j == 1 or sentence[i:i + j] in wordlist:
                res.append(sentence[i:i + j])
                i += j
                break
    return res

def list2word(string_list,start,end):
    str1 = ''
    end = min(len(string_list),end)
    for i in range(start,end):
        str1 += string_list[i]+' '
    str1 = str1[0:-1]
    

    # print(str1)
    return str1

def seg_sentence_en(sentence,wordlist,model,max_word_len=5):
    """
    model= 1 为正向，0为逆向
    """
    i = 0
    res = []
    while i < len(sentence):
        # if method == self.L or method == self.S:
        j_range = list(range(max_word_len, 0, -1)) if model == 0 else list(range(2, max_word_len + 1)) + [1]
        for j in j_range:
            if j == 1 or list2word(sentence,i,i+j) in wordlist:
                res.append(list2word(sentence,i,i+j))
                i += j
                break
    return res




if __name__ == '__main__':

    # en_seg()
    # ch_seg()

    # doc = '据悉，中国的三名航天员已经成功地完成了两次出舱任务。而保管好这个出舱航天服就是们需要进行的第一个准备。这个出舱航天服不同于一般的航天服，它们是用于出舱也就是不在空间站舱内会用的航天服，这个出舱航天服不是一次性的，可以多次使用，所以使用过后需要报管好。保管好之前需要对这个出舱航天服干燥，这样才能确保下一次上来的航天员能够更快地熟悉适应。'
    
    fl_ch = '/data/zbh/wordsegment_allanguages/all_language_seg/ch.txt'
    fl_en = '/data/zbh/wordsegment_allanguages/all_language_seg/en.txt'
    f1 = open(fl_en,'r',encoding='utf-8')


    doc = ''
    for i in f1.readlines():
        doc += i.strip('\n')
    seg_for_alllanguage(doc)

    
    

    





