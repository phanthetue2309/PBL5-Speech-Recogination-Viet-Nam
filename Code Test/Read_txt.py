with open('file.txt') as f:
    data = []
    one_line = ''
    for line in f:   
        line = line.replace('[', '')
        line = line.replace(']', '')
        one_line += line
        
    data = [float(item) for item in one_line.split()]    
    print(data)