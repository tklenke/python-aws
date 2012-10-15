#! /usr/bin/env python
import boto
import re
import os

CACHE_CONTROL_VALUE = "max-age=" + str(60*60*24*30) #one month
BUCKET_NAME = 'highlandadventures'
cwd = os.getcwd()

print("cache-control" + CACHE_CONTROL_VALUE)
print("s3 bucket: " + BUCKET_NAME)
print("cwd: " + cwd)


s3 = boto.connect_s3()
bucket = s3.get_bucket(BUCKET_NAME) 
#~ rs = bucket.list()
#~ patKeep = re.compile('^(index\.html)|(robots\.txt)|(s3\/)$')

def update_img_metadata(key):
    if key.name.lower().endswith('.jpg'):
        contentType = 'image/jpeg'
    elif key.name.lower().endswith('.png'):
        contentType = 'image/png'
    elif key.name.lower().endswith('.gif'):
        contentType = 'image/gif'
    else:
        contentType = None
        
    if contentType is not None:
        key.metadata.update({
            'Content-Type': contentType,
            'Cache-Control': CACHE_CONTROL_VALUE
            })
        return key
    else:
        print("not image file skipping")
        return None
      

def set_img_metadata(key):
    key = update_img_metadata(key)
    #need the following to push up to S3 otherwise just local change
    if key is not None:
        key.copy(
            key.bucket.name, 
            key.name, 
            key.metadata, 
            preserve_acl=True
            )
    return key

    
#get list from cwd
for root, dirs, files in os.walk(cwd):
    for directory in dirs:
        dpath = os.path.join(root, directory)
        s3key = dpath.replace(cwd,"")
        print("d:" + dpath)
        key = bucket.get_key(s3key)
        if key is None:
            key = bucket.new_key(s3key)
            print("directory " + dpath + " created as key " + key.name)
        else:
            print("directory:" + dpath + "already exists as " + key.name) 
                       
    for name in files:
        fpath = os.path.join(root, name)
        s3key = fpath.replace(cwd + "/","")
        key = bucket.get_key(s3key)
        stat = os.stat(fpath)
        print("f:" + fpath + " s3k:" + s3key)
        print("file size:" + str(stat.st_size))
        
        if key is not None:
            if key.size == stat.st_size:
                print("f:" + fpath + " on s3 as:" + key.name + " updating metas")
                set_img_metadata(key)
                continue
            else: 
                print("f:" + fpath + " size does not match s3 as:" + key.name + " deleting s3 key")
                key.delete() #the old
                
        key = bucket.new_key(s3key)        
        print("up f:" + fpath + ":" + str(stat.st_size) + " as s3 " + key.name)       
        key = update_img_metadata(key)
        key.set_contents_from_filename(fpath)
