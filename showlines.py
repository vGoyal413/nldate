lines = open('nldate/_parse.py').readlines() 
[print(i+1, repr(l)) for i, l in enumerate(lines)] 
