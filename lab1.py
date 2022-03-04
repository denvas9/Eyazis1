# -*- coding: utf-8 -*-
import nltk
import time
from striprtf.striprtf import rtf_to_text
from xml.dom import minidom

from tkinter import messagebox as mb
from tkinter import *

from tkinter import Tk, Label, Button, Entry, END, Frame, NO, W, WORD, Text
import tkinter.ttk as ttk
from pymorphy2 import MorphAnalyzer
from tkinter import *
from tkinter.filedialog import askopenfilename,asksaveasfile

from pymorphy2 import MorphAnalyzer
from pymorphy2.tagset import OpencorporaTag
from enum import Enum

#start_time = time.time()

#основное хранилище данных
main_dictionary =[]
    
part_of_sentence = {
    'subject': 'NOUN nomn,NPRO',
    'predicate': 'VERB',
    'definition': 'ADJF,ADJS,NUMR',
    'addition': 'NOUN,NPRO',
    'circumstance': 'INFN,ADVB,GRND,PRTF,PRTS',
}

class RuPartOfSent(Enum):
    SUBJECT = 'Подлежащее'
    PREDICATE = 'Сказуемое'
    DEFINITION = 'Определение'
    ADDITION = 'Дополнение'
    CIRCUMSTANCE = 'Обстоятельство'
    UNKNOWN = ''

class Lexeme:
    lexeme = ''
    tags = ''
    part_of_sent = ''

    def __eq__(self, other):
        return True if self.lexeme.lower() == other.lexeme.lower() and self.tags.lower() == other.tags.lower() and self.part_of_sent.lower() == other.part_of_sent.lower() else False

    def __ne__(self, other):
        return True if self.lexeme.lower() != other.lexeme.lower() and self.tags.lower() != other.tags.lower() and self.part_of_sent.lower() != other.part_of_sent.lower() else False

    def __gt__(self, other):
        return True if self.lexeme.lower() > other.lexeme.lower() else False

    def __ge__(self, other):
        return True if self.lexem.lower() >= other.lexeme.lower() else False
        
    def __lt__(self, other):
        return True if self.lexeme.lower() < other.lexeme.lower() else False

    def __le__(self, other):
        return True if self.lexeme.lower() <= other.lexeme.lower() else False


#функции для получения и обработки слов
def get_words_from_text(text: str) -> list:
    sentences = nltk.sent_tokenize(text)
    words = []
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence):
            if word != '.' and word != ',' and word != '?' and word != '!':
                words.append(word.lower())
    return words

def get_part_of_sent(tags: OpencorporaTag, has_subject: bool) -> RuPartOfSent:
    if tags.POS == 'NOUN' and tags.case == 'nomn':
        return RuPartOfSent.SUBJECT
    elif tags.POS == 'NOUN':
        return RuPartOfSent.ADDITION
    elif tags.POS == 'NPRO' and has_subject:
        return RuPartOfSent.ADDITION
    elif tags.POS == 'NPRO':
        return RuPartOfSent.SUBJECT
    for i in part_of_sentence.items():
        if tags.POS in i[1]:
            return RuPartOfSent[i[0].upper()]
    return RuPartOfSent.UNKNOWN

def get_lexemes_from_text(text: str) -> list:
    lexemes = []
    words = get_words_from_text(text)
    morph = MorphAnalyzer()
    has_subject = False
    for word in words:
        le = morph.parse(word)[0]
        lexeme = Lexeme()
        lexeme.lexeme = word
        lexeme.tags = le.tag.cyr_repr
        lexeme.part_of_sent = get_part_of_sent(le.tag, has_subject).value
        if lexeme.part_of_sent == 'Подлежащее':
            has_subject = True
        lexemes.append(lexeme)
    return lexemes
