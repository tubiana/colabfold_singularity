import sys
import argparse
from pathlib import Path


def parse_arg():
    parser = argparse.ArgumentParser(description='Convert TXT sequence file in format .')
    parser.add_argument('-f', required=True, help='Input sequence file in format HEADER\tXXXXXXXX*', )
    parser.add_argument('-o', default=None, help='Output file')


    args = vars(parser.parse_args())

    return args




def read_and_format(inputFile):

    with open(inputFile,'r') as txtfile:
        lines = txtfile.readlines()
        
    sequences = []
    for seq in lines:
        sequences.append(seq.strip()[:-1].split('\t'))
    return sequences

def write_fasta(sequences, output):
    with open(output, 'w') as out:
        for seq in sequences:
            out.write(f">{seq[0]}\n")
            out.write(f"{seq[1]}\n")
    



if __name__ == '__main__':
    args = parse_arg()
    txtfile = args['f']
    output = args['o']
    if output == None:
        output = txtfile.replace(".txt",'.fasta')
    sequences=read_and_format(txtfile)
    write_fasta(sequences, output)



