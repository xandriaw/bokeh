import sys
import os
import time
from copy import deepcopy
from pprint import pprint
import json
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify

from bokeh.client import push_session
from bokeh.document import Document

import subprocess

DEBUG=True

app = Flask(__name__)
app.config.from_object(__name__)

sessions = {}

jss = []
scripts = []

# Define commands absolute paths
PY_EXECUTABLE = (sys.executable)
bin_folder = os.path.abspath(os.path.join(PY_EXECUTABLE, os.pardir))
BK_CMD = os.path.join(bin_folder, "bokeh")
JUPYTER_CMD = os.path.join(bin_folder, "jupyter")

# define current dir location
here = os.path.realpath(__file__)
here_dir = os.path.abspath(os.path.join(here, os.pardir))

args = sys.argv[1:]
if args:
    examples_dir = args[-1]
    if not os.path.exists(examples_dir):
        print ("PATH PROVIDED %s DO NOT EXIST. SWITCHING TO LOCAL PATH" % examples_dir)

        examples_dir = os.path.abspath(os.path.join(
            here, os.pardir, os.pardir, os.pardir, "examples"))
else:
    examples_dir = os.path.abspath(os.path.join(
        here, os.pardir, os.pardir, os.pardir, "examples"))

sessions_dir = os.path.abspath(os.path.join(
    here, os.pardir))
DEFAULT_SESSION_FILE = session_file = os.path.join(sessions_dir, "SESSION.json")



def is_server_app(path):
    if os.path.isdir(path):
        return True
    else:
        with open(path, 'r') as fp:
            content = fp.read()

        # TODO: THERE MUST BE A BETTER WAY TO CHECK THIS...
        if "output_file(" or "output_server(":
            return False

    return True



def get_cmd(some_file, notebook_options=""):
    """Determines how to open a file depending
    on whether it is a .py or a .ipynb file
    """

    if some_file.endswith('.py'):
        command = PY_EXECUTABLE
        args = []
    elif some_file.endswith('.ipynb'):
        command = JUPYTER_CMD
        args = ['notebook']
        if notebook_options:
            args.append(notebook_options)

    return command, args


def start_bokeh_server(force=False):
    """Print to screen what file is being opened and then open the file using
    the command method provided.
    """
    print ("USE SESSION SERVER?", Session.running_server)
    if Session.running_server:
        if force:
            Session.running_server.kill()
            Session.running_server = None
        else:
            print ("REUSING PREVIOUS SERVER SESSION")
            return Session.running_server

    kmd = "/Users/fpliger/miniconda3/envs/big_n/bin/bokeh serve"
    errored = False
    error = None
    result = None
    print ("STARTING BOKEH SERVER")
    with open('ERROUT.txt', 'w') as fp:
        try:
            Session.running_server = subprocess.Popen(kmd, shell=True)
            print ("STARTED BOKEH SERVER")
        except subprocess.CalledProcessError:
            print ("BOKEH SERVER ERRORED")
            errored = True

    if errored:
        with open('ERROUT.txt', 'r') as fp:
            error = fp.read()

    return error, Session.running_server


def opener(some_file, kommand, args, script_type):
    """Print to screen what file is being opened and then open the file using
    the command method provided.
    """

    errored = False
    error = None
    result = None
    with open('ERROUT.txt', 'w') as fp:
        # listener = get_listener()
        try:
            print ("STARTING", kommand, some_file)
            if not "jupyter" in kommand:
                if script_type == 'server app':
                    kmd = "%s serve %s" % (BK_CMD, some_file)

                    print ("SERVER SESSIONS TO CLOSE:", Session.running_server)
                    if Session.running_server:
                        Session.running_server.kill()
                        print ("SESSION STOPPED")

                    print ("RUNNING APP", kmd)
                    Session.running_server = subprocess.Popen(kmd, shell=True)
                    print ("DONE")
                    return None, Session.running_server

                elif script_type == 'server script':
                    # in this case we need to make sure we have a bokeh server
                    # running
                    start_bokeh_server(force=True)

                print  ('......')
                result = subprocess.check_output([kommand] + args + [some_file], stderr=fp)
                print ("FILE   EXECUTED")
            else:
                kmd = " ".join([kommand] + args + [some_file])
                result = subprocess.Popen(kmd, shell=True)

        except subprocess.CalledProcessError:
            errored = True

    if errored:
        with open('ERROUT.txt', 'r') as fp:
            error = fp.read()
    print ("ERRORS", errored, error)
    return error, result

def makeid(path):
    return path.replace('/', '_').replace('\\', '_').replace("__py", "").replace("__ipynb", "")

def get_image_file_path(path, example, parent):

    image_file = "%s.png" % example['id'].replace(parent['id'], '')
    image_path = "/static/images/examples/%s" % image_file
    file_path = os.path.join(here_dir, 'static', 'images', 'examples', image_file)

    if os.path.exists(file_path):
        return image_path
    else:
        return '/static/images/logo.png'

