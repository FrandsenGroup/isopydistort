#!/usr/bin/env python
##############################################################################
#
# isopydistort         by Frandsen Group
#                     Benjamin A. Frandsen benfrandsen@byu.edu
#                     (c) 2023 Benjamin Allen Frandsen
#                      All rights reserved
#
# File coded by:    Parker Hamilton, Tobias Bird, Ben Frandsen
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
# We acknowledge Brian Toby and Robert Von Dreele as the first to develop a
# python interface to ISODISTORT, which served as a valuable starting point
# for this package. Their work can be found as part of the GSAS-II software at
# https://subversion.xray.aps.anl.gov/trac/pyGSAS/browser/trunk/ISODISTORT.py
##############################################################################

"""Tools to interface with ISODISTORT"""

import requests
import re

ISO_UPLOAD_SITE = "https://iso.byu.edu/iso/isodistortuploadfile.php"
ISO_FORM_SITE = "https://iso.byu.edu/iso/isodistortform.php"


def _uploadCIF(cif):
    """Upload CIF to ISODISTORT.
    """
    f = open(cif, 'rb')
    up = {'toProcess': (cif, f), }
    out = requests.post(ISO_UPLOAD_SITE, files=up).text
    f.close()

    start = out.index("VALUE=")
    start = out.index('"', start + 1) + 1
    end = out.index('"', start)
    fname = out[start:end]

    return fname

def _postParentCIF(fname):
    #posts initially uploaded CIF, sets all data
    up = {'filename': fname, 'input': 'uploadparentcif'}
    out = requests.post(ISO_FORM_SITE, up)
    data = {}
    line_iter = out.iter_lines()

    for line in line_iter:
        if b'INPUT TYPE="hidden"' in line:
            items = line.decode('utf-8').split(' ', 3)
            name = items[2].split('=')[1].strip('"')

            val = items[3].split('=', 1)[1].strip('>"')
            data[name] = val

    return out, data

def _setDatam3(out, data, var_dict = {}, selection = 1):
    """sets necessary data for method 3 - rolls in postIsosubgroup and part of postParentm3"""
    line_iter = out.iter_lines()
    for line in line_iter:
        if b"Method 3" in line:
            break

    for line in line_iter:
        if b'INPUT TYPE="hidden"' in line:
            items = line.decode('utf-8').split(' ', 3)
            name = items[2].split('=')[1].strip('"')

            val = items[3].split('=', 1)[1].strip('>"')
            data[name] = val
        if b'Method 4' in line:
            break

    data['subgroupsym'] = '1 P1 C1-1'
    data['pointgroupsym'] = '0'
    data['latticetype'] = 'direct'
    data['centering'] = 'd'
    data['basis11'] = '1'
    data['basis12'] = '0'
    data['basis13'] = '0'
    data['basis21'] = '0'
    data['basis22'] = '1'
    data['basis23'] = '0'
    data['basis31'] = '0'
    data['basis32'] = '0'
    data['basis33'] = '1'
    for key, value in var_dict.items():
        data[key] = value
    #For later: allow non-default selections of types of distortions
    #to be considered. Examples shown below.
    #del data['includedisplacive001'] #de-selects displacive modes for first atom
    #data['includemagnetic002'] = 'true' #selects magnetic modes for second atom
    out = requests.post(ISO_FORM_SITE, data=data)
    data = {}
    line_iter = out.iter_lines()

    for line in line_iter:
        if b"<FORM ACTION" in line:
            break

    for line in line_iter:
        if b'INPUT TYPE="hidden"' in line:
            items = line.decode('utf-8').split(' ', 3)
            name = items[2].split('=')[1].strip('"')

            val = items[3].split('=', 1)[1].strip('>"')
            data[name] = val
        if b'<br>' in line:
            break

    counter = 0  # keep track of which distortion we are on
    for line in line_iter:
        if b'RADIO' in line:
            counter += 1
            if counter == selection:  # grab data just for the one we want
                items = line.decode('utf-8').split(' ', 3)
                name = items[2].split('=')[1].strip('"')

                val = items[3].split('=', 1)[1].strip('>"')
                data[name] = val

        if b'</FORM>' in line:
            break
    
    return out, data





