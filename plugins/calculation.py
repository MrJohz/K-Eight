import urllib, urllib2, re
from tools import plugin
import HTMLParser

@plugin.alias('c')
def do_calculate(keight, event):
    """Simple calculator function."""
    msg = event.message.split(' ', 1)
    try:
        inp = msg[1]
    except IndexError:
        ret = "I can't calculate something that isn't there, {}"
        return ret.format(event.source)
    if not inp.strip():
        ret = "I can't calculate something that isn't there, {}"
        return ret.format(event.source)
    query = inp.encode('utf-8')
    query = query.replace('\xcf\x95', 'phi')
    query = urllib.quote(query.replace('\xcf\x80', 'pi'))
    url = 'http://www.google.com/ig/calculator?q='
    retval = urllib.urlopen(url + query).read()
    parts = retval.split('",')
    answer = [p for p in parts if p.startswith('rhs: "')][0][6:]
    if answer:
        answer = answer.decode('utf-8', 'ignore')
        answer = answer.replace(u'\xc2\xa0', ',')
        answer = answer.replace('&#215;', '*')
        answer = answer.replace('<sup>', '^(')
        answer = answer.replace('</sup>', ')')
        return answer
    else:
        return "Sorry {}, I can't get a result.  :/".format(event.source)
        

def do_wa(keight, event):
    """Wolfram Alpha request."""
    msg = event.message.split(' ', 1)
    try:
        inp = msg[1]
    except IndexError:
        return "That's a blank input, {}".format(event.source)
    if not inp.strip():
        return "That's a blank input, {}".format(event.source)
    query = inp.encode('utf-8')
    uri = 'http://tumbolia.appspot.com/wa/'
    answer = urllib.urlopen(uri + urllib.quote(query.replace('+', '%2B')))
    answer = answer.read()
    if answer.strip():
        answers = answer.split(';')
        if not len(answers) > 1:
            return "I'm sorry, {}, but I couldn't find anything.".format(event.source)
        answer = answers[1:3]
        if len(answers) > 3:
            advice = "For more, see http://www.wolframalpha.com/input/?i={}"
            advice = advice.format(urllib.quote(query.replace('+', '%2B')))
            answer.append(advice)
        return answer
    else: return "I couldn't find anything, sorry."

PYTHON_CODE = """
import code
console = code.InteractiveConsole()

def prettify_return(code, console=console):
    print "Snippet run by codepad.org for K-Eight (http://mrjohz.github.io/K-Eight/)"
    print '-' * 10
    answer = console.push(code)
    print '-' * 10
    print answer

runcode = r'''
{code}
'''.strip()

prettify_return(runcode)
""".strip()

RE_FOR_CODE = re.compile(r'''
(.*?)Snippet run by codepad\.org for K-Eight.*?
----------(.*)
----------
(False|True)
'''.strip(), flags=re.DOTALL)

class CodepadParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.tag_rank = []
        
    def handle_starttag(self, tag, attrs):
        self.tag_rank.append(tag)
    
    def handle_endtag(self, tag):
        if tag in self.tag_rank:
            self.tag_rank.remove(tag)
    
    def handle_data(self, data):
        if self.tag_rank[-3:] == ['td', 'div', 'pre']:
            self.code = data.strip()

@plugin.alias('py')
def do_python(keight, event):
    """Runs a snippet of code through a python interpreter using codepad.org"""
    runcode = event.args
    codepad_message = PYTHON_CODE.format(code=runcode)
    data = urllib.urlencode({'lang': 'Python',
                             'code': codepad_message,
                             'private': 'True',
                             'run': 'True',
                             'submit': 'Submit'})
    request = urllib2.Request('http://codepad.org/', data=data)
    response = urllib2.urlopen(request)
    parser = CodepadParser()
    parser.feed(response.read())
    code = parser.code
    try:
        error, printout, answer = RE_FOR_CODE.search(code).groups()
    except AttributeError:
        return "An unexpected error occured. (calculation.do_python)"
    if error != '':
        return error.strip().split('\n')[-1]
    elif answer.strip() == "True":
        return "SyntaxError - .py command cannot take potentially multiple lines of input."
    else:
        return printout.strip().split('\n')[0]