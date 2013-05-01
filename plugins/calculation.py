from tools.web import urllib
from tools import plugin

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


def do_python(keight, event):
    """Runs a snippet of code through a python interpreter using codepad.org"""
    pass