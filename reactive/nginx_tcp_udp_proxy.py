import os
from subprocess import run, CalledProcessError
from charms.reactive import (
    when, 
    when_not, 
    set_flag, 
    clear_flag,
    endpoint_from_flag,
)
from charmhelpers.core import unitdata
from charmhelpers.core.hookenv import log, status_set
from charmhelpers.core.templating import render
from charms.layer.nginx_config_helper import (
    NginxConfig, 
    NginxConfigError, 
    NginxModule,
)


########################################################################
# Install
########################################################################

@when('nginx-config.installed')
@when_not('nginx-tcp-udp-proxy.installed')
def install_nginx_tcp_udp_proxy():
    nginxcfg = NginxConfig()
    tcp_path = os.path.join(nginxcfg.streams_available_path, 'tcp')
    udp_path = os.path.join(nginxcfg.streams_available_path, 'udp')
    os.makedirs(tcp_path, exist_ok=True)
    os.makedirs(udp_path, exist_ok=True)
    set_flag('nginx-tcp-udp-proxy.installed')


########################################################################
# TCP Interface
########################################################################

@when('nginx-tcp-udp-proxy.installed',
      'endpoint.tcp.update')
def tcp_update():
    tcp = endpoint_from_flag('endpoint.tcp.update')
    services = tcp.tcp_services()
    if configure_services(services, 'tcp', 'tcp.tmpl'):
        clear_flag('endpoint.tcp.update')


########################################################################
# UDP Interface
########################################################################

@when('nginx-tcp-udp-proxy.installed',
      'endpoint.udp.update')
def udp_update():
    udp = endpoint_from_flag('endpoint.udp.update')
    services = udp.udp_services()
    if configure_services(services, 'udp', 'udp.tmpl'): 
        clear_flag('endpoint.udp.update')


########################################################################
# Helper methods
########################################################################


def configure_services(services, dir, templ):
    nginxcfg = NginxConfig()
    try:
        nginxcfg.delete_all_config(NginxModule.STREAM, subdir=dir)
        # Append a count to the filename to prevent duplicate filenames
        service_count = unitdata.kv().get('tcp_udp_service_count', 0)
        for service in services:
            ips = []
            ports = set()
            for host in service['hosts']:
                ips.append(host['host'])
                ports.add(host['port'])

            if not ips or len(ports) != 1:
                status_set('blocked', 
                        'Service ({}) has missing ip/port information.'
                                .format(service['service_name']))
                return
            port = ports.pop()
            service_context = {
                'upstream_name': "{}-{}".format(service['service_name'],
                                                service_count),
                'upstreams': ips,
                'port': port,
            }

            tcp_config = render(source=templ,
                                target=None,
                                context=service_context)
            
            nginxcfg.write_config(NginxModule.STREAM,
                                  tcp_config, 
                                  "{}-{}".format(service['service_name'],
                                                 service_count),
                                  subdir=dir)
            service_count += 1
        unitdata.kv().set('tcp_udp_service_count', service_count)
        nginxcfg.enable_all_config(NginxModule.STREAM, subdir=dir) \
                .validate_nginx() \
                .reload_nginx()
    except NginxConfigError as e:
        log(e)
        status_set('blocked', '{}'.format(e))
        return False
    return True