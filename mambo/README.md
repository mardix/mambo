# Mambo !

Mambo is an elegant static site generator built in Python. 

It’s a great choice for website, blogs and documentation. Content can be written in HTML and Markdown, oganized however you want with any URL structure, and metadata can be defined in front-matter. 


https://github.com/mardix/mambo

---

## Command Line API

Mambo aims to be simple with a simple API.

### Install

```
pip install mambo
```
    
### Setup a site 

To setup a site, the command below will create a new directory name `/mysitename.com/`. All the necessary files and folders will be created in there.

```html
 cd ~
 mambo setup mysitename.com
```

#### Or initialize in an existing folder

All the necessary files and folders will be created in there.

```html
cd ./mysitename.com
mambo init
```

### Create a page

The command below will create a `hello-world.html` by default. To create it as markdown, add the `.md` as file extension. Page can only be either `html` or `markdown`, any other format will be ignored.

```html
mambo create hello-world 
```

#### Create multiple pages

To create multiples pages, separate them by space

```html
mambo create hello-world page1.md pag2.html another-page
```


### Serve site in dev mode 

To serve the site in evelopment mode, cd into the directory and run, a browser window will be open. By default it uses port 8000

```html
mambo serve
```

#### Options

```html
-p | --port [ -p 8001 ]: Use the specified port. Default 8000
--env [ --env prod ] : Select the environment to build
--no-livereload [ --no-livereload ]
--open-url [ --open-url ]

```

### Build site for production 

Build the site to be deployed to production. The content will be placed in `.build` directory, which can be uploaded to any servers.

```html
mambo build
```

#### Options

```html
-i | --info [ -i ] boolean, default False: To display build information
--env [ --env prod ] : Select the environment to build

```

### Clean the build directory 

To cleanup the `.build` directory

```
mambo clean 
```

--- 

## Add-ons

Just for your convenience, we have included `milligram.css`

- https://github.com/milligram/milligram
    


