import graphene
from graphene import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Tag, Article, Category
from graphene_file_upload.scalars import Upload


class TagNode(DjangoObjectType):
    class Meta:
        model = Tag
        interfaces = (Node,)
        filter_fields = ['name', 'tags']


class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        interfaces = (Node,)
        filter_fields = ['name', 'children']


class ArticleNode(DjangoObjectType):
    class Meta:
        model = Article
        interfaces = (Node,)
        filter_fields = ['title', 'tag', 'category']
        exclude = ('featured_img', 'featured_mob_img')

    featured_image = graphene.String()
    featured_image_small = graphene.String()
    extra_field = graphene.JSONString()

    def resolve_featured_image(self, info):
        return info.context.build_absolute_uri(self.featured_img.url)

    def resolve_featured_image_small(self, info):
        return info.context.build_absolute_uri(self.featured_mob_img.url)
        # return  info.context.build_absolute_uri(self.featured_mob_img.url)


class Query(graphene.ObjectType):
    tag = Node.Field(TagNode)
    all_tags = DjangoFilterConnectionField(TagNode)

    category = Node.Field(CategoryNode)
    all_categorys = DjangoFilterConnectionField(CategoryNode)

    article = Node.Field(ArticleNode)
    all_articles = DjangoFilterConnectionField(ArticleNode)


class TagMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        id = graphene.ID()

    tag = graphene.Field(TagNode)

    @classmethod
    def mutate(cls, root, info, name, id=None):
        if id is not None:
            tag = Tag.objects.get(id=id)
        else:
            tag = Tag()
        tag.name = name
        tag.save()
        return TagMutation(tag=tag)


class CategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        parent_id = graphene.Int()
        name = graphene.String()

    category = graphene.Field(CategoryNode)

    @classmethod
    def mutate(cls, self, info, id, name=None):
        c = Category.objects.get(id=id)
        return CategoryMutation(category=c)


class ArticleMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        content = graphene.JSONString(require=True)
        published = graphene.Boolean()
        featured_img = Upload()
        category_id = graphene.Int()



    @classmethod
    def mutate(cls,self,info):
        pass


class Mutation(graphene.ObjectType):
    create_or_update_tag = TagMutation.Field()
    test_cat = CategoryMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