# def traverse_examplesOLD(path, level=3):
#     bad_prefixes = [".", "__"]
#     filesmap = {'type': 'folder', 'children': [], 'name': path, "id": makeid(path),
#         'shortname': os.path.split(path)[-1], 'files': [], 'folders': {},
#         'all_files': {}}
#
#     for firstlevel in os.listdir(path):
#         fullpath = os.path.join(path, firstlevel)
#         curr = None
#         if not any([firstlevel.startswith(k) for k in bad_prefixes]):
#             if os.path.isdir(fullpath):
#                 if level > 0:
#                     curr = traverse_examples(fullpath, level-1)
#                 else:
#                     curr = {'type': 'folder', 'children': [], 'name': fullpath,
#                         'shortname': firstlevel, 'files': [], 'folders': {}, "id": makeid(fullpath),
#                         'all_files': []}
#
#             elif firstlevel.endswith('.py') or firstlevel.endswith('.ipynb'):
#                 curr = {'type': 'file', 'children': [], 'name': fullpath, "id": makeid(fullpath),
#                     'shortname': firstlevel, 'files': [], 'folders': {}, 'status': '',
#                     'bug_report': ''}
#
#                 if firstlevel.endswith('.ipynb'):
#                     curr['script_type'] = 'jupyter notebook'
#                 else:
#                     source = Session.get_source(fullpath)
#                     # TODO: Those are very weak way of verifying the script type!!
#                     if "output_file(" in source:
#                         curr['script_type'] = 'file'
#
#                     elif "output_server(" in source or "push_session(" in source:
#                         curr['script_type'] = 'server script'
#
#                     else:
#                         # in this case assum it's a server app
#                         curr['script_type'] = 'server app'
#
#             if curr:
#                 filesmap['children'].append(curr)
#
#                 if curr['type'] == 'folder':
#                     filesmap['folders'][curr['shortname']] = curr
#                     filesmap['all_files'].update(curr['all_files'])
#                 else:
#                     filesmap['files'].append(curr['id'])
#                     filesmap['all_files'][curr['id']] = curr
#
#     return filesmap

def traverse_examples(path, level=3, parent=None):
    bad_prefixes = [".", "__"]

    filesmap = {'type': 'folder', 'children': [], 'name': path, "id": makeid(path),
        'shortname': os.path.split(path)[-1], 'files': [], 'all_folders': {},
        'relative_folders': {}, 'folders': [],
        'all_files': {}}

    parent = parent or filesmap

    for firstlevel in os.listdir(path):
        fullpath = os.path.join(path, firstlevel)
        curr = None
        if not any([firstlevel.startswith(k) for k in bad_prefixes]):
            if os.path.isdir(fullpath):
                if level > 0:
                    curr = traverse_examples(fullpath, level-1, parent)
                else:
                    curr = {'type': 'folder', 'children': [], 'name': fullpath,
                        'shortname': firstlevel, 'files': [], 'all_folders': {},
                        'relative_folders': {}, 'folders': [], "id": makeid(fullpath),
                        'all_files': [], }

            elif firstlevel.endswith('.py') or firstlevel.endswith('.ipynb'):
                curr = {'type': 'file', 'children': [], 'name': fullpath, "id": makeid(fullpath),
                    'shortname': firstlevel, 'files': [], 'all_folders': {},
                    'folders': [], 'status': '',
                    'bug_report': ''}

                curr['image_file'] = get_image_file_path(fullpath, curr, parent)

                if firstlevel.endswith('.ipynb'):
                    curr['script_type'] = 'jupyter notebook'
                else:
                    source = Session.get_source(curr)
                    # TODO: Those are very weak way of verifying the script type!!
                    if "output_file(" in source:
                        curr['script_type'] = 'file'

                    elif "output_server(" in source or "push_session(" in source:
                        curr['script_type'] = 'server script'

                    else:
                        # in this case assum it's a server app
                        curr['script_type'] = 'server app'

            if curr:
                if curr['type'] == 'folder':
                    filesmap['folders'].append(curr['id'])
                    filesmap['relative_folders'][curr['shortname']] = curr['id']
                    if parent:
                        parent['all_folders'][curr['id']] = curr
                else:
                    filesmap['files'].append(curr['id'])
                    if parent:
                        parent['all_files'][curr['id']] = curr

    return filesmap

