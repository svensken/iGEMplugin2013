""" Sep 2013: Kenny Kostenbader
      PyMOL plugin for Rutgers iGEM 2013 winning-team awesomeness
"""

### IMPORTANT ATTRIBUTION NOTE: This script was adapted from Hongbo Zhu's
### msms pymol plugin. Thank you, Hongbo! His copyright notice is:

# Copyright Notice
# ================
#
# The PyMOL Plugin source code in this file is copyrighted, but you can
# freely use and copy it as long as you don't change or remove any of
# the copyright notices.
#
# ----------------------------------------------------------------------
#               This PyMOL Plugin is Copyright (C) 2010 by
#                 Hongbo Zhu <macrozhu at gmail dot com>
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name(s) of the author(s) not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# THE AUTHOR(S) DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.  IN
# NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------



import os
import sys, platform, subprocess, tempfile
import time
import difflib

import tkSimpleDialog
import tkMessageBox
import tkFileDialog
import tkColorChooser

import Tkinter

# pymol
from pymol import cmd
from pymol.cgo import *
# tkinter
import Pmw
# links
#import webbrowser


VERBOSE = True


def __init__(self):
    """ rutgers iGEM oligo-purchasing plugin for PyMol
    """
    self.menuBar.addmenuitem('Plugin', 'command',
                             'oligos', label = 'oligos',
                             command = lambda s=self : OligoPurchase(s))


