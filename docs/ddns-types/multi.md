---
title: "Multi-IP: v4m, v6m, m"
nav_order: 2020
parent: DDNS Types
---

# `v4m` and `v6m`

Short for "multiple", as in multiple IPs can be registered this way. For security/anti-abuse reasons, the requesting IP must be included in the JSON payload.

For these two endpoints you send a JSON array of strings, such as `["1.1.1.1", "8.8.8.8"]` (your own IP included here) and the server registers and returns all of them.

## `v4m`

Accepts input of IPv4 addresses. There are a variety of services to make finding your external IPv4 easy, or perhaps you're just on a cloud VPS with a public IP.

```bash
# One such address-returning service
my_ipv4=$(curl -4 ip.me)
# Also provided by the nanobots API:
my_ip=$(curl {{page.nanobots_api}}/ip/me)
```

If you have multiple interfaces, perhaps you'd want to run that command on each one (curl's `--interface` option) to get each IPv4.

## `v6m`

`jq` and the linux `ip --json` commands are especially useful here:

```bash
# Get local IPv6 addresses as a JSON array:
ip --json addr show scope global | \
  jq -cr '[(.[] | .addr_info[] | select(.family == "inet6") | .local)]'
# prints:
# ["2600:3c04::2000:ffff:fe6b:5707"]

# If you have lots of dynamic addresses or perhaps ULA addresses (like the docker daemon might create) you can use jq filters,
# this example works because we set IPv6 address tokens on the interfaces we care about ahead of time
ip --json addr show scope global | \
  jq -cr '[(.[] | .addr_info[] | select(.family == "inet6") | select(.local | test(":ffff:74")) | .local)]'
# prints:
# ["2606:83c0:2004:8606:ffff:74:8:42","2606:83c0:2004:8606:ffff:74:8:40"]
```

# `m`

`*.m.{{page.nanobots_domain}}` provides dual-stack resolution of multiple IP addresses based on the data from v4m and v6m requests.
