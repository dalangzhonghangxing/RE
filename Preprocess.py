# _*_coding:utf-8_*_
import re

def writeFile(filename,content):
    output = open('F:\\学习\\一课一练\\沪教版数学知识点整理\\preprocess\\'+filename+'.txt', 'w',encoding='UTF-8')
    output.write(content)
    output.close()

def writeKnowledge(filename, knowledges):
      i=0
      output = open('F:\\学习\\一课一练\\沪教版数学知识点整理\\preprocess\\' + filename + '.txt', 'w', encoding='UTF-8')
      content = ""
      for key in knowledges:
          if len(key)==0: continue
          content = content+key+":"
          for subKnowledge in knowledges[key]:
              content = content + subKnowledge+","
              i = i+1
          content = content[0:-1]+"\n"
      output.write(content)
      output.close()
      print(i)

first_level_pattern1 = re.compile(r'(?<=第.章 ).*') #匹配所有一级知识点
first_level_pattern2 = re.compile(r'(?<=第..章 ).*') #匹配所有一级知识点

second_level_pattern1 = re.compile(r'(?<=\d\.\d{1}).*') #匹配所有二级知识点
second_level_pattern2 = re.compile(r'(?<=\d\.\d{2}).*') #匹配所有二级知识点
first_level_knowledge = {}
file = open('F:\\学习\\一课一练\\沪教版数学知识点整理\\沪教版初中数学知识点整理.txt','r',encoding='UTF-8')
# fileContet = file.read().decode('utf-8')
current_first_level_knowledge = ""
current_subKnowledge = []
content = ""
last_knowledge = ""
for line in file:
    second_level_value = second_level_pattern2.findall(line)
    first_level_value = first_level_pattern2.findall(line)
    if len(second_level_value) == 0:
        second_level_value = second_level_pattern1.findall(line)
    if len(first_level_value) == 0:
        first_level_value = first_level_pattern1.findall(line)
    if len(second_level_value) >0:
        subKnowledge = second_level_value[0].lstrip().split("：")[0]
        if(len(subKnowledge.split("."))>1):
            subKnowledge = subKnowledge.split(".")[1]
        current_subKnowledge.append(subKnowledge)
        if content != "":
            writeFile(last_knowledge,content)
        last_knowledge = subKnowledge
        content = ""
    elif len(first_level_value) >0:
        first_level_knowledge[current_first_level_knowledge] = current_subKnowledge
        current_first_level_knowledge = first_level_value[0]
        current_subKnowledge = []
    else:
        content = content+(line.lstrip());
file.close()
writeKnowledge("初中知识点关系",first_level_knowledge)

