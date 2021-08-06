import os

from django.db import models
from django.template.defaultfilters import slugify
from django_editorjs_fields import EditorJsJSONField
from mptt.models import  MPTTModel,TreeForeignKey
from PIL import  Image
from django.core.files.storage import FileSystemStorage

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return  self.name

class Category(MPTTModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self',null=True,blank=True,related_name='children',db_index=True,on_delete=models.CASCADE)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return  self.name
    def __unicode__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = EditorJsJSONField(
        plugins=[
            "@editorjs/image",
            "@editorjs/header",
            "@editorjs/list",
            "editorjs-github-gist-plugin",
            "editorjs-hyperlink",
            "@editorjs/code",
            "@editorjs/inline-code",
            "@editorjs/table@1.3.0",
        ],
        tools={
            "Gist": {
                "class": "Gist"
            },
            "Hyperlink": {
                "class": "Hyperlink",
                "config": {
                    "shortcut": 'CMD+L',
                    "target": '_blank',
                    "rel": 'nofollow',
                    "availableTargets": ['_blank', '_self'],
                    "availableRels": ['author', 'noreferrer'],
                    "validate": False,
                }
            },
            "Image": {
                'class': 'ImageTool',
                "config": {
                    "endpoints": {
                        # Your custom backend file uploader endpoint
                        "byFile": "/editorjs/image_upload/"
                    }
                }
            }
        },
        null=True,
        blank=True,
    )
    slug = models.SlugField(blank=True,null=True)
    published = models.BooleanField(default=False,blank=True,null=True)
    featured_img = models.ImageField(upload_to='feature_images/',blank=True,null=True)
    featured_mob_img = models.ImageField(upload_to='feature_mob_images/',blank=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,blank=True,null=True)
    tag = models.ManyToManyField(Tag,related_name='tags')
    category = TreeForeignKey('Category',null=True,blank=True,on_delete=models.DO_NOTHING,related_name='category')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args,**kwargs):
        self.slug = slugify(self.title)
        fs = FileSystemStorage()
        name, extension = os.path.splitext(self.featured_img.name)
        _name = f"feature_mob_images/{name}300*300{extension}"
        file = fs.save(_name,self.featured_img.file)
        self.featured_mob_img =fs.url(file).strip('/media')
        super(Article, self).save(*args, **kwargs)
        img = Image.open(self.featured_mob_img.path)
        new_img = (300, 300)
        img.thumbnail(new_img)
        img.save(self.featured_mob_img.path)

        return "True"


    def __str__(self):
        return self.title