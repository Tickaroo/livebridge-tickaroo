# livebridge-tickaroo

A [Tickaroo](https://www.tickaroo.com) plugin for [Livebridge](https://github.com/dpa-newslab/livebridge).

It allows to use Tickaroo tickers as target for [Livebridge](https://github.com/dpa-newslab/livebridge). 

[Converter](livebridge_tickaroo/converters/) from Liveblog to Tickaroo are part of this plugin.

## Installation
**Python>=3.5** is needed.
```sh
pip3 install livebridge-tickaroo
```
The plugin will be automatically detected and included from **livebridge** at start time, but it has to be available in **[PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)**.

See https://pythonhosted.org/livebridge/plugins.html#installing-plugins for more infos.

## Plugin specific control file parameters
Under **auth:**
* **client_id** - your Tickaroo client_id
* **client_secret** - your Tickaroo client_secret

Under **bridges:** and **targets**:
* **type: "tickaroo"**
* **ticker_id** - id from the Tickaroo ticker
* **endpoint** - the Tickaroo server Endpoint (e.g. https://staging.tickaroo.com/api/v5/ for staging, https://www.tickaroo.com/api/v5/ for live)

**Example:**
```
auth:
    tickaroo:
        client_id: "012345678909876543231XYZ"
        client_secret: "XYZ012345678909876543231"
bridges:
    - source_id: "56fceedda505e600f7195cch"
      endpoint: "https://liveblog.pro/api/"
      type: "liveblog"
      label: "Example"
      targets:
        - type: "tickaroo"
          ticker_id: "01238XYZ"
          auth: "tickaroo"
          endpoint: "https://staging.tickaroo.com/api/v5/"
```

See https://pythonhosted.org/livebridge/control.html for more infos.


## Testing
**Livebridge** uses [py.test](http://pytest.org/) and [asynctest](http://asynctest.readthedocs.io/) for testing.

Run tests:

```sh
    py.test -v tests/
```

## License
Copyright 2016 Tickaroo GmbH

Apache License, Version 2.0 - see LICENSE for details
