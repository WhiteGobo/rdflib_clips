import setuptools

setuptools.setup(
    name='rdflib_clips',
    version='0.1',
    description='Parser and serializer as plugin for rdflib to clips',
    long_description="""This module enables the communcation between clips
        and rdflib. It provides a serializer and parser plugin for rdflib
        to clips.
        """,
    long_description_content_type="text/markdown",

    # url="https://example.com/rif-parser-rdflib",
    
    author='Richard Focke Fechner',
    author_email='richardfechner@posteo.net',

    py_modules=['rdflib_clips'],
    #scripts = ['rif_parser.py',],

    packages=setuptools.find_packages(),
    install_requires=['rdflib', 're', 'tempfile'],
    
    # Classifiers allow your Package to be categorized based on functionality
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    # Entry points speficy, what is the functionability in rdflib
    # Also this sepicifies, how the plugin is reached
    entry_points = {
        # rdflib.Graph().parse( source, format="rif"/"application/rif+xml" )
        'rdf.plugins.parser': [
            'clp = rdflib_clips.clips_parser:ClipsParser',
            'Clips = rdflib_clips.clips_parser:ClipsParser',
            'clips = rdflib_clips.clips_parser:ClipsParser',
        ],
        'rdf.plugins.serializer': [
            'clp = rdflib_clips.serializer:ClipsSerializer',
            'Clips = rdflib_clips.serializer:ClipsSerializer',
            'clips = rdflib_clips.serializer:ClipsSerializer',
        ],
    },

    extras_require = {
        'builtinlogic':  ["clipspy"],
        'test':  ["clipspy", "pathlib", "os"],
    },
)
