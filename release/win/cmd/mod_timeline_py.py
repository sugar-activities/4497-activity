f = open("..\\..\\..\\timeline.py", "r")
text = f.read()
lines = text.split("\n")
for line in lines:
    if line[0:16] == "sys.path.insert(":
        print "exepath = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))"
        print "sys.path.insert(0, exepath)"
    else:
        print line
f.close()


