#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import string
import base64
import datetime
import logging
import StringIO
import mimetypes
import hashlib

import filestorage
import flask
from werkzeug.utils import secure_filename

#### Init Logger
logging.getLogger().setLevel(logging.INFO)

#### Create App and configuration
app = flask.Flask(__name__)
app.config['verbose'] = 1
app.config['maxsize'] = 0
app.config['root_path'] = '/tmp/upload';

FS = filestorage.FileStorage(app.config)
FS.initialize()

def ajax_response(resp):
    return json.dumps(resp)

@app.errorhandler(500)
def internal_error(e):
    return ajax_response({'status':-1, 'msg':'Internal error'})

@app.route('/app/file/upload', methods=['POST'])
def upload():
    def upload_single_file(fobj):
        result = {}
        buffio = StringIO.StringIO()
        fobj.save(buffio)
        buffio.seek(0, os.SEEK_END)
        file_length = buffio.tell()
        buffio.seek(0)

        file_name = secure_filename(fobj.filename)
        tmp_path = os.path.join(app.config['root_path'], file_name)

        try:
            fp = open(tmp_path, 'w')
        except:
            logging.error("failed to open {0}".format(tmp_path))
            result['error'] = 'open temp file'
            return result

        m = hashlib.sha256()
        while True:
            buff = buffio.read(4096)
            if not buff:
                break;
            m.update(buff)
            fp.write(buff)

        fp.close()
        buffio.close()
        file_hash = m.hexdigest()
        new_path = os.path.join(app.config['root_path'], file_hash[0],
                                file_hash[1], file_hash)

        if os.path.isfile(new_path):
            logging.info("file {0} already exists".format(new_path))
            file_id = FS.get_file_id(file_hash)
            result['file_id'] = file_id
            return result

        os.makedirs(os.path.dirname(new_path))
        try:
            os.rename(tmp_path, new_path)
        except:
            logging.error("move {0} to {1} error".format(tmp_path, new_path))
            result['error'] = 'move file'
            return result

        file_id = FS.add(file_hash, file_name, file_length, new_path)
        logging.info('save file {0} to {1}, file id is {2}'.format(file_name, new_path, file_id))

        result['file_id'] = file_id
        result['file_hash'] = file_hash

        return result

    if 'file' not in flask.request.files:
        return ajax_response({'status':2, 'msg':'No file selected'})

    result = {'status':0, 'msg':'success', 'result':[]}
    for upload in flask.request.files.getlist("file"):
        r = upload_single_file(upload)
        result['result'].append(r)

    return ajax_response(result)

@app.route('/app/file/download', methods=['GET'])
def download():
    file_id = flask.request.args.get('file_id')
    if not file_id:
        logging.error('No file_id query string provided')
        return 'Invalid Parameter'

    result = FS.get(file_id)
    if not result:
        msg = 'No record for {0}'.format(file_id)
        logging.error(msg)
        return msg

    file_name, file_size, file_path = result
    if not os.path.isfile(file_path):
        msg = 'File id:{0} name:{1} no longer exists'.format(file_id, file_name)
        logging.error(msg)
        return msg

    response = flask.make_response(flask.send_file(file_path))
    response.headers['Content-Type'] = mimetypes.guess_type(file_name)[0]
    response.headers['Content-Disposition'] = 'attachment; filename="%s"' % file_name

    return response

if __name__ == "__main__":
    app.run('0.0.0.0')
