# Таблиця лексем мови
tableOfLanguageTokens = {'program': 'keyword', 'if': 'keyword', 'do': 'keyword', 'while': 'keyword', 'enddo': 'keyword',
                         'print': 'keyword', 'read': 'keyword',
                         'int': 'keyword', 'double': 'keyword', 'bool': 'keyword', ';': 'semicolon', ',': 'coma',
                         '=': 'assign_op', '.': 'dot', ' ': 'ws', '\t': 'ws', '\n': 'nl',
                         '-': 'add_op', '+': 'add_op', '*': 'mult_op', '/': 'div_op', '//': 'div_op', '^': 'pow_op',
                         '{': 'braces_op', '}': 'braces_op', '(': 'par_op', ')': 'par_op',
                         '<': 'rel_op', '>': 'rel_op', '!=': 'rel_op', '<=': 'rel_op', '>=': 'rel_op','==': 'rel_op',
                         '&': '&', '|': '|', '!': 'bool_op', '&&': 'bool_op', '||': 'bool_op'}
# Решту токенів визначаємо не за лексемою, а за заключним станом
tableIdentFloatInt = {2: 'ident', 5: 'double', 6: 'int', 10: 'double'}

# Діаграма станів
#               Q                                   q0          F
# M = ({0,1,2,4,5,6,9,11,12,13,14,101,102}, Σ,  δ , 0 , {2,6,9,12,13,14,101,102})

# δ - state-transition_function
stf = {(0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2, (0, 'ws'): 0,
       (0, 'Digit'): 3, (3, 'Digit'): 3, (3, 'dot'): 4, (3, 'other'): 6, (4, 'Digit'): 4, (4, 'other'): 5, (4, 'e'): 10,
       (0, 'dot'): 7, (7, 'other'): 401, (7, 'Digit'): 4, (4, 'e'): 9, (9, 'Digit'): 9, (9, 'other'): 10,
       (0, 'assign_op'): 11, (11, 'assign_op'): 16, (11, 'other'): 12, (0, 'rel_op'): 11, (0, '!'): 11,
       (0, '&'): 17, (17, '&'): 18, (17, 'other'): 402, (0, '|'): 19, (19, '|'): 20, (19, 'other'): 403,
       (0, 'add_op'): 8, (0, 'mult_op'): 8, (0, 'pow_op'): 8, (0, 'div_op'): 21, (21, 'div_op'): 22, (21, 'other'): 23,
       (0, 'nl'): 13, (0, 'semicolon'): 14, (0, 'par_op'): 15, (0, 'braces_op'): 15, (0, 'coma'): 14,
       (0, 'other'): 404
       }

initState = 0  # q0 - стартовий стан
F = {2, 5, 6, 8, 10, 12, 13, 14, 15, 16, 18, 20, 22, 23, 401, 402, 403, 404}
Fstar = {2, 5, 6, 10}  # зірочка
Ferror = {401, 402, 403, 404}  # обробка помилок

tableOfId = {}  # Таблиця ідентифікаторів
tableOfConst = {}  # Таблиць констант
tableOfSymb = {}  # Таблиця символів програми (таблиця розбору)

state = initState  # поточний стан

f = open('test.my_lang', 'r')
sourceCode = f.read()
f.close()

# FSuccess - ознака успішності розбору
FSuccess = (True, 'Lexer')

lenCode = len(sourceCode) - 1  # номер останнього символа у файлі з кодом програми
numLine = 1  # лексичний аналіз починаємо з першого рядка
numChar = -1  # з першого символа (в Python'і нумерація - з 0)
char = ''  # ще не брали жодного символа
lexeme = ''  # ще не починали розпізнавати лексеми


def lex():
    global state, numLine, char, lexeme, numChar, FSuccess
    try:
        while numChar < lenCode:
            char = nextChar()  # прочитати наступний символ
            classCh = classOfChar(char)  # до якого класу належить
            state = nextState(state, classCh)  # обчислити наступний стан
            if (is_final(state)):  # якщо стан заключний
                processing()  # виконати семантичні процедури
            # if state in Ferror:	    # якщо це стан обробки помилки
            # break					#      то припинити подальшу обробку
            elif state == initState:
                lexeme = ''  # якщо стан НЕ заключний, а стартовий - нова лексема
            else:
                lexeme += char  # якщо стан НЕ закл. і не стартовий - додати символ до лексеми
        print('Lexer: Лексичний аналіз завершено успішно')
    except SystemExit as e:
        # Встановити ознаку неуспішності
        FSuccess = (False, 'Lexer')
        # Повідомити про факт виявлення помилки
        print('Lexer: Аварійне завершення програми з кодом {0}'.format(e))


def processing():
    global state, lexeme, char, numLine, numChar, tableOfSymb
    if state == 13:  # \n
        numLine += 1
        state = initState
    if state in (2, 5, 6, 10):  # keyword, ident, double, int
        token = getToken(state, lexeme)
        if token != 'keyword':  # не keyword
            index = indexIdConst(state, lexeme)
            print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(numLine, lexeme, token, index))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:  # якщо keyword
            print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))  # print(numLine,lexeme,token)
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)  # зірочка
        state = initState
    if state in (14, 15, 8, 16, 18, 20, 22, 23):  # 12:         # assign_op # in (12,14):
        lexeme += char
        token = getToken(state, lexeme)
        print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
    if state == 12:
        token = getToken(state, lexeme)
        print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)  # зірочка
        state = initState
    if state in Ferror:  # (401,404):  # ERROR
        fail()


