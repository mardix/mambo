
import os
import sys
import time
import click
import logging
import pkg_resources
from livereload import Server, shell
from . import Mambo
from .mambo import PAGE_FORMAT
from .__about__ import *


logging.basicConfig(filename='./error.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

CWD = os.getcwd()


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    

TPL_HEADER = """
---
title: Page Title
description: Page Description
---

"""

TPL_BODY = {
    # HTML
    "html": """

<div>
    <h1>{{ page.title }}</h1>
</div>

""",

    # MD
    "md": """

# My markdown Mambo!

"""

}


def copy_resource(src, dest):
    """
    To copy package data to destination
    """
    package_name = "mambo"
    dest = (dest + "/" + os.path.basename(src)).rstrip("/")
    if pkg_resources.resource_isdir(package_name, src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        for res in pkg_resources.resource_listdir(__name__, src):
            copy_resource(src + "/" + res, dest)
    else:
        if not os.path.isfile(dest) \
                and os.path.splitext(src)[1] not in [".pyc"]:
            with open(dest, "wb") as f:
                f.write(pkg_resources.resource_string(__name__, src))
        else:
            print("File exists: %s " % dest)


def stamp_mambo_current_version(dir):
    f = os.path.join(dir, Mambo.config_yml)
    if os.path.isfile(f):
        with open(f, "r+") as file:
            content = file.read()
            content = content.replace("##VERSION##", __version__)
            file.seek(0)
            file.write(content)
            file.truncate()


def title(txt):
    message = "%s\n" % txt
    print(color.BOLD + message + color.END)


def footer():
    print("-" * 80)

def done():
    info('DONE!')
    footer()

def error(message):
    print(color.BOLD + color.RED + "::ERROR::" + color.END)
    print(color.RED + message + color.END )

def error_exit(message):
    error(message)
    footer()
    exit()

def info(message):
    print(color.DARKCYAN + message + color.END )

def log(message): 
    print(message)

@click.group()
def cli():
    """
    Mambo: An elegant static site generator
    """
    pass


@cli.command("version")
def version():
    """Return the vesion of Mambo"""
    print(__version__)
    footer()


@cli.command("setup")
@click.argument("sitename")
def create_site(sitename):
    """Create a new site directory and init Mambo"""
    title('Create new site')
    mambo_conf = os.path.join(CWD, Mambo.config_yml)
    if os.path.isfile(mambo_conf):
        error_exit("Can't create new site in a directory that contain 'mambo.yml'")
    
    sitepath = os.path.join(CWD, sitename)
    if os.path.isdir(sitepath):
        error_exit("Site directory '%s' exists already!" % sitename)
    else:
        info("Creating site: %s..." % sitename)
        os.makedirs(sitepath)
        copy_resource("skel/", sitepath)
        stamp_mambo_current_version(sitepath)
        info("Site created successfully!")
        info("CD into '%s' and run 'mambo serve' to view the site" % sitename)

    done()


@cli.command("init")
def init():
    """Initialize Mambo in the current directory """
    title("Init Mambo...")
    mambo_conf = os.path.join(CWD, Mambo.config_yml)
    if os.path.isfile(mambo_conf):
        error_exit("Mambo is already initialized in '%s'. Or delete 'mambo.yml' if it's a mistake " % CWD)
    else:
        copy_resource("skel/", CWD)
        stamp_mambo_current_version(CWD)
        info("Mambo init successfully!")
        info("Run 'mambo serve' to view the site")
    done()


@cli.command("create")
@click.argument("pagenames", nargs=-1)
def create_page(pagenames):
    """Create new pages"""
    M = Mambo(CWD)
    defaultExt = "html"
    pages = []
    title("Creating new pages...")

    # Prepare and check the files
    for pagename in pagenames:
        page = pagename.lstrip("/").rstrip("/")
        _, _ext = os.path.splitext(pagename)

        # If the file doesn't have an extension, we'll just create one
        if not _ext or _ext == "":
            page += ".%s" % defaultExt

        # Destination file
        dest_file = os.path.join(M.pages_dir, page)
        if not page.endswith(PAGE_FORMAT):
            error_exit("Invalid file format: '%s'. Only '%s'" %
                       (page, " ".join(PAGE_FORMAT)))
        elif os.path.isfile(dest_file):
            error_exit("File exists already: '%s'" % dest_file)
        else:
            pages.append((page, dest_file))

    for page, dest_file in pages:
        # Making sure dir is created
        dest_dir = os.path.dirname(dest_file)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        markup = os.path.splitext(page)[1].strip('.')
        content = TPL_HEADER
        content += TPL_BODY[markup]
        with open(dest_file, "w") as f:
            f.write(content)
        log("- %s" % page)
    done()


@cli.command("build")
@click.option("-i", "--info", is_flag=True)
@click.option("--env", default=None)
def build(info, env):
    """Build the site"""
    title("Building site...")
    M = Mambo(CWD, {"env": env, "build": "build"})
    log('Name: %s' % M.site_config.get('name'))
    log('Env: %s' % M.site_env)
    log('Base Url: %s' % M.base_url)
    log('Static Url: %s' % M.static_url) 
    log('Timezone: %s' % M.GLOBAL_TIMEZONE)  
    log('Sitemap: %s ' % ('Yes' if M.build_config.get('generate_sitemap') else 'No'))
    log('')
    M.build(print_info=info)
    done()

@cli.command('serve')
@click.option("-p", "--port", default=None)
@click.option("--no-livereload", default=None)
@click.option("--open-url", default=None)
@click.option("--env", default=None)
def serve(port, no_livereload, open_url, env):
    """Serve the site """
    
    M = Mambo(CWD, {"env": env, "build": "serve"})
    if not port:
        port = M.config.get("serve.port", 8000)
    if no_livereload is None:
        no_livereload = True if M.config.get(
            "serve.livereload") is False else False
    if open_url is None:
        open_url = False if M.config.get(
            "serve.open_url") is False else True
    title('Serving on port %s' % port)
    log('Env: %s' % M.site_env)
    log('Base Url: %s' % M.base_url)
    log('Static Url: %s' % M.static_url)
    log("Livereload: %s" % ("OFF" if no_livereload else "ON"))

    def build_static():
        M.build_static()

    def build_pages():
        M.build_pages()
 

    M.build()

    server = Server()
    if no_livereload is False:
        server.watch(M.static_dir + "/", build_static)
        for c in [M.pages_dir, M.templates_dir, M.content_dir, M.data_dir]:
            server.watch(c + "/", build_pages)

    server.serve(open_url_delay=open_url, port=str(port), root=M.build_dir)


@cli.command("clean")
def clean():
    """Clean the build dir """
    title("Cleaning build dir...")
    Mambo(CWD).clean_build_dir()
    done()


def cmd():
    try:
        print("*" * 80)
        print("=" * 80)
        title("Mambo %s!" % __version__)
        print("-" * 80)
        sys_argv = sys.argv
        exempt_argv = ["init", "setup", "version", "--version", "-v"]
        mambo_conf = os.path.join(CWD, Mambo.config_yml)
        mambo_init = os.path.isfile(mambo_conf)
        if len(sys_argv) > 1:
            if sys_argv[1] in ['-v', '--version']:
                pass                
            elif not mambo_init and sys_argv[1] not in exempt_argv:
                error("Mambo is not initialized yet in this directory: %s" % CWD)
                log("Run 'mambo init' to initialize Mambo in the current directory")
                footer()
            else:
                cli()
        else:
            cli()
    except Exception as e:
        logger.error(e)
        error("FATAL ERROR. Check error.log file")
        log(">> %s " % e.__repr__())
        footer()