class OligoPurchase:

    def __init__(self, app):
        self.parent = app.root
        self.dialog = Pmw.Dialog(self.parent,
                                 buttons = ('Buy Gene', 'Buy Mutational Oligo', 'Exit'),
                                 title = 'Order your Oligos',
                                 command = self.execute)
        Pmw.setbusycursorattributes(self.dialog.component('hull'))

        # parameters
        self.pymol_sel_gene = Tkinter.StringVar()
        self.dnaseq_fn = Tkinter.StringVar()
        self.seqpos = Tkinter.StringVar()
        self.new_aa = Tkinter.StringVar()

        self.plasmidify = Tkinter.BooleanVar()
        self.plasmidify.set(True) # by default, plasmidify


        w = Tkinter.Label(self.dialog.interior(),
                          text = '\nOligo-ordering plugin for PyMOL\nRutgers iGEM, 2013.\n\nBuy your oligos right off the screen.',
                          background = 'black', foreground = 'green'
                          )
        w.pack(expand = 1, fill = 'both', padx = 10, pady = 5)

        # make a few tabs within the dialog
        self.notebook = Pmw.NoteBook(self.dialog.interior())
        self.notebook.pack(fill = 'both', expand=1, padx=10, pady=10)


        ############################
        # Tab : Regular Sequence Tab
        ############################
        page = self.notebook.add('Gene Sequence')
        self.notebook.tab('Gene Sequence').focus_set()
        group_seq = Tkinter.LabelFrame(page, text = 'Order simple gene sequence')
        group_seq.pack(fill='both', expand=True, padx=10, pady=5)

        pymol_sel_ent_gene = Pmw.EntryField(group_seq,
                                           label_text='PyMOL selection:',
                                           labelpos='wn',
                                           entry_textvariable=self.pymol_sel_gene
                                           )
        plasmid_box = Tkinter.Checkbutton(group_seq,
                                           text='plasmidify (gene in pSB1C3, ready for iGEM biobricks submission)',
                                           variable=self.plasmidify,
                                           onvalue=True, offvalue=False)

        # arrange widgets using grid
        pymol_sel_ent_gene.grid(sticky='we', row=0, column=0,
                           columnspan=2, padx=5, pady=5)
        plasmid_box.grid(sticky='w', row=1, column=0,
                         columnspan=2, padx=1, pady=1)
        group_seq.columnconfigure(0, weight=9)
        group_seq.columnconfigure(1, weight=1)

        #########################
        # Tab : Mutational Oligos
        #########################
        page = self.notebook.add('Mutational Oligos')
        group_mut = Tkinter.LabelFrame(page, text = 'Craft Mutational Oligos to order')
        group_mut.pack(fill='both', expand=True, padx=10, pady=5)

        dnaseq_ent = Pmw.EntryField(group_mut,
                                    label_text = 'Original DNA seq (FASTA file):', labelpos='wn',
                                    entry_textvariable=self.dnaseq_fn)
        dnaseq_but = Tkinter.Button(group_mut, text = 'Browse...',
                                    command = self.getFastaFile)
        seqpos_ent = Pmw.EntryField(group_mut,
                                    label_text='Sequence Position: (eg 54)',
                                    labelpos='wn',
                                    entry_textvariable=self.seqpos
                                    )
        new_aa_ent = Pmw.EntryField(group_mut,
                                    label_text='New amino acid: (eg H)',
                                    labelpos='wn',
                                    entry_textvariable=self.new_aa
                                    )

        # arrange widgets using grid
        dnaseq_ent.grid(sticky='we', row=0, column=0, padx=5, pady=5)
        dnaseq_but.grid(sticky='we', row=0, column=1, padx=5, pady=5)
        seqpos_ent.grid(sticky='we', row=1, column=0,
                        columnspan=2, padx=1, pady=1)
        new_aa_ent.grid(sticky='we', row=2, column=0,
                        columnspan=2, padx=1, pady=1)
        group_mut.columnconfigure(0, weight=9)
        group_mut.columnconfigure(1, weight=1)


        #################
        # Tab : About Tab
        #################
        page = self.notebook.add('About')
        group_about = Tkinter.LabelFrame(page, text = 'About Oligo-ordering Plugin for PyMOL')
        group_about.grid(sticky='we', row=0,column=0,padx=10,pady=5)
        about_plugin = """ This plugin provides a GUI for easily placing useful oligo orders in PyMOL.
Created by Rutgers iGEM team 2013, Rutgers University, NJ.

"""
        label_about = Tkinter.Label(group_about,text=about_plugin)
        label_about.grid(sticky='we', row=0, column=0, padx=5, pady=10)


        self.notebook.setnaturalsize()

        return


    def getFastaFile(self):
        file_name = tkFileDialog.askopenfilename(
            title='DNA Sequence File', initialdir='',
            filetypes=[('fasta files', '*.fasta'), ('all files', '*')],
            parent=self.parent)
        self.dnaseq_fn.set(file_name)

    def codon_optimization(self, aaseq):
        ## super crude codon optimization :)
        dnaseq = []
        for letter in aaseq:
            if letter == 'A':
                letter = 'GCG'
            elif letter == 'R':
                letter = 'AGG'
            elif letter == 'N':
                letter = 'AAT'
            elif letter == 'D':
                letter = 'GAT'
            elif letter == 'C':
                letter = 'TGT'
            elif letter == 'E':
                letter = 'GAG'
            elif letter == 'Q':
                letter = 'CAG'
            elif letter == 'G':
                letter = 'GGG'
            elif letter == 'H':
                letter = 'CAT'
            elif letter == 'I':
                letter = 'ATA'
            elif letter == 'L':
                letter = 'TTG'
            elif letter == 'K':
                letter = 'AAG'
            elif letter == 'M':
                letter = 'ATG'
            elif letter == 'F':
                letter = 'TTT'
            elif letter == 'P':
                letter = 'CCG'
            elif letter == 'S':
                letter = 'AGT'
            elif letter == 'T':
                letter = 'ACG'
            elif letter == 'W':
                letter = 'TGG'
            elif letter == 'Y':
                letter = 'TAT'
            elif letter == 'V':
                letter = 'GTG'
            if letter not in '\n':
                dnaseq.append(letter)
        dnaseq = ''.join(dnaseq)
        return dnaseq

    def derive_sequence_from_selection(self, pymol_selection, plasmid):
        _handle, temp_fasta_path = tempfile.mkstemp(suffix=".fasta")
        cmd.save( temp_fasta_path, pymol_selection )
        with open(temp_fasta_path,'r') as fastafile:
            fastafile = fastafile.readlines()
            aaseq = ''.join( fastafile[1:] ) # all lines except title line
        os.remove(temp_fasta_path)

        dnaseq = self.codon_optimization(aaseq)
        ## TODO: important! last "A" base is outside reading frame O_o
        print "with plasmid!"
        print dnaseq
        if not plasmid:
            print "without plasmid! (includes insert prefix and suffix)"
            dnaseq = "GTTTCTTCGAATTCGCGGCCGCTTCTAGAG"+dnaseq+"GTTTCTTCCTGCAGCGGCCGCTACTAGTATTATTA"
            print dnaseq
        return dnaseq

    def show_how_NOPLASMID(self, local_dna_fastafile):
        ## TODO: change URL to GeneArt
        gene_insert_howto = """
1) Copy the DNA sequence from:

""" + os.path.abspath( local_dna_fastafile ) + """

2) Please visit:
http://www.idtdna.com/order/OrderEntry.aspx?type=dna&qs=1

3) Paste the sequence into the textbox and order your oligo!
"""
        tkMessageBox.showinfo(title='Gene without Plasmid - Instructions', message=gene_insert_howto)

    def show_how_YESPLASMID(self, local_dna_fastafile):
        gene_plasmid_howto = """
1) Copy the DNA sequence from:

""" + os.path.abspath( local_dna_fastafile ) + """

2) Please visit:
https://www.genscript.com/ssl-bin/quote_gene_synthesis

3) Prepare the custom biobrick-compatible pSB1C3 plasmid as per instructions

4) Paste the DNA sequence into the textbox and order your plasmid!
"""
        tkMessageBox.showinfo(title='Gene with Plasmid - Instructions', message=gene_plasmid_howto)

    ### this function is not necessary with FASTA input. 
    ### if we switch back to directly pasting dnaseq into text field, this function will be good to have
    def gene_parse(self, gene_input):
        dna_string = ''.join( [letter.upper() for letter in gene_input if letter.upper() in ['A','C', 'G','T'] ] ) # DNA letters
        non_dna_string = ''.join( [letter.upper() for letter in gene_input if letter.upper() not in ['A','C', 'G','T'] ] ) # non-DNA letters
        if non_dna_string:
            print "psyyyych. gimme DNA only"
            return False
        
        if dna_string and not non_dna_string:
            return dna_string

    def derive_sequence_from_fastafile(self, fastafile):
        with open(fastafile,'r') as orig_dna:
            orig_dna = orig_dna.readlines()
            orig_dna = ''.join(orig_dna[1:]).replace('\n','')
        return orig_dna

    ## TODO: very important: convert pose-numbering to pdb-numbering
    def gimme_mutational_oligo( self, dnaseq, seqpos, newaa ):
        clip_before, clip_after = (int(seqpos)-1)*3, int(seqpos)*3
        orig_codon = dnaseq[ clip_before : clip_after ]
        potential_codons = {
            'A':['GCG','GCA','GCT','GCC'],
            'R':['AGG','AGA','CGG','CGA','CGT','CGC'],
            'N':['AAT','AAC'],
            'D':['GAT','GAC'],
            'C':['TGT','TGC'],
            'E':['GAG','GAA'],
            'Q':['CAG','CAA'],
            'G':['GGG','GGA','GGT','GGC'],
            'H':['CAT','CAC'],
            'I':['ATA','ATT','ATC'],
            'L':['TTG','TTA','CTG','CTA','CTT','CTC'],
            'K':['AAG','AAA'],
            'M':['ATG'],
            'F':['TTT','TTC'],
            'P':['CCG','CCA','CCT','CCC'],
            'S':['AGT','AGC','TCG','TCA','TCT','TCC'],
            'T':['ACG','ACA','ACT','ACC'],
            'W':['TGG'],
            'Y':['TAT','TAC'],
            'V':['GTG','GTA','GTT','GTC']
            }
        new_codon = difflib.get_close_matches( orig_codon, potential_codons[ newaa ], 1 ) # only return best
        if not new_codon: # nothing even close :P
            new_codon = [ potential_codons[ newaa ][0] ]
        # return oligo, which extends 15 bases in each direction (terminal mutations are extremely rare... unless... His-tag?)
        
        oligo_to_order = dnaseq[ clip_before-15 : clip_before ] + new_codon[0] + dnaseq[ clip_after : clip_after+15 ]
        print oligo_to_order
        return oligo_to_order

    def show_how_MUTATION(self, local_dna_fastafile):
        mut_oligo_howto = """
1) Copy the DNA sequence from:

""" + os.path.abspath( local_dna_fastafile ) + """

2) Please visit:
http://www.idtdna.com/order/OrderEntry.aspx?type=dna&qs=1

3) Paste the DNA sequence into the textbox and order your plasmid!
"""
        tkMessageBox.showinfo(title='Mutational Oligo - Instructions', message=mut_oligo_howto)

    def execute(self, command):
        """ Run the command represented by the botton clicked by user.
        """
        if command == 'OK':
            print 'cool'

        elif command == 'Buy Gene':
            protein_sel = self.pymol_sel_gene.get()

            ## make sure text exists
            if not protein_sel:
                print "no protein?"
                return False
            else:
                if not self.plasmidify.get():
                    gene_insert_string = self.derive_sequence_from_selection(protein_sel,plasmid=False)
                else:
                    gene_insert_string = self.derive_sequence_from_selection(protein_sel,plasmid=True)
                if not gene_insert_string:
                    gene_insert_string = "[error...hmmm]"
                local_dna_fastafile = protein_sel+".iGEMplugin.DNA.gene.fasta"
                with open(local_dna_fastafile,'w') as dnafastafile:
                    dnafastafile.write( ">"+protein_sel+"\n"+gene_insert_string )
                if not self.plasmidify.get():
                    self.show_how_NOPLASMID(local_dna_fastafile)
                else:
                    self.show_how_YESPLASMID(local_dna_fastafile)

        elif command == 'Buy Mutational Oligo':
            # original DNA sequence
            fastafile = self.dnaseq_fn.get()

            ## make sure there's input
            if not fastafile:
                print "psyyyych. gimme a file."
                return False
            else:
                dnaseq = self.derive_sequence_from_fastafile( fastafile )
                oligoseq = self.gimme_mutational_oligo( dnaseq, self.seqpos.get(), self.new_aa.get() )
                # just differentiate file by time made...
                local_dna_fastafile = time.strftime("%H_%M_%S", time.gmtime())+".iGEMplugin.DNA.mutation.fasta"
                with open(local_dna_fastafile,'w') as dnafastafile:
                    dnafastafile.write( ">mutation\n"+oligoseq )
                self.show_how_MUTATION(local_dna_fastafile)

        elif command == 'Display Vertices':
            if len(self.msp.vert_coords) == 0:
                err_msg = 'Please execute MSMS first.'
                print 'ERROR: %s' % (err_msg,)
                tkMessageBox.showinfo(title='ERROR', message=err_msg)

            else:
                print 'Vertex sphere radius =', self.vert_rad.get()
                print 'Normal vector length =', self.norm_len.get()
                print 'Vertex color = (%.2f, %.2f, %.2f)' % \
                      (self.vert_col_R/255.0, self.vert_col_G/255.0, self.vert_col_B/255.0)
                print 'Normal vector color = (%.2f, %.2f, %.2f)' % \
                      (self.norm_col_R/255.0, self.norm_col_G/255.0, self.norm_col_B/255.0)
                self.msp.displayMsmsSurfVert(r=self.vert_rad.get(),
                                             norm_len=self.norm_len.get(),
                                             vert_cgo_color=(self.vert_col_R/255.0,
                                                             self.vert_col_G/255.0,
                                                             self.vert_col_B/255.0),
                                             norm_cgo_color=(self.norm_col_R/255.0,
                                                             self.norm_col_G/255.0,
                                                             self.norm_col_B/255.0)
                                             )
                if self.allcpn:
                    for i in xrange(len(self.cpn_msp_list)):
                        self.cpn_msp_list[i].displayMsmsSurfVert(
                            r=self.vert_rad.get(),
                            norm_len=self.norm_len.get(),
                            vert_cgo_color= (self.vert_col_R/255.0,
                                             self.vert_col_G/255.0,
                                             self.vert_col_B/255.0),
                            norm_cgo_color= (self.norm_col_R/255.0,
                                             self.norm_col_G/255.0,
                                             self.norm_col_B/255.0),
                            vert_cgo_name='msms_surf_vert_%d' % (i+1),
                            norm_cgo_name='msms_surf_nrom_%d' % (i+1)
                            )

        elif command == 'Exit':
            print 'Exiting oligo-ordering Plugin ...'
            if __name__ == '__main__':
                self.parent.destroy()
            else:
                self.dialog.withdraw()
            print 'Done.'
        else:
            print 'Exiting oligo-ordering Plugin ...'
            self.dialog.withdraw()
            print 'Done.'


    def quit(self):
        self.dialog.destroy()


