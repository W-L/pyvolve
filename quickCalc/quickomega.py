###### Rewritten for my simulator.

import os
import re
import sys
import subprocess
import numpy as np

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import *

date='3.7.14'
home='/Users/sjspielman/' # Change if on MacMini or MacBook
sys.path.append(home+"Omega_MutSel/Simulator/src/")

from misc import *
from newick import *
from stateFreqs import *
from matrixBuilder import *
from evolver import *


#################################################################################################################################
def ensure_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    return 0
#################################################################################################################################

#################################################################################################################################
def callSim(home, outfile, kappa, omegas, numPart, partLen):

	molecules = Genetics()
	
	print "reading tree"
	my_tree, flag_list  = readTree(file=home+"Omega_MutSel/Simulator/trees/100.tre", show=False) # set True to print out the tree
	
	print "collecting state frequencies"
	fgen = EqualFreqs(by='codon', alnfile=home+'Omega_MutSel/Simulator/flu_ish.fasta', save='stateFreqs.txt')
	commonFreqs = fgen.getCodonFreqs()
	fgen.save2file()

	## temporary code for constructing multiple GY94 models. Will formalize in the future.
	partitions = []
	print "constructing models for", numPart, "partitions"
	for i in range(numPart):
		# Define model object and its parameters. Build model matrix. Add tuple (partition length, model) to partitions list
		model = misc.Model()
		model.params = { "kappa": kappa, "omega": omegas[i], "stateFreqs": commonFreqs }
		m = GY94(model)
		model.Q = m.buildQ()
		partitions.append( (partLen, model) )

	print "evolving"
	myEvolver = StaticEvolver(partitions = partitions, tree = my_tree, outfile = seqfile)
	myEvolver.sim_sub_tree(my_tree)
	myEvolver.writeSequences()
#################################################################################################################################

#################################################################################################################################
## For a given codon, returns a list of its synonymous changes and of its nonsynonymous changes, with only one nucleotide change permitted.
def findSynNonsyn(codon_raw):
	syn=[]
	nonsyn=[]
	codon=Seq(codon_raw, generic_dna)
	aa_source=str(codon.translate())
	for n in range(0,3):
		for nuc in ['A', 'C', 'T', 'G']:
			#Don't count the changes to the same nucleotide. upper as in upper case.
			if codon[n].upper()==nuc:
				continue
			target = codon[0:n]+nuc+codon[n+1:3]
			aa_target = str(target.translate())
			if aa_target=='*':	#disregard nonsense mutations
				continue
			if aa_source==aa_target:
				syn.append(str(target))
			elif aa_source != target:
				nonsyn.append(str(target))
	return(syn, nonsyn)
#################################################################################################################################


#################################################################################################################################
## Given F(i) and F(j), where F() is the frequency of the given codon in that column, return fix_(i->j).
def fix(fi, fj):
	return (np.log(fj) - np.log(fi)) / (1 - fi/fj)
#################################################################################################################################

#################################################################################################################################
### Given a source codon and target codon, return True if the change is nonsynonymous. probably not needed.
def isNonsyn(codon_source_raw, codon_target_raw):

	# Convert to biopython object so can use the translate() function
	codon_source = Seq(codon_source_raw, generic_dna)
	codon_target = Seq(codon_target_raw, generic_dna)

	if (codon_source.translate() == codon_target.translate()):
		return False
	else:
		return True
#################################################################################################################################



