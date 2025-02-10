from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models.devolucao import Devolucao
from models.transportadora import Transportadora
from models.carga import Carga
from datetime import datetime
from extensions import db
import traceback

devolucao_bp = Blueprint('devolucao', __name__, url_prefix='/devolucao')

@devolucao_bp.route('/')
@login_required
def index():
    transportadoras = Transportadora.query.all()
    return render_template('devolucao.html', transportadoras=transportadoras)

@devolucao_bp.route('/api/devolucoes', methods=['GET'])
@login_required
def get_devolucoes():
    try:
        devolucoes = Devolucao.query.all()
        result = []
        
        for d in devolucoes:
            # Buscar a carga e calcular totais
            carga = Carga.query.filter_by(carga=d.numero_carga).first()
            if carga:
                # Calcular totais dos romaneios
                total_embalagens = 0
                peso_total = 0
                valor_total = 0
                
                for romaneio in carga.romaneios:
                    if romaneio.qtd_embalagens is not None:
                        total_embalagens += int(romaneio.qtd_embalagens)
                    if romaneio.peso_bruto is not None:
                        peso_total += float(romaneio.peso_bruto)
                    if romaneio.valor_liquido is not None:
                        valor_total += float(romaneio.valor_liquido)
                
                # Subtrair devoluções aprovadas
                devolucoes_aprovadas = Devolucao.query.filter_by(
                    numero_carga=d.numero_carga,
                    aprovado=True
                ).all()
                
                for dev in devolucoes_aprovadas:
                    if dev.qtd_embalagens is not None:
                        total_embalagens -= int(dev.qtd_embalagens)
                    if dev.peso_devolvido is not None:
                        peso_total -= float(dev.peso_devolvido)
                    if dev.valor_mercadoria is not None:
                        valor_total -= float(dev.valor_mercadoria)
            else:
                total_embalagens = 0
                peso_total = 0
                valor_total = 0
            
            result.append({
                'id': d.id,
                'numero_carga': d.numero_carga,
                'numero_nfe': d.numero_nfe,
                'data_devolucao': d.data_devolucao.isoformat() if d.data_devolucao else None,
                'tipo_movimento': d.tipo_movimento,
                'qtd_embalagens': d.qtd_embalagens,
                'peso_devolvido': d.peso_devolvido,
                'valor_mercadoria': d.valor_mercadoria,
                'tipo_mercadoria': d.tipo_mercadoria,
                'aprovado': d.aprovado,
                'data_aprovacao': d.data_aprovacao.isoformat() if d.data_aprovacao else None,
                'aprovado_por': d.aprovado_por,
                'observacoes': d.observacoes,
                'totais_atualizados': {
                    'total_embalagens': total_embalagens,
                    'peso_total': round(peso_total, 2),
                    'valor_total': round(valor_total, 2)
                }
            })
            
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Erro ao listar devoluções: {str(e)}')
        return jsonify({'error': 'Erro ao listar devoluções'}), 500

@devolucao_bp.route('/api/devolucoes', methods=['POST'])
@login_required
def create_devolucao():
    try:
        data = request.get_json()
        current_app.logger.info(f'Dados recebidos: {data}')
        
        if not data:
            current_app.logger.error('Nenhum dado recebido no request')
            return jsonify({'error': 'Nenhum dado recebido'}), 400
            
        # Validar dados obrigatórios
        required_fields = ['numero_carga', 'numero_nfe', 'tipo_movimento', 'transportadora_id']
        for field in required_fields:
            if not data.get(field):
                current_app.logger.error(f'Campo obrigatório não informado: {field}')
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Criar nova devolução
        devolucao = Devolucao(
            numero_carga=data['numero_carga'],
            numero_nfe=data['numero_nfe'],
            tipo_movimento=data['tipo_movimento'],
            transportadora_id=data['transportadora_id'],
            peso_devolvido=data.get('peso_devolvido'),
            valor_mercadoria=data.get('valor_mercadoria'),
            qtd_embalagens=data.get('qtd_embalagens'),
            tipo_mercadoria=data.get('tipo_mercadoria'),
            observacoes=data.get('observacoes'),
            data_devolucao=datetime.now()
        )
        
        # Adicionar devolução ao banco de dados
        db.session.add(devolucao)
        db.session.commit()
        
        current_app.logger.info(f'Devolução criada com sucesso: {devolucao.id}')
        return jsonify({'message': 'Devolução registrada com sucesso', 'id': devolucao.id}), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao registrar devolução: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({'error': f'Erro ao registrar devolução: {str(e)}'}), 500

