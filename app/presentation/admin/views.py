from flask_admin.contrib.sqla import ModelView
from flask import redirect, session, url_for, request


from flask_admin import AdminIndexView
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import SelectField
from app.infrastructure.database import sync_session


from app.infrastructure.models import Category

# ==================================================== View Models Admin


class MyModelView(ModelView):

    def is_accessible(self):
        return session.get("is_admin") is True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login"))


class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return session.get("is_admin") is True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login"))

    @expose("/", methods=["GET", "POST"])
    def index(self):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return super().index()


class PostsView(ModelView):
    form_columns = ["title", "slug", "content", "main_image", "category_id"]

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.category_id = SelectField(
            "Категорія",
            choices=[(str(c.id), c.name) for c in sync_session().query(Category).all()],
            coerce=int,
        )
        return form_class


# class PostsView(ModelView):

#     edit_template = "admin/edit_article.html"
#     create_template = "admin/edit_article.html"
#     # page_size = 50  # the number of entries to display on the list view
#     column_exclude_list = ["textbody"]
#     form_widget_args = {"textbody": {"rows": 25, "class": "form-control wysiwyg"}}

#     def _change_alias(self, _form):
#         try:
#             if _form.alias.data is None:
#                 _form.alias.data = utilites.transliterate(_form.title.data)
#             else:
#                 _form.alias.data = utilites.transliterate(_form.alias.data)

#         except Exception as ex:
#             print(ex)

#         return _form

#     def edit_form(self, obj=None):
#         return self._change_alias(super(PostsView, self).edit_form(obj))

#     def create_form(self, obj=None):
#         return self._change_alias(super(PostsView, self).create_form(obj))