#сохранение словаря в файл (переименованного) xml формата
def save_dictionary():
    file = asksaveasfile(filetypes=(("dict file", "*.dict"),), defaultextension=("dict file", "*.dict"))
    if file== None:
       return
    doc = minidom.Document()
    root = doc.createElement('root')

    lexemes = main_dictionary

    lexemes.sort(reverse=True)

    for i in lexemes:
        word = doc.createElement('word')
        lexeme = doc.createElement('lexeme')
        tag = doc.createElement('tag')
        description = doc.createElement('description')

        text1 = doc.createTextNode(i.lexeme)
        text2 = doc.createTextNode(i.tags)
        text3 = doc.createTextNode(i.part_of_sent)

        lexeme.appendChild(text1)
        tag.appendChild(text2)
        description.appendChild(text3)

        word.appendChild(lexeme)
        word.appendChild(tag)
        word.appendChild(description)

        root.appendChild(word)
    doc.appendChild(root)

    xml_str = doc.toprettyxml(indent="  ", encoding='UTF-8')

    file.write(str(xml_str, 'UTF-8'))
    file.close()
#загрузка словаря из файла (переименованного) xml формата
def load_dictionary():
    filename = askopenfilename(filetypes=(("dict file", "*.dict"),), defaultextension=("dict file", "*.dict"))
    if filename== None:
       return
    file_str = ''
    with open(filename) as file:
        file.readline()
        for line in file:
            file_str = file_str + line
    doc = minidom.parseString(file_str).documentElement
    word_elements = doc.getElementsByTagName("word")

    main_dictionary.clear()
    vocabularyTree.delete(*vocabularyTree.get_children())
    for i in word_elements:
        lexeme = Lexeme()
        lexeme.lexeme = i.getElementsByTagName("lexeme")[0].childNodes[0].nodeValue
        if len(i.getElementsByTagName('tag')[0].childNodes):
            lexeme.tags=i.getElementsByTagName("tag")[0].childNodes[0].nodeValue
        else:
            lexeme.tags=''
        
        if len(i.getElementsByTagName('description')[0].childNodes):
            lexeme.part_of_sent = i.getElementsByTagName("description")[0].childNodes[0].nodeValue
        else:
            lexeme.part_of_sent = ''
        main_dictionary.append(lexeme)

    updateVocabulary()

#парсер
def parser(string:str ):

    miscSymbols = ['.',',','!','?',':',';','(',')']
    for i in miscSymbols:
        string = string.replace(i, '')
    lexemes = get_lexemes_from_text(string)
    lexemes.sort(reverse=True)

    for lex in lexemes:
        add_flag = True
        for j in main_dictionary:
            if lex == j:
                add_flag = False
        if add_flag:
            main_dictionary.append(lex)

#обновление содержимого таблицы
def updateVocabulary():
    vocabularyTree.delete(*vocabularyTree.get_children())

    global main_dictionary
    main_dictionary.sort(reverse=False)

    for lexeme in main_dictionary:
        
        vocabularyTree.insert('', 'end', values=(lexeme.lexeme,
                                                 lexeme.tags,
                                                 lexeme.part_of_sent))

#создание словаря из текстового поля программы                                               
def createVocabularyFromTextField():
    text = inputText.get(1.0, END).replace('\n', '')
    parser(text)
    updateVocabulary()

#создание словаря из текстового файла (форматы txt и rtf)
def open_file_to_read():
    filename = askopenfilename(filetypes=[("rtf file", "*.rtf"),("txt file", "*.txt")], defaultextension=("rtf file", "*.rtf"))
    if filename== None:
       return

    if (filename.endswith(".txt")):
        with open(filename,mode="r", encoding="utf-8") as file:
            file_str = file.read()

    elif(filename.endswith(".rtf")):
        with open(filename) as file:
            content = file.read()
            file_str = rtf_to_text(content)
    else:
        return
    parser(file_str)
    updateVocabulary()

#очистка словаря
def clearVocabulary():
    vocabularyTree.delete(*vocabularyTree.get_children())
    main_dictionary.clear()

#сортировка для колонок таблицы
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
                                    
def sortVocabl():
    columns = ("Лексема", "Тэги", "Возможная роль в предложении")
    for col in columns:
        vocabularyTree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(vocabularyTree, _col, True))
#удаление элементов
def delete_item():
    try:
        selected=vocabularyTree.focus()
        temp = vocabularyTree.item(selected, 'values')

        for word in main_dictionary:
            if word.lexeme == temp[0]:
                main_dictionary.remove(word)

        vocabularyTree.delete(selected)
    except Exception:
        mb.showerror(title="Error", message="Have you selected any item before ckicking that button?..")
        return 

