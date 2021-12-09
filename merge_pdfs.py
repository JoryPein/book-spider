import os
import re
from PyPDF2 import PdfFileWriter, PdfFileReader


def main():
    root_path = "res/moby_dick/pdf"
    l = list()
    for item in os.listdir(root_path):
        l.append(dict(
            index=int(item.split(".")[0]),
            path=os.path.join(root_path,item),
            title=re.search(r"\d+.白鲸 (.*?).pdf", item).group(1)
        ))
    l.sort(key=lambda i:i.get("index"), reverse=False)

    file_writer = PdfFileWriter()
    index = 0
    for item in l:
        file_reader = PdfFileReader(item["path"])
        for page in range(file_reader.getNumPages()):
            file_writer.addPage(file_reader.getPage(page))
        file_writer.addBookmark(item["title"], index)
        index += file_reader.getNumPages()
    with open("res/moby_dick/moby_dick.pdf",'wb') as fp:
        file_writer.write(fp)   
    print("finished")

if __name__ == '__main__':
    main()
