from googletrans import Translator

translator = Translator()

translations = translator.translate("Catalytic network", src='en', dest='zh-cn')
#print(translations)
print(translations.text)