#в temp 0 - лексема, 1 - тэги, 2 - возм. роль
def update_item():

    tags=tagEditingEntry.get()
    role=roleEditingEntry.get()

    if (tags=="" and role==""):
        mb.showerror(title="Empty fields error", message="All fields are empty! You are supposed to enter something before clicking that button.") 
        return

    selected = vocabularyTree.focus()
    temp = vocabularyTree.item(selected, 'values')

    for word in main_dictionary:
        if word.lexeme.lower()==temp[0].lower() and word.tags.lower() == temp[1].lower() and word.part_of_sent.lower() == temp[2].lower() :
            for dupWord in main_dictionary:
                if (dupWord.lexeme.lower()==temp[0].lower() and dupWord.tags.lower()==tags.lower() and dupWord.part_of_sent.lower()== role.lower()):
                    mb.showerror(title="Duplicate error", message="Duplication detected, cancelling edit...") 
                    return
            if role=="":
                vocabularyTree.item(selected, values=(temp[0], tags, temp[2]))
                word.tags=tags
            elif tags=="":
                vocabularyTree.item(selected, values=(temp[0], temp[1], role))
                word.part_of_sent=role
            else:
                vocabularyTree.item(selected, values=(temp[0], tags, role))
                word.tags=tags
                word.part_of_sent=role


def add_item():

    lexeme=lexAddingEntry.get()
    

    if (lexeme==""):
        mb.showerror(title="Empty field error", message="Lexeme field is empty! You are supposed to enter something before clicking that button.") 
        return

    addLex=Lexeme()
    addLex.lexeme=lexeme.lower()
    addLex.tags=tagAddingEntry.get()
    addLex.part_of_sent=roleAddingEntry.get()

    for lex in main_dictionary:
        if lex==addLex:
            mb.showerror(title="Duplicate error", message="The lexeme you are trying to add already exists in the main dictionary.") 
            return

    main_dictionary.append(addLex)
    updateVocabulary()
        
def get_search_result():
    
    searchReq=searchEntry.get()
    if (searchReq==""):
        mb.showerror(title="Empty field error", message="Search field is empty! You are supposed to enter something before clicking that button.") 
        return

    treeItems=vocabularyTree.get_children()
    for item in treeItems:
        temp = vocabularyTree.item(item, 'values')
        if temp[0].lower().find(searchReq.lower())==-1:
            vocabularyTree.delete(item)
    

def clear_search_result():
    updateVocabulary()

HELPTEXT =  '''                    

    Программа предназначена для для обработки текстов на руском языке.
    
    Проверяет текст на наличие слов, определяет их характеристики и на их основе
делает вывод о возможной роли конкретного слова в составе предложения (если
существительное в именительномо падеже, то возм. подлежащее).

    Для сортировки по значениям в отдельных столбцах таблицы нажимать на названия 
столбцов.

    Поддерживаемые форматы входных текстовых файлов - rtf и txt.

    Для хранения данных словаря используется формат .dict (переименованный .xml).

    При считывании данных из текстового файла и из текстового поля данные добавляются 
в активный словарь.При загрузке имеющегося словаря активный словарь очищается и 
перезаполняется данными из загружаемого

'''

def showHelp():
    mb.showinfo(title="Помощь", message=HELPTEXT)


root = Tk()
mainmenu = Menu(root)
mainmenu.add_command(label='Сохранить имеющийся словарь в файл', command=save_dictionary)
mainmenu.add_command(label='Загрузить имеющийся словарь из файла', command=load_dictionary)
mainmenu.add_command(label='Помощь', command=showHelp)
root.config(menu=mainmenu)

space0 = Label(root)
inputFrame = Frame(root, bd=2)
inputText = Text(inputFrame, height=10, width=130, wrap=WORD)

createVocabularyButton_textField = Button(inputFrame, text='Создать словарь по тексту', width=30, height=2, bg='grey')
createVocabularyButton_textFile = Button(inputFrame, text='Создать словарь из текстового файла (txt или rtf)', width=50, height=2, bg='grey')
clearVocabularyButton = Button(inputFrame, text='Очистить словарь', width=30, height=2, bg='grey')

deleteElementButton= Button(inputFrame, text='Удалить элемент', width=30, height=2, bg='grey')

space1 = Label(root)
vocabularyFrame = Frame(root, bd=2)
vocabularyTree = ttk.Treeview(vocabularyFrame, columns=("Лексема", "Тэги", "Возможная роль в предложении"), selectmode='browse',
                              height=11)
