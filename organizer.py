import glob
import exifreader
import datetime
import os
import posixpath
import argparse

parser = argparse.ArgumentParser(description='Organize your photos and videos with date')
parser.add_argument( '--input', help="input directory")
parser.add_argument( '--output',  help="output directory")
args = parser.parse_args()


if not any(vars(args).values()):
    parser.print_help()
    exit()
    
    
file_types = ['*.jpg', '*.jpeg', '*.png', '*.mov']
out_dir = os.path.join(args.output,'')
input_dir = os.path.join(args.input,'')

files = []
for ftype in file_types:
    files.append(glob.glob(input_dir+'/*/'+ftype))
    files.append(glob.glob(input_dir+ftype))



# convert list of list to list    
files = sum(files, [])

def date_to_foldername(d):
    date = datetime.datetime.strptime(d, "%Y:%m:%d %H:%M:%S")
    return '%s_%02d' %(date.year , date.month)

def move(filedatelist):
    date = datetime.datetime.strptime(filedatelist[1], "%Y:%m:%d %H:%M:%S")
    filename = os.path.basename(filedatelist[0])
    new_name = os.path.join(out_dir + date_to_foldername(filedatelist[1]), filename)
    os.replace(posixpath.join(*filedatelist[0].split('\\')), posixpath.join(*new_name.split('\\')))
    
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(int(t)).strftime('%Y:%m:%d %H:%M:%S')
    
    
dates = []
folder_names = []

for k, f in enumerate(files):
    with open(f, 'rb') as o:
        tags = exifreader.process_file(o, details=False)
      
        if tags.get('Image DateTime'):
            dates.append([f, str(tags['Image DateTime']) ])
        elif tags.get('EXIF DateTimeOriginal'):
            dates.append([f, str(tags['EXIF DateTimeOriginal']) ])
        else:
            dates.append([f, str(modification_date(f)) ])

for _,d in dates:
    date = datetime.datetime.strptime(d, "%Y:%m:%d %H:%M:%S")
    folder_names.append('%s_%02d' %(date.year , date.month))


for u in list(set(folder_names)):
    if not os.path.exists(out_dir+u):
        os.mkdir(out_dir+u)
 

for d in dates:
    move(d)

    
for dirs in glob.glob(out_dir+'*'):
    for k,file in enumerate(glob.glob(dirs+'/*')):
        newfilename = ('%s/%s.%s' % (os.path.dirname(file), k+1,os.path.basename(file).split('.')[1]))
        os.replace(file, newfilename)