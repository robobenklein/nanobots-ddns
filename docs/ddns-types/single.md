---
title: "Most basic: `v4`, `v6`, `ds`"
nav_order: 2010
parent: DDNS Types
---

# `v4` and `v6`

`*.v4.{{page.nanobots_domain}}` and `*.v6.{{page.nanobots_domain}}`

The v4 and v6 types do not take any inputs, and will set the the UUID subdomain to the IP the request came from.

You can use them like:

```bash
# IPv4
curl -4sSLX POST '{{page.nanobots_api}}/v4/SomewhereOverTheRainbow'
# IPv6
curl -6sSLX POST '{{page.nanobots_api}}/v6/SomewhereOverTheRainbow'
```

These will cause their respective updates to the UUID subdomain,

```bash
# v4
dig +short A 527e640f-5511-5bca-c4d3-ae1cf6cf3122.v4.{{page.nanobots_domain}}
# v6
dig +short AAAA 527e640f-5511-5bca-c4d3-ae1cf6cf3122.v6.{{page.nanobots_domain}}
```

# `ds` (`*.ds.{{page.nanobots_domain}}`)

Short for "dual-stack", this reads records submitted via both `v4` and `v6` API routes, and returns the address family requested (A or AAAA).

```bash
# v4
dig +short A 527e640f-5511-5bca-c4d3-ae1cf6cf3122.ds.{{page.nanobots_domain}}
# v6
dig +short AAAA 527e640f-5511-5bca-c4d3-ae1cf6cf3122.ds.{{page.nanobots_domain}}
```
