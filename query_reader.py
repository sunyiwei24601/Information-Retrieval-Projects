import re
class QueryReader:
    def __init__(self, query_file_path):
        self.query_file_path = query_file_path

    # a query generator by reading the documents line by line query like[(query_num, query_topic),]
    def get_query(self):
        query = []
        with open(self.query_file_path) as f:
            line = f.readline()
            while(line):
                num = self.identify_number(line)
                if num:
                    query.append(num)
                    line = f.readline()
                    continue
                topic = self.identify_topic(line)
                if topic:
                    query.append(topic)
                    yield query
                    query = []
                line = f.readline()

    def get_query_with_narrative(self):
        query = []
        with open(self.query_file_path) as f:
            line = f.readline()
            while(line):
                num = self.identify_number(line)
                if num:
                    query = []
                    query.append(num)
                    line = f.readline()
                    continue

                topic = self.identify_topic(line)
                if topic:
                    query.append(topic)
                    line = f.readline()
                    continue

                if self.identify_narrative(line):
                    line = f.readline()
                    narrative = ""
                    while(line != "</top>\n" and line):
                        narrative += line
                        line = f.readline()
                    query.append(narrative)
                    yield query
                    
                


                line = f.readline()

    def identify_number(self, line):
        s = re.match("<num> Number: ([0-9]+)", line)
        if s:
            num = s.groups()[0]
            return int(num)
        else: 
            return False
    
    def identify_topic(self, line):
        s = re.match("<title> Topic: (.+)", line)
        if s:
            topic = s.groups()[0]
            return topic.strip(" ")
        else: 
            return False

    def identify_narrative(self, line):
        s = re.match("<narr> Narrative.+", line)
        if s:
            return True
        else:
            return False

if __name__ == "__main__":
    query_file_path = "queryfile.txt"
    reader = QueryReader(query_file_path)
    for i in reader.get_query_with_narrative():
        print(i)
