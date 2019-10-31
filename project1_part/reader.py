import re
import os
import collections
import json
def strip_tag(s):
    result = re.findall("<([a-zA-Z]*)>(.*)</[a-zA-Z]*>", s)
    return result

def read_file(file_path):
    f = open(file_path)
    line = f.readline()
    documents = collections.defaultdict(dict)
    while(line):
        if line == "\n" or line == " \n":
            line = f.readline()
            continue

        if len(line) > 0 and line[0] == "<":
            temp = strip_tag(line)
            if temp:
                tag, text = temp[0]
                if tag == 'DOCNO':
                    current_doc = text
                    documents[current_doc]['text'] = []
                elif tag == "PARENT":
                    documents[current_doc]['PARENT'] = text 
                else:
                    text = filter(text)
                    documents[current_doc]['text'].append(text.strip("\n"))
        else:
            text = filter(line)
            documents[current_doc]["text"].append(text.strip("\n"))
        
        line  = f.readline()
    return documents

def extract_parent_inf(documents):
    parents = {}
    for doc in documents:
        parents[doc] = documents[doc]["PARENT"]
    return parents

# replace xml symbol with characters
def filter(text):
    """ 
    replace the special character with symbols
    """
    replace_lists = [("&amp;", "&"), ("&para;", "¶"), ("&sect;", "§"), ("&hyph;", "-"),\
                    ("&times;", "×"), ("&blank;", " "), ("&mu;", "μ"), ("&ntilde", "ñ"),\
                    ("&bull;", "•")]
    for word, char in replace_lists:
        text = text.replace(word, char)
    return text 

def read_files(file_path_lists):
    doc_text = {}
    results = {}
    # read different files and conbine them together
    for file_path in file_path_lists:
        documents = read_file(file_path)
        results.update(documents)
    # extract parents information in case it's useful
    doc_Parents = extract_parent_inf(documents)
    #extract the text only
    for doc in results:
        # join different line together
        doc_text[doc] = " ".join(results[doc]["text"])
    return doc_text


class reader:
    def __init__(self, file_dir):
        files = os.listdir(file_dir)[:]
        files_path = [os.path.join(file_dir, file_path) for file_path in files]
        self.file_path_lists = files_path
    
    def read_doc(self):
        for file_path in self.file_path_lists:
            print("reading file ", file_path)
            documents = self.read_file(file_path)
            
            for docid, document in documents:
                document = " ".join(document)
                yield docid.strip(" "), document
    
    def read_file(self, file_path):
        f = open(file_path)
        line = f.readline()
        document = []
        current_doc = None
        while(line):
            if line == "\n" or line == " \n":
                line = f.readline()
                continue   
            if len(line) > 0 and line[0] == "<":
                temp = strip_tag(line)
                if temp:
                    tag, text = temp[0]
                    if tag == 'DOCNO':
                        if current_doc:
                            yield current_doc, document
                            
                        current_doc = text
                        document = []
                    elif tag == "PARENT":
                        pass
                    else:
                        text = filter(text)
                        document.append(text.strip("\n"))
            else:
                text = filter(line)
                document.append(text.strip("\n"))
            line = f.readline()
        f.close()
        return current_doc, document

if __name__ == "__main__":
    files_path = os.path.join(".","BigSample")
    # files= os.listdir(files_path)
    # files_path = [os.path.join(".", "BigSample", file_path) for file_path in files]
    read = reader(files_path)
    documents = read.read_doc()
    result = []
    for docid, document in documents:
        result.append((docid,document))
    with open(r"C:\Users\Carl\Desktop\2019Fall\Information Retrieval\HW-2 11.4\Elastic_Search_Test\document.json", "w", encoding="utf-8") as f:
        n = 0 
        for docid,document in result :
            index  = {"index":{"_id": n}}
            f.writelines(json.dumps(index))
            f.write("\n")
            content = {"doc_name": docid, "text": document}
            f.writelines(json.dumps(content))
            f.write("\n")
            n += 1

    
    

    
    
