from docx import Document


def get_text(filename):
    try:
        if str(filename).endswith('docx'):
            s = ''
            doc = Document(filename)
            for i in doc.paragraphs:
                s += i.text + '\n'
            return s
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None
    except UnicodeDecodeError:
        return None
    except:
        return None