def fail():
    global state, numLine, char
    print(numLine)
    if state in (401, 403, 402, 404):
        print('Lexer: у рядку ', numLine, ' неочікуваний символ ' + char)
        exit(state)


def is_final(state):
    return True if state in F else False


def nextState(state, classCh):
    try:
        return stf[(state, classCh)]
    except KeyError:
        return stf[(state, 'other')]


def nextChar():
    global numChar
    numChar += 1
    return sourceCode[numChar]


def putCharBack(numChar):
    return numChar - 1


def classOfChar(char):
    global state
    if char in '.':
        res = "dot"
    elif char in ',':
        res = "coma"
    elif char in ';':
        res = "semicolon"
    elif char in 'abcdefghijklmnopqrstuvwxyz':
        res = "Letter"
        if state == 4 and char == 'e':
            res = 'e'
    elif char in "0123456789":
        res = "Digit"
    elif char in " \t":
        res = "ws"
    elif char in "\n":
        res = "nl"
    elif char in "*":
        res = 'mult_op'
    elif char in "^":
        res = 'pow_op'
    elif char in "/":
        res = 'div_op'
    elif char in "+-":
        res = 'add_op'
    elif char in "=":
        res = "assign_op"
    elif char in "()":
        res = "par_op"
    elif char in "{}":
        res = "braces_op"
    elif char in "<>":
        res = "rel_op"
    elif char in "!&|":
        res = char
    else:
        res = 'символ не належить алфавіту'
    return res


def getToken(state, lexeme):
    try:
        return tableOfLanguageTokens[lexeme]
    except KeyError:
        try:
            return tableIdentFloatInt[state]
        except KeyError:
            print("error unexpected token " + lexeme)
            exit(401)


def indexIdConst(state, lexeme):
    indx = 0
    if state == 2:
        indx = tableOfId.get(lexeme)
        #		token=getToken(state,lexeme)
        if indx is None:
            indx = len(tableOfId) + 1
            tableOfId[lexeme] = indx
    if state == 5 or state == 10:
        indx = tableOfConst.get(lexeme)
        if indx is None:
            indx = len(tableOfConst) + 1
            tableOfConst[lexeme] = indx
    if state == 6:
        indx = tableOfConst.get(lexeme)
        if indx is None:
            indx = len(tableOfConst) + 1
            tableOfConst[lexeme] = indx
    return indx


# запуск лексичного аналізатора
lex()

# Таблиці: розбору, ідентифікаторів та констант
print('-' * 30)
print('tableOfSymb:{0}'.format(tableOfSymb))
print('tableOfId:{0}'.format(tableOfId))
print('tableOfConst:{0}'.format(tableOfConst))
