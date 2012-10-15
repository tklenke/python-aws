#! /usr/bin/env python
import boto
import re

CACHE_CONTROL_VALUE = "max-age=" + str(60*60*24*30) #one month
BUCKET_NAME = 'highlandadventures'
print(CACHE_CONTROL_VALUE)
print(BUCKET_NAME)


s3 = boto.connect_s3()
bucket = s3.get_bucket(BUCKET_NAME) 
rs = bucket.list()

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
        #need the following to push up to S3 otherwise just local change
        key.copy(
            key.bucket.name, 
            key.name, 
            key.metadata, 
            preserve_acl=True
            )
        return key
    else:
        print("skipping mera image update: " + key.name)  
        return None
        
for key in rs:
    update_img_metadata(key)
 
