import sys
import os
import getopt
import random
import commands
import multiprocessing
def getAttriValueFromSeqName(seqname,attribute):
    """get a specified attribute value from the sequence name."""
    attributeStart=seqname.find(attribute)
    if attributeStart==-1:
        return False
    else: 
        attributeEnd=attributeStart+len(attribute)
        valueStart=seqname.find("=",attributeEnd)+len("=")
        valueEnd=seqname.find(";",valueStart)
        if valueEnd>valueStart:
            value=seqname[valueStart:valueEnd].strip()
        else:
            value=seqname[valueStart:].strip()
        if len(value)==0:
            return False
        else:
            return value

def extractMode(inputlist):
    maxfrequence=0
    mode=""
    for one in list(set(inputlist)):
        frequence=inputlist.count(one)
        if frequence>maxfrequence:
            mode=one
            maxfrequence=frequence
        else:
            continue
    return mode

def file2dict(inputfile):
    OTUDict={}
    for line in open(inputfile,'r'):
        lineList=line.strip().split()
        identify=float(lineList[2])
        name=lineList[0]
        annotated=lineList[1].split(';')[6]
        if OTUDict.get(name,False):
            OTUDict[name].append([identify,annotated])
        else:
            OTUDict[name]=[[identify,annotated]]
    return OTUDict

def extractMax(filedict):
    AnnotatedDict={}
    for OTU in filedict:
        maxid=99
        namelist=[]
        while True:
            for align in filedict[OTU]:
                identify=align[0]
                name=align[1]
                if identify>=maxid:
                    namelist.append(name)
                else:
                    continue
            if len(namelist)==0:
                maxid-=1
            else:
                annotated=extractMode(namelist)
                AnnotatedDict[OTU]=annotated
                break
    return AnnotatedDict

if __name__=="__main__":
    usage="""usage: python annotated.py --input <inputfile>

 --input/-i	the alignment result from usearch
 --help/-h	help
"""
    opts,arg=getopt.getopt(sys.argv[1:],"i:h",["input=",'help'])

    parameters=[a[0] for a in opts]
    if '-h' in parameters or '--help' in parameters:
        print usage
        sys.exit(1)
    if len(parameters)==0:
        print usage
        sys.exit(1)
    if '-i' not in parameters and '--input' not in parameters:
        print "***Error, an input file is requred.***\n"
        print usage
        sys.exit(1)

    for i,a in opts:
        if i in ('-i','--input'):
           inputfile=a
    output=os.path.splitext(a)[0]+".annotated"
    fout=open(output,'w')
    filedict=file2dict(inputfile)
    otudict=extractMax(filedict)
    for otu in otudict:
        fout.write("%s\t%s\n"%(otu,otudict[otu]))
    print "\noutput file name:"
    print os.path.basename(output)
    print ""
