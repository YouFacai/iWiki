from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from modules.doc.models import (
    Doc,
    DocVersion,
    Comment,
    CommentVersion,
    PinDoc,
    DocCollaborator,
)
from modules.repo.models import Repo


@admin.register(Doc)
class DocAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "repo_name",
        "creator_name",
        "update_at",
        "update_by_name",
        "is_publish",
        "is_deleted",
    ]
    search_fields = ["id", "title"]
    list_filter = ["is_publish", "is_deleted"]

    @admin.display(description=_("库名"))
    def repo_name(self, obj):
        return Repo.objects.get(id=obj.repo_id).name

    @admin.display(description=_("创建人"))
    def creator_name(self, obj):
        return get_user_model().objects.get(uid=obj.creator).username

    @admin.display(description=_("更新人"))
    def update_by_name(self, obj):
        return get_user_model().objects.get(uid=obj.update_by).username


@admin.register(DocVersion)
class DocAdmin(DocAdmin):
    pass


@admin.register(DocCollaborator)
class DocCollaboratorAdmin(admin.ModelAdmin):
    list_display = ["doc_title", "username", "add_at"]
    ordering = ["id"]

    @admin.display(description=_("标题"))
    def doc_title(self, obj):
        return Doc.objects.get(id=obj.doc_id).title

    @admin.display(description=_("用户名"))
    def username(self, obj):
        return get_user_model().objects.get(uid=obj.uid).username


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "doc_title", "creator_name", "update_at", "is_deleted"]
    search_fields = ["content"]
    list_filter = ["is_deleted"]

    @admin.display(description=_("文章"))
    def doc_title(self, obj):
        return Doc.objects.get(id=obj.doc_id).title

    @admin.display(description=_("用户名"))
    def creator_name(self, obj):
        return get_user_model().objects.get(uid=obj.creator).username


@admin.register(CommentVersion)
class CommentVersionAdmin(CommentAdmin):
    pass


@admin.register(PinDoc)
class PinDocAdmin(admin.ModelAdmin):
    list_display = [
        "doc_id",
        "doc_title",
        "create_at",
        "pin_to",
        "operator_name",
        "in_use",
    ]
    list_filter = ["in_use"]
    ordering = ["-in_use"]

    @admin.display(description=_("文章"))
    def doc_title(self, obj):
        return Doc.objects.get(id=obj.doc_id).title

    @admin.display(description=_("操作人"))
    def operator_name(self, obj):
        return get_user_model().objects.get(uid=obj.operator).username
