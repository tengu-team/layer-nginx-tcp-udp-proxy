# Layer-nginx-tcp-udp-proxy

# Overview
This layer configures TCP/UDP proxies for [NGINX](https://nginx.org/en/).
# Usage
Add the layer to your `layer.yaml`:

`includes: ['layer:nginx-tcp-udp-proxy']`

Add a relation with a charm that provides a [tcp](https://github.com/tengu-team/interface-tcp) or [udp](https://github.com/tengu-team/interface-udp) interface.

`juju add-relation nginx service`

## Authors

This software was created in the [IDLab research group](https://www.ugent.be/ea/idlab) of [Ghent University](https://www.ugent.be) in Belgium. This software is used in [Tengu](https://tengu.io), a project that aims to make experimenting with data frameworks and tools as easy as possible.

 - Sander Borny <sander.borny@ugent.be>

