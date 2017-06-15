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

#### Create App and configuration
app = flask.Flask(__name__)
app.config['verbose'] = 1
app.config['root_path'] = '/tmp/upload';

filestore = filestorage.FileStorage(app.config)

def ajax_response(resp):
    return json.dumps(resp)

@app.errorhandler(500)
def internal_error(e):
    return ajax_response({'status':-1, 'msg':'Internal error'})

@app.route('/app/file/upload', methods=['POST'])
def upload():
    if 'files' not in flask.request.files:
        return ajax_response({'status':2, 'msg':'No file selected'})

    file = flask.request.files['files']

    buffio = StringIO.StringIO()
    file.save(buffio)
    buffio.seek(0, os.SEEK_END)
    file_length = buffio.tell()
    buffio.seek(0)

    file_name = secure_filename(file.filename)
    tmp_path = os.path.join(app.config['root_path'], file_name)

    try:
        fp = open(tmp_path, 'w')
    except:
        return ajax_response({'status':2, 'msg':'Open file error'})

    m = hashlib.sha1()
    while True:
        buff = buffio.read(4096)
        if not buff:
            break;
        m.update(buff)
        fp.write(buff)

    fp.close()
    buffio.close()
    file_hash = m.hexdigest()
    new_path = os.path.join(app.config['root_path'], file_hash[0], file_hash[1], file_hash)

    try:
        os.makedirs(os.path.dirname(new_path))
        os.rename(tmp_path, new_path)
    except:
        return ajax_response({'status':2, 'msg':'Move file error'})

    file_id = filestore.add(file_name, file_length, file_hash, new_path)

    logging.info('save file{0} to {0}'.format(file_name, new_path))
    result = {'status':0, 'msg':'success', 'hash':file_hash, 'file_id': file_id}
    return ajax_response(result)

@app.route('/app/file/download', methods=['GET'])
def download():
    file_id = flask.request.args.get('file_id')
    if not file_id:
        logging.error('No file_id query string provided')
        return 'Invalid Parameter'

    result = filestore.get(file_id)
    if not result:
        msg = 'No record for {0}'.format(file_id)
        logging.error(msg)
        return msg

    file_name, file_size, _, file_path = result
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
