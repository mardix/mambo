# ==============================================================================
# -------------------------------- Mambo -------------------------------------
# ==============================================================================

"""
~ Mambo ~
An elegant static site generator
"""

import os
import re
import sys
import copy
import json
import time
import yaml
import arrow
import shutil
import jinja2
import htmlmin
import logging
import functools
import frontmatter
import pkg_resources
from slugify import slugify
from distutils.dir_util import copy_tree
from .__about__ import *
from . import utils
from . import md_ext


# ==============================================================================

NAME = "Mambo"
CONFIG_FILE = "mambo.yml"
PAGE_FORMAT = (".html", ".md")
DEFAULT_LAYOUT = "layouts/default.html"

GLOBAL_TIMEZONE = 'America/New_York'
DEFAULT_PAGE_META = {
    "title": "",            # The title of the page
    "markup": None,         # The markup to use. ie: md | html (default)
    "slug": None,           # The pretty url new name of the file. A file with the same name will be created
    "url": "",              # This will be added when processed. Should never be modified
    "description": "",      # Page description
    "pretty_url": True,     # By default, all url will be pretty (search engine friendly) Set to False to keep the .html
    "meta": {},
    "layout": None,         # The layout for the page
    "sitemap": {
        "lastmod": None, 
        "priority": "0.7",
        "changefreq": "monthly",
        "exclude": False
    },
    "collections": None,
    "assets": {             # Contains all assets generated 
        "scripts": [],      # List of all scripts url in the page
        "stylesheets": []   # List of all CSS url in the page
    }    
}

DEFAULT_JS_SCRIPT_TYPE = 'type="text/javascript"'
RE_BLOCK_BODY = re.compile(r'{%\s*block\s+__PAGE_CONTENT__\s*%}')
RE_BLOCK_BODY_PARSED = re.compile(r'{%\s*block\s+__PAGE_CONTENT__\s*%}(.*?){%\s*endblock\s*%}')
RE_EXTENDS = re.compile(r'{%\s*extends\s+(.*?)\s*%}')

# ==============================================================================


def print_info(message, _print=False):
    if _print: print("- %s" % message)


def format_date(dt="now", format="MM/DD/YYYY h:mm a", tz=None):
    '''
    returns a formatted date
    :param dt: string of date time
    :param format: date format using Arrow
    :param tz: Timezone to use ie America/New_York 
    '''
    tz = tz if tz else GLOBAL_TIMEZONE
    d = arrow.utcnow() if dt is None or dt in ["now", "today"] else arrow.get(dt)
    d.to(tz)
    return d.format(format)

def gen_dest_file_and_url(filepath, page_meta={}):
    ''' 
    returns tuple of the file destination and url 
    :param filepath: the full path of the file
    :param page_meta: dict of page meta data
    '''

    filename = filepath.split("/")[-1]
    filepath_base = filepath.replace(filename, "").rstrip("/")
    slug = page_meta.get("slug")
    fname = slugify(slug) if slug else filename 
    fname = functools.reduce(lambda a, kv: a.replace(*kv), ((_, "")  for _ in PAGE_FORMAT), fname)
    if page_meta.get("pretty_url") is False:
        dest_file = os.path.join(filepath_base, "%s.html" % fname)
    else:
        dest_dir = filepath_base
        if filename not in ["index.html", "index.md"]:
            dest_dir = os.path.join(filepath_base, fname)
        dest_file = os.path.join(dest_dir, "index.html")
    url = "/" + dest_file.lstrip("/").replace("index.html", "")
    return dest_file, url

def read_markup_file(filepath, root=""):
  '''
  Read a markup file (.html|.md) and return its property
  :param filepath: the full path of the file
  :param root: the root path of filepath. It will be used to clean up
  :returns dict:
  '''

  markup = utils.get_ext(filepath)
  basename = os.path.basename(filepath)
  basefile = filepath.replace(root, "")
  with open(filepath) as f:
      meta = copy.deepcopy(DEFAULT_PAGE_META)
      sitemap = meta["sitemap"]
      assets = meta["assets"]
      _meta, content = frontmatter.parse(f.read())
      if "sitemap" in _meta: 
          sitemap.update(_meta["sitemap"])

      if "assets" in _meta: 
            _scripts = utils.convert_assets_items_to_dict(_meta["assets"].get("scripts"), DEFAULT_JS_SCRIPT_TYPE)
            _stylesheets = utils.convert_assets_items_to_dict(_meta["assets"].get("stylesheets"))
            assets["scripts"] += _scripts 
            assets["stylesheets"] += _stylesheets 
        
      meta.update(_meta)
      dest_file, url = gen_dest_file_and_url(basefile, meta)
      if meta.get('url'): url = meta.get('url')

      meta.update({
        "url": url.lstrip('/').rstrip('/'), 
        "filepath": dest_file,
        "filedest": dest_file,
        "basefile": basefile,
        "markup": markup,
        "sitemap": sitemap,
        "assets": assets
      })
      return ({
        "meta": meta, 
        "content": content, 
        "markup": markup
        })

