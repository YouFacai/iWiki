from django.db.models import Q
from rest_framework.permissions import BasePermission

from constents import UserTypeChoices, RepoTypeChoices, DocAvailableChoices
from modules.doc.models import Doc, DocCollaborator, Comment
from modules.repo.models import RepoUser, Repo
from utils.exceptions import PermissionDenied, Error404


def check_repo_user_or_public(repo_id: int, uid: str):
    """检查是否为仓库成员或仓库为公开"""
    try:
        repo = Repo.objects.get(id=repo_id, is_deleted=False)
        # 公开仓库，允许访问
        if repo.r_type == RepoTypeChoices.PUBLIC:
            return True
        # 非公开仓库，成员可以访问
        RepoUser.objects.get(
            Q(repo_id=repo_id, uid=uid) & ~Q(u_type=UserTypeChoices.VISITOR)
        )
        return True
    except Repo.DoesNotExist:
        raise Error404()
    except RepoUser.DoesNotExist:
        raise PermissionDenied()


def check_doc_privacy(obj: Doc, uid: str):
    """检查文章为公开或作者"""
    if obj.available == DocAvailableChoices.PUBLIC:
        return True
    if obj.creator == uid:
        return True
    raise PermissionDenied()


def is_manager(uid: str, repo_id: int):
    try:
        RepoUser.objects.get(
            Q(repo_id=repo_id)
            & Q(uid=uid)
            & Q(u_type__in=[UserTypeChoices.ADMIN, UserTypeChoices.OWNER])
        )
        return True
    except RepoUser.DoesNotExist:
        return False


class DocManagePermission(BasePermission):
    """
    文章管理权限
    1. 创建文章：仓库成员或公开仓库
    2. 文章实例：创建人
    """

    def has_permission(self, request, view):
        # 超级管理员拥有全部权限
        if request.user.is_superuser:
            return True
        # 正常鉴权
        repo_id = request.data.get("repo_id", None)
        if view.action == "create" or (
            view.action in ["partial_update", "update"] and repo_id is not None
        ):
            return check_repo_user_or_public(repo_id, request.user.uid)
        return True

    def has_object_permission(self, request, view, obj: Doc):
        # 超管/库管理/创建者 授权
        if (
            obj.creator == request.user.uid
            or request.user.is_superuser
            or is_manager(request.user.uid, obj.repo_id)
        ):
            return True
        # 协作者 获取/更新 授权
        if view.action in [
            "partial_update",
            "update",
            "retrieve",
            "edit_status",
            "export",
        ]:
            try:
                DocCollaborator.objects.get(doc_id=obj.id, uid=request.user.uid)
                return True
            except DocCollaborator.DoesNotExist:
                raise PermissionDenied()
        raise PermissionDenied()


class DocCommonPermission(BasePermission):
    """
    文章常规权限
    1. 查看仓库文章列表：成员或公开仓库
    2. 文章实例：成员或公开仓库 且 文章公开或为创建人
    """

    def has_permission(self, request, view):
        # 超级管理员拥有全部权限
        if request.user.is_superuser:
            return True
        # 正常鉴权
        if view.action in ["list", "load_pin_doc"]:
            repo_id = request.GET.get("repo_id", None)
            return check_repo_user_or_public(repo_id, request.user.uid)
        return True

    def has_object_permission(self, request, view, obj: Doc):
        if request.user.is_superuser:
            return True
        check_repo_user_or_public(obj.repo_id, request.user.uid)
        check_doc_privacy(obj, request.user.uid)
        return True


class CommentPermission(BasePermission):
    """
    评论权限
    1. 查看评论列表或创建评论：仓库成员或公开仓库 且 文章公开或为创建人
    2. 评论实例： 创建人
    """

    def has_permission(self, request, view):
        if view.action in ["list", "create"]:
            doc_id = request.GET.get("doc_id") or request.data.get("doc_id")
            try:
                doc = Doc.objects.get(id=doc_id, is_deleted=False)
                check_repo_user_or_public(doc.repo_id, request.user.uid)
                check_doc_privacy(doc, request.user.uid)
                return True
            except Doc.DoesNotExist:
                raise Error404()
        return True

    def has_object_permission(self, request, view, obj: Comment):
        if obj.creator == request.user.uid:
            return True
        raise PermissionDenied()
