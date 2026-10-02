from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..models import User

users_bp = Blueprint("users", __name__, url_prefix="/usuarios")


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "admin":
            flash("Acesso restrito ao administrador.")
            return redirect(url_for("main.index"))
        return view(*args, **kwargs)
    return wrapped


@users_bp.route("/")
@admin_required
def index():
    users = User.query.order_by(User.username.asc()).all()
    return render_template("users.html", users=users, title="Usuários")


@users_bp.route("/novo", methods=["GET", "POST"])
@admin_required
def create():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "funcionario")

        if not username or not password:
            flash("Informe usuário e senha.")
            return render_template("user_form.html", user=None, title="Novo usuário")
        if len(username) < 3:
            flash("O usuário deve ter pelo menos 3 caracteres.")
            return render_template("user_form.html", user=None, title="Novo usuário")
        if password != confirm:
            flash("As senhas não conferem.")
            return render_template("user_form.html", user=None, title="Novo usuário")
        if len(password) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.")
            return render_template("user_form.html", user=None, title="Novo usuário")
        if role not in ("admin", "funcionario"):
            role = "funcionario"
        if User.query.filter_by(username=username).first():
            flash("Esse nome de usuário já está em uso.")
            return render_template("user_form.html", user=None, title="Novo usuário")

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Usuário '{username}' criado com sucesso.")
        return redirect(url_for("users.index"))

    return render_template("user_form.html", user=None, title="Novo usuário")


@users_bp.route("/<int:user_id>/editar", methods=["GET", "POST"])
@admin_required
def edit(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("Usuário não encontrado.")
        return redirect(url_for("users.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "funcionario")
        new_password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or len(username) < 3:
            flash("O usuário deve ter pelo menos 3 caracteres.")
            return render_template("user_form.html", user=user, title="Editar usuário")
        if role not in ("admin", "funcionario"):
            role = "funcionario"
        other = User.query.filter(User.username == username, User.id != user.id).first()
        if other:
            flash("Esse nome de usuário já está em uso.")
            return render_template("user_form.html", user=user, title="Editar usuário")

        # Não permite que o último administrador seja rebaixado.
        if user.role == "admin" and role != "admin":
            admins = User.query.filter_by(role="admin").count()
            if admins <= 1:
                flash("O sistema precisa manter pelo menos um administrador.")
                return render_template("user_form.html", user=user, title="Editar usuário")

        if new_password:
            if len(new_password) < 6:
                flash("A nova senha deve ter pelo menos 6 caracteres.")
                return render_template("user_form.html", user=user, title="Editar usuário")
            if new_password != confirm:
                flash("As senhas não conferem.")
                return render_template("user_form.html", user=user, title="Editar usuário")
            user.password_hash = generate_password_hash(new_password)

        user.username = username
        user.role = role
        db.session.commit()
        flash(f"Usuário '{username}' atualizado com sucesso.")
        return redirect(url_for("users.index"))

    return render_template("user_form.html", user=user, title="Editar usuário")


@users_bp.route("/<int:user_id>/excluir", methods=["POST"])
@admin_required
def delete(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("Usuário não encontrado.")
        return redirect(url_for("users.index"))
    if user.id == current_user.id:
        flash("Você não pode excluir o próprio usuário enquanto estiver logado.")
        return redirect(url_for("users.index"))
    if user.role == "admin" and User.query.filter_by(role="admin").count() <= 1:
        flash("Não é possível excluir o último administrador.")
        return redirect(url_for("users.index"))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f"Usuário '{username}' excluído.")
    return redirect(url_for("users.index"))


@users_bp.route("/meu-perfil", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username or len(username) < 3:
            flash("O usuário deve ter pelo menos 3 caracteres.")
            return render_template("profile.html", title="Meu perfil")
        other = User.query.filter(User.username == username, User.id != current_user.id).first()
        if other:
            flash("Esse nome de usuário já está em uso.")
            return render_template("profile.html", title="Meu perfil")
        current_user.username = username
        db.session.commit()
        flash("Seu usuário foi atualizado.")
        return redirect(url_for("users.profile"))
    return render_template("profile.html", title="Meu perfil")


@users_bp.route("/meu-perfil/senha", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        if not check_password_hash(current_user.password_hash, current_password):
            flash("A senha atual está incorreta.")
            return render_template("change_password.html", title="Alterar senha")
        if len(new_password) < 6:
            flash("A nova senha deve ter pelo menos 6 caracteres.")
            return render_template("change_password.html", title="Alterar senha")
        if new_password != confirm:
            flash("As senhas não conferem.")
            return render_template("change_password.html", title="Alterar senha")
        if new_password == current_password:
            flash("A nova senha deve ser diferente da senha atual.")
            return render_template("change_password.html", title="Alterar senha")

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Senha alterada com sucesso.")
        return redirect(url_for("users.profile"))

    return render_template("change_password.html", title="Alterar senha")
