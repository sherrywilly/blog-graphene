import graphene
import graphql_jwt
from PIL.ImageGrab import grab
from graphene import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_auth import mutations
from .models import Tag, Article, Category
from graphql_jwt.decorators import login_required,superuser_required


class TagNode(DjangoObjectType):
    class Meta:
        model = Tag
        interfaces = (Node,)
        filter_fields = ['name', 'articles']


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
    all_parent_categories = DjangoFilterConnectionField(CategoryNode)
    all_childs_by_parent_category = DjangoFilterConnectionField(CategoryNode,id= graphene.Int())



    article = Node.Field(ArticleNode)
    all_articles = DjangoFilterConnectionField(ArticleNode)

    def resolve_all_parent_categories(self, info):
        return Category.objects.all().exclude(parent__isnull=True)

    def resolve_all_childs_by_parent_category(self, info,id):
        print(id)
        return Category.objects.filter(parent_id = id,).exclude(id=id)
class TagMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        id = graphene.ID()

    tag = graphene.Field(TagNode)

    @classmethod
    @superuser_required
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

    @login_required
    @superuser_required
    @classmethod
    def mutate(cls, self, info,name ,parent_id=None,id= None):

        cat,_ = Category.objects.get_or_create(id =id)
        cat.name = name
        if parent_id is not None:
            cat.parent_id = parent_id
        cat.save()
        return CategoryMutation(category=cat)

#  need to pass it as a list to add the tag list as many to many field
class TagInputType(graphene.InputObjectType):
    tag_id = graphene.ID()

class ArticleMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        title = graphene.String(required=True)
        content = graphene.JSONString(required=True)
        published = graphene.Boolean()
        featured_img = Upload()
        # tag_input: {tagId: "U291cmNlVmlkZW9Ob2RlOjE1,U291cmNlVmlkZW9Ob2RlOjE0,"}
        category_id = graphene.Int(required=True)
        tag_input = graphene.List(TagInputType)

    article = graphene.Field(ArticleNode)

    @classmethod
    @login_required
    @superuser_required
    def mutate(cls,self,info,title,content,category_id,**kwargs):
        id = kwargs.get('id',None)
        published = kwargs.get('published',False)
        tag_list = kwargs.get('tag_input',[])

        if id is not None:
            article = Article.objects.get(id =id)
        else:
            article = Article()
        article.title = title
        article.content = content
        article.published = published
        try:
            article.featured_img = info.context.FILES['featured_img']

        except:
            raise GraphQLError("unable to get the image")

        article.category_id = category_id
        print(tag_list)
        article.save()
        for _i in tag_list:
            _inum = _i['tag_id']
            try:
                article.tag.add(_inum)
            except Exception as e:
                print(e)
        return ArticleMutation(article = article)





class Mutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    create_or_update_tag = TagMutation.Field()
    test_cat = CategoryMutation.Field()
    create_or_update_article = ArticleMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)