#################################################################################################################################
#################################################################################################################################	
# List of all codons. Note that the slist and nslist lists are also in this order.
codons=["AAA", "AAC", "AAG", "AAT", "ACA", "ACC", "ACG", "ACT", "AGA", "AGC", "AGG", "AGT", "ATA", "ATC", "ATG", "ATT", "CAA", "CAC", "CAG", "CAT", "CCA", "CCC", "CCG", "CCT", "CGA", "CGC", "CGG", "CGT", "CTA", "CTC", "CTG", "CTT", "GAA", "GAC", "GAG", "GAT", "GCA", "GCC", "GCG", "GCT", "GGA", "GGC", "GGG", "GGT", "GTA", "GTC", "GTG", "GTT", "TAC", "TAT", "TCA", "TCC", "TCG", "TCT", "TGC", "TGG", "TGT", "TTA", "TTC", "TTG", "TTT"]
slist=[['AAG'], ['AAT'], ['AAA'], ['AAC'], ['ACC', 'ACT', 'ACG'], ['ACA', 'ACT', 'ACG'], ['ACA', 'ACC', 'ACT'], ['ACA', 'ACC', 'ACG'], ['CGA', 'AGG'], ['AGT'], ['CGG', 'AGA'], ['AGC'], ['ATC', 'ATT'], ['ATA', 'ATT'], [], ['ATA', 'ATC'], ['CAG'], ['CAT'], ['CAA'], ['CAC'], ['CCC', 'CCT', 'CCG'], ['CCA', 'CCT', 'CCG'], ['CCA', 'CCC', 'CCT'], ['CCA', 'CCC', 'CCG'], ['AGA', 'CGC', 'CGT', 'CGG'], ['CGA', 'CGT', 'CGG'], ['AGG', 'CGA', 'CGC', 'CGT'], ['CGA', 'CGC', 'CGG'], ['TTA', 'CTC', 'CTT', 'CTG'], ['CTA', 'CTT', 'CTG'], ['TTG', 'CTA', 'CTC', 'CTT'], ['CTA', 'CTC', 'CTG'], ['GAG'], ['GAT'], ['GAA'], ['GAC'], ['GCC', 'GCT', 'GCG'], ['GCA', 'GCT', 'GCG'], ['GCA', 'GCC', 'GCT'], ['GCA', 'GCC', 'GCG'], ['GGC', 'GGT', 'GGG'], ['GGA', 'GGT', 'GGG'], ['GGA', 'GGC', 'GGT'], ['GGA', 'GGC', 'GGG'], ['GTC', 'GTT', 'GTG'], ['GTA', 'GTT', 'GTG'], ['GTA', 'GTC', 'GTT'], ['GTA', 'GTC', 'GTG'], ['TAT'], ['TAC'], ['TCC', 'TCT', 'TCG'], ['TCA', 'TCT', 'TCG'], ['TCA', 'TCC', 'TCT'], ['TCA', 'TCC', 'TCG'], ['TGT'], [], ['TGC'], ['CTA', 'TTG'], ['TTT'], ['CTG', 'TTA'], ['TTC']]
nslist = [['CAA', 'GAA', 'ACA', 'ATA', 'AGA', 'AAC', 'AAT'], ['CAC', 'TAC', 'GAC', 'ACC', 'ATC', 'AGC', 'AAA', 'AAG'], ['CAG', 'GAG', 'ACG', 'ATG', 'AGG', 'AAC', 'AAT'], ['CAT', 'TAT', 'GAT', 'ACT', 'ATT', 'AGT', 'AAA', 'AAG'], ['CCA', 'TCA', 'GCA', 'AAA', 'ATA', 'AGA'], ['CCC', 'TCC', 'GCC', 'AAC', 'ATC', 'AGC'], ['CCG', 'TCG', 'GCG', 'AAG', 'ATG', 'AGG'], ['CCT', 'TCT', 'GCT', 'AAT', 'ATT', 'AGT'], ['GGA', 'AAA', 'ACA', 'ATA', 'AGC', 'AGT'], ['CGC', 'TGC', 'GGC', 'AAC', 'ACC', 'ATC', 'AGA', 'AGG'], ['TGG', 'GGG', 'AAG', 'ACG', 'ATG', 'AGC', 'AGT'], ['CGT', 'TGT', 'GGT', 'AAT', 'ACT', 'ATT', 'AGA', 'AGG'], ['CTA', 'TTA', 'GTA', 'AAA', 'ACA', 'AGA', 'ATG'], ['CTC', 'TTC', 'GTC', 'AAC', 'ACC', 'AGC', 'ATG'], ['CTG', 'TTG', 'GTG', 'AAG', 'ACG', 'AGG', 'ATA', 'ATC', 'ATT'], ['CTT', 'TTT', 'GTT', 'AAT', 'ACT', 'AGT', 'ATG'], ['AAA', 'GAA', 'CCA', 'CTA', 'CGA', 'CAC', 'CAT'], ['AAC', 'TAC', 'GAC', 'CCC', 'CTC', 'CGC', 'CAA', 'CAG'], ['AAG', 'GAG', 'CCG', 'CTG', 'CGG', 'CAC', 'CAT'], ['AAT', 'TAT', 'GAT', 'CCT', 'CTT', 'CGT', 'CAA', 'CAG'], ['ACA', 'TCA', 'GCA', 'CAA', 'CTA', 'CGA'], ['ACC', 'TCC', 'GCC', 'CAC', 'CTC', 'CGC'], ['ACG', 'TCG', 'GCG', 'CAG', 'CTG', 'CGG'], ['ACT', 'TCT', 'GCT', 'CAT', 'CTT', 'CGT'], ['GGA', 'CAA', 'CCA', 'CTA'], ['AGC', 'TGC', 'GGC', 'CAC', 'CCC', 'CTC'], ['TGG', 'GGG', 'CAG', 'CCG', 'CTG'], ['AGT', 'TGT', 'GGT', 'CAT', 'CCT', 'CTT'], ['ATA', 'GTA', 'CAA', 'CCA', 'CGA'], ['ATC', 'TTC', 'GTC', 'CAC', 'CCC', 'CGC'], ['ATG', 'GTG', 'CAG', 'CCG', 'CGG'], ['ATT', 'TTT', 'GTT', 'CAT', 'CCT', 'CGT'], ['AAA', 'CAA', 'GCA', 'GTA', 'GGA', 'GAC', 'GAT'], ['AAC', 'CAC', 'TAC', 'GCC', 'GTC', 'GGC', 'GAA', 'GAG'], ['AAG', 'CAG', 'GCG', 'GTG', 'GGG', 'GAC', 'GAT'], ['AAT', 'CAT', 'TAT', 'GCT', 'GTT', 'GGT', 'GAA', 'GAG'], ['ACA', 'CCA', 'TCA', 'GAA', 'GTA', 'GGA'], ['ACC', 'CCC', 'TCC', 'GAC', 'GTC', 'GGC'], ['ACG', 'CCG', 'TCG', 'GAG', 'GTG', 'GGG'], ['ACT', 'CCT', 'TCT', 'GAT', 'GTT', 'GGT'], ['AGA', 'CGA', 'GAA', 'GCA', 'GTA'], ['AGC', 'CGC', 'TGC', 'GAC', 'GCC', 'GTC'], ['AGG', 'CGG', 'TGG', 'GAG', 'GCG', 'GTG'], ['AGT', 'CGT', 'TGT', 'GAT', 'GCT', 'GTT'], ['ATA', 'CTA', 'TTA', 'GAA', 'GCA', 'GGA'], ['ATC', 'CTC', 'TTC', 'GAC', 'GCC', 'GGC'], ['ATG', 'CTG', 'TTG', 'GAG', 'GCG', 'GGG'], ['ATT', 'CTT', 'TTT', 'GAT', 'GCT', 'GGT'], ['AAC', 'CAC', 'GAC', 'TCC', 'TTC', 'TGC'], ['AAT', 'CAT', 'GAT', 'TCT', 'TTT', 'TGT'], ['ACA', 'CCA', 'GCA', 'TTA'], ['ACC', 'CCC', 'GCC', 'TAC', 'TTC', 'TGC'], ['ACG', 'CCG', 'GCG', 'TTG', 'TGG'], ['ACT', 'CCT', 'GCT', 'TAT', 'TTT', 'TGT'], ['AGC', 'CGC', 'GGC', 'TAC', 'TCC', 'TTC', 'TGG'], ['AGG', 'CGG', 'GGG', 'TCG', 'TTG', 'TGC', 'TGT'], ['AGT', 'CGT', 'GGT', 'TAT', 'TCT', 'TTT', 'TGG'], ['ATA', 'GTA', 'TCA', 'TTC', 'TTT'], ['ATC', 'CTC', 'GTC', 'TAC', 'TCC', 'TGC', 'TTA', 'TTG'], ['ATG', 'GTG', 'TCG', 'TGG', 'TTC', 'TTT'], ['ATT', 'CTT', 'GTT', 'TAT', 'TCT', 'TGT', 'TTA', 'TTG']]

