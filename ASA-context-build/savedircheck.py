import os,getpass
from context_builder import *
from shutil import copyfile

username = getpass.getuser() 

savepath = '/home/' + username + '/context/'
savedircheck = os.path.exists(savepath)

if savedircheck == False:
	savedir = os.makedirs(savepath)
	configcopy = copyfile('/usr/local/scripts/context_builder/contextconfig.ini',savepath + 'contextconfig.ini')
	configexample = copyfile('/usr/local/scripts/context_builder/contextconfig-EXAMPLE.ini',savepath + 'contextconfig-EXAMPLE.ini')
	print("\nCopying contextconfig.ini to /home/%s/context.....\n" % username)
	print("Please modify the contextconfig.ini file in your home directory and re-run the script.\n")
else:

	custinfo = context(config, 'custinfo')
	custname = custinfo.custname
	filename = custname + '_template.txt'
	fullpath = os.path.join(savepath,filename)
	
	print("Building %s_template.txt...." % custname)
	
	fout = open(fullpath, 'w')
	fout.write(contextbuilder())
	fout.close()
	print("Done! Build template is at: %s" % fullpath)


