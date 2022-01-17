#Reads in text from json file and converts to braille 
#Opens json.text and reads filename. Opens json file and reads in text.
import json
from pybrl import translate, toUnicodeSymbols
file1 = open('json.txt', 'r')
jname = file1.read()
    
extract = []
with open(jname) as json_file:
        data = json.load(json_file)
        for p in data['textAnnotations']: #adds words and converts to lowercase 
                extract.append(p['description'].lower())
print(extract)

translated = []
for i in range(0, len(extract)):
    text = translate(extract[i])
    braille = toUnicodeSymbols(text, flatten=True)
    translated.append(braille)
print(translated)