def get_data_files(dir):
    data = {}
    for root, _, files in os.walk(dir):
        for fname in files:
            if fname.endswith((".json",)):
                name = fname.replace(".json", "")
                fname = os.path.join(root, fname)
                if os.path.isfile(fname):
                    with open(fname) as f:
                        _ = json.load(f)
                        if isinstance(_, dict):
                            _ = utils.dictdot(_)
                        data[name] = _
    return utils.dictdot(data)

def get_content_files_collection(dir):
  '''
  Generator to read markup files from directory
  :param dir: directory path
  :yield object:
  '''
  for root, _, files in os.walk(dir):
    for fname in files:
      if not fname.endswith(PAGE_FORMAT): continue
      fname = os.path.join(root, fname)
      if os.path.isfile(fname):
        yield read_markup_file(fname, root=dir)

def generate_sitemap(dir, manifest):
    '''
    Generate a sitemap.xml file
    :param dir: The base dir for the sitemap
    :param list: manifest of list of dict of pages
    '''
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for link in manifest:
        if link["sitemap"]["exclude"] is True:
            continue

        lastmod = format_date(link["sitemap"]["lastmod"] if link["sitemap"]["lastmod"] else "now", "YYYY-MM-DD" )
        sitemap += "\t<url>\n"
        sitemap += "\t\t<loc>%s</loc>\n" % link["url"]   
        sitemap += "\t\t<lastmod>%s</lastmod>\n" % lastmod   
        sitemap += "\t\t<changefreq>%s</changefreq>\n" % link["sitemap"]["changefreq"]   
        sitemap += "\t\t<priority>%s</priority>\n" % link["sitemap"]["priority"]  
        sitemap += "\t</url>\n"    
    sitemap += '\n</urlset>'

    sitemapxml = os.path.join(dir, 'sitemap.xml')
    with open(sitemapxml, 'w') as f:
        f.write(sitemap)

# ==============================================================================

