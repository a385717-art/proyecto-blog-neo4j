"""Operaciones de persistencia del blog en Neo4j."""

from .articles import (
    createArticle,
    deleteArticle,
    getArticleByTitleAndDate,
    getArticles,
    updateArticle,
)
from .categories import (
    createCategory,
    deleteCategory,
    getCategories,
    getCategoryByName,
    updateCategory,
)
from .comments import (
    createComment,
    deleteComment,
    getCommentByUrl,
    getComments,
    updateComment,
)
from .relations import (
    addCategoryToArticle,
    addComment,
    addTagToArticle,
    getArticleDetail,
    getArticlesByCategory,
    getArticlesByTag,
    getArticlesByUser,
    getCommentsByArticle,
    linkArticleAuthor,
    removeCategoryFromArticle,
    removeTagFromArticle,
)
from .tags import (
    createTag,
    deleteTag,
    getTagByName,
    getTags,
    updateTag,
)
from .user import (
    createUser,
    deleteUser,
    getUserByEmail,
    getUsers,
    updateUser,
)

__all__ = [
    "createArticle",
    "getArticles",
    "getArticleByTitleAndDate",
    "updateArticle",
    "deleteArticle",
    "createCategory",
    "getCategories",
    "getCategoryByName",
    "updateCategory",
    "deleteCategory",
    "createComment",
    "getComments",
    "getCommentByUrl",
    "updateComment",
    "deleteComment",
    "createTag",
    "getTags",
    "getTagByName",
    "updateTag",
    "deleteTag",
    "createUser",
    "getUsers",
    "getUserByEmail",
    "updateUser",
    "deleteUser",
    "linkArticleAuthor",
    "addComment",
    "addTagToArticle",
    "removeTagFromArticle",
    "addCategoryToArticle",
    "removeCategoryFromArticle",
    "getArticleDetail",
    "getArticlesByUser",
    "getArticlesByTag",
    "getArticlesByCategory",
    "getCommentsByArticle",
]