######################## code to generate slist, nslist ################################
#slist=[] #Contains syn codons for the given index. Indices as in list, codons
#nslist=[] #Contains nonsyn codons for the given index. Indices as in list, codons
for codon in codons:
	(syn, nonsyn) = findSynNonsyn(codon)
	slist.append(syn)
	nslist.append(nonsyn)

#################################################################################################################################
#################################################################################################################################	


## Conduct 100 simulations to confirm that the correlation between ML dN/dS and our derived dN/dS really exists

zero=1e-10


results_dir=home+'Dropbox/MutSelProject/quickCalc/SimSeqs_'+date+'_pos/'
numPart = 10
partLen = 20
omegas = np.linspace(1.2, 3.0, num=numPart, dtype=float)
kappa = 4.5
ensure_dir(results_dir)

simulate = home+'Omega_MutSel/Simulator/main.py'

for n in range(100):
	print n
	
	seqfile = results_dir+"seqs"+str(n)+".fasta"
	
	# Simulate
	callSim(home, seqfile, kappa, omegas, numPart, partLen)
		
	# Calculate derived dN/dS from the alignment. Save those values to rates_codonfreq(n).txt
	# aln will contain the alignment. 
	aln=[] #list of lists wherein each nested list is a row
	aln_raw = list(SeqIO.parse(seqfile, 'fasta'))
	for record in aln_raw:
		aln.append(str(record.seq))
	
	alnlen=len(aln[0])
	numseq=len(aln)

	ratename = results_dir+'rates_codonfreq'+str(n)+'.txt'
	ratefile=open(ratename, 'w')
	ratefile.write("position\tomega_simple\tomega_count\n")
	
	position=1
	for col in range(0,alnlen,3):
	
		kN=0 #dN numerator
		nN_simple=0 #dN denominator. Does not consider number of nonsyn options
		nN_count=0 #dN denominator. DOES consider number of nonsyn options.
		
		fix_sum=0
		
		codonFreq=np.zeros(len(codons)) # will contain frequencies for all codons in a given column
		nonZero=[] # will contain the nonzero indices for codonFreq
		
		#Find codon frequencies
		for row in range(numseq):
			codon=aln[row][col:col+3]
			codonFreq[codons.index(codon)] += 1	
		codonFreq/=float(numseq)
		

		# Fill nonZero with codonFreq indices whose values are not 0
		for i in range(len(codonFreq)):
			if codonFreq[i] > zero:
				nonZero.append(i)
	
		# Calculations
		for i in nonZero:
			fix_sum=0
			
			### Nonsynonymous.  and BH methods here
			for nscodon in nslist[i]:
				nscodon_freq = codonFreq[codons.index(nscodon)]
				if nscodon_freq==0 or codonFreq[i]==nscodon_freq:
					continue
				else:
					fix_sum += fix(float(codonFreq[i]), float(nscodon_freq))					
					nN_simple += codonFreq[i]
					nN_count += codonFreq[i] * len(nslist[i])
			kN += fix_sum*codonFreq[i]

		# Final dN/dS
		if kN < zero:
			dNdS_simple = 0
			dNdS_count = 0
		else:
			dNdS_simple=kN/nN_simple
			dNdS_count=kN/nN_count
		
		ratefile.write(str(position)+'\t'+str(dNdS_simple)+'\t'+str(dNdS_count)+'\n')
		position+=1
			
	ratefile.close()
