citygml-solidifier
==================

Takes a CityGML file with Buildings stored as __gml:MultiSurfaces__ and creates __gml:Solids__. It doesn't modify the geometries nor validate them, it just converts the tags (or add new ones) so that buildings are 'bundled' as __gml:Solid__ too. The rationale is that often buildings are solids and should be represented as such (it permits to for instance calculate the volume of a building, its surface area, etc.).

`$ python ./solidifier.py in.gml > out.gml`


## Current limitations

  * doesn't support __gml:Solid__ with interior shells
  * only one LOD per building is supported