def _setDatam4(data, subcif, specify = False, basis = [], var_dict = {}):

    subfname = _uploadCIF(subcif)
    data['input'] = 'uploadsubgroupcif'
    data['filename'] = subfname

    out = requests.post(ISO_FORM_SITE, data=data)
    line_iter = out.iter_lines()
    # for line in line_iter:
    # print(line.decode('utf-8'))

    for line in line_iter:
        if b'INPUT TYPE="hidden"' in line:
            items = line.decode('utf-8').split(' ', 3)
            name = items[2].split('=')[1].strip('"')

            val = items[3].split('=', 1)[1].strip('>"')
            data[name] = val
        if specify == False and b'OPTION VALUE=' in line:
            data['inputbasis'] = 'list'
            items = line.decode('utf-8').split(' ', 1)
            data['basisselect'] = items[1].split('=')[1].split(">")[0].strip('"')
            print(items[1].split('=')[1].split(">")[0].strip('"'))

    data['input'] = 'distort'
    data['origintype'] = 'method4'

    if specify == True:
        basis_vars = ["basis11", "basis12", "basis13", "basis21", "basis22", "basis23", "basis31", "basis32", "basis33"]
        if not basis:
            print("No basis specified. Exiting...")
            print("Try specifying a basis or setting specify to False")
        if len(basis) != 9:
            print("Incorrect number of elements for basis, expected 9")
        else:
            data['inputbasis'] = 'specify'
            for i in range(len(basis_vars)):
                data[basis_vars[i]] = f'{basis[i]}'

    data['chooseorigin'] = False
    data['trynearest'] = True
    data['dmax'] = 1
    data['zeromodes'] = False

    for key, value in var_dict.items():
        data[key] = value

    return out, data



def _postDistort(data, isoformat, output_dict = {}, generate_zipped_files=False):
    """Prepare the data for downloading.
    
    output_dict: options for the isodistort output, such as whether strain should be
                 included in the topas files, zipped files should be prepared, etc.
                 Non-exhaustive list of options to set to 'true' if desired:
                 'topasstrain' (include strain in topas file)
                 'treecif' (generate CIFs for all subgroups in tree)
                 'treetopas' (generate topas files for all subgroups in tree)
                 
    """
    out = requests.post(ISO_FORM_SITE, data=data)
    
    data = {}
    line_iter = out.iter_lines()
    for line in line_iter:
        if b"<FORM ACTION" in line:
            break

    for line in line_iter:
        if b'INPUT TYPE="hidden"' in line:
            items = line.decode('utf-8').split(' ', 3)
            name = items[2].split('=')[1].strip('"')

            val = items[3].split('=', 1)[1].strip('>"')
            data[name] = val

        if b'input type="text"' in line:
            items = line.decode('utf-8').split(' ', 5)
            name = [s for s in items if 'name=' in s][0].split('=')[1].strip('"')

            val = [s for s in items if 'value=' in s][0].split('=')[1].strip('"')
            data[name] = val

        if b'RADIO' in line and b'CHECKED' in line:
            items = line.decode('utf-8').split(' ', 3)
            name = items[2].split('"')[1]

            val = items[3].split('"')[1]
            data[name] = val

        if b'</FORM>' in line:
            break

    data['origintype'] = isoformat
    for key, value in output_dict.items():
        data[key] = value
    
    return out, data


def _postDisplayDistort(data, fname, zipped=False):
    """Download the ISODISTORT output.
    """
    out = requests.post(ISO_FORM_SITE, data=data)
    f = open(fname, 'wb')
    if zipped:
       f.write(out.content)
    else:
        f.write(out.text.encode('utf-8'))
    f.close()
    return out



def _find_zip_file_name(output):
    """Parse http output from ISODISTORT to get file names of zipped topas and cif files"""
    
    # Helper lambda to extract zip filename
    extract_zip_name = lambda line: re.findall(r'[a-zA-Z]+[0-9]+', line.strip().split('VALUE=')[-1].strip())[0]

    returndict = {}
    lines = list(output.iter_lines())[::-1]  # Reverse lines
    
    try:
        for line in lines:
            line = str(line)
            
            if 'zipfilename' in line and 'cif' in line and 'cifzipname' not in returndict:
                returndict['cifzipname'] = extract_zip_name(line)
            
            if 'zipfilename' in line and 'topas' in line and 'topaszipname' not in returndict:
                returndict['topaszipname'] = extract_zip_name(line)

            # check for ISODISTORT server error with keyword 'bombed' that occcurs in ISODISTORT's error message
            if 'bombed' in line:
                raise RuntimeError(f'''\nRUNTIME ERROR MESSAGE FROM ISODISTORT SERVER: \n{line}\n
Double Check your input, and if there is no user error, email Branton Campbell at BYU with a detailed log of your error. 
Things to include in your error report:
1. Parent CIF 
2. Detailed steps to reproduce your error. 
Email: branton_campbell@byu.edu \n''')
            
            # If both files are found, exit the loop early
            if len(returndict) == 2:
                break
        
        if len(returndict) < 2:
            raise ValueError("Both 'cif' and 'topas' zip filenames could not be found.")

    except (IndexError, KeyError, ValueError, RuntimeError) as e:
        raise RuntimeError(f"Error parsing output: {e}")

    return returndict



