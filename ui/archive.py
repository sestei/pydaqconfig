from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

import time
import os.path
import daq.utils as utils

try:
    import pysvn
    HAS_PYSVN = True
except ImportError:
    HAS_PYSVN = False

ENV_SVN_DAQ_CHANS = 'PYDAQCONFIG_SVN_CHAN_DIR'
ENV_SVN_CREDENTIALS = 'PYDAQCONFIG_SVN_CREDENTIALS'

def wait_cursor(fn):
    def decorator(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        retval = None
        try:
            retval = fn(*args, **kwargs)
        finally:
            QApplication.restoreOverrideCursor()
        return retval
    return decorator

def get_login(realm, username, may_save):
    credentials = utils.get_env_variable(ENV_SVN_CREDENTIALS)
    if not credentials:
        QMessageBox.critical(parent, 'SVN Credentials not set', 
            ('Please set the environmental variable {0} to '+
            'the subversion login credentials (username:password).').format(
                ENV_SVN_DAQ_CHANS))
    user, passwd = credentials.split(':')
    return True, user, passwd, True

def get_svn_directory(parent = None):
    svndir = utils.get_env_variable(ENV_SVN_DAQ_CHANS)
    if not svndir:
        QMessageBox.critical(parent, 'Unable to access archive', 
            ('Please set the environmental variable {0} to '+
            'the subversion directory which contains the DAQ .ini files.').format(
                ENV_SVN_DAQ_CHANS))
    return svndir

class ArchivedIni(object):
    def __init__(self, modelname, inifile, log):
        self._inifile = inifile
        self.modelname = modelname
        self._log = log
        self.date = time.ctime(log.date)

    @property
    def revision(self):
        return self._log.revision.number

    @property
    def message(self):
        return self._log.message
    
    def __str__(self):
        return '{a.modelname} @ {a.date} [rev #{a.revision}]'.format(a=self)

    def contents(self):
        try:
            import pysvn
        except ImportError:
            return None

        client = pysvn.Client()
        return client.cat(self._inifile, revision=self._log.revision)
            
class ArchiveDialog(QDialog):
    def __init__(self, parent, modelname):
        super(ArchiveDialog, self).__init__(parent)
        uic.loadUi('ui/archive.ui', self)
        self._archive = []
        self._modelname = modelname
        
        self.lblArchive.setText(self.lblArchive.text() + modelname + ':')
        if HAS_PYSVN:
            self.load_archive()
            self.update_list()
        else:
            self.set_no_archive()

    def set_no_archive(self, e=None):
        self.lstArchive.addItem('No archived versions available')
        if e:
            self.lstArchive.addItem(str(e))
        self.lstArchive.setEnabled(False)

    @wait_cursor
    def load_archive(self):
        try:
            client = pysvn.Client()
            client.callback_get_login = get_login
            folder = get_svn_directory(self)
            inifile = os.path.join(folder, self._modelname+'.ini')
            client.update(inifile)
            for log in client.log(inifile):
                self._archive.append(ArchivedIni(self._modelname, inifile, log))
        except pysvn.ClientError as e:
            self.set_no_archive(e)

    def update_list(self):
        for a in self._archive:
            item = QListWidgetItem()
            item.setText(str(a))
            item.setToolTip(a.message)
            self.lstArchive.addItem(item)
        self.lstArchive.setCurrentRow(0)

    @wait_cursor
    def get_archived_ini(self):
        row = self.lstArchive.currentRow()
        if row < 0 or not self.lstArchive.isEnabled():
            return None
        else:
            return self._archive[row]
