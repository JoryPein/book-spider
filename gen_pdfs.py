import os
import pdfkit

options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'custom-header': [
        ('Accept-Encoding', 'gzip')
    ],
    'no-outline': None
}

def main():
    root_path = "res/moby_dick"
    root_path_text = os.path.join(root_path, "text")
    root_path_pdf = os.path.join(root_path, "pdf")
    if not os.path.exists(root_path_pdf):
        os.mkdir(root_path_pdf)

    for item in os.listdir(root_path_text):
        old = os.path.join(root_path_text, item)
        new = os.path.join(root_path_pdf, item.replace("txt", "pdf"))
        pdfkit.from_file(old, new, options=options)
        print("generated", new)
        # break


if __name__ == '__main__':
    main()
