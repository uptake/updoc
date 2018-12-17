"""
Module to house the functionality used to manage the local storage of document tarballs.
"""

import os

from ._base import Storage
from docserver.utils import logger
from shutil import copyfile, rmtree


class LocalStorage(Storage):
    """Storage class extension to store document tarballs locally.

    Args:
        tarball_dir (str): Directory in which to store incoming tarballs.
    """

    def __init__(self,
                 tarball_dir: str = '/src/contrib'):
        self.tarball_dir = tarball_dir
        super(LocalStorage, self).__init__()

    def store_tarball(self,
                      category: str,
                      doc_name: str,
                      tmp_tarball_fp: str):
        """Stores an incoming tarball locally in ``tarball_dir``.

        Args:
            category (str): Category of the incoming document tarball.
            doc_name (str): Document name of the incoming tarball.
            tmp_tarball_fp (str): File path to the tarball to store.
        """
        logger.info("Storing document: {doc_filename} with category: "
                    "{doc_category} locally.".format(doc_filename=doc_name,
                                                     doc_category=category))
        tarball_category_dir = os.path.join(self.tarball_dir, category)
        dest_tarball_fp = os.path.join(tarball_category_dir, doc_name + ".tar.gz")

        # Create category directory if it doesn't exist.
        if not os.path.exists(tarball_category_dir):
            os.mkdir(tarball_category_dir)

        # Remove previous tarball if it's already there.
        if os.path.exists(dest_tarball_fp):
            rmtree(dest_tarball_fp, ignore_errors=True)

        copyfile(tmp_tarball_fp, dest_tarball_fp)

    def delete_tarball(self,
                       category: str,
                       doc_name: str):
        """Removes the local tarball file.

        Args:
            category (str): Category of the tarball to remove.
            doc_name (str): Document name of the tarball to remove.
        """
        tarball_fp = os.path.join(self.tarball_dir, category, doc_name + ".tar.gz")

        if os.path.exists(tarball_fp):
            rmtree(tarball_fp, ignore_errors=True)

    def initialize_storage(self):
        """Initializes the local storage if any pre-existing tarballs are in ``tarball_dir``."""
        for category_dir_name in os.listdir(self.tarball_dir):
            category_dir_path = os.path.join(self.tarball_dir, category_dir_name)

            if os.path.isdir(category_dir_path):
                for tarball_filename in os.listdir(category_dir_path):
                    tarball_fp = os.path.join(category_dir_path, tarball_filename)

                    self.extract_docs_from_tarball(category=category_dir_name,
                                                   doc_name=tarball_filename.replace(".tar.gz", ""),
                                                   tmp_tarball_fp=tarball_fp)
