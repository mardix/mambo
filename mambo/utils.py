
import os
import re
import uuid
import yaml
import mimetypes
from scss import Compiler as SCSS

'''
For Single File Component
'''
RE_SFC_TEMPLATE = re.compile(
    r'<template\s*>\n?([\S\s]*?)<\/template\s*>', re.IGNORECASE)
RE_SFC_SCRIPT = re.compile(
    r'<script\s*(.*)\s*>\n?([\S\s]*?)<\/script\s*>', re.IGNORECASE)
RE_SFC_STYLE = re.compile(
    r'<style\s*(.*)\s*>\n?([\S\s]*?)<\/style\s*>', re.IGNORECASE)

RE_IS_URL = re.compile(r'^(http|https)://')


def is_https_string(url):
  '''
  returns bool if url is a https link
  :param url: string
  '''
  return RE_IS_URL.match(url) is not None

def get_ext(filepath):
    '''
    returns the extension of filepath
    :param filepath: string
    '''
    _, _ext = os.path.splitext(filepath)
    return _ext.replace(".", "")

def gen_hash():
    '''
    :returns string: a random hash
    '''
    return uuid.uuid4().hex

def meta_tag_custom(namespace, name, value=''):
    return '<meta {namespace}="{name}" content="{value}">'.format(namespace=namespace, name=name, value=value)

def meta_tag(name, value):
    '''
    Create meta tag
    '''
    return meta_tag_custom('name', name, value);

def destruct_sfc(content):
    '''
    To destruct a single file component into template, script, style
    :param: string content 
    :returns: tuple - (Bool, {template, script, style, script_props, style_props})
    '''
    s_template = re.search(RE_SFC_TEMPLATE, content)
    s_script = re.search(RE_SFC_SCRIPT, content)
    s_style = re.search(RE_SFC_STYLE, content)

    if s_template:
        return (True, {
            "template": s_template.group(1) if s_template else content,
            "script": s_script.group(2).replace("\"","'") if s_script else None,
            "script_props": s_script.group(1) if s_script else None,
            "style": s_style.group(2) if s_style else None,
            "style_props": s_style.group(1) if s_style else None,
        })
    else:
        return (False, {"template": content, "script": None, "style": None, "script_props": "", "style_props": ""})

class dictdot(dict):
    '''
    A dict extension that allows dot notation to access the data.
    ie: dict.get('key.key2.0.keyx'). Still can use dict[key1][k2]
    To create: dictdot(my)
    '''
    def get(self, key, default=None):
        ''' access data via dot notation '''
        try:
            val = self
            if "." not in key:
                return self[key]
            for k in key.split('.'):
                if k.isdigit():
                    k = int(k)
                val = val[k]
            return val
        except (TypeError, KeyError, IndexError) as e:
            return default

def load_conf(yml_file, conf={}):
    '''
    To load the config
    :param yml_file: the config file path
    :param conf: dict, to override global config
    :return: dict
    '''
    with open(yml_file) as f:
        data = yaml.load(f)
        if conf:
            data.update(conf)
        return dictdot(data)

def extract_sitename(s):
    return re.sub(r"https?://(www\.)?", '', s).replace("www.", "")

def chunk_list(items, size):
    '''
    Return a list of chunks
    :param items: List
    :param size: int The number of items per chunk
    :return: List
    '''
    size = max(1, size)
    return [items[i:i + size] for i in range(0, len(items), size)]

def merge_dicts(dict1, dict2):
    ''' Recursively merges dict2 into dict1 '''
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for k in dict2:
        if k in dict1:
            dict1[k] = merge_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict1

def convert_scss_to_css(content):
    return SCSS().compile_string(content)

def convert_assets_items_to_dict(assets, attributes=""):
  '''
  Convert an assets list to proper dict
  '''
  b = []
  if not assets:
      return b
  for a in assets:
    if a: 
        b.append({"url": a, "attributes": attributes} if not isinstance(a, (dict,)) else a)
  return b