@devolucao_bp.route('/api/cargas/<numero_carga>/totais', methods=['GET'])
@login_required
def get_totais_carga(numero_carga):
    try:
        # Buscar a carga e seus romaneios
        carga = Carga.query.filter_by(carga=numero_carga).first()
        if not carga:
            return jsonify({'error': 'Carga não encontrada'}), 404
            
        # Calcular totais dos romaneios
        total_embalagens = 0
        peso_total = 0
        valor_total = 0
        
        # Somar todos os valores dos romaneios
        for romaneio in carga.romaneios:
            if romaneio.qtd_embalagens is not None:
                total_embalagens += int(romaneio.qtd_embalagens)
            if romaneio.peso_bruto is not None:
                peso_total += float(romaneio.peso_bruto)
            if romaneio.valor_liquido is not None:
                valor_total += float(romaneio.valor_liquido)
                
        # Buscar todas as devoluções aprovadas para esta carga
        devolucoes = Devolucao.query.filter_by(
            numero_carga=numero_carga,
            aprovado=True
        ).all()
        
        # Subtrair os valores das devoluções aprovadas
        total_devolucoes_embalagens = 0
        total_devolucoes_peso = 0
        total_devolucoes_valor = 0
        
        for devolucao in devolucoes:
            if devolucao.qtd_embalagens is not None:
                total_devolucoes_embalagens += int(devolucao.qtd_embalagens)
            if devolucao.peso_devolvido is not None:
                total_devolucoes_peso += float(devolucao.peso_devolvido)
            if devolucao.valor_mercadoria is not None:
                total_devolucoes_valor += float(devolucao.valor_mercadoria)
        
        # Calcular os totais finais
        total_embalagens_final = total_embalagens - total_devolucoes_embalagens
        peso_total_final = peso_total - total_devolucoes_peso
        valor_total_final = valor_total - total_devolucoes_valor
                
        return jsonify({
            'totais_romaneios': {
                'embalagens': total_embalagens,
                'peso': round(peso_total, 2),
                'valor': round(valor_total, 2)
            },
            'totais_devolucoes': {
                'embalagens': total_devolucoes_embalagens,
                'peso': round(total_devolucoes_peso, 2),
                'valor': round(total_devolucoes_valor, 2)
            },
            'totais_finais': {
                'embalagens': total_embalagens_final,
                'peso': round(peso_total_final, 2),
                'valor': round(valor_total_final, 2)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro ao buscar totais da carga: {str(e)}')
        return jsonify({'error': 'Erro ao buscar totais da carga'}), 500

@devolucao_bp.route('/api/devolucoes/<int:id>/aprovar', methods=['POST'])
@login_required
def aprovar_devolucao(id):
    try:
        current_app.logger.info(f'Tentando aprovar devolução {id}. Usuário: {current_user.username}, Role: {current_user.role}')
        
        if current_user.role != 'gerencia':
            current_app.logger.warning(f'Usuário {current_user.username} sem permissão para aprovar devoluções')
            return jsonify({'error': 'Usuário não tem permissão para aprovar devoluções'}), 403
        
        devolucao = Devolucao.query.get_or_404(id)
        current_app.logger.info(f'Devolução encontrada: {devolucao.__dict__}')
        
        if devolucao.aprovado:
            current_app.logger.warning(f'Devolução {id} já está aprovada')
            return jsonify({'error': 'Devolução já está aprovada'}), 400
        
        # Atualizar a devolução
        devolucao.aprovado = True
        devolucao.data_aprovacao = datetime.now()
        devolucao.aprovado_por = current_user.username
        
        # Buscar e validar a carga
        carga = Carga.query.filter_by(carga=devolucao.numero_carga).first()
        if not carga:
            current_app.logger.error(f'Carga {devolucao.numero_carga} não encontrada')
            return jsonify({'error': f'Carga {devolucao.numero_carga} não encontrada'}), 404
            
        current_app.logger.info(f'Carga encontrada: {carga.__dict__}')
        
        # Atualizar a carga com validações
        try:
            if carga.peso_total is not None and devolucao.peso_devolvido is not None:
                novo_peso = float(carga.peso_total) - float(devolucao.peso_devolvido)
                if novo_peso < 0:
                    raise ValueError(f'Peso total não pode ficar negativo: {novo_peso}')
                carga.peso_total = novo_peso
                current_app.logger.info(f'Peso atualizado: {carga.peso_total}')
                
            if hasattr(carga, 'valor_mercadoria') and carga.valor_mercadoria is not None and devolucao.valor_mercadoria is not None:
                novo_valor = float(carga.valor_mercadoria) - float(devolucao.valor_mercadoria)
                if novo_valor < 0:
                    raise ValueError(f'Valor da mercadoria não pode ficar negativo: {novo_valor}')
                carga.valor_mercadoria = novo_valor
                current_app.logger.info(f'Valor atualizado: {carga.valor_mercadoria}')
            
            current_app.logger.info('Valores atualizados com sucesso')
            
        except ValueError as ve:
            current_app.logger.error(f'Erro de validação: {str(ve)}')
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            current_app.logger.error(f'Erro ao atualizar valores: {str(e)}')
            raise
        
        try:
            db.session.commit()
            current_app.logger.info('Devolução aprovada com sucesso')
            return jsonify({'message': 'Devolução aprovada com sucesso'})
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erro ao salvar no banco: {str(e)}')
            raise
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao aprovar devolução: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({'error': f'Erro ao aprovar devolução: {str(e)}'}), 500
