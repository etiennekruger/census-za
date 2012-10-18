#!/usr/bin/env python

try:
    import mapnik2 as mapnik
except:
    import mapnik

NUM_THREADS = 4

stylesheet = 'hh_density.xml'
image = 'hh_density.png'

m = mapnik.Map(1800,1200)
mapnik.load_map(m, stylesheet)
m.zoom_all()

mapnik.render_to_file(m, image)
print "Rendered map to '%s'." % (image)