def get(cifname, outfname, method=3, var_dict={}, isoformat='topas',
        selection=1, subcif = "", specify = False, basis = [],
        generate_tree_zip = False, output_dict={}):
    """Interacts with the ISODISTORT website to get distortion modes.

    Args:
        cifname (str): The name of the local cif file you want to use.
        outfname (str): The name of the file where you want the ISODISTORT
            output saved.
        method (int): Method number to be used by the ISODISTORT server. The
            currently available method numbers are 3 and 4.
        var_dict (dict): Variables to pass to ISODISTORT to set up the
            subgroup symmetry, lattice, and basis. The required dictionary
            keys depend on the method number chosen, as described below.

            Method 3: Keys and default values are given below. It defaults to
            P1 symmetry and an identity matrix for the supercell basis.\n
                'subgroupsym' = '1 P1 C1-1'\n
                'pointgroupsym' = '0'\n
                'latticetype' = 'direct'\n
                'centering' = 'd' (for default)\n
                'basis11' = '1'\n
                'basis12' = '0'\n
                'basis13' = '0'\n
                'basis21' = '0'\n
                'basis22' = '1'\n
                'basis23' = '0'\n
                'basis31' = '0'\n
                'basis32' = '0'\n
                'basis33' = '1'\n
            Note that the 'subgroupsym' value can simply be the space group
            number (as a string) for the desired subgroup. It is not
            recommended to use the space group symbol alone, since this is
            not always read correctly.
        isoformat (str): format of the output file requested from the
            ISODISTORT server. Allowed values are:\n
                'isovizdistortion'\n
                'isovizdiffraction'\n
                'structurefile'\n
                'distortionfile'\n
                'domains'\n
                'primary'\n
                'modesdetails'\n
                'completemodesdetails'\n
                'topas'\n
                'fullprof'\n
                'irreps'\n
                'tree'\n
            See https://stokes.byu.edu/iso/isodistorthelp.php#savedist for
            information about each format.
        selection (int): The number of the desired distortion from the list
            of possible distortions provided by ISODISTORT, starting from 1
            at the top and increasing as you move downward through the list.
            Default value is 1.
        generate_tree_zip (boolean): True if zipped directories containing CIFs
            and topas files for the full subgroup tree are desired. Only
            applicable if 'tree' is chosen as the isoformat for Method 3.
            Output will include the tree file and the zipped directories.
        output_dict (dictionary): Various other options for the isodistort
            output. Currently, the only supported option is:\n
                'topasstrain' : 'true'\n
            which includes strain parameters in the topas files.
    """
    ### check that the format and method number are acceptable
    formatlist = ['isovizdistortion',
                  'isovizdiffraction',
                  'structurefile',
                  'distortionfile',
                  'domains',
                  'primary',
                  'modesdetails',
                  'completemodesdetails',
                  'topas',
                  'fullprof',
                  'irreps',
                  'tree']
    methodlist = [3,4]

    ### if everything is good, move on to the interaction with ISODISTORT
    if (isoformat in formatlist) and (method in methodlist):
        parentcif = _uploadCIF(cifname)
        out1, data1 = _postParentCIF(parentcif)
        # use the correct post function for the user-supplied method number
        #data = eval('_postParentCIFm' + str(method) + '(parentcif, var_dict)')
        if method == 3:
            out2, data2 = _setDatam3(out1, data1, var_dict = var_dict, selection = selection)
            if not generate_tree_zip:
                out3, data3 = _postDistort(data2, isoformat, output_dict)
                out4 = _postDisplayDistort(data3, outfname)
            if generate_tree_zip:
                if isoformat == 'tree':
                    output_dict['treecif'] = 'true'
                    output_dict['treetopas'] = 'true'
                    out3, data3 = _postDistort(data2, isoformat, output_dict)
                    out4 = _postDisplayDistort(data3, outfname) # generate tree file
                    # now generate zipped directories
                    # first, find the file names of the zipped directories
                    filedict = _find_zip_file_name(out4)
                    # download the zipped topas directory
                    data3['origintype'] = 'topaszip'
                    data3['input'] = 'download'
                    data3['zipfilename'] = filedict['topaszipname']
                    temp = _postDisplayDistort(data3, outfname+'_topas.zip', zipped=True)
                    # download the zipped cif directory
                    data3['origintype'] = 'topaszip'
                    data3['zipfilename'] = filedict['cifzipname']
                    temp = _postDisplayDistort(data3, outfname+'_cif.zip', zipped=True)
                else:
                    print('To generate zipped directories of topas and cif files from a subgroup tree,')
                    print("you must set isoformat to 'tree'.")
                    out3 = []
                    data3 = []
                    out4 = []

        if method == 4:
            out2, data2 = _setDatam4(data1, subcif, specify = specify, basis = basis, var_dict = var_dict)
            out3, data3 = _postDistort(data2, isoformat)
            out4 = _postDisplayDistort(data3, outfname)
        return [out1, data1, out2, data2, out3, data3, out4]
    ### inform the user if there is a problem
    if isoformat not in formatlist:
        print('This is not a valid format. Acceptable options are:\n')
        print('isovizdistortion')
        print('isovizdiffraction')
        print('structurefile (which generates a cif)')
        print('distortionfile')
        print('domains')
        print('primary')
        print('modesdetails')
        print('completemodesdetails')
        print('topas')
        print('fullprof')
        print('irreps')
        print('tree\n')
        print('Please try again with one of these formats.')
        return
    if method not in methodlist:
        print('This is not a valid method number. Acceptable options are:\n')
        print(methodlist)
        print('Please try again with one of these methods.')
        print('Additional methods may become available in the future.')
        return