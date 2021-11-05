import time
import os.path
import subprocess
import wlanpi_fpms.modules.wlanpi_oled as oled

from wlanpi_fpms.modules.pages.alert import Alert
from wlanpi_fpms.modules.pages.simpletable import SimpleTable
from wlanpi_fpms.modules.constants import (
    WCONSOLE_SWITCHER_FILE,
    HOTSPOT_SWITCHER_FILE,
    WIPERF_SWITCHER_FILE,
    SERVER_SWITCHER_FILE,
)

class Mode(object):

    def __init__(self, g_vars):

        # create simple table
        self.simple_table_obj = SimpleTable(g_vars)

        # create alert
        self.alert_obj = Alert(g_vars)

    def switcher(self, g_vars, resource_title, resource_switcher_file, mode_name):
        '''
        Function to perform generic set of operations to switch wlanpi mode
        '''

        reboot_image = g_vars['reboot_image']

        # check resource is available
        if not os.path.isfile(resource_switcher_file):

            self.alert_obj.display_alert_error(g_vars, '{} mode not available.'.format(resource_title))
            g_vars['display_state'] = 'page'
            return

        # Resource switcher was detected, so assume it's installed
        if g_vars['current_mode'] == "classic":
            # if in classic mode, switch to the resource
            alert_msg = 'Switching to {} mode (rebooting...)'.format(resource_title)
            switch = "on"
        elif g_vars['current_mode'] == mode_name:
            alert_msg = 'Switching to Classic mode (rebooting...)'
            switch = "off"
        else:
            self.alert_obj.display_alert_error(g_vars, 'Unknown mode: {}'.format(g_vars['current_mode']))
            g_vars['display_state'] = 'page'
            return False

        # Flip the mode
        self.alert_obj.display_alert_info(g_vars, alert_msg, title="Success")
        g_vars['shutdown_in_progress'] = True
        time.sleep(2)

        oled.drawImage(g_vars['reboot_image'])
        g_vars['screen_cleared'] = True

        try:
            alert_msg = subprocess.check_output("{} {}".format(resource_switcher_file, switch), shell=True).decode()  # reboots
            time.sleep(1)
        except subprocess.CalledProcessError as exc:
            alert_msg = exc.output.decode()

        # We only get to this point if the switch has failed for some reason
        # (Note that the switcher script reboots the WLANPi)
        g_vars['shutdown_in_progress'] = False
        g_vars['screen_cleared'] = False
        self.alert_obj.display_alert_error(g_vars, alert_msg)
        g_vars['display_state'] = 'menu'

        # allow 5 secs to view failure msg
        time.sleep(3)
        # move back up to menu branch
        g_vars['current_menu_location'].pop()

        return False

    def wconsole_switcher(self, g_vars):

        wconsole_switcher_file = WCONSOLE_SWITCHER_FILE

        resource_title = "Wi-Fi Console"
        mode_name = "wconsole"
        resource_switcher_file = wconsole_switcher_file

        # switch
        self.switcher(g_vars, resource_title, resource_switcher_file, mode_name)
        return True


    def hotspot_switcher(self, g_vars):

        hotspot_switcher_file = HOTSPOT_SWITCHER_FILE

        resource_title = "Hotspot"
        mode_name = "hotspot"
        resource_switcher_file = hotspot_switcher_file

        self.switcher(g_vars, resource_title, resource_switcher_file, mode_name)
        return True


    def wiperf_switcher(self, g_vars):

        wiperf_switcher_file = WIPERF_SWITCHER_FILE

        resource_title = "Wiperf"
        mode_name = "wiperf"
        resource_switcher_file = wiperf_switcher_file

        self.switcher(g_vars, resource_title, resource_switcher_file, mode_name)
        return True


    def server_switcher(self, g_vars):

        server_switcher_file = SERVER_SWITCHER_FILE

        resource_title = "Server"
        mode_name = "server"
        resource_switcher_file = server_switcher_file

        self.switcher(g_vars, resource_title, resource_switcher_file, mode_name)
        return True
