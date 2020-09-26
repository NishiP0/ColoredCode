import xml.etree.ElementTree as ET
from settings import database
import re
import numpy as np
import sys

class Code_coloring:
    def __init__(self):
        #settings
        self.program_filename = "test_sample.cpp"
        self.save_filename = "test_output.html"
        self.template_html_filename = "template.html"
        self.Color_XML_filename = "color_setting.xml"
        self.language = "cpp"
        self.string_color_dic = {}

        #data preset
        self.splitter_list = []
        self.prime_splitter_list = []
        self.yoyakugo_dic = {}
        self.comment_bfaf = {}
        self.unique_char_dic = {}
        self.usertype_bfaf = {}
        self.string_sted_list = ["\"", "\'"]

        self.program_after = ""
        self.css_text = ""

        #内部変数（処理に使う）
        self.AddLineNumber = True
        self.program_before = ""
        self.line_number = 0
        self._text_list_oneLine = []
        self._CurIndex = 0
        self._Curstate = "NONE" #Com_1, Com_2, Macro, String

        self.getLanguage()
        self.LoadColorSetting()
        self.getDataSettings()

    def run(self):
        #self.language = self.getLanguage()
        in_f = open(self.program_filename, "r", encoding="utf-8_sig")
        print("-----   main process started -------")
        while(1):
            one_sentence = in_f.readline()
            if not one_sentence:
                in_f.close()
                print("-----   main process finished -------")
                print("[INFO]  ファイル終端に到達しました")
                self.saveFile()
                return

            self._text_list_oneLine = self._mysplitter(one_sentence)
            for index, one_word in enumerate(self._text_list_oneLine):
                self._CurIndex = index
                self.program_after += self._setColor_oneWord_inline_CSS(one_word)

    def _setColor_oneWord_inline_CSS(self, one_word):
        for uniqueChar in self.unique_char_dic.keys():
            one_word = one_word.replace(uniqueChar, self.unique_char_dic[uniqueChar])

        if(self._Curstate == "Com_1"):
            if(one_word == "\n"):
                self._Curstate = "NONE"
                return "</span>\n"
            return one_word

        if(self._Curstate == "Com_2"):
            if(one_word in self.comment_bfaf["after"]):
                self._Curstate = "NONE"
                return f"{one_word}</span>"
            return one_word

        if(self._Curstate == "String"):
            if(one_word in self.string_sted_list):
                self._Curstate = "NONE"
                return f"{one_word}</span>"
            return one_word

        if(one_word in self.string_sted_list):
            self._Curstate = "String"
            return f"<span class=\"String\" style=\"color:#d7ba7d;\">{one_word}"


        if(one_word in self.comment_bfaf["line"]):
            self._Curstate = "Com_1"
            return f"<span class=\"Com_1\" style=\"color:#32ff2e;\">{one_word}"

        if(one_word in self.comment_bfaf["before"]):
            self._Curstate = "Com_2"
            return f"<span class=\"Com_2\" style=\"color:#19edfb;\">{one_word}"

        if(one_word.isnumeric()):
            return f"<span class=\"Number\" style=\"color:#ff6a00;\">{one_word}</span>"

        if(one_word in self.splitter_list or one_word in self.prime_splitter_list):
            return one_word

        if(one_word in self.yoyakugo_dic.keys()):
            return f"<span class=\"{self.yoyakugo_dic[one_word]}\" style=\"color:#569cd6;\">{one_word}</span>"

        before_word, after_word = self.getBfAfWord()
        for key in self.usertype_bfaf.keys():
            if(((before_word in self.usertype_bfaf[key][0]) or (self.usertype_bfaf[key][0] == ["ALL_STRING_OK"]))
                    and ((after_word in self.usertype_bfaf[key][1]) or (self.usertype_bfaf[key][1] == ["ALL_STRING_OK"]) )):
                print(f"new {key} found!! --> {one_word}")
                self.yoyakugo_dic[one_word] = key
                return f"<span class=\"{key}\">{one_word}</span>"

        if((one_word.upper() == one_word) and re.search('[A-Z]', one_word) and (self.language == "cpp" or self.language == "arduino")):
            print(f"new Macro found!! --> {one_word}")
            self.yoyakugo_dic[one_word] = "Macro"
            return f"<span class=\"Macro\">{one_word}</span>"
        return one_word


    def _setColor_oneWord(self, one_word):
        for uniqueChar in self.unique_char_dic.keys():
            one_word = one_word.replace(uniqueChar, self.unique_char_dic[uniqueChar])

        if(self._Curstate == "Com_1"):
            if(one_word == "\n"):
                self._Curstate = "NONE"
                return "</span>\n"
            return one_word

        if(self._Curstate == "Com_2"):
            if(one_word in self.comment_bfaf["after"]):
                self._Curstate = "NONE"
                return f"{one_word}</span>"
            return one_word

        if(self._Curstate == "String"):
            if(one_word in self.string_sted_list):
                self._Curstate = "NONE"
                return f"{one_word}</span>"
            return one_word

        if(one_word in self.string_sted_list):
            self._Curstate = "String"
            return f"<span class=\"String\">{one_word}"


        if(one_word in self.comment_bfaf["line"]):
            self._Curstate = "Com_1"
            return f"<span class=\"Com_1\">{one_word}"

        if(one_word in self.comment_bfaf["before"]):
            self._Curstate = "Com_2"
            return f"<span class=\"Com_2\">{one_word}"

        if(one_word.isnumeric()):
            return f"<span class=\"Number\">{one_word}</span>"

        if(one_word in self.splitter_list or one_word in self.prime_splitter_list):
            return one_word

        if(one_word in self.yoyakugo_dic.keys()):
            return f"<span class=\"{self.yoyakugo_dic[one_word]}\">{one_word}</span>"

        before_word, after_word = self.getBfAfWord()
        for key in self.usertype_bfaf.keys():
            if(((before_word in self.usertype_bfaf[key][0]) or (self.usertype_bfaf[key][0] == ["ALL_STRING_OK"]))
                    and ((after_word in self.usertype_bfaf[key][1]) or (self.usertype_bfaf[key][1] == ["ALL_STRING_OK"]) )):
                print(f"new {key} found!! --> {one_word}")
                self.yoyakugo_dic[one_word] = key
                return f"<span class=\"{key}\">{one_word}</span>"

        if((one_word.upper() == one_word) and re.search('[A-Z]', one_word) and (self.language == "cpp" or self.language == "arduino")):
            print(f"new Macro found!! --> {one_word}")
            self.yoyakugo_dic[one_word] = "Macro"
            return f"<span class=\"Macro\">{one_word}</span>"
        return one_word

    def LoadColorSetting(self):
        # XMLファイルを解析して文字の色をしゅとくする
        tree = ET.parse('color_setting.xml')
        root = tree.getroot()

        for child in root:
            self.string_color_dic[child.attrib["Name"]] = [child.attrib["Foreground"], child.attrib["Background"], child.attrib["BoldFont"]]
        return self.string_color_dic

    def saveFile(self):
        template_text = ""
        self.CreateCSS()
        with open(self.template_html_filename, "r",  encoding="utf-8_sig") as f_template:
            template_text = f_template.read()

        line_number_text = ""
        if(self.AddLineNumber):
            line_number_text = "<div class=\"L_Number\">"
            for i in range(len(self.program_after.split("\n"))+1):
                line_number_text += str(i+1) + "<br>"
            line_number_text += "__<br></div>"

        template_text = template_text.replace("$$$PROGRAM_HTML$$$", self.program_after)
        template_text = template_text.replace("$$$PROGRAM_CSS$$$", self.css_text)
        template_text = template_text.replace("$$$LINE_NUMBER$$$", line_number_text)
        template_text = template_text.replace("$$$LANGUAGE$$$", self.language)

        with open(self.save_filename, "w",  encoding="utf-8_sig") as f_out:
            f_out.write(template_text)

        print("-------     ファイルに保存しました    ------------")

    def CreateCSS(self):
        tag_list = ["Number", "Com_1","Com_2", "String"]
        for text in self.yoyakugo_dic.values():
            if(text not in tag_list):
                tag_list.append(text)

        self.css_text = ""
        for tag_name in tag_list:
            if(tag_name in self.string_color_dic.keys()):
                self.css_text += "." + tag_name + "{ color:" + self.string_color_dic[tag_name][0] + "; }\n"
            else:
                print("[ERROR]  CSSタグが見つかりません -> "+ tag_name)
                self.css_text += tag_name + "{red}\n"


    ################################################################
    #                  その他の補助関数
    ################################################################

    def getLanguage(self):
        extention = self.program_filename.split(".")[1]
        extention_language_dic = {"cpp":"cpp", "c":"cpp", "h":"cpp","py":"python","java":"java","html":"html","css":"css","ino":"arduino","pro":"processing"}
        if(extention in extention_language_dic):
            self.language = extention_language_dic[extention]
            print("[INFO]  言語が設定されました -> " + self.language)
            return self.language
        print("[ERROR]  拡張子に合う言語が見受かりませんでした")
        return ""

    def getBfAfWord(self):
        before_word = ""
        after_word = ""

        for i in range(self._CurIndex):
            if((self._text_list_oneLine[self._CurIndex - i - 1] not in self.splitter_list) and (self._text_list_oneLine[self._CurIndex - i - 1] not in self.prime_splitter_list)):
                before_word = self._text_list_oneLine[self._CurIndex - i - 1]
                break

        for i in range(len(self._text_list_oneLine) - self._CurIndex - 1):
            if((self._text_list_oneLine[self._CurIndex + i + 1] not in self.splitter_list) and (self._text_list_oneLine[self._CurIndex + i + 1] not in self.prime_splitter_list)):
                after_word = self._text_list_oneLine[self._CurIndex + i + 1]
                break
        #print(f"{before_word}, {after_word}")
        return before_word, after_word

    def getDataSettings(self):
        db = database()
        db.LoadAll()
        if(self.language not in db.language_list):
            print("[ERROR]  言語が見つかりませんでした")
            self.language = ""
        self.splitter_list = db.splitter_text_dic[self.language]
        self.prime_splitter_list = db.prime_splitter_dic[self.language]
        self.yoyakugo_dic =db.yoyakugo_dic[self.language]
        self.comment_bfaf = db.comment_bfaf[self.language]
        self.unique_char_dic = db.unique_char_dic
        self.usertype_bfaf = db.usertype_bfaf[self.language]
        return

    def _mysplitter(self, one_sentence):
        split_index_list = np.array([0])
        for splitter_word in self.prime_splitter_list:
            list1 = np.array([i for i in range(len(one_sentence)) if one_sentence.startswith(splitter_word, i)], dtype=int)
            list2 =list1 + len(splitter_word)
            split_index_list = np.concatenate([split_index_list, list1, list2])

        list3 = list(split_index_list)
        list3 = sorted(set(list3))

        #referencce: https://stackoverflow.com/questions/10851445/splitting-a-string-by-list-of-indices
        splited_text = [one_sentence[i:j] for i,j in zip(list3, list3[1:]+[None])]
        output_list = []

        for word in splited_text:
            if(word in self.prime_splitter_list):
                output_list.append(word)
            else:
                splited_list = self._split_byCharList(word, self.splitter_list)
                for word2 in splited_list:
                    if(word2 != ""):
                        output_list.append(word2)

        return output_list

    def _split_byCharList(self, word, splitter_list):
        output_list = []
        tmp_text = ""
        for char in list(word):
            if(char in splitter_list):
                output_list.append(tmp_text)
                output_list.append(char)
                tmp_text = ""
            else:
                tmp_text += char
        output_list.append(tmp_text)
        return output_list


CodePainter = Code_coloring()
CodePainter.run()