vocabularyTree.heading('Лексема', text="Лексема", anchor=W)
vocabularyTree.heading('Тэги', text="Тэги", anchor=W)
vocabularyTree.heading('Возможная роль в предложении', text="Возможная роль в предложении", anchor=W)
vocabularyTree.column('#0', stretch=NO, minwidth=0, width=0)
vocabularyTree.column('#1', stretch=NO, minwidth=347, width=347)
vocabularyTree.column('#2', stretch=NO, minwidth=347, width=347)
vocabularyTree.column('#3', stretch=NO, minwidth=347, width=347)

space2 = Label(root, text='\n')
editingFrame = Frame(root, bg='grey', bd=5)
tagEditingLabel = Label(editingFrame, text=' Тэги: ', width=14, height=2, bg='grey', fg='white')
tagEditingEntry = Entry(editingFrame, width=23)
roleEditingLabel = Label(editingFrame, text=' Роль: ', width=10, height=2, bg='grey', fg='white')
roleEditingEntry = Entry(editingFrame, width=23)
space21 = Label(editingFrame, text='      ', bg='grey')
editButton = Button(editingFrame, text='Изменить', width=8, height=2, bg='grey')


space3 = Label(root, text='\n')
addingFrame = Frame(root, bg='grey', bd=5)
lexAddingLabel = Label(addingFrame, text=' Лексема: ', width=14, height=2, bg='grey', fg='white')
lexAddingEntry = Entry(addingFrame, width=23)
tagAddingLabel = Label(addingFrame, text=' Тэги: ', width=14, height=2, bg='grey', fg='white')
tagAddingEntry = Entry(addingFrame, width=23)
roleAddingLabel = Label(addingFrame, text=' Роль: ', width=10, height=2, bg='grey', fg='white')
roleAddingEntry = Entry(addingFrame, width=23)
space31 = Label(addingFrame, text='      ', bg='grey')
addButton = Button(addingFrame, text='Добавить', width=8, height=2, bg='grey')

space4 = Label(root, text='\n')
searchFrame = Frame(root, bg='grey', bd=5)
searchLabel = Label(searchFrame, text=' Запрос: ', width=14, height=2, bg='grey', fg='white')
searchEntry = Entry(searchFrame, width=23)
space41 = Label(searchFrame, text='      ', bg='grey')
searchButton = Button(searchFrame, text='Найти', width=8, height=2, bg='grey')
clearSearchButton = Button(searchFrame, text='Сброс', width=8, height=2, bg='grey')

createVocabularyButton_textFile.config(command=open_file_to_read)
createVocabularyButton_textField.config(command=createVocabularyFromTextField)
clearVocabularyButton.config(command=clearVocabulary)
deleteElementButton.config(command=delete_item)
searchButton.config(command=get_search_result)
clearSearchButton.config(command=clear_search_result)

editButton.config(command=update_item)
addButton.config(command=add_item)

space0.pack()
inputFrame.pack()
inputText.pack()

createVocabularyButton_textFile.pack(side='left')
createVocabularyButton_textField.pack(side='left')
clearVocabularyButton.pack(side='left')
deleteElementButton.pack(side='left')

space1.pack()
vocabularyFrame.pack()
vocabularyTree.pack()

#editing block
space2.pack()
editingFrame.pack()
tagEditingLabel.pack(side='left')
tagEditingEntry.pack(side='left')
roleEditingLabel.pack(side='left')
roleEditingEntry.pack(side='left')
space21.pack(side='left')
editButton.pack(side='left')

#adding block
space3.pack()
addingFrame.pack()
lexAddingLabel.pack(side='left')
lexAddingEntry.pack(side='left')
tagAddingLabel.pack(side='left')
tagAddingEntry.pack(side='left')
roleAddingLabel.pack(side='left')
roleAddingEntry.pack(side='left')
space31.pack(side='left')
addButton.pack(side='left')

#searching block
space4.pack()
searchFrame.pack()
searchLabel.pack(side='left')
searchEntry.pack(side='left')
space41.pack(side='left')
searchButton.pack(side='left')
clearSearchButton.pack(side='left')

sortVocabl()

root.mainloop()
#print(f"{(time.time() - start_time)*1000} миллисекунд")



