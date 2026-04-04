---
title: DDNS Types
nav_order: 20
---

The nanobots DDNS service exposes a variety of DDNS behaviors under different API routes and subdomains. These 'types' are identified by a short name in the API route and the DNS subdomain.

For this instance, the API is hosted at `{{page.nanobots_api}}` and the DNS TLD is `{{page.nanobots_domain}}`

Check the navigation sidebar to see more information about each type, including sample usages, scripts, and behavior details.

Overview:

|Type|Desc|
|--|--|
|`v4`|IPv4 single-address|
|`v6`|IPv6 single-address|
|`ds`|IPv4 and IPv6, based on query type with data provided by `v4` or `v6`|
|`v4m`|Multi-address IPv4|
|`v6m`|Multi-address IPv6|
|`m`|IPv4 and IPv6, based on query type with data provided by `v4m` or `v6m`|

# Common behaviors

The default behavior is to return successful responses (2xx-3xx) in JSON format, and error responses (4xx-5xx) in plain text.

If a route takes request input, it will normally be JSON. Send `Content-Type: application/json` when you do, or your tooling might do that for you. (like `httpie`)


