import os
import os.path
import base64

# import traitlets.config import Config
from traitlets import default, Unicode
from nbconvert.exporters.html import HTMLExporter
from traitlets.log import get_logger
from ipython_genutils.ipstruct import Struct

try:
    from urllib.request import urlopen  # py3
except ImportError:
    from urllib2 import urlopen

class HideCode2HTMLExporter(HTMLExporter):
    def __init__(self, config=None, **kw):
        # self.register_preprocessor('hide_code.HideCodePreprocessor', True)
        super(HideCode2HTMLExporter, self).__init__(config, **kw)
        # self.preprocessors = ['hide_code.HideCodePreprocessor']
        # self._init_preprocessors()
         self.inliner_resources['css'].append("""
/* no local copies of fontawesome fonts in basic templates, so use cdn */
@import url(https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css)
""")  # noqa: E501

        ch_dir = os.path.join(
            os.path.dirname(contrib_init), 'nbextensions',
            'collapsible_headings')

        with open(os.path.join(ch_dir, 'main.css'), 'r') as f:
            self.inliner_resources['css'].append(f.read())

        with open(os.path.join(ch_dir, 'main.js'), 'r') as f:
            self.inliner_resources['js'].append(f.read())

        cm = ConfigManager()
        collapsible_headings_options = cm.get('notebook').get(
            'collapsible_headings', {})
        self.inliner_resources['js'].append("""
$(document).ready(function () {
    require(['nbextensions/collapsible_headings/main'], function (ch) {
        ch.set_collapsible_headings_options(%s);
        ch.refresh_all_headings();
    });
});
""" % json.dumps(collapsible_headings_options))

    def from_notebook_node(self, nb, resources=None, **kw):
        # The parent nbconvert_support module imports this module, and
        # nbconvert_support is imported as part of our install scripts, and
        # other fairly basic stuff.
        # By keeping lxml import in this method, we can still import this
        # module even if lxml isn't available, or is missing dependencies, etc.
        # In this way, problems with lxml should only bother people who are
        # actually trying to *use* this.
        import lxml.etree as et
        output, resources = super(
            HideCode2HTMLExporter, self).from_notebook_node(nb, resources)

        self.path = resources['metadata']['path']

        # Get attachments
        self.attachments = Struct()
        for cell in nb.cells:
            if 'attachments' in cell.keys():
                self.attachments += cell['attachments']

        # Parse HTML and replace <img> tags with the embedded data
        parser = et.HTMLParser()
        root = et.fromstring(output, parser=parser)
        nodes = root.findall(".//img")
        for n in nodes:
            self.replfunc(n)

        # Convert back to HTML
        embedded_output = et.tostring(root.getroottree(),
                                      method="html",
                                      encoding='unicode')

        return embedded_output, resources

    def replfunc(self, node):
        """Replace source url or file link with base64 encoded blob."""
        url = node.attrib["src"]
        imgformat = url.split('.')[-1]
        b64_data = None
        prefix = None

        if url.startswith('data'):
            return  # Already in base64 Format

        self.log.info("try embedding url: %s, format: %s" % (url, imgformat))

        if url.startswith('http'):
            b64_data = base64.b64encode(urlopen(url).read()).decode("utf-8")
        elif url.startswith('attachment'):
            imgname = url.split(':')[1]
            available_formats = self.attachments[imgname]
            # get the image based on the configured image type priority
            for imgformat in self.config.NbConvertBase.display_data_priority:
                if imgformat in available_formats.keys():
                    b64_data = self.attachments[imgname][imgformat]
                    prefix = "data:%s;base64," % imgformat
            if b64_data is None:
                raise ValueError("""Could not find attachment for image '%s'
                                    in notebook""" % imgname)
        else:
            filename = os.path.join(self.path, url)
            with open(filename, 'rb') as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")

        if prefix is None:
            if imgformat == "svg":
                prefix = "data:image/svg+xml;base64,"
            elif imgformat == "pdf":
                prefix = "data:application/pdf;base64,"
            else:
                prefix = "data:image/" + imgformat + ';base64,'

        node.attrib["src"] = prefix + b64_data

    @default('template_file')
    def _template_file_default(self):
        return 'hide_code_full_.tpl'

    @property
    def template_path(self):
        """
        We want to inherit from HTML template, and have template under
        `./templates/` so append it to the search path. (see next section)
        """
        return super(HideCode2HTMLExporter, self).template_path + [os.path.join(os.path.dirname(__file__), "Templates")]

    # @default('default_template_path')
    # def _default_template_path_default(self):
    #     return os.path.join(os.path.dirname(__file__), "Templates")

