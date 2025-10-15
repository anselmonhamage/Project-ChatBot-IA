import os
from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from app import csrf

from app.services.unified_chatbot import generate_response, get_available_models
from app.services.pix2latex_service import process_image, get_service_status
from app.services.chat_history_service import chat_history_service
from app.services.whatsapp_formatter import format_for_whatsapp

from app.models.tables import User
from app.models.forms import LoginForm, Cadastro, UpdateProfileForm
import base64

from app.auth.decorators import auth_role

try:
    from twilio.twiml.messaging_response import MessagingResponse
    from app.services.twilio_service import client, to_whatsapp_number, from_whatsapp_number
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()


@app.route('/favicon.ico')
def favicon():
    """Rota para servir favicon ou retornar 204 se não existir"""
    try:
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )
    except:
        return '', 204


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    
    form = Cadastro()
    user = User.query.filter_by(email=form.email.data).first()

    if user:
        flash("Esse utilizador já existe!")
        return redirect(url_for('signup'))

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


@app.route("/login", methods=["POST", "GET"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("chatbot"))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("Login efetuado com sucesso!", "success")
            return redirect(url_for("chatbot"))
        else:
            flash("Login Inválido!.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão Encerrada!", "info")
    return redirect(url_for("index"))


@app.route('/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Retorna dados do perfil do usuário incluindo imagem"""
    return jsonify({
        "name": current_user.name,
        "email": current_user.email,
        "tel": current_user.tel,
        "profile_image": current_user.profile_image
    })


@app.route("/profile/update", methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.tel = form.tel.data
        
        if form.profile_image.data:
            image_file = form.profile_image.data
            image_data = image_file.read()
            current_user.profile_image = base64.b64encode(image_data).decode('utf-8')
        
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
@auth_role("admin")
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


@app.route("/chat/history", methods=["GET"])
@login_required
def get_chat_history():
    """Retorna histórico de chat do utilizador"""
    limit = request.args.get('limit', 50, type=int)
    session_id = request.args.get('session_id', None)
    
    history = chat_history_service.get_user_history(
        user_id=current_user.id,
        limit=limit,
        session_id=session_id
    )
    
    return jsonify({
        "history": [h.to_dict() for h in history]
    })

@app.route("/chat/history/delete", methods=["POST"])
@login_required
def delete_chat_history():
    """Deleta histórico de chat do usuário"""
    count = chat_history_service.delete_user_history(current_user.id)
    return jsonify({
        "success": True,
        "deleted": count
    })


@app.route("/chatbot", methods=["GET", "POST"])
@csrf.exempt
@login_required
def chatbot():
    if request.method == "GET":
        try:
            available_models = get_available_models(ollama_url=None)
            return render_template("chatbot.html", available_models=available_models)
        except Exception as e:
            flash(f"Erro ao carregar página: {str(e)}", "error")
            return redirect(url_for('index'))
    
    try:
        if 'image' in request.files and request.files['image'].filename:
            image_file = request.files['image']
            extraction_mode = request.form.get('mode', 'text')
            
            crop_box = None
            if all(k in request.form for k in ['crop_x1', 'crop_y1', 'crop_x2', 'crop_y2']):
                crop_box = (
                    int(request.form['crop_x1']),
                    int(request.form['crop_y1']),
                    int(request.form['crop_x2']),
                    int(request.form['crop_y2'])
                )
            
            extraction_result = process_image(image_file, mode=extraction_mode, crop_box=crop_box)
            
            if not extraction_result["success"]:
                return jsonify({"error": extraction_result["error"]}), 400
            
            if extraction_result["type"] == "latex":
                user_message = f"Explique esta fórmula: {extraction_result['content']}"
            else:
                user_message = extraction_result["content"]
            
            model_type = request.form.get("model", "gemini")
            session_id = request.form.get("session_id") or chat_history_service.create_session_id()
        
        else:
            if request.is_json:
                data = request.get_json()
                user_message = data.get("message", "").strip()
                model_type = data.get("model", "gemini")
                session_id = data.get("session_id") or chat_history_service.create_session_id()
            else:
                user_message = request.form.get("message", "").strip()
                model_type = request.form.get("model", "gemini")
                session_id = request.form.get("session_id") or chat_history_service.create_session_id()
            
            if not user_message:
                return jsonify({"error": "Mensagem vazia"}), 400
        
        recent_history = chat_history_service.get_recent_history(current_user.id, hours=2, limit=5)
        context = "\n".join([f"User: {h.message}\nBot: {h.response}" for h in reversed(recent_history)])
        
        ollama_url = request.form.get("ollama_url", None)
        
        result = generate_response(
            message=user_message,
            model_type=model_type,
            ollama_url=ollama_url,
            context=context
        )
        
        if not result["success"]:
            error_msg = result.get("error", "Erro ao gerar resposta")
            return jsonify({"error": error_msg}), 500
        
        try:
            chat_history_service.save_message(
                user_id=current_user.id,
                message=user_message,
                response=result["response"],
                model_used=result["model"],
                service_type=result["type"],
                session_id=session_id
            )
        except Exception as e:
            pass
        
        return jsonify({
            "response": result["response"],
            "model": result["model"],
            "type": result["type"],
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@app.route("/api/extraction-status", methods=["GET"])
@login_required
def extraction_status():
    """Retorna status dos serviços de extração de imagem"""
    status = get_service_status()
    return jsonify(status)


@app.route("/api/models/available", methods=["GET", "POST"])
@login_required
def get_available_models_api():
    """API: Retorna modelos disponíveis dinamicamente"""
    try:
        ollama_url = None
        if request.method == "POST":
            data = request.get_json()
            ollama_url = data.get("ollama_url") if data else None
        
        models = get_available_models(ollama_url=ollama_url)
        
        import os
        has_gemini = bool(os.environ.get("GEMINI_API_KEY"))
        has_ollama_url = bool(ollama_url)
        
        return jsonify({
            "models": models,
            "config": {
                "gemini_configured": has_gemini,
                "ollama_configured": has_ollama_url,
                "ollama_url": ollama_url,
                "default_model": os.environ.get("DEFAULT_MODEL", "gemini")
            }
        })
    except Exception as e:
        return jsonify({
            "error": str(e), 
            "models": {},
            "config": {
                "gemini_configured": False,
                "ollama_configured": False,
                "ollama_url": None,
                "default_model": "gemini"
            }
        }), 200


@app.route('/whatsapp', methods=['POST'])
@csrf.exempt
def whatsapp_webhook():
    """
    Webhook do Twilio para integração com WhatsApp.
    Usa o Gemini via unified_chatbot com as mesmas regras de negócio do /chatbot.
    """
    if not TWILIO_AVAILABLE:
        return "Twilio não configurado", 500
    
    try:
        user_message = request.form.get('Body', '').strip()
        from_number = request.form.get('From', '')
        
        response = MessagingResponse()
        
        if not user_message:
            response.message("Por favor, envie uma mensagem.")
            return str(response)
        
        session_id = from_number.replace('whatsapp:', '').replace('+', '').replace(' ', '')
        
        """
        Busca histórico recente (usando session_id como user_id temporário)
        Nota: Para produção, você pode querer criar um usuário específico para WhatsApp
        """
        try:
            from app.models.tables import ChatHistory
            recent_messages = ChatHistory.query.filter_by(
                session_id=session_id
            ).order_by(
                ChatHistory.timestamp.desc()
            ).limit(5).all()
            
            context = "\n".join([
                f"User: {h.message}\nBot: {h.response}" 
                for h in reversed(recent_messages)
            ])
        except:
            context = ""
        
        result = generate_response(
            message=user_message,
            model_type="gemini",
            ollama_url=None,
            context=context
        )
        
        if not result["success"]:
            error_msg = "Desculpe, não consegui processar sua mensagem no momento. Tente novamente."
            response.message(error_msg)
            return str(response)
        
        """
        Formata resposta especificamente para WhatsApp
        Converte Markdown para formato WhatsApp, limita tamanho e melhora legibilidade
        """
        bot_response = format_for_whatsapp(result["response"], max_length=1500)
        
        try:
            # TODO Cria um registro genérico para WhatsApp
            # TODO Se quiser associar a um utilizador real, você precisará implementar
            # TODO um sistema de autenticação via WhatsApp
            chat_history_service.save_message(
                user_id=1,  # User ID genérico para WhatsApp (você pode criar um Utilizador "WhatsApp Bot")
                message=user_message,
                response=result["response"],
                model_used=result["model"],
                service_type="whatsapp",
                session_id=session_id  # Usa número do telefone como session_id
            )
        except Exception as e:
            app.logger.error(f"Erro ao salvar histórico WhatsApp: {str(e)}")
        
        response.message(bot_response)
        
        return str(response)
        
    except Exception as e:
        app.logger.error(f"Erro no webhook WhatsApp: {str(e)}")
        response = MessagingResponse()
        response.message("Desculpe, ocorreu um erro. Por favor, tente novamente.")
        return str(response)
        