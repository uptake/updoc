from __future__ import print_function
import os
import json

from docserver.utils import logger, log_exception
from flask import abort
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from tempfile import TemporaryDirectory
from shutil import copyfileobj


###############
### STORAGE ###
###############

STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'filesystem')

if STORAGE_BACKEND == 'filesystem':
    from docserver.storage import LocalStorage
    TARBALL_DIR = os.getenv('DOCSERVER_TAR_LOC', "/opt/docs/src/contrib/")
    doc_storage = LocalStorage(tarball_dir=TARBALL_DIR)
elif STORAGE_BACKEND == 's3':
    from docserver.storage import S3Storage
    AWS_DEFAULT_BUCKET = os.getenv('AWS_DEFAULT_BUCKET')
    AWS_BUCKET_FOLDER_PATH = os.getenv('AWS_BUCKET_FOLDER_PATH', "")
    doc_storage = S3Storage(bucket_name=AWS_DEFAULT_BUCKET,
                            s3_folder=AWS_BUCKET_FOLDER_PATH)
else:
    raise Exception('Storage backend "{storage_backend}" not supported'.format(storage_backend=STORAGE_BACKEND))


###################
### APPLICATION ###
###################

ERROR_CODE = 500

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/available', methods=['GET'])
def get_available():
    return json.dumps(doc_storage.available_docs)


@app.route('/', methods=['GET'])
def home_get():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def home_post():
    if 'file' not in request.files:
        return redirect(request.url)
    doc_obj = request.files['file']
    if doc_obj:
        try:
            logger.info('Attempting to save {filename} document tarball.'.format(filename=doc_obj.filename))
            doc_id = doc_obj.filename.replace(".tar.gz", "")
            _, doc_name = doc_id.split('_', 1)
            doc_obj.seek(0)
            
            with TemporaryDirectory() as tmp_dir:
                tmp_tarball_fp = os.path.join(tmp_dir, doc_name + ".tar.gz")

                with open(tmp_tarball_fp, 'wb') as tmp_tarball_file:
                    copyfileobj(doc_obj, tmp_tarball_file, length=16384)

                doc_storage[doc_id] = tmp_tarball_fp
        except Exception as e:
            log_exception(raised_exception=e)
            abort(ERROR_CODE, 'Something failed with uploading, storing, or extracting your document tarball.')
        else:
            msg = "Document: {doc_name} was correctly uploaded, stored, and extracted.\n".format(doc_name=doc_name)
            return msg, 201

    return abort(400, 'You must upload a tarball file to use the POST endpoint.')


@app.route('/health')
def health():
    return 'OK\n', 200
