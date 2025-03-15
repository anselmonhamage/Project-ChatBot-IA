from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import cross_origin
from app import csrf
from twilio.twiml.messaging_response import MessagingResponse

from app.services.twilio_service import client, to_whatsapp_number, from_whatsapp_number
from app.services.format_text import format_text
from app.services.chatbot_genai import model

from app.models.tables import User, Question
from app.models.forms import LoginForm, Cadastro, UpdateProfileForm, QuestionForm


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login efetuado com sucesso!", "success")
            return redirect(url_for("chatbot"))
        else:
            flash("Login Inválido!.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sessão.", "info")
    return redirect(url_for("index"))


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("chatbot"))

    form = Cadastro()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            password=hashed_password,
            name=form.name.data,
            email=form.email.data,
            tel=form.tel.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Sua conta foi criada com sucesso!", "success")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route("/profile/update", methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.tel = form.tel.data
        db.session.commit()
        flash("Seu perfil foi atualizado com sucesso!", "success")
        return redirect(url_for('chatbot'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.tel.data = current_user.tel
    return render_template('edit.html', form=form)


@app.route("/user/delete/<int:id>")
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("A conta foi excluída com sucesso!", "info")
    return redirect(url_for('index'))


@app.route("/profile/delete")
@login_required
def delete_profile():
    user = User.query.get_or_404(current_user.id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("A conta foi excluída com sucesso!", "info")
    return redirect(url_for('index'))


@app.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():
    if request.method == "POST":
        data = request.get_json()
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Mensagem vazia."}), 400

        similar_questions = Question.query.filter(Question.question_text.ilike(f"%{user_message}%")).all()

        if similar_questions:
            answer = similar_questions[0].answer
        else:
            all_questions = Question.query.all()

            contexto = ""
            for question in all_questions:
                contexto += f"Pergunta: {question.question_text}\n Resposta: {question.answer}\n"

            try:
                response = model.generate_content(f"Use o seguinte contexto {contexto} para responder aseguinte,\n Pergunta: {user_message}")
                aux = response.text.strip()
                answer = format_text(aux, option='plain')
            except Exception as e:
                print(f"Erro ao processar a resposta: {str(e)}")
                answer = "Desculpe, ocorreu um erro ao processar sua solicitação."

        return jsonify({"answer": answer})

    return render_template("chatbot.html")


@app.route("/add_question", methods=['GET', 'POST'])
# @cross_origin()
@login_required
def add_question():
    form = QuestionForm()
    if request.method == 'POST':
        question_text = form.question_text.data
        answer = form.answer.data
        if not question_text or not answer:
            flash("Ambos campos de questão e resposta são obrigatórios!", "warning")
            return redirect(url_for('add_question'))
        new_question = Question(
            question_text=question_text,
            answer=answer,
            user_id=current_user.id
        )

        db.session.add(new_question)
        db.session.commit()
        flash("Nova questão adicionada com sucesso!", "success")
        return redirect(url_for('chatbot'))
    
    return render_template('add_question.html', form=form)


def responder_mensagem(msg):
    client.messages.create(
        body=msg,
        from_=from_whatsapp_number, 
        to=to_whatsapp_number
    )


@app.route('/whatsapp', methods=['GET', 'POST'])
@csrf.exempt
def whatsapp():
    user_message = request.form.get('Body', '') 

    similar_questions = Question.query.filter(Question.question_text.ilike(f"%{user_message}%")).all()

    response = MessagingResponse()
    msg = response.message()
    msg.body(f"Recebemos sua mensagem: {user_message}")

    if similar_questions:
        answer = similar_questions[0].answer
        responder_mensagem(answer)
    else:
        all_questions = Question.query.all()

        contexto = ""
        for question in all_questions:
            contexto += f"Pergunta: {question.question_text}\n Resposta: {question.answer}\n"
        
        response = model.generate_content(f"Use o seguinte contexto {contexto} para responder a seguinte,\n Pergunta: {user_message}")
        aux = response.text.strip()

        answer = format_text(aux, option='plain')  

        responder_mensagem(answer)

    return str(msg)