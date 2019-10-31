import json
import time
import csv
from test_time import *

@test_time(show_time=False)
def merge_file(file1, file2, path):
    reader_1 = csv.reader(open(file1, encoding="utf-8", newline=""), delimiter=",")
    reader_2 = csv.reader(open(file2, encoding="utf-8", newline=""), delimiter=",")
    writer = open(path, "w", encoding="utf-8", newline="")
    csv_writer = csv.writer(writer, delimiter=",")
    line1 = next(reader_1)
    line1[1:] = map(int, line1[1:])
    line2 = next(reader_2)
    line2[1:] = map(int, line2[1:])
    while(line1 and line2):
        if line1 < line2:
            csv_writer.writerow(line1)
            try:
                line1 = next(reader_1)
                line1[1:] = map(int, line1[1:])
            except:
                line1 = None
                break
        else:
            csv_writer.writerow(line2)
            try:
                line2 = next(reader_2)
                line2[1:] = map(int, line2[1:])
            except:
                line2 = None
                break
    if line2 == None:
        for line in reader_1:
            csv_writer.writerow(line)
    if line1 == None:
        for line in reader_2:
            csv_writer.writerow(line)
    writer.close()
        
def copy_file(file1, file2):
    f_read = open(file1, encoding="utf-8")
    f_write = open(file2, "w", encoding="utf-8")
    l = f_read.readline()
    while(l):
        f_write.write(l)
        l = f_read.readline()
    f_read.close()
    f_write.close()

@test_time(show_time=True)
def merge_triple_files(path, num):
    file_lists = [path + str(i) for i in range(num)]
    while(len(file_lists) > 1):
        for i in range(0, len(file_lists), 2):
            if i == len(file_lists) - 1:
                copy_file(file_lists[i], file_lists[i//2])
                continue
            temp_file =  path + 'temp'+ str(i//2)
            merge_file(file_lists[i], file_lists[i+1], temp_file)
            copy_file(temp_file, path + str(i//2))
        file_lists = file_lists[: (len(file_lists) + 1)//2 ]
        print(len(file_lists), "files left to be merged")
    copy_file(file_lists[0], path + "_total")
    return path + "_total"
    
def write_triples(triples, path, number = None):
    if number == None:
        number = write_triples.num
        write_triples.num += 1

    with open(path + str(number), "w", encoding = "utf-8", newline='') as f:
        csv_writer = csv.writer(f, delimiter=',')
        for triple in triples:
            csv_writer.writerow(triple)
            
write_triples.num = 0

def translate_file(term_id, file_path, output_file, positions = False):
    reader = open(file_path)
    writer = open(output_file, "w", newline='')
    csv_writer = csv.writer(writer, delimiter=',')
    current_line = reader.readline().split(' ')
    triple = [term_id[int(current_line[0])], int(current_line[1]), int(current_line[2])]
    if not positions:
        while(current_line):
            next_line = reader.readline().split(' ')
            if next_line[0] == current_line[0]:
                triple += [int(i) for i in next_line[1:]]
                current_line = next_line
            else:
                csv_writer.writerow(triple)
                current_line = next_line
                if len(current_line) >= 2:
                    triple = [term_id[int(current_line[0])], int(current_line[1]), int(current_line[2])]
                else:
                    break
    else:
        while(len(current_line)>2):
            triple = [term_id[int(current_line[0])]] + [ int(i) for i in current_line[1:] ]
            csv_writer.writerow(triple)
            current_line = reader.readline().split(' ')
    writer.close()
    return output_file



        
            





