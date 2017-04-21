f = open("..\\..\\..\\timelinelib\\config\\paths.py", "r")
text = f.read()
lines = text.split("\n")
for line in lines:
    if line[0:7] == "_ROOT =":
        print "import sys"
        print "_ROOT = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))"
    else:
        print line
f.close()

