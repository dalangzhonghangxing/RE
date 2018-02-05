def writeFile(filepath, content):
    output = open(filepath, 'w', encoding='UTF-8')
    output.write(content)
    output.close()


def writeFile_Add(filepath, content):
    output = open(filepath, 'a', encoding='utf-8')
    output.write(content)
    output.close()
