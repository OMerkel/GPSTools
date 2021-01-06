import sys
if len(sys.argv) == 1:
  filepath = '../gpx/W1-Waschenbach-Neutsch-Perlenkette.gpx'
else:
  filepath = sys.argv[1]
with open(filepath) as fp:
  line = fp.readline()
  cnt = 0
  while line:
    if line.strip().startswith("<time"):
      cnt += 1
    elif line.strip().startswith("<ele"):
      cnt += 1
    else:
      print(line.replace('\t', '  ').strip('\n'))
    line = fp.readline()
