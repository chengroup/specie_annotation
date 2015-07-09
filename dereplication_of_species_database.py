import os,sys,getopt
import multiprocessing

def fasta2DictDere(input_fasta,seqdict):
    """ read a fasta into dictionary and remove the full equal (sequence and length)"""
    finput=open(input_fasta,"r")
    first=True
    for line in finput:
        if line.startswith(">"):
            if first:
                first=False
            else:
                name_list=seqdict.get(sequence,False)
                if name_list:
                    seqdict[sequence].append(name)
                else:
                    seqdict[sequence]=[name]
            #new circle
            name=line.strip().lstrip(">")
            sequence=""
        else:
            line=line.strip()
            sequence+=line
    #the last
    name_list=seqdict.get(sequence,False)
    if name_list:
        seqdict[sequence].append(name)
    else:
        seqdict[sequence]=[name]
    return seqdict

def createLenDict(seqDict):
    """create a dictionary and sequence length as the key, a list that consisted by sequence and sequence name as value"""
    lenDict={}
    for sequence in seqDict:
        length=len(sequence)
        if lenDict.get(length,False):
            lenDict[length][sequence]=seqDict[sequence]
        else:
            lenDict[length]={sequence:seqDict[sequence]}
    return lenDict

def removesub(lenDict,Qlength):
    removeSeqList=[]
    targetList=[]
    queryList=lenDict[Qlength].keys()
    for length in lenDict:
        if length>Qlength:
            targetList+=lenDict[length]
    for query in queryList:
        for target in targetList:
            if query in target:
                removeSeqList.append(query)
    return removeSeqList

def derepmulti(filepath,processors):
    totalDict={}
    totalDict=fasta2DictDere(filepath,totalDict)
    lenDict=createLenDict(totalDict)
    lenNum=len(lenDict)
    lenList=lenDict.keys()
    lenList.sort()

    pool=multiprocessing.Pool(processes=processors)
    removeList=[]
    resultList=[]
    for length in lenList:
        result=pool.apply_async(removesub,(lenDict,length))
        resultList.append(result)
    pool.close()
    pool.join()
    for res in resultList:
        result=res.get()
        removeList+=result 
    for rseq in list(set(removeList)):
        del totalDict[rseq]
    return totalDict
if __name__=="__main__":
    usage="""usage: python dereplication.py 

    --input/-i   the database sequence in fasta format
    --processors/-p   processors
    """
    opts,arg=getopt.getopt(sys.argv[1:],"i:p:",['input=','processors='],)
    parameters=[a[0] for a in opts]
    if len(parameters)<=0:
        print usage
        sys.exit(1)
    for i,a in opts:
        if i in ("--input","-i"):
            if not os.path.isfile(a):
                print "%s is not found."%(a)
                sys.exit(1)
            fastafile=a
        if i in ("--processors","-p"):
            processors=int(a)

    outfasta=os.path.splitext(fastafile)[0]+"_derep"+os.path.splitext(fastafile)[1]
    fout=open(outfasta,'w')
    
    resultDict=derepmulti(fastafile,processors)
    for seq in resultDict:
        seqname=resultDict[seq][0]
        fout.write(">%s\n%s\n"%(seqname,seq))

    print "\noutput file:\n"
    print os.path.basename(outfasta)
