"""
Module to house the functionality used to manage the storage of document tarballs in an AWS S3 bucket.
"""

import boto3
import os

from ._base import Storage
from docserver.utils import logger
from tempfile import TemporaryDirectory


class S3Storage(Storage):
    """Storage class extension to store document tarballs in AWS S3.

    In order to use this type of storage, you must have the following environment variables set:

        * AWS_ACCESS_KEY_ID
        * AWS_SECRET_ACCESS_KEY

    Args:
        bucket_name (str): The name of the AWS bucket to use for storing the document tarballs.
        s3_folder (str): The folder path in the bucket to treat as the directory for housing the tarballs.
    """

    def __init__(self,
                 bucket_name: str,
                 s3_folder: str):
        self.bucket_name = bucket_name
        self.bucket = boto3.resource('s3').Bucket(bucket_name)
        self.s3_folder = s3_folder
        super(S3Storage, self).__init__()

    def store_tarball(self,
                      category: str,
                      doc_name: str,
                      tmp_tarball_fp: str):
        """Stores the tarball in the folder specified by ``category`` in the S3 bucket.

        Args:
            category (str): Category of the incoming document tarball.
            doc_name (str): Document name of the incoming tarball.
            tmp_tarball_fp (str): File path to the tarball to store.
        """
        logger.info("Storing document: {doc_filename} with category: "
                    "{doc_category} in S3 bucket.".format(doc_filename=doc_name,
                                                          doc_category=category))
        s3_tarball_loc = os.path.join(self.s3_folder, category, doc_name + ".tar.gz")

        self.bucket.upload_file(tmp_tarball_fp, s3_tarball_loc)

    # TODO: Add delete_tarball method

    def initialize_storage(self):
        """Pulls down any previously stored tarballs from S3 and initializes the static html for each."""
        logger.info("Initializing S3 storage, pulling down any docs from S3 if they exist.")
        available_docs = [obj.key for obj in self.bucket.objects.filter(Prefix=os.path.join(self.s3_folder))]

        for document_key in available_docs:
            # Only want to download non-directories.
            *_, doc_category, doc_filename = document_key.split("/")

            if doc_filename != '':
                logger.info("Downloading document: {doc_filename} with category: "
                            "{doc_category} from S3.".format(doc_filename=doc_filename,
                                                             doc_category=doc_category))

                with TemporaryDirectory() as tmp_dir:
                    target_path = os.path.join(tmp_dir, doc_filename)
                    self.bucket.download_file(document_key, target_path)
                    self.extract_docs_from_tarball(category=doc_category,
                                                   doc_name=doc_filename.replace(".tar.gz", ""),
                                                   tmp_tarball_fp=target_path)
