from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import current_user, login_required
from models.chat import Mensagem
from models.user import User
from extensions import db
from werkzeug.utils import secure_filename
import os

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def index():
    usuarios = User.query.filter(User.id != current_user.id).all()
    return render_template('chat/index.html', usuarios=usuarios)

@chat_bp.route('/api/mensagens')
@login_required
def get_mensagens():
    tipo = request.args.get('tipo', 'individual')
    
    if tipo == 'grupo':
        mensagens = Mensagem.query.filter_by(tipo='grupo').order_by(Mensagem.data_envio).all()
    else:
        destinatario_id = request.args.get('destinatario_id', type=int)
        if not destinatario_id:
            return jsonify([])
            
        mensagens = Mensagem.query.filter(
            ((Mensagem.remetente_id == current_user.id) & (Mensagem.destinatario_id == destinatario_id)) |
            ((Mensagem.remetente_id == destinatario_id) & (Mensagem.destinatario_id == current_user.id))
        ).filter_by(tipo='individual').order_by(Mensagem.data_envio).all()
    
    return jsonify([msg.to_dict() for msg in mensagens])

@chat_bp.route('/api/mensagens', methods=['POST'])
@login_required
def enviar_mensagem():
    try:
        data = request.get_json()
        
        # Validar dados
        if not data or 'conteudo' not in data or 'tipo' not in data:
            return jsonify({'error': 'Dados inválidos'}), 400
            
        if not data['conteudo'].strip():
            return jsonify({'error': 'Mensagem vazia'}), 400
            
        if data['tipo'] not in ['grupo', 'individual']:
            return jsonify({'error': 'Tipo de mensagem inválido'}), 400
            
        if data['tipo'] == 'individual' and 'destinatario_id' not in data:
            return jsonify({'error': 'Destinatário não especificado'}), 400
            
        # Criar mensagem
        mensagem = Mensagem(
            remetente_id=current_user.id,
            conteudo=data['conteudo'].strip(),
            tipo=data['tipo']
        )
        
        if data['tipo'] == 'individual':
            destinatario = User.query.get(data['destinatario_id'])
            if not destinatario:
                return jsonify({'error': 'Destinatário não encontrado'}), 404
            mensagem.destinatario_id = destinatario.id
        
        db.session.add(mensagem)
        db.session.commit()
        
        return jsonify(mensagem.to_dict())
        
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar mensagem: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/api/mensagens/lidas', methods=['POST'])
@login_required
def marcar_mensagens_lidas():
    try:
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({'error': 'IDs das mensagens não fornecidos'}), 400
            
        # Buscar mensagens não lidas do usuário atual
        mensagens = Mensagem.query.filter(
            Mensagem.id.in_(data['ids']),
            Mensagem.lida == False,
            Mensagem.remetente_id != current_user.id
        ).all()
        
        # Marcar como lidas
        for msg in mensagens:
            msg.lida = True
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Erro ao marcar mensagens como lidas: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/api/mensagens/nao-lidas')
@login_required
def get_mensagens_nao_lidas():
    try:
        # Buscar mensagens não lidas do grupo
        grupo_count = Mensagem.query.filter_by(
            tipo='grupo',
            lida=False
        ).filter(Mensagem.remetente_id != current_user.id).count()
        
        # Buscar mensagens não lidas individuais agrupadas por remetente
        individuais = db.session.query(
            Mensagem.remetente_id,
            db.func.count(Mensagem.id).label('count')
        ).filter(
            Mensagem.tipo == 'individual',
            Mensagem.destinatario_id == current_user.id,
            Mensagem.lida == False
        ).group_by(Mensagem.remetente_id).all()
        
        # Criar dicionário com contagens
        result = {'grupo': grupo_count}
        for remetente_id, count in individuais:
            result[str(remetente_id)] = count
            
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar mensagens não lidas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/api/usuario/<int:user_id>/perfil')
@login_required
def get_perfil_usuario(user_id):
    usuario = User.query.get_or_404(user_id)
    return jsonify({
        'id': usuario.id,
        'username': usuario.username,
        'display_name': usuario.display_name or usuario.username,
        'icon': usuario.profile_icon or None
    })

@chat_bp.route('/api/usuario/perfil', methods=['POST'])
@login_required
def atualizar_perfil():
    try:
        # Atualizar display_name
        display_name = request.form.get('display_name')
        if display_name:
            current_user.display_name = display_name
            
        # Processar imagem do perfil
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                current_user.profile_icon = f'/uploads/{filename}'
        elif 'icon' in request.form:
            current_user.profile_icon = request.form['icon']
            
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
