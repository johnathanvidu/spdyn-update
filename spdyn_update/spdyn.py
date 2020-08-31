import os
import getpass
import logging
import ipaddress
import configparser
import urllib.request as urllib

import spdyn_update.consts as consts

from urllib.parse import urlencode

logger = logging.getLogger(__name__)

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
        spdyn_config['current_ip'] = ''

        # saving to config file
        self._save_config(args.file, config)

        logger.info(' [*] success!')

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
        success = False
        logger.info(' [*] update requested')

        if args.config is None:
            args.config = os.path.join(os.path.expandvars(consts.SPDYN_FOLDER), 'config.ini')

        config = configparser.ConfigParser()
        config.read(args.config)
        site_conf = config['spdyn.de']
        curr_ip = site_conf['current_ip'] or '0.0.0.0'  # fallback to 0.0.0.0 (shouldn't affect the operation)

        for address in ADDRESSES:
            ipaddr = urllib.urlopen(address).read().decode('utf-8')

            logger.debug(f' [!] checking the validity of {ipaddr}')
            if not self._valid_address(ipaddr):
                logger.debug(' [!] invalid, skipping...')
                continue
            if ipaddress.IPv4Address(ipaddr) == ipaddress.IPv4Address(curr_ip):  # if ip address hasn't changed there's no need to flood the dns provider
                logger.debug(' [!] matching ip address, skipping...')
                break

            query_str = urlencode({
                'hostname': site_conf['host'],
                'myip': ipaddr,
                'user': site_conf['user'],
                'pass': site_conf['password']})
            url = 'https://update.spdyn.de/nic/update'
            logger.info(f' [*] address found: {ipaddr}')
            logger.debug(f' [*] update url -{url}?%s{query_str}')
            response_code = self._send_update_request(url, query_str)  # actual update request
            if response_code == 200:  
                success = True
                site_conf['current_ip'] = ipaddr  # update config with current successful ip update
                self._save_config(args.config, config)
                logger.debug(' [!] config updated with a new shiny ip address')
            break
        logger.info(' [*] done - success') if success else logger.info(' [*] done - nothing happened')

    def _save_config(self, path, config):
        with open(path, 'w') as configfile:
            config.write(configfile)

    def _valid_address(self, ipaddr):
        try:
            ipaddress.IPv4Address(ipaddr)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False

    def _send_update_request(self, url, query_str):
        try:
            request = urllib.Request(url, query_str.encode('utf-8'))
            response = urllib.urlopen(request)
            result = response.read()
            logger.info(f' [*] result - {result}')  # result should look like - good <ip-addr>
            return response.getcode()
        except Exception as e:
            logger.error(f' [x] error occured while trying to update ip. message: {str(e)}')
