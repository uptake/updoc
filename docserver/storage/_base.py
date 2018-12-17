"""
Base storage class.
"""

import os
import redis
import tarfile

from collections.abc import MutableMapping
from docserver.utils import logger
from shutil import rmtree


class Storage(MutableMapping):
    """Storage base class.

    This class takes care of initializing a Redis database, and providing an interface to store and untar document
    tarballs while allowing extensions to customize the storing of the tarballs and initialization of the application.
    """
    def __init__(self):
        self.registry = redis.StrictRedis(decode_responses=True)
        self.initialize_storage()

    def __iter__(self):
        """Iterates through the doc_ids (keys) in the Redis database."""
        return self.registry.scan_iter()

    def __len__(self):
        """Returns the number of documents (number of keys) tracked in the Redis database."""
        return len(list(self.registry.scan_iter()))

    def __getitem__(self, doc_id: str):
        """Returns the document name, category, and the relative path to the documentation for serving in the app.

        Args:
            doc_id (str): String with the format "CATEGORY_DOCNAME".

        Returns:
            tuple: For the relevant ``doc_id``, a tuple containing the document name, category, and static html path.
        """
        category, doc_name = doc_id.split('_', 1)
        doc_dir = self.registry.get(doc_id)
        return doc_name, category, os.path.join(doc_dir, 'index.html')

    def __setitem__(self,
                    doc_id: str,
                    tmp_tarball_fp: str):
        """Adds the tarball to storage, the registry, and extracts it to the static folder.

        Args:
            doc_id (str): String with the format "CATEGORY_DOCNAME".
            tmp_tarball_fp (str): File path to the tarball to store and extract.
        """
        category, doc_name = doc_id.split('_', 1)

        self.store_tarball(category=category,
                           doc_name=doc_name,
                           tmp_tarball_fp=tmp_tarball_fp)

        self.extract_docs_from_tarball(category=category,
                                       doc_name=doc_name,
                                       tmp_tarball_fp=tmp_tarball_fp)

    def __delitem__(self, doc_id: str):
        """Deletes the tarball from storage, the registry, and from the static folder.

        Args:
            doc_id (str): String with the format "CATEGORY_DOCNAME".
        """
        doc_name, category, doc_path = self.registry.get(doc_id)

        # Delete docs from /docserver/static
        if os.path.exists(os.path.join('docserver', doc_path)):
            rmtree(os.path.join('docserver', doc_path), ignore_errors=True)

        self.registry.delete(doc_id)
        self.delete_tarball(category=category,
                            doc_name=doc_name)

    @property
    def available_docs(self):
        """
        Returns the currently available documentation from the Redis database in a format for the Javascript frontend.

        The structure of the returned list looks like the following::

            [
              {
                "category": "CATEGORY1",
                "documents": [
                  {
                    "doc_name": "document_a",
                    "doc_path": "static/CATEGORY1/document_a/index.html"
                  },
                  {
                    "doc_name": "document_b",
                    "doc_path": "static/CATEGORY1/document_b/index.html"
                  }
                ]
              },
              {
                "category": "CATEGORY2",
                "documents": [
                  {
                    "doc_name": "document_c",
                    "doc_path": "static/CATEGORY2/document_c/index.html"
                  }
                ]
              },
              ...
            ]

        """
        # TODO: Cache this so we only recreate this object when there have been updates in redis since last creation.
        doc_dict_temp = dict()

        for doc_name, category, doc_path in self.values():
            doc_meta = {
                'doc_name': doc_name,
                'doc_path': doc_path
            }

            # Add metadata to dictionary.
            if doc_dict_temp.get(category) is not None:
                doc_dict_temp[category].append(doc_meta)
            else:
                doc_dict_temp[category] = [doc_meta]

        doc_list = [{'category': k,
                     'documents': sorted(v,
                                         key=lambda x: x.get('doc_name'),
                                         reverse=False)}
                    for k, v in doc_dict_temp.items()]
        doc_list.sort(key=lambda x: x.get('category'))

        return doc_list

    def extract_docs_from_tarball(self,
                                  category: str,
                                  doc_name: str,
                                  tmp_tarball_fp: str):
        """
        Extracts the tarball into a static html folder for serving in the application and adds the doc to the registry.

        Args:
            category (str): Category of the incoming document tarball.
            doc_name (str): Document name of the incoming tarball.
            tmp_tarball_fp (str): File path to the tarball to store and extract.
        """
        logger.info("Extracting document: {doc_filename} with category: "
                    "{doc_category} from tarball.".format(doc_filename=doc_name,
                                                          doc_category=category))
        doc_category_dir = os.path.join('docserver', 'static', category)
        this_doc_dir = os.path.join(doc_category_dir, doc_name)
        flask_doc_path = os.path.join('static', category, doc_name)

        # Create category directory if it doesn't exist.
        if not os.path.exists(doc_category_dir):
            os.mkdir(doc_category_dir)

        # Remove previous document html if it's already there.
        if os.path.exists(this_doc_dir):
            rmtree(this_doc_dir, ignore_errors=True)

        # TODO: Add check to make sure extracted tarball folder has the same name as doc_name.
        # TODO: Add check to make sure index.html exists.
        with tarfile.open(tmp_tarball_fp, mode="r:gz") as tar:
            tar.extractall(path=doc_category_dir)

        self.registry.set(name=category + "_" + doc_name,
                          value=flask_doc_path)

    def initialize_storage(self, *args, **kwargs):
        """Placeholder method to make sure extensions of the class implement initialize_storage."""
        raise NotImplementedError

    def store_tarball(self, *args, **kwargs):
        """Placeholder method to make sure extensions of the class implement store_tarball."""
        raise NotImplementedError

    def delete_tarball(self, *args, **kwargs):
        """Placeholder method to make sure extensions of the class implement delete_tarball."""
        raise NotImplementedError
