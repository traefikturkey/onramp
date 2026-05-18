# Search Indexing

OnRamp sends `X-Robots-Tag: none,noarchive,nosnippet,notranslate,noimageindex,` by default through the Traefik `default-headers` middleware. This keeps newly exposed services out of search indexes unless you explicitly opt in.

## Allow Indexing For A Docker Service

Services that define a router-level middleware label can opt in by appending `allow-indexing-headers@file` to that router's middleware chain.

For a service whose only router middleware is the default headers middleware:

```bash
FEISHIN_MIDDLEWARES=default-headers@file,allow-indexing-headers@file
```

For a service with functional middleware, keep the existing middleware and append `allow-indexing-headers@file`:

```bash
MINIO_MIDDLEWARES=gzip-compress@docker,allow-indexing-headers@file
PIHOLE_MIDDLEWARES=piholeredirect,allow-indexing-headers@file
OPENSPEEDTEST_MIDDLEWARES=limit,allow-indexing-headers@file
```

Do not remove existing middleware unless you mean to remove its behavior. Some middleware handles redirects, buffering limits, compression, authentication, or other routing behavior.

## Allow Indexing For An External Service

External services use file-provider YAML. Add `allow-indexing-headers` after `default-headers` on the external router:

```yaml
http:
  routers:
    myservice:
      middlewares:
        - default-headers
        - allow-indexing-headers
```

The ordering matters. `allow-indexing-headers` removes the `X-Robots-Tag` response header after `default-headers` sets it.
