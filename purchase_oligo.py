""" Sep 2013: Kenny Kostenbader
      PyMOL plugin for Rutgers iGEM 2013 winning-team awesomeness
"""

# Copyright Notice
# ================
#
# uhhh... no copyright.
# Code taken from MSMS plugin. Thanks, Hongbo Zhu.




import os
import sys, platform, subprocess
import time
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
        self.pymol_sel_mut = Tkinter.StringVar()
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

        pymol_sel_ent = Pmw.EntryField(group_mut,
                                       label_text='PyMOL selection:',
                                       labelpos='wn',
                                       entry_textvariable=self.pymol_sel_mut
                                       )
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
        pymol_sel_ent.grid(sticky='we', row=0, column=0,
                           columnspan=2, padx=5, pady=5)
        seqpos_ent.grid(sticky='we', row=1, column=0,
                        columnspan=2, padx=1, pady=1)
        new_aa_ent.grid(sticky='we', row=2, column=0,
                        columnspan=2, padx=1, pady=1)
        group_mut.columnconfigure(0, weight=9)
        group_mut.columnconfigure(1, weight=1)


        ######################
        # Tab : About Tab
        ######################
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


    def getPDBFile(self):
        file_name = tkFileDialog.askopenfilename(
            title='PDB File', initialdir='',
            filetypes=[('pdb files', '*.pdb *.ent'), ('all files', '*')],
            parent=self.parent)
        self.pdb_fn.set(file_name)

    def getMsmsBin(self):
        msms_bin_fname = tkFileDialog.askopenfilename(
            title='MSMS Binary', initialdir='',
            filetypes=[('all','*')], parent=self.parent)
        self.msms_bin.set(msms_bin_fname)

