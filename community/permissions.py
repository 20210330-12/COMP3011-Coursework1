from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        # 읽기 요청은 모두 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 수정/삭제는 작성자만 가능
        return obj.author == request.user