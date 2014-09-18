# standard library modules, , ,
import argparse
import errno
import logging
import os

# colorama, BSD 3-Clause license, color terminal output, pip install colorama
import colorama

# fsutils, , misc filesystem utils, internal
from lib import fsutils
# validate, , validate things, internal
from lib import validate
# folders, , get places to install things, internal
from . import folders
# install, , install subcommand, internal
from . import install

def addOptions(parser):
    parser.add_argument('component', default=None, nargs='?',
        help='Link a globally installed (or globally linked) module into'+
             'the current module\'s dependencies. If ommited, globally'+
             'link the current module.'
    )

def dropSudoPrivs(fn):
    running_as_root = (os.geteuid() == 0)
    if running_as_root and os.environ['SUDO_UID']:
        os.seteuid(int(os.environ['SUDO_UID']))
    r = fn()
    if running_as_root:
        os.seteuid(0)
    return r

def execCommand(args):
    c = validate.currentDirectoryModule()
    if not c:
        return 1
    if args.component:
        fsutils.mkDirP(os.path.join(os.getcwd(), 'yotta_modules'))
        src = os.path.join(folders.globalInstallDirectory(), args.component)
        dst = os.path.join(os.getcwd(), 'yotta_modules', args.component)
        # if the component is already installed, rm it
        fsutils.rmRf(dst)
    else:
        # run the install command first, if we're being run sudo'd, drop sudo
        # privileges for this
        args.act_globally = False
        dropSudoPrivs(lambda: install.execCommand(args))
        fsutils.mkDirP(folders.globalInstallDirectory())

        src = os.getcwd()
        dst = os.path.join(folders.globalInstallDirectory(), c.getName())

    if args.component:
        realsrc = os.path.realpath(src)
        if src == realsrc:
            logging.warning(
              ('%s -> %s -> ' % (dst, src)) + colorama.Fore.RED + 'BROKEN' + colorama.Fore.RESET
            )
        else:
            logging.info('%s -> %s -> %s' % (dst, src, realsrc))
    else:
        logging.info('%s -> %s' % (dst, src))

    fsutils.symlink(src, dst)

