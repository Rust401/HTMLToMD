import re
import os

root = './data'
files = [os.path.join(root, i) for i in os.listdir(root)]
indexPage = [i for i in files if os.path.isfile(i)][0]
def ReadFile(path):
    with open(path) as f:
        return ''.join(f.readlines())

indexContent = ReadFile(indexPage)

play = re.search('class="play"[^>]*>([a-zA-Z0-9 ]*)', indexContent, re.I).group(1)
indexPattern = re.compile('Act ([0-9]*), Scene ([0-9]*): <a href="([^"]*html)">([^<]*)<', re.I)
indexScenes = [{'actNo':url.group(1),
                'sceneNo':url.group(2),
                'href':url.group(3),
                'sceneTitle':url.group(4)}
               for url in indexPattern.finditer(indexContent)]


scenePattern = re.compile('<h3>([^<]*)</h3>', re.I)
cNamePattern = re.compile('<A NAME=speech[0-9]*> *<b>([a-zA-Z ]*)<', re.I)
cLinePattern = re.compile('<A NAME=[0-9 ]*> *([^<]*)</A>', re.I)
sHintPattern = re.compile('<i>([^<]*)</i>', re.I)

def FormatContent(line):
    theType = line['type']
    content = line['content']
    if theType == 'scene':
        return '\n### %s\n' % content
    elif theType == 'cName':
        return '\n**%s**\n' % content
    elif theType == 'cLine':
        return '%s  ' % content
    else:
        return '\n*%s*\n' % content

def ProcessContent(href):
    content = ReadFile(os.path.join(root, href))
    def Match(pattern, theType):
        return [{'start': match.start(),
                 'content': match.group(1),
                 'type': theType}
                for match in pattern.finditer(content)]

    scenes = Match(scenePattern, 'scene')
    cNames = Match(cNamePattern, 'cName')
    cLines = Match(cLinePattern, 'cLine')
    sHints = Match(sHintPattern, 'sHint')

    lines = sorted(scenes + cNames + cLines + sHints, key=lambda x: x['start'])
    return [FormatContent(line) for line in lines]

allContents = ['\n'.join(ProcessContent(scene['href'])) for scene in indexScenes]


acts = [scene['actNo'] for scene in indexScenes]
actFlag = [True] + [acts[i] != acts[i-1] for i in range(1,len(acts))]
for index,flag in enumerate(actFlag):
    if flag:
        allContents[index] = ('\n## ACT %s\n' % acts[index]) + allContents[index]
                   

allContents[0] = ('# %s\n' % play) + allContents[0]

result = '\n'.join(allContents).replace('\n\n\n','\n\n')
with open('result.md','w') as f:
    f.write(result)