##     def getPdb2xyzrBin(self):
##         pdb2xyzr_bin_fname = tkFileDialog.askopenfilename(
##             title='pdb2xyzr Binary', initialdir='',
##             filetypes=[('all','*')], parent=self.parent)
##         self.pdb2xyzr_bin.set(pdb2xyzr_bin_fname)

    def getPdb2xyzrnBin(self):
        pdb2xyzrn_bin_fname = tkFileDialog.askopenfilename(
            title='pdb2xyzrn Binary', initialdir='',
            filetypes=[('all','*')], parent=self.parent)
        self.pdb2xyzrn_bin.set(pdb2xyzrn_bin_fname)

    def getTmpDir(self):
        tmp_dir = tkFileDialog.askdirectory()
        self.tmp_dir.set(tmp_dir)

    def getStrucPDBFname(self):
        """ get the PDB file name for the structure to work on
            if the structure is specified by a pymol selection, save it in the temp dir;
            if the structure is specified by a separate PDB file, use it.
        """
        pdb_fn = None
        sel = self.pymol_sel.get()

        if len(sel) > 0: # if any pymol selection is specified
            # save the pymol selection in the tmp dir
            all_sel_names = cmd.get_names('selections') # get names of all selections

            tmp_dir = self.tmp_dir.get()
            if tmp_dir[-1] == '/' or tmp_dir[-1] == '\\':
                tmp_dir = tmp_dir[:-1]
                self.tmp_dir.set(tmp_dir)

            if sel in all_sel_names:
                #pdb_fn = '%s/pymol_sele_%s_%s.pdb' % (self.tmp_dir.get(), sel,
                #                                      str(time.time()).replace('.',''))
                pdb_fn = os.path.join(self.tmp_dir.get(),"pymol_sele_%s_%s.pdb"%(sel,str(time.time()).replace('.','')))
                cmd.save(filename=pdb_fn,selection=sel)
                if VERBOSE:
                    print 'Selection %s saved to %s.' % (sel, pdb_fn)
            else:  # sel is unknown
                err_msg = 'Unknown selection name: %s' % (sel,)
                print 'ERROR: %s' % (err_msg,)
                tkMessageBox.showinfo(title='ERROR', message=err_msg)

        elif len(self.pdb_fn.get()) > 0:  # if no selection specified, use specified PDB file
            pdb_fn = self.pdb_fn.get()
            if not os.path.isfile(pdb_fn):
                err_msg = 'PDB file does not exist: %s' % (pdb_fn,)
                print 'ERROR: %s' % (err_msg,)
                tkMessageBox.showinfo(title='ERROR', message=err_msg)

        else:   # what structure do you want MSMS to work on?
            err_msg = 'Neither PyMOL selection nor PDB file specified!'
            print 'ERROR: %s' % (err_msg,)
            tkMessageBox.showinfo(title='ERROR', message=err_msg)

        return pdb_fn


    def cleanMSMSOutput(self):

        if os.path.isfile(self.msms_vert_fn):
            if VERBOSE: print 'Cleaning msms vert file', self.msms_vert_fn
            os.remove(self.msms_vert_fn)
            self.msms_vert_fn = None
        if os.path.isfile(self.msms_face_fn):
            if VERBOSE: print 'Cleaning msms face file', self.msms_face_fn
            os.remove(self.msms_face_fn)
            self.msms_face_fn = None

        for i in xrange(len(self.msms_cpn_vert_fn_list)):
            vfn = self.msms_cpn_vert_fn_list[i]
            ffn = self.msms_cpn_face_fn_list[i]
            if os.path.isfile(vfn):
                if VERBOSE: print 'Cleaning msms face file', vfn
                os.remove(vfn)
            if os.path.isfile(ffn):
                if VERBOSE: print 'Cleaning msms face file', ffn
                os.remove(ffn)

        self.msms_cpn_vert_fn_list = []
        self.msms_cpn_face_fn_list = []

        return

    def runMSMS(self):
        """
            @return: whether MSMS has been executed successfully
            @rtype: boolean
        """
        # clean up old results, which might be from previous execution
        self.msms_vert_fn = None  # external surface
        self.msms_face_fn = None
        self.msms_cpn_vert_fn_list = [] # internal components
        self.msms_cpn_face_fn_list = []
        self.msp = MSMSSurfPymol()
        self.cpn_msp_list = [] # MSMSSurfPymol objects for internal components

        tmp_dir = self.tmp_dir.get()
        if tmp_dir[-1] == '/' or tmp_dir[-1] == '\\':
            tmp_dir = tmp_dir[:-1]
            self.tmp_dir.set(tmp_dir)

        if VERBOSE:
            print 'MSMS bin  =',self.msms_bin.get()
