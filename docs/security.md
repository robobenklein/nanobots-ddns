---
title: Security
nav_order: 70
---

Obviously being a service with no accounts, registration, or moderation controls of any kind, a working security model is needed to prevent abuse.

# Secrets and UUID DNS names

The first and most unique concept with this service is how you ensure that nobody else can point your DDNS name to a malicious server. This is accomplished using the Key Derivation Function `bcrypt`, along with a secret salt only the server knows.

This ensures that only someone who knows the original secret input (part of the request to the API) can update that specific UUID DNS name. Great! We don't need to store the secret, and with a serverside salt (+ratelimiting) the name is protected against bruteforcing.

Generally any secret with an entropy over 128 bits will be plenty, after all the UUIDs produced are only 128-bit anyways. Notably IPv6 addresses are also 128-bit, but there are far more possible UUIDs than IPv6 addresses for now at least until the nanobot swarm consumes a significant portion of the planet, at which point we probably have bigger things to worry about.

# Ratelimits

In order to keep the service online certain limitations have to be put in place, and since the secret is freeform and we don't have any form of authentication, we have to rely on IP-based rate limiting.

While IPv4 addresses are costly enough to limit per each, [IPv6 addresses can be quickly exhausted up to 2^64](https://brutecat.com/articles/leaking-google-phones) without too much cost.

So for ratelimiting purposes, an IPv4 is considered as approximately the same vulnerability surface as a IPv6 `/64`. Of course, it would be great if each DDNS request type had it's own limit counter, but I haven't implemented that part yet. Fingers crossed I don't need to get too restrictive with the limits.

# Requiring Authentication

So what if you *do* want to keep your own service private? e.g. you're using this in an environment where performance and uptime is a critical necessity.

## Web API

I recommend you put the authentication layer at the reverse proxy to the API. The nanobots DDNS web API doesn't care about any of the other headers, so you are free to use whichever authentication scheme you desire or that your reverse proxy supports. The bottle-based web API shouldn't be run outside a proxy anyways as it depends on accurate X-Forwarded-For headers, along with all the reasons bottle isn't suitable to be directly exposed.

I use Caddy personally, so one example would be [https://caddyserver.com/docs/caddyfile/directives/basic_auth](https://caddyserver.com/docs/caddyfile/directives/basic_auth)

## DNS provider

The DNS service is exclusively using read-only logic and does not allow listing known UUIDs. Therefore there isn't much reason to require authentication for the DNS queries. Follow [the nserver recommendation of placing the nanobots DNS server behind a proxy](https://nhairs.github.io/nserver/latest/production-deployment/)
