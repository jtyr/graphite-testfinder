Test Finder for Graphite
========================


Description
-----------

This is a custom finder for Graphite which returns random data timeserie. It's
especially suitable for testing.


Installation
------------

Download the finder into your Python `lib` directory:

```
git clone https://github.com/jtyr/graphite-testfinder.git \
  /path/to/lib/python/graphite-testfinder
```

Add the `graphite-testfinder.finder.TestFinder` into the
`/opt/graphite/webapp/graphite/settings.py`:

```
STORAGE_FINDERS = (
    'graphite.finders.standard.StandardFinder',
    'graphite-testfinder.finder.TestFinder',
)
```

Specify path to the module in the `--libs` command line option. For example:

```
sudo python /opt/graphite/bin/run-graphite-devel-server.py \
  --libs /path/to/lib/python/ /opt/graphite/
```


Dependencies
------------

- `graphite`


Sources
-------

http://graphite.readthedocs.org/en/latest/storage-backends.html


Author
------

Jiri Tyr <jiri.tyr@gmail.com>
