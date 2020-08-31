import os
import sys
import logging
import argparse

import spdyn_update.spdyn as spdyn
import spdyn_update.consts as consts


def main():
    spdyn_folder = os.path.expandvars(consts.SPDYN_FOLDER)
    if not os.path.exists(spdyn_folder):
        os.mkdir(spdyn_folder)
    spdyn_update = spdyn.SpDynUpdate()
    parser = argparse.ArgumentParser(prog='spdyn-update', usage="""How to use:...
    do 1
    do 2""")
    subparsers = parser.add_subparsers(title='sub commands')
    list_parser = subparsers.add_parser('list', help='list help')
    list_parser.set_defaults(func=spdyn_update.list)
    update_parser = subparsers.add_parser('update', help='update help')
    update_parser.add_argument('-l', '--log', type=argparse.FileType('a'), help='log file path', required=False)
    update_parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    update_parser.add_argument('-c', '--config', type=argparse.FileType('a'), help='config file path', required=False)
    update_parser.set_defaults(func=spdyn_update.update)
    config_parser = subparsers.add_parser('config', help='config help')
    config_parser.add_argument('-n', '--host', help='host address', required=False)
    config_parser.add_argument('-u', '--user', help='username', required=False)
    config_parser.add_argument('-p', '--password', help='password (not secured) or token', required=False)
    config_parser.add_argument('-f', '--file', help='file path to save config',
                               type=argparse.FileType('a'), required=False)
    config_parser.set_defaults(func=spdyn_update.config)
    print_parser = config_parser.add_subparsers(title='config sub commands').add_parser('print',
                                                                                        help='print config help')
    print_parser.add_argument('-c', '--config', type=argparse.FileType('a'), help='config file path', required=False)
    print_parser.set_defaults(func=spdyn_update.print_config)
    # parse arguments
    args = parser.parse_args()

    # logging
    root = logging.getLogger()
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s  | %(asctime)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # invoke requested method
    args.func(args)


if __name__ == "__main__":
    main()


