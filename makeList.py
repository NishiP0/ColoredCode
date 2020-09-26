import re

# def is_japanese(str):
#     #https://qiita.com/MichiHosokawa/items/83da0ad58905c79c867d
#     return True if re.search(r'[ぁ-んァ-ン]', str) else False

import unicodedata
def is_japanese(string):
    for ch in list(string):
        text_A = unicodedata.name(ch)
        if ("CJK UNIFIED" in text_A ) or ("HIRAGANA" in text_A  )or ("KATAKANA" in text_A):
            return True
    return False


def run():
    f = open("win32API.txt", "r", encoding = "utf-8_sig")
    text_all = ""
    myList = []
    while(1):
        text = f.readline()
        if not text:
            f.close()
            return text_all
        text = text.replace("\n", "")
        text = text.split(" ")[0]
        text = text.split("(")[0]

        Ope_A = is_japanese(text) == False
        Ope_B = text.isnumeric() == False
        Ope_C = "http" not in text
        Ope_D = " " not in text
        Ope_E =  "■" not in text
        Ope_F = text is not ""
        Ope_G = text not in myList
        if(Ope_A and Ope_B and Ope_C and Ope_D and Ope_E and Ope_F and Ope_G):
            text = text.replace("<", "")
            text = text.replace(">", "")
            myList.append(text)
            print("aaaa-> " + text)
            text_all += "\"" + text + "\", "

text= run()
f =  open("api.txt", "w", encoding = "utf-8_sig")
f.write(text)
f.close()

