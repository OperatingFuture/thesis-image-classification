import os
from dotenv import load_dotenv

ROOT_DIR = os.path.realpath("..")
load_dotenv(os.path.join(ROOT_DIR, ".env"))

models_policy = {"Version": "2012-10-17",
                 "Statement": [
                     {
                         "Sid": "AddPerm",
                         "Effect": "Allow",
                         "Principal": "*",
                         "Action": ["s3:GetBucketLocation"],
                         "Resource": "arn:aws:s3:::" + os.getenv("MODELS_BUCKET")
                     },
                     {
                         "Sid": "AddPerm",
                         "Effect": "Allow",
                         "Principal": "*",
                         "Action": ["s3:ListBucket"],
                         "Resource": "arn:aws:s3:::" + os.getenv("MODELS_BUCKET")
                     },
                     {
                         "Sid": "AddPerm",
                         "Effect": "Allow",
                         "Principal": "*",
                         "Action": ["s3:GetObject"],
                         "Resource": "arn:aws:s3:::" + os.getenv("MODELS_BUCKET") + "/*"
                     },
                     {
                         "Sid": "AddPerm",
                         "Effect": "Allow",
                         "Principal": "*",
                         "Action": ["s3:PutObject"],
                         "Resource": "arn:aws:s3:::" + os.getenv("MODELS_BUCKET") + "/*"
                     }

                 ]}

images_policy = {"Version": "2012-10-17",
                 "Statement": [
                     {
                         "Sid": "AddPerm",
                         "Effect": "Allow",
                         "Principal": "*",
                         "Action": ["s3:GetBucketLocation"],
                         "Resource": "arn:aws:s3:::" + os.getenv("IMAGES_BUCKET")
                     },
                     {
                         "Sid": "AddPerm",
                         "Effect": "Allow",
                         "Principal": "*",
                         "Action": ["s3:ListBucket"],
                         "Resource": "arn:aws:s3:::" + os.getenv("IMAGES_BUCKET")
                     },
                     {
                         "Sid": "AddPerm",
                         "Effect": "Allow",
                         "Principal": "*",
                         "Action": ["s3:GetObject"],
                         "Resource": "arn:aws:s3:::" + os.getenv("IMAGES_BUCKET") + "/*"
                     },
                     {
                         "Sid": "AddPerm",
                         "Effect": "Allow",
                         "Principal": "*",
                         "Action": ["s3:PutObject"],
                         "Resource": "arn:aws:s3:::" + os.getenv("IMAGES_BUCKET") + "/*"
                     }

                 ]}