class Mambo(object):

    config_yml = CONFIG_FILE
    tpl_env = None
    templates = {}
    pages = {}
    pages_short_mapper = {}
    manifest = []
    _verbose = False


    def __init__(self, root_dir, options={}):
        """
        :param root_dir: The application root dir
        :param options: options to build
        """
        global GLOBAL_TIMEZONE

        self.root_dir = root_dir
        self.build_dir = os.path.join(self.root_dir, ".build")
        self.static_dir = os.path.join(self.root_dir, "static")
        self.content_dir = os.path.join(self.root_dir, "content")
        self.data_dir = os.path.join(self.root_dir, "data")
        self.pages_dir = os.path.join(self.root_dir, "pages")
        self.templates_dir = os.path.join(self.root_dir, "templates")
        self.build_static_dir = os.path.join(self.build_dir, "static")
        self.build_static_page_assets_dir = os.path.join(self.build_static_dir, "pages_assets__")

        self.config_file = os.path.join(self.root_dir, self.config_yml)
        self.config = utils.load_conf(self.config_file)
        self.config.setdefault("env", {}) 
        self.config.setdefault("serve", {}) 
        self.config.setdefault("build", {}) 
        self.config.setdefault("globals", {}) 
        self.layout = self.config.get("globals.layout", DEFAULT_LAYOUT)
        
        # timezone
        if self.config.get('globals.timezone'):
            GLOBAL_TIMEZONE = self.config.get('globals.timezone')
        self.GLOBAL_TIMEZONE = GLOBAL_TIMEZONE

        # default sitemap
        if self.config.get('globals.sitemap'):
            DEFAULT_PAGE_META["sitemap"].update(self.config.get('globals.sitemap'))

        # global assets
        if self.config.get('globals.assets'):
            _scripts = utils.convert_assets_items_to_dict(self.config.get('globals.assets.scripts'), DEFAULT_JS_SCRIPT_TYPE)
            _stylesheets = utils.convert_assets_items_to_dict(self.config.get('globals.assets.stylesheets'))
            DEFAULT_PAGE_META["assets"] = {
                "scripts": _scripts,
                "stylesheets": _stylesheets
            }

        build_type = options.get("build", "build")
        self.build_config = utils.dictdot(self.config[build_type])
        site_env = self.build_config.get("env")
        if options and options.get("env") is not None: 
            site_env = options.get("env")

        self.site_config = utils.dictdot(self.config.get("site", {}))
        if site_env: 
            if site_env in self.config["env"]: 
                self.site_config = utils.merge_dicts(self.site_config, self.config.get('env.%s' % site_env))
            else: 
                raise ValueError("Environment Error: env %s@%s not found" % (site_env,build_type))
        
        self.site_env = site_env 
        self.site_config.setdefault("base_url", "/")
        self.site_config.setdefault("static_url", "/static")
        self.base_url = self.site_config.get("base_url")
        self.static_url = self.site_config.get("static_url")    

        self.setup_jinja()

    def setup_jinja(self):

        filters = {
            "format_date": format_date
        }

        global_context = {
            # Methods
            "page_url": self._fn_page_url,
            "page_link": self._fn_page_link,
            "page_info": self._fn_page_info,
            "static_url": self._fn_static_url,
            "script_tag": self._fn_script_tag,
            "stylesheet_tag": self._fn_stylesheet_tag,
            "format_date": format_date,
            "meta_tag": utils.meta_tag,
            "meta_tag_custom": utils.meta_tag_custom,

            # Other objects
            "site": self.site_config,
            "data": {},
            "__info__": {
                "name": __title__,
                "version": __version__,
                "url": __uri__,
                "generator": "%s %s" % (__title__, __version__),
                "timestamp": int(time.time())
            }
        }

        env_extensions = [
            "mambo.md_ext.MarkdownExtension",
            "mambo.md_ext.MarkdownTagExtension",
        ]
        content_loaders = [
            jinja2.PrefixLoader({"content": jinja2.FileSystemLoader(self.content_dir)}),
            jinja2.FileSystemLoader(self.templates_dir)
        ]

        loader = jinja2.ChoiceLoader(content_loaders) 
        self.tpl_env = jinja2.Environment(loader=loader, extensions=env_extensions)
        self.tpl_env.globals.update(global_context)
        self.tpl_env.filters.update(filters)
    
    #----->
    # _fn_* helper method to be used in the jinja template

    def _fn_page_link(self, filename, text=None, title=None, _class="", id="", alt="", **kwargs):
        """ Build the ahref to a page."""
        anchor = ""
        if "#" in filename:
            filename, anchor = filename.split("#")
            anchor = "#" + anchor
        return "<a href='{url}' class='{_class}' id='{id}'  title=\"{title}\">{text}</a>".format(
            url=self._fn_page_url(filename, "/") + anchor,
            text=text or title or self._fn_page_info(filename, "title", title),
            title=title or text or "",
            _class=_class,
            id=id
        )

    def _fn_page_url(self, filename, default_=""):
        ''' Get the url of a  page '''
        anchor = ""
        if "#" in filename:
            filename, anchor = filename.split("#")
            anchor = "#" + anchor
        return self._make_url(self._fn_page_info(filename, "url", default_))

    def _fn_page_info(self, filename, path, default_=None):
        """Return the page meta info"""
        page = self.pages_short_mapper.get(filename) 
        meta = self.pages[page]["meta"]
        return utils.dictdot(meta).get(path, default_)

    def _fn_static_url(self, url):
        '''Returns the static url'''
        if utils.is_https_string(url):
            return url
        return self.static_url.rstrip("/") + "/" + url.lstrip("/")

    def _fn_script_tag(self, src, attributes=None, absolute=False): 
        url = src if absolute is True else self._fn_static_url(src)
        props_ = attributes if attributes else "type='text/javascript'"
        return "<script {props} src=\"{url}\"></script>".format(props=props_, url=url)

    def _fn_stylesheet_tag(self, src, absolute=False): 
        url = src if absolute is True else self._fn_static_url(src)
        return "<link rel=\"stylesheet\" href=\"{url}\" type=\"text/css\" >".format(url=url)

    #----

    def _update_app_data(self):
        self.data_files = get_data_files(self.data_dir)
        self.tpl_env.globals.update({"data": self.data_files})

    def _make_url(self, url):
        return self.base_url.rstrip("/") + "/" + url.lstrip("/")

    def clean_build_dir(self):
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.makedirs(self.build_dir)

    def build_static(self):
        ''' Build static files '''
        if not os.path.isdir(self.build_static_dir):
            os.makedirs(self.build_static_dir)
        print_info('copying static dir to build folder...', self._verbose)
        if self.build_config.get("cache_bust_assets") is True:
            pass
        copy_tree(self.static_dir, self.build_static_dir)

    def build_pages(self):
        self.aggregate_pages_data()
        print_info('initiating page building...', self._verbose)
        [self._build_page(filename) for filename in self.pages.keys()]

    def aggregate_pages_data(self):
        self.pages = {}
        self.manifest = []
        self._update_app_data()

        print_info('aggregating pages files...', self._verbose)

        for root, _, files in os.walk(self.pages_dir):            
            base_dir = root.replace(self.pages_dir, "").lstrip("/")
            if base_dir.startswith("_"): continue 
            for f in files:
                if f.startswith(("_", ".")) or not f.endswith(PAGE_FORMAT): continue 
                base_filename = os.path.join(base_dir, f)
                fname, _ext = os.path.splitext(base_filename)
                self.pages_short_mapper.update({fname: base_filename, base_filename: base_filename})
                filename = os.path.join(base_dir, f)
                filepath = os.path.join(root, f)
                self.pages.update({
                    filename: read_markup_file(filepath, root=self.pages_dir)
                })

    def _build_page(self, filename):
        filename = self.pages_short_mapper.get(filename) 
        meta = self.pages[filename]["meta"]
        content = self.pages[filename]["content"]

        sfc = self._parse_sfc_content(filename, content)
        page_assets = {
            "scripts": meta["assets"]["scripts"] + sfc["assets"]["scripts"],
            "stylesheets": meta["assets"]["stylesheets"] + sfc["assets"]["stylesheets"]
        } 
        base_content = sfc["content"]
        context = {"page": meta}
        context["page"]["assets"] = page_assets
        page = {
            "filepath": meta.get("filepath"),
            "context": context,
            "content": base_content,
            "layout": meta.get("layout") or self.layout
        }

        '''
        Collections 
        A generator that will grab a folder under /content, or *data.json from /data and iterate
        over the entries, to create new pages using the base page as a template. 

        Format:
            meta:
                title
                url
                description
            content: the text
            markup: html|md
        
        The page context page.collections will be exposed containing the list of items.
        
        Base page requirement:
            'meta.collections.url': Must exist, contains the url path for the collection
                meta.collections.url: /blog/{url}

            '%%COLLECTION_CONTENT%%': must be placed to display the content of the item
        '''   
        if meta.get("collections"):
            if meta.get('collections').get("data_file"):
                data = self.data_files.get(meta["collections"]["data_file"]) 
            elif meta.get('collections').get("content_dir"):
                data = get_content_files_collection(os.path.join(self.content_dir, meta["collections"]["content_dir"] ))
            else: 
                raise ValueError('Page collection: %s, missing data_file or content_dir ' % filename)

            # Create url permalink
            permalink = meta.get('collections').get("url")
            if not permalink:
                permalink = meta["url"].rstrip('/').lstrip('/') + "/" + "{url}"
                print("Page collection '%s' is missing 'url'" % filename)
            permalink = "/" + permalink.lstrip('/')
            
            # hold data of all the items meta
            collections = []
            # hold data for all the pages to be rendered
            collection_pages = []

            # Aggregate
            for d in data:
                subpage = copy.deepcopy(page)
                submeta = copy.deepcopy(meta)
                submeta.update(d["meta"])

                # If the collection page is SFC, just grab the content only
                sub_sfc = self._parse_sfc_content(submeta.get("filepath", "random"), d.get("content"), d.get("markup"))
                sub_content = base_content.replace("%%COLLECTION_CONTENT%%", sub_sfc["content"])

                slug = permalink.format(**submeta)
                submeta["url"] = slug.format(**submeta)

                sub_context = subpage.get('context')
                sub_context = {"page": submeta}
                sub_context["page"]["assets"] = page_assets
                
                subpage.update({
                    "filepath": slug,
                    "content": sub_content,
                    "context": sub_context
                })

                collections.append(submeta)
                collection_pages.append(subpage)

            for page in collection_pages: 
                page["context"]["page"]["collections"] = collections
                self.create_page(**page)

        # NORMAL PAGE
        else:
            self.create_page(**page)

    def create_page(self, filepath, context={}, content=None, layout=None):
        '''
        To dynamically create a page and save it in the build_dir
        :param filepath: (string) the name of the file to create. May  contain slash to indicate directory
                        It will also create the url based on that name
                        If the filename doesn't end with .html, it will create a subdirectory
                        and create `index.html`
                        If file contains `.html` it will stays as is
                        ie:
                            post/waldo/where-is-waldo/ -> post/waldo/where-is-waldo/index.html
                            another/music/new-rap-song.html -> another/music/new-rap-song.html
                            post/page/5 -> post/page/5/index.html
        :param context: (dict) context data
        :param content: (text) The content of the file to be created. Will be overriden by template
        :param layout: (string) when using content. The layout to use.
                        The file location is relative to `/templates/`
                        file can be in html|md
        :return:
        '''

        filepath = filepath.lstrip("/").rstrip("/")
        self.manifest.append({
            "filepath": filepath,
            "title": context["page"]["title"],
            "url": self._make_url(filepath.replace("index.html", "")),  
            "full_url": self._make_url(filepath),  
            "sitemap": context["page"]["sitemap"]
        })

        build_dir = self.build_dir.rstrip("/")
        if not filepath.endswith(".html"): 
            filepath += "/index.html"
        dest_file = os.path.join(build_dir, filepath)
        dest_dir = os.path.dirname(dest_file)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        
        '''
        Extends the layout if it's missing
        The layout must contain __PAGE_CONTENT__ block
        ie: {% extends 'layouts/default.html' %}
        '''
        if re.search(RE_EXTENDS, content) is None:
            layout = layout or self.layout
            content = "\n{% extends '{}' %} \n\n".replace("{}", layout) + content

        '''
        Wrap the block __PAGE_CONTENT__ around the content
        Must be invoked in the layout
        ie: {% block __PAGE_CONTENT__ %}{% endblock %}
        '''
        if re.search(RE_BLOCK_BODY, content) is None:
            _layout_block = re.search(RE_EXTENDS, content).group(0)
            content = content.replace(_layout_block, "")
            _content = "\n" + _layout_block + "\n"
            _content += "{% block __PAGE_CONTENT__ %} \n" 
            _content += content.strip() 
            _content += "\n{% endblock %}"
            content = _content


        print_info('creating page: %s...' % filepath, self._verbose)

        # Write file
        with open(dest_file, "w") as fw:
            tpl = self.tpl_env.from_string(content)
            render_content = tpl.render(**context)
            if self.build_config.get("minify_html") is True:
                render_content = htmlmin.minify(render_content.decode("utf-8"), keep_pre=True)
            fw.write(render_content)

    def _parse_sfc_content(self, filename, content, markup=None):
        sfc = utils.destruct_sfc(content)
        content = sfc[1].get('template')
        markup = markup if markup else utils.get_ext(filename)
        if markup == "md":
            content = md_ext.convert(content)
        assets = self._parse_sfc_assets(filename, sfc)
        return {"content": content, "assets": assets}

    def _parse_sfc_assets(self, filename, sfc):
        assets = {"scripts": [], "stylesheets": []}
        # to add to _context["page"]["assets"]
        if sfc[0] is True:
            if not os.path.isdir(self.build_static_page_assets_dir):
                os.makedirs(self.build_static_page_assets_dir)
            sfc_c = sfc[1]
            sfc_hash = utils.gen_hash()
            filepath = slugify(filename)
            sfc_o = {"script": "js", "style": "css"}

            for o in sfc_o:
                if (sfc_c.get(o)):
                    _ff = os.path.join(self.build_static_page_assets_dir, "%s_%s.%s" % (filepath, sfc_hash, sfc_o[o]))
                    _sff = _ff.replace(self.build_static_dir, '').lstrip("/")
                    with open(_ff, "w") as f:
                        content = sfc_c.get(o)
                        content = content.replace('%%STATIC_URL%%', self.static_url.rstrip("/"))
                        '''
                        For stylesheet, if the tag contains 'scss' attribute, 
                        convert scss to css
                        '''
                        if o == 'style' and "scss" in sfc_c["style_props"].strip():
                            content = utils.convert_scss_to_css(content)
                        f.write(content)

                    assets_key = "scripts" if o == "script" else "stylesheets"
                    assets[assets_key].append({
                        "url": _sff,
                        "attributes": sfc_c["script_props"] if o == "script" else None
                        })
        return assets

    def build(self, print_info=False):
        self._verbose = print_info
        self.clean_build_dir()
        if not os.path.isdir(self.build_dir):
            os.makedirs(self.build_dir)
        self.build_static()
        self.build_pages()
        
        if self.build_config.get("generate_sitemap") is True:
            generate_sitemap(self.build_dir, self.manifest)




