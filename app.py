import sys
import record_dataset
    
def main(args):
    title,user,imDir,outFolder = ('test_record','','./_images/','./records/')
    for i, arg in enumerate(args):
        if(arg == '-t'):
            title = args[i+1]
        elif(arg=='-u'): #user
            user = args[i+1]
        elif(arg=='-d'): #images dir
            imDir = args[i+1]
        elif(arg=='-o'):
            outFolder = args[i+1]
    return title,user, imDir, outFolder
if __name__ == "__main__":
    title,user,imDir,outFolder = main(sys.argv[1:])
    record_dataset.main(title, user)