class Session(object):
    open_ps = {}
    running_server = None
    def __init__(self, session=None, session_file=None):
        if not session_file:
            session_file = DEFAULT_SESSION_FILE
        self._session_file = session_file

        if not session:
            session = self.get_session(session_file)

        self._session = session

    @staticmethod
    def get_session(filename):
        if not os.path.exists(filename):
            examples = traverse_examples(examples_dir, 3)
            examples['session'] = {k: '' for k in examples['all_files']}
            examples['bugs'] = []
        else:
            with open(filename, 'r') as fp:
                examples = json.load(fp)

        examples['session'] = examples['all_files']

        return examples

    def save_session(self):
        self.clear_session(self._session_file)

        with open(self._session_file, 'w') as fp:
            json.dump(self._session, fp)

    @staticmethod
    def clear_session(session_file=None):
        if not session_file:
            session_file = DEFAULT_SESSION_FILE

        if os.path.exists(session_file):
            os.remove(session_file)

    def __getitem__(self, item):
        return self._session[item]

    def get_folders(self, folders):
        return [self.get_folder(k) for k in folders]

    def get_files(self, files):
        return [self.get_file(k) for k in files]

    def get_folder(self, id, convert_folders=True):
        try:
            folder = self._session['all_folders'][id]
        except KeyError:
            # Maybe a relative folder
            # TODO: should have  abetter way for doing this...
            folder = self._session['all_folders'][self['relative_folders'][id]]

        if convert_folders:
            folder['folders'] = {k: self.get_folder(k, False) for k in folder['folders']}

        folder['files'] = self.get_files(folder['files'])
        return folder

    def get_file(self, id):
        return self._session['all_files'][id]

    @property
    def my_folders(self):
        return self.get_folders(self['folders'])

    def count_folder_total_files(self, folder):
        files_count = len(folder['files'])

        try:
            for folder_ in folder['folders'].values():
                files_count += len(folder_['files'])

        except AttributeError:
            for folder_ in folder['folders']:
                files_count += len(folder_['files'])


        return files_count

    def count_folder_seen_files(self, folder):
        files_count = 0
        for file_ in folder['files']:
            if file_['status'] == 'seen':
                files_count += 1

        try:
            for folder_ in folder['folders'].values():
                for file_ in folder_['files']:
                    if file_['status'] == 'seen':
                        files_count += 1
        except AttributeError:
            for folder_ in folder['folders']:
                for file_ in folder_['files']:
                    if file_['status'] == 'seen':
                        files_count += 1

        return files_count

    @staticmethod
    def get_source(example):
        if example['type'] == 'file':
            with open(example['name'], 'r') as efile:
                return efile.read()
        raise NotImplementedError("Only files have source!")


@app.route('/')
def show_entries():
    # examples = get_session()
    examples = Session(session_file=session_file)
    def getter(x):
        return examples['session'].get(x)

    # import pdb; pdb.set_trace()
    return render_template('index.html', examples=examples, get_in_session=getter)


@app.route('/api/session')
def server_session():
    args = request.args
    # examples = get_session()
    examples = Session(session_file=session_file)

    folder_name = args.get('folder', "")

    if folder_name:
        return jsonify(examples.get_folder(folder_name))
    else:
        session = examples._session
        session['folders'] = {fn: examples.get_folder(fn) for fn in examples['folders']}

        return jsonify(session)


def run_example(path, notebook_options, script_type):
    command, args = get_cmd(path, notebook_options)

    return opener(path, command, args, script_type)

@app.route('/api/run', methods=['POST', 'OPTIONS'])
def run():
    examples = Session(session_file=session_file)
    args = request.form
    id_ = args['path']

    running_ps = set(Session.open_ps.keys())
    for rid in running_ps:
        proc = Session.open_ps.pop(rid)
        proc.kill()
        print ("Children process running", rid, "killed")

    example = examples.get_file(id_)
    try:
        error, result = run_example(
            example['name'],
            args.get('notebook_options', ''),
            example['script_type'])
        example['status'] = "seen"
        if result:
            Session.open_ps[id_] = result
        if error:
            example['bug_report'] = error

    except:
        example['status'] = ""
        example['bug_report'] = "unknown error executing example"
        example['bug_report_type'] = 'system'
        raise

    examples['all_files'][id_] = example
    examples.save_session()

    if 'server app' == example['script_type']:
        example['url_to_open'] = "http://localhost:5006/%s" % example['shortname'].\
            replace(".py", "").replace(".ipynb", "")
        # wait some time to let bokeh server start
        time.sleep(1.5)
    else:
        example['url_to_open'] = None

    return jsonify(example)


@app.route('/api/source', methods=['GET', 'OPTIONS'])
def get_source():
    examples = Session(session_file=session_file)
    args = request.values
    id_ = args['id']
    example = examples.get_file(id_)
    example['source'] = examples.get_source(example)

    return jsonify(example)


@app.route('/api/register_bug', methods=['POST', 'OPTIONS'])
def register_bug():
    examples = Session(session_file=session_file)
    args = request.form
    id_ = args['id']
    example = examples.get_file(id_)
    example['bug_report'] = args.get('bug_report')
    example['bug_report_type'] = 'user'

    examples['all_files'][id_] = example

    examples.save_session()

    return jsonify(example)


@app.route('/api/clear_session', methods=['POST'])
def get_scripts():
    Session.clear_session(session_file)
    return jsonify({'result': "OK"})


if __name__ == '__main__':
    app.run()
