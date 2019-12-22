import os
import getpass
import ipaddress
import configparser
import urllib.request as urllib

import spdyn_update.consts as consts

from urllib.parse import urlencode

ADDRESSES = ['https://api.ipify.org', 'http://checkip4.spdns.de']


class SpDynUpdate(object):
    def __init__(self):
        pass

    def list(self, args):
        print('list of available addresses')
        for index, address in enumerate(ADDRESSES):
            print(' [*]', index + 1, '-', address)

    def config(self, args):
        # arguments handling
        if args.host is None:
            args.host = input(' [?] please enter the desired host you wish to update (no need for http/https): ')
        if args.user is None:
            args.user = input(' [?] please enter your spdyn.de username: ')
        if args.password is None:
            args.password = getpass.getpass(' [?] please enter your spdyn.de password (not secured) | or token: ')

        # config file path handling
        if args.file is None:
            save_to = input(' [?] saving into %s%s(config.ini)? [Y/n] ' %
                            (os.path.expandvars(consts.SPDYN_FOLDER), os.path.sep)).lower()
            if save_to == 'n' or save_to == 'no':
                args.file = input(' [?] please enter config full path: ')
            else:
                args.file = os.path.join(os.path.expandvars(consts.SPDYN_FOLDER), 'config.ini')

        # setting the config parser
        config = configparser.ConfigParser()
        config['spdyn.de'] = {}
        spdyn_config = config['spdyn.de']
        spdyn_config['host'] = args.host
        spdyn_config['user'] = args.user
        spdyn_config['password'] = args.password

        # saving to config file
        with open(args.file, 'w') as configfile:
            config.write(configfile)

        print(' [*] success!')

    def print_config(self, args):
        if args.config is None:
            args.config = os.path.join(os.path.expandvars(consts.SPDYN_FOLDER), 'config.ini')

        config = configparser.ConfigParser()
        config.read(args.config)
        for section in config.sections():
            print('[%s]' % section)
            for key, value in config.items(section):
                print('%s=%s' % (key, value))

    def update(self, args):
        if args.config is None:
            args.config = os.path.join(os.path.expandvars(consts.SPDYN_FOLDER), 'config.ini')

        config = configparser.ConfigParser()
        config.read(args.config)
        site_conf = config['spdyn.de']

        for address in ADDRESSES:
            ipaddr = urllib.urlopen(address).read().decode('utf-8')
            if not self._valid_address(ipaddr):
                continue
            query_str = urlencode({
                'hostname': site_conf['host'],
                'myip': ipaddr,
                'user': site_conf['user'],
                'pass': site_conf['password']})
            url = 'https://update.spdyn.de/nic/update'
            print(' [*] address found:', ipaddr)
            print(' [*] update url -', url + '?%s' % query_str)
            # pwd_mgr = urllib.HTTPPasswordMgr()
            # pwd_mgr.add_password("spdyn nic update", url, , )
            # handler = urllib.HTTPBasicAuthHandler()
            # opener = urllib.build_opener(handler)
            # opener_open = opener.open(url)
            # result = opener_open.read()
            request = urllib.Request(url, query_str.encode('utf-8'))
            result = urllib.urlopen(request).read()
            print(' [*] result -', result)
            # result should look like - good <ip-addr>
            print(' [*] done')
            break

    def _valid_address(self, ipaddr):
        try:
            ipaddress.IPv4Address(ipaddr)
            return True
        except (ipaddress.AddressValueError, ValueError) as e:
            return False
