#!/usr/bin/python

# @desc     Tired of having to go into each sub dir to find out whether or 
#           not you did a git commit? Tire no more, just use this!
#           
# @author   Mike Pearce <mike@mikepearce.net>
# @since    18/05/2010

# Forked by ap

# Grab some libraries
import sys
import os
import glob
import subprocess
from optparse import OptionParser

# Setup some stuff
dirname = './'
gitted  = False
svnned  = False
mini    = True

messages = ""

parser = OptionParser(description="\
Show Status is awesome. If you tell it a directory to look in, it'll scan \
through all the sub dirs looking for a .git directory. When it finds one \
it'll look to see if there are any changes and let you know. \
It can also push and pull to/from a remote location (like github.com) \
(but only if there are no changes.) \
Contact mike@mikepearce.net for any support.")
parser.add_option("-d", "--dir", 
                    dest    = "dirname", 
                    action  = "store",
                    help    = "The directory to parse sub dirs from", 
                    default = os.path.abspath("./")+"/"
                    )

parser.add_option("-v", "--verbose",
                  action    = "store_true", 
                  dest      = "verbose", 
                  default   = False,
                  help      = "Show the full detail of git status"
                  )

parser.add_option("-r", "--remote",
                action      = "store", 
                dest        = "remote", 
                default     = "",
                help        = "Set the remote name (remotename:branchname)"
                )

parser.add_option("--push",
                action      = "store_true", 
                dest        = "push", 
                default     = False,
                help        = "Do a 'git push' if you've set a remote with -r it will push to there"
                )

parser.add_option("-p", "--pull",
                action      = "store_true", 
                dest        = "pull", 
                default     = False,
                help        = "Do a 'git pull' if you've set a remote with -r it will pull from there"
                )

# Now, parse the args
(options, args) = parser.parse_args()
    
#-------------------
def show_error(error="Undefined Error!"):
#-------------------
    """Writes an error to stderr"""
    sys.stderr.write(error)
    sys.exit(1)

#-------------------
def check_output(command, allowretcode):
#-------------------
    """Wrapper to subprocess.check_output to handle git misbehavior"""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output = process.communicate()
    retcode = process.poll()
    if retcode:
            if retcode != allowretcode:
                raise subprocess.CalledProcessError(retcode, command, output=output[0])
            else:
                global messages
                messages = "\n\tWarning: git status returned %d.\
                \n\tPlease run verbose mode for more information\n" %( retcode)
                return output[0]
    return output[0] 

    
#-------------------
# Now, onto the main event!
#-------------------
if __name__ == "__main__":

    sys.stdout.write('Scanning sub directories of %s\n' %options.dirname)


    # ------------------------------------------------------
    #       git Part
    # ------------------------------------------------------
    
    # See whats here
    for infile in glob.glob( os.path.join(options.dirname, '*') ):

        #is there a .git file
        if os.path.exists( os.path.join(infile, ".git") ):
            
            #Yay, we found one!
            gitted = True
            
            # OK, contains a .git file. Let's descend into it
            # and ask git for a status
            #out = commands.getoutput('cd '+ infile + '; git status')
            out = check_output("cd \"" + infile + "\" && git status ", 1)
            
            # Mini?
            if False == options.verbose:
                if -1 != out.find('nothing'):
                    result = ": No Changes"
                    
                    # Pull from the remote
                    if False != options.pull:
                        push = check_output(
                            "cd \"" + infile + "\" && git pull " +
                            ' '.join(options.remote.split(":")),0
                        )
                        result = result + " (Pulled) \n" + push
                                          
                    # Push to the remote  
                    if False != options.push:
                        push = check_output(
                            "cd \"" + infile + "\" && git push " +
                            ' '.join(options.remote.split(":")),0
                        )
                        result = result + " (Pushed) \n" + push
                        
                    # Write to screen
                    sys.stdout.write("[git] " + os.path.basename(infile).ljust(30) + result +"\n")
                else:
                    sys.stdout.write("[git] " + os.path.basename(infile).ljust(30) + ": Changes\n")
            else:
                #Print some repo details
                sys.stdout.write("\n---------------- "+ infile +" -----------------\n")
                sys.stdout.write(out)
                sys.stdout.write("\n---------------- "+ infile +" -----------------\n")
                
            # Come out of the dir and into the next
            #commands.getoutput('cd ../')
            check_output("cd ..",0)
                
            

            
    if False == gitted:
        show_error("Error: None of those sub directories had a .git file.\n")


    # ------------------------------------------------------
    #       svn Part
    # ------------------------------------------------------
    # See whats here
    for infile in glob.glob( os.path.join(options.dirname, '*') ):

        #is there a .svn folder
        if os.path.exists( os.path.join(infile, ".svn") ):
            
            #Yay, we found one!
            svnned = True
            
            # OK, contains a .svn folder. Let's descend into it
            # and ask svn for info
            out = check_output("cd \"" + infile + "\" && svn diff | grep Index ", 1)
            
            # Mini?
            if False == options.verbose:
                if -1 == out.find('Index'):
                    result = ": No Changes"
                    
                    # Pull from the remote
                    if False != options.pull:
                        push = check_output(
                            "cd \"" + infile + "\" && svn up " +
                            ' '.join(options.remote.split(":")),0
                        )
                        result = result + " (Pulled) \n" + push
                                          
                    # Push to the remote  
                    if False != options.push:
                        # do nothing
                        result = result + " ( n/a  ) \n" + push
                        
                    # Write to screen
                    sys.stdout.write("[svn] " + os.path.basename(infile).ljust(30) + result +"\n")
                else:
                    sys.stdout.write("[svn] " + os.path.basename(infile).ljust(30) + ": Changes\n")
            else:
                #Print some repo details
                sys.stdout.write("\n---------------- "+ infile +" -----------------\n")
                sys.stdout.write(out)
                sys.stdout.write("\n---------------- "+ infile +" -----------------\n")
                
            # Come out of the dir and into the next
            check_output("cd ..",0)

            
    if False == svnned:
        show_error("Error: None of those sub directories had .svn\n")

    print messages
      
    raw_input("Press Enter to Exit")
