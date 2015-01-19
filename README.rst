TFS Tools
=========

Team Foundation Server commandline utility. Implements some useful commands
otherwise missing from tf.exe. Written in Python.


Usage
-----

Automate (recursively) destroying itemspecs (folders, branches, files) that are
older than N days:

.. code:: bash
     
    $ python tft.py -vn destroy -d 90 $/THOR/Tags/

Means destroy every brancher under '$/THOR/Tags' older than 90 days without
confirmation (-n).


License
-------

Copyright 2015 Sascha Peilicke

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