##             print self.pdb2xyzr_bin.get()
            print 'pdb2xyzrn =', self.pdb2xyzrn_bin.get()
            print 'tmp dir   =', self.tmp_dir.get()

        pdb_fn = self.getStrucPDBFname()
        if pdb_fn is None: return None

        print 'Running MSMS ...'
        if VERBOSE:
            print 'Probe raidus            =', self.probe_radius.get()
            print 'Surface vertex density  =', self.density.get()
            print 'Surface vertex hdensity =', self.hdensity.get()
            print 'Ignore hydrogen atoms   =', str(self.noh.get())
            print 'Consider all surface components =', str(self.allcpn.get())

        msms = Msms(msms_bin=self.msms_bin.get(),
                    #pdb2xyzr_bin=self.pdb2xyzr_bin.get(),
                    pdb2xyzrn_bin=self.pdb2xyzrn_bin.get(),
                    pr=self.probe_radius.get(),
                    den=self.density.get(),
                    hden=self.hdensity.get(),
                    noh=self.noh.get(), all_components=self.allcpn.get(),
                    output_dir=self.tmp_dir.get()
                    )
        msms.run(pdb_fn)
        print 'done!'

        # remove temp file (saved pymol selection)
        if self.cleanup_saved_pymol_sel and \
                len(self.pymol_sel.get()) > 0 and os.path.isfile(pdb_fn):
            if VERBOSE: print 'Cleaning temp file(s)', pdb_fn
            #!os.remove(pdb_fn)  # clean up (remove pdb file of the pymol selection)

        fn_list = msms.getOutputFiles()
        self.msms_vert_fn = fn_list[0]
        self.msms_face_fn = fn_list[1]

        # make copies. do not use reference
        [self.msms_cpn_vert_fn_list.append(fni) for fni in fn_list[2]]
        [self.msms_cpn_face_fn_list.append(fni) for fni in fn_list[3]]

        if VERBOSE:
            print 'MSMS .vert file:', self.msms_vert_fn
            print 'MSMS .face file:', self.msms_face_fn

        return msms

    def custermizeMeshColor(self):
        try:
            color_tuple, color = tkColorChooser.askcolor(color=self.mesh_col)
            if color_tuple is not None and color is not None:
                self.mesh_col_R, self.mesh_col_G, self.mesh_col_B = color_tuple
                self.mesh_col = color
                self.mesh_col_but['bg']=self.mesh_col
                self.mesh_col_but['activebackground']=self.mesh_col
                self.mesh_col_but.update()
        except Tkinter._tkinter.TclError:
            print 'Old color (%s) will be used.' % (self.mesh_col)

        return

    def custermizeVertColor(self):
        try:
            color_tuple, color = tkColorChooser.askcolor(color=self.vert_col)
            if color_tuple is not None and color is not None:
                self.vert_col_R, self.vert_col_G, self.vert_col_B = color_tuple
                self.vert_col = color
                self.vert_col_but['bg']=self.vert_col
                self.vert_col_but['activebackground']=self.vert_col
                self.vert_col_but.update()
        except Tkinter._tkinter.TclError:
            print 'Old color (%s) will be used.' % (self.vert_col)

        return

    def custermizeNormColor(self):
        try:
            color_tuple, color = tkColorChooser.askcolor(color=self.norm_col)
            if color_tuple is not None and color is not None:
                self.norm_col_R, self.norm_col_G, self.norm_col_B = color_tuple
                self.norm_col = color
                self.norm_col_but['bg']=self.norm_col
                self.norm_col_but['activebackground']=self.norm_col
                self.norm_col_but.update()
        except Tkinter._tkinter.TclError:
            print 'Old color (%s) will be used.' % (self.norm_col)

        return

    def execute(self, cmd):
        """ Run the cmd represented by the botton clicked by user.
        """
        if cmd == 'OK':
            print 'is everything OK?'

        elif cmd == 'Run MSMS':

            if self.runMSMS() is not None: # msms has been executed successfully

                if VERBOSE: print 'Parsing MSMS output ...'
                self.msp.parseVertFile(self.msms_vert_fn)
                self.msp.parseFaceFile(self.msms_face_fn)

                if self.allcpn: # all componenents of surface
                    for i in xrange(len(self.msms_cpn_vert_fn_list)):
                        vfn = self.msms_cpn_vert_fn_list[i]
                        ffn = self.msms_cpn_face_fn_list[i]
                        cpn_msp = MSMSSurfPymol()
                        cpn_msp.parseVertFile(vfn)
                        cpn_msp.parseFaceFile(ffn)
                        self.cpn_msp_list.append(cpn_msp)

                if VERBOSE: print 'done!'

                if self.cleanup_msms_output.get(): # clean up
                    self.cleanMSMSOutput()

        elif cmd == 'Display Mesh':
            if len(self.msp.vert_coords) == 0:
                err_msg = 'Please execute MSMS first.'
                print 'ERROR: %s' % (err_msg,)
                tkMessageBox.showinfo(title='ERROR', message=err_msg)
            else:
                self.msp.displayMsmsSurfMesh(mesh_cgo_color= \
                                             (self.mesh_col_R/255.0,
                                              self.mesh_col_G/255.0,
                                              self.mesh_col_B/255.0))
                if self.allcpn:
                    for i in xrange(len(self.cpn_msp_list)):
                        self.cpn_msp_list[i].displayMsmsSurfMesh(
                            mesh_cgo_name='msms_surf_mesh_%d' % (i+1),
                            mesh_cgo_color= (self.mesh_col_R/255.0,
                                             self.mesh_col_G/255.0,
                                             self.mesh_col_B/255.0))

        elif cmd == 'Display Vertices':
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

        elif cmd == 'Exit':
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


