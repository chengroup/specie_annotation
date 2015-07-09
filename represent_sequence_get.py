import sys
import os
import getopt

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

def fasta2dict(input_fasta):
    """convert a fasta type file into a python dictionary. sequence name as key, sequence as value."""
    if os.path.isfile(input_fasta):
        pass
    else:
        print "Error,%s not found."%(input_fasta)
        sys.exit(1)
    fasta_dict={}
    finput=open(input_fasta,"r")
    for line in finput:
        if line.startswith(">"):
            sequence_name=line.strip().lstrip(">")
            fasta_dict[sequence_name]=""
        else:
            sequence=line.strip()
            fasta_dict[sequence_name]+=sequence
    return fasta_dict

def orderbySSAndAband(NameList):
    sizeVList=[]
    abundVList=[]
    valueDict={}
    value_nameDict={}
    reList=[]
    for Name in NameList:
        size=int(getAttriValueFromSeqName(Name,"sampleSize"))
        abundance=int(getAttriValueFromSeqName(Name,"abundance"))
        valueDict[Name]=[size,abundance]
        abundVList.append(abundance)
    abMax=max(abundVList)+1 #as weight value of sampleSize
    for name in valueDict:
        size=valueDict[name][0]
        abundance=valueDict[name][1]
        key=size*abMax+abundance
        if value_nameDict.get(key,False):
            value_nameDict[key].append(name)
        else:
            value_nameDict[key]=[name]

    valueList=value_nameDict.keys()
    valueList.sort()
    for value in valueList:
        reList+=value_nameDict[value]
    return reList

if __name__=="__main__":
    usage="""
 --otulist/-l	OTU list which outputted by bioOTU (taxonomy_guided_OTU.list)
 --fasta/-f	the fasta which should containing all sequences of OTUs, it always gnerated by bioOTU (taxonomy_guided_OTU.fa)
 --number/-n	the maximum number of representive sequece to get, default:1
 --sample_size/-s	the minimum sample sizede of sequence as represent, fault:1
"""
    number=1
    sampleSize=1
    opts,arg=getopt.getopt(sys.argv[1:],"l:f:n:s:h",['outlist=','fasta=','number=','sample_size=','help'],)

    parameters=[a[0] for a in opts]
    if '-h' in parameters or '--help' in parameters:
        print usage
        sys.exit(1)
    if len(parameters)==0:
        print usage
        sys.exit(1)
    if '-l' not in parameters and '--outlist' not in parameters:
        print "***Error, an OTU list file as input is requred.***\n"
        print usage
        sys.exit(1)

    if '-f' not in parameters and '--fasta' not in parameters:
        print "***Error, a fasta file as input is requred..***\n"
        print usage
        sys.exit(1)

    for i,a in opts:
        if i in ("--otulist","-l"):
            if not os.path.isfile(a):
                print "%s is not found."%(a)
                sys.exit(1)
            OTUlist=a
        if i in ("--fasta","-f"):
            if not os.path.isfile(a):
                print "%s is not found."%(a)
                sys.exit(1)
            fasta=a
        if i in ("--number","-n"):
            number=int(a)
        if i in ("--sample_size","-s"):
            sampleSize=int(a)
    output=os.path.splitext(OTUlist)[0]+"_represent"+os.path.splitext(OTUlist)[1]
    fout=open(output,'w')
    faDict=fasta2dict(fasta)
    for line in open(OTUlist,'r'):
        lineList=line.strip().split()
        OTUname=lineList[0]
        uniqueSeqList=lineList[1].split(',')
        OTUrepList=[]
        for uniqName in uniqueSeqList:
            if "*" in uniqName:
                seqName=uniqName.strip('*')
                OTUrepList.append(seqName)
        OTUrepListSort=orderbySSAndAband(OTUrepList)
        OTUrepListSort.reverse()
        if len(OTUrepListSort)<=number:
            for name in OTUrepListSort:
                if int(getAttriValueFromSeqName(name,"sampleSize"))<sampleSize:
                    continue
                sequence=faDict.get(name,False)
                if sequence:
                    fout.write(">%sOTUname=%s;\n%s\n"%(name,OTUname,sequence))
                else:
                    print "warning, %s is not found in %s"%(uniqName,fasta)
        else:
            for name in OTUrepListSort[:number]:
                if int(getAttriValueFromSeqName(name,"sampleSize"))<sampleSize:
                    continue
                sequence=faDict.get(name,False)
                if sequence:
                    fout.write(">%sOTUname=%s;\n%s\n"%(name,OTUname,sequence))
                else:
                    print "warning, %s is not found in %s"%(uniqName,fasta)
    print "\noutput file:\n"
    print os.path.basename(output)
