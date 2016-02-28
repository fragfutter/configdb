# configdb

goal provide a restful interface to configuration data


### what should be stored
  * strings
  * integer
  * float
  * boolean
  * list/array
  * hash/dictionary
  * blob

### known configuration file formats
  * xml
  * yaml
  * json
  * java property files
  * ini files

### nice (future) features
  * include other sections
  * reference other sections
  * global defaults
  * inheritance
  * allow file format options (for example: equal sign or colon in ini)

### questions
if the base format is a json or yaml like format. How to store xml node attributes. Should xml nodes always be 
```
<foo a="42" b="43">bar</foo>
foo:
  _value: bar
  _properties:
    a: 42
    b: 43
```

and without properties
```
<foo>bar</foo>

foo: bar
```
