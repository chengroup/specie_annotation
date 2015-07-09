import os,sys,getopt

usage="""usage: reference_filter.py --fasta <fastafile>
 --fasta/-f	the database file in fasta format
 --help/-f	help
    """
opts,arg=getopt.getopt(sys.argv[1:],"f:h",['fasta=','help'],)
parameters=[a[0] for a in opts]
if len(parameters)==0:
    print usage
    sys.exit(1)

for i,a in opts:
    if i in ('-f','--fasta'):
        alignmentFile=a
outFile=os.path.splitext(alignmentFile)[0]+"_sp.fa"
fout=open(outFile,'w')
k=False
n=0
for line in open(alignmentFile,'r'):
    if line.startswith('>'):
        lineList=line.split(';')
        if '_sp.' not in lineList[6]:
            k=True
            fout.write(line)
        else:
            n+=1
            k=False
    elif k:
        fout.write(line)
    else:
        pass
print "\noutput file name:"
print os.path.basename(outFile)
print ''
