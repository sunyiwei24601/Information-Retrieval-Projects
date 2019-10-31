import re
import json
import string
import time

prefixes = ["en", "ex", "extra","hetero","homo", "homeo","hyper","il","im","in","ir","inter","intra",
            "intro","macro","micro","mono","non","omni","post","pre","pro","sub","sym","syn","tele",
            "trans","tri","un","uni","up"]
def strip_tokenier(word):
    strips = ",."
    trans = str.maketrans({key: None for key in strips})
    word = word.translate(trans)
    return [word]

def split_tokenier(word):
    tokens = [word.replace('-', '').replace('.', '').replace(",", '')]
    if "-" in word:
        parts = word.split("-")
        for part in parts:
            if len(part) >= 3 and part not in prefixes:
                tokens.append(part)
        return tokens
    else:
        # num = re.findall("[0-9]{3,}", word)
        char = re.findall("[a-z]{3,}", word)
        char = [i for i in char if i not in prefixes]
        tokens += char 
        return tokens

def date_tokenier(word, word2=None, word3=None, filter=None):
    t = None 
    try:
        if filter == "filter_date1":
            t = time.strptime(word, "%m/%d/%Y")
        if filter == "filter_date2":
            t = time.strptime(word, "%m-%d-%Y")
        if filter == "filter_date3":
            t = time.strptime(word, "%b-%d-%Y")
        if filter == "filter_date4":
            t = time.strptime(word, "%m/%d/%y")
        if word2:
            word2 = word2.strip(",.")
            word3 = word3.strip(",.")
            word = " ".join([word, word2, word3])
            t = time.strptime(word, "%B %d %Y")
    except:
        pass
    if t:
        return [time.strftime("%m/%d/%Y", t)]
    else:
        return []
    
def constraint_tokenier(word):
    nums = [int(i) for i in word.split(".")]
    for num in nums:
        if num > 255 :
            return nums + [word.replace(".", "")]
    return  [word]
    
def email_tokenier(word):
    tokens = word.split("@")
    if len(tokens) <= 2:
        return [word]
    else:
        res = []
        for i in range(len(tokens)-1):
            mid = ["." for j in range(len(tokens) - 1)]
            mid[i] = "@"
            s = ""
            for j in range(len(mid)):
                s += tokens[j]
                s += mid[j]
            s += tokens[-1]
            res.append(s)
        return res
    
def other_tokenizer(word):
    tokens = []
    #special token 
    special_sym = (u"\u03bc", u"\u00d7", u'\u00f1')
    for i in special_sym:
        if i in word:
            return [word]
    # monetary detect
    monetary = r"\$[0-9\.]+"
    money = re.findall(monetary, word)
    if money:
        tokens += money
    
    # word detect
    w = r"[a-z]{3,}"
    words = re.findall(w, word)
    if words:
        tokens += words

    #unit detect
    unit = re.match(r'([a-z]{1,3}/){1,2}[0-9]{0,3}[a-z]{,3}', word)
    if unit:
        tokens.append(unit.group())
    
    return tokens