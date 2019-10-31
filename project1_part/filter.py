import json
import re
import string
from tokenizer import *

filter_dot_notes = r"[a-zA-Z]+\.[a-zA-Z.]+"  #simple
filter_monetory = r"\$[0-9\.,]+"      #simple
filter_digits = r"[0-9]+"             #simple
filter_alpha_digit = r"[a-zA-Z]+-[0-9]+" 
filter_digit_alpha = r"[0-9]+-[a-zA-Z]+"
filter_digit_alpha_mixes = r"[0-9a-zA-Z]+-[0-9a-zA-Z-]+"  #'FV93-907-1FIR'
filter_hyphen = r"[a-zA-Z]*(-[a-zA-Z]*){1,3}"
# date processer special
filter_date1 = r"[0-9]{2}/[0-9]{2}/[0-9]{4}" #MM/DD/YYYY
filter_date2 = r"[0-9]+-[0-9]+-[0-9]-" #MM-DD-YYYY
filter_date3 = r"[a-zA-Z]{3}-[0-9]+-[0-9]+" #MMM-DD-YYYY
filter_date4 = r"[0-9]{2}/[0-9]{2}/[0-9]{2}" #MM-DD-YY

filter_integer = r"[0-9]{1,3}(,[0-9]{3})*" #simple
filter_dots = r"[0-9,]*\.[0-9]+"   #simple
filter_email = r"([a-zA-Z.]+@)+[a-z.]+" #simple check more
filter_ip = r"([0-9]{1,3}\.){3}[0-9]{1,3}" #simple
filter_telephone = r"\([0-9]{3}\)"  #no hyphen
filter_word = r"[a-zA-Z]+"   
filter_no_hyphen_mixes = r"[a-z0-9]*([0-9][a-z]|[a-z][0-9])[a-z0-9]*" #102a 1a2 a21 a21a
filter_paragraph = r'(§|¶)+[a-z0-9\.-]+'
filter_percent = r'[0-9.]+%'
filter_url = r'https?://.+'
filter_url2 = r'www\..+'
filter_url3 = r'.+\.(com|org|cn|us|edu).+'
filter_file = r'.+\.(pdf|html|sh|txt|doc|zip|exe|rar|avi|xls|dll|gif|jpg|pic|png|avi|bat)'
filter_number_range = r'[0-9\.]+-[0-9\.]+'
filter_alpha_digit_dot = r'[a-z0-9\.-]+'
filter_special_sym = u'(#|\u00d7|\u03bc|)'

def parenthesis(word):
    pass

def strip_word(word):
    strips = "(),•"
    trans = str.maketrans({key: None for key in strips})
    word = word.translate(trans)
    return word.strip(".")

def double_filter(word, word2):
    temp = re.match(r"\(([0-9]{3})[/\)]",word)

    #tele filter and tokenizer
    if temp:
        district = temp.groups()[0]
        tele = re.findall(r"([0-9]{3})-([0-9]{4})", word)
        if tele:
            tele = tele[0]
            return "telephone",[district, tele[0], tele[1], district + tele[0] + tele[1]]
        else:
            tele = re.match(r"([0-9]{3})-([0-9]{4})", word2)
            if tele:
                tele = tele.groups()
                return "district", [district, district + tele[0] + tele[1]]
    
    #date filter and tokenizer
        

        
    return None,None 

def regex_filter(filter, text):
    
    result = re.match(globals()[filter], text)
    if result and len(result.group()) == len(text):
        return result

def regex_filtering(word):
    filters = [ 'filter_alpha_digit', 'filter_date1', 'filter_date2', 'filter_date3','filter_date4',
                'filter_digit_alpha', 'filter_dot_notes', 'filter_ip', 'filter_dots', 'filter_email',
                'filter_hyphen', 'filter_integer',  'filter_monetory', 'filter_url3', 'filter_file',
                'filter_word', 'filter_digits',"filter_paragraph", 'filter_url', 'filter_url2',
                'filter_digit_alpha_mixes', 'filter_no_hyphen_mixes','filter_percent',
                'filter_alpha_digit_dot', 'filter_number_range'] 
    unchange_filters = ['filter_word', 'filter_digits', 'filter_percent',
                        'filter_dots', 'filter_url', 'filter_url2', 'filter_url3' ]
    strip_filters = ['filter_dot_notes', 'filter_monetory', 'filter_integer']
    date_filters = ['filter_date' + str(i) for i in range(1,5)]
    split_filters = ['filter_alpha_digit', 'filter_digit_alpha', 'filter_hyphen', 'filter_digit_alpha_mixes',
                     'filter_no_hyphen_mixes', 'filter_file', 'filter_alpha_digit_dot',  'filter_number_range']
    email_filters = ['filter_email']
    ip_filters = ['filter_ip']
    for filter in filters:
        temp = regex_filter(filter, word)
        if temp:
            if filter in unchange_filters:
                token = [temp.group()]
            elif filter == 'filter_paragraph':
                token = [word[0], word[1:]]
            elif filter in strip_filters:
                token = strip_tokenier(temp.group())
            elif filter in date_filters:
                token = date_tokenier(temp.group(), filter=filter)
            elif filter in split_filters:
                token = split_tokenier(temp.group())
            elif filter in email_filters:
                token = email_tokenier(temp.group())
            elif filter in ip_filters:
                token = constraint_tokenier(temp.group())
            return filter,token
    token = other_tokenizer(word)
    if len(token) == 0:
        return None,None
    else:
        filter = "other"
    return filter, token