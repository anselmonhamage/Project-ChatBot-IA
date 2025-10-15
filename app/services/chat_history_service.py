"""
Serviço de Histórico de Chat
Preparado para migração futura para Redis
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app import db
from app.models.tables import ChatHistory
import uuid


class ChatHistoryService:
    """
    Serviço para gerenciar histórico de conversas
    Atualmente usa SQL, mas preparado para migração para Redis
    """
    
    def __init__(self):
        # TODO: Adicionar configuração Redis quando implementado
        self.use_redis = os.getenv('USE_REDIS', 'False').lower() == 'true'
        self.redis_client = None
        
    def create_session_id(self) -> str:
        """Gera um ID único para sessão de chat"""
        return str(uuid.uuid4())
    
    def save_message(
        self,
        user_id: int,
        message: str,
        response: str = None,
        model_used: str = None,
        service_type: str = None,
        session_id: str = None
    ) -> ChatHistory:
        """
        Salva uma mensagem no histórico
        
        Args:
            user_id: ID do usuário
            message: Mensagem do usuário
            response: Resposta do bot
            model_used: Modelo usado (gemini, qwen)
            service_type: Tipo de serviço (online, local)
            session_id: ID da sessão
            
        Returns:
            ChatHistory object
        """
        if self.use_redis:
            # TODO: Implementar salvamento no Redis
            pass
        
        chat = ChatHistory(
            user_id=user_id,
            message=message,
            response=response,
            model_used=model_used,
            service_type=service_type,
            session_id=session_id
        )
        
        db.session.add(chat)
        db.session.commit()
        
        return chat
    
    def get_user_history(
        self,
        user_id: int,
        limit: int = 50,
        session_id: str = None
    ) -> List[ChatHistory]:
        """
        Obtém histórico de conversas do usuário
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de mensagens
            session_id: Filtrar por sessão específica
            
        Returns:
            Lista de ChatHistory
        """
        if self.use_redis:
            # TODO: Buscar do Redis
            pass
        
        query = ChatHistory.query.filter_by(user_id=user_id)
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        return query.order_by(ChatHistory.created_at.desc()).limit(limit).all()
    
    def get_recent_history(
        self,
        user_id: int,
        hours: int = 24,
        limit: int = 20
    ) -> List[ChatHistory]:
        """
        Obtém histórico recente do usuário
        
        Args:
            user_id: ID do usuário
            hours: Número de horas para buscar
            limit: Número máximo de mensagens
            
        Returns:
            Lista de ChatHistory
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        return ChatHistory.query.filter(
            ChatHistory.user_id == user_id,
            ChatHistory.created_at >= since
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
    
    def get_session_history(self, session_id: str) -> List[ChatHistory]:
        """
        Obtém todo histórico de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Lista de ChatHistory
        """
        return ChatHistory.query.filter_by(
            session_id=session_id
        ).order_by(ChatHistory.created_at.asc()).all()
    
    def delete_user_history(self, user_id: int) -> int:
        """
        Deleta todo histórico do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Número de registros deletados
        """
        if self.use_redis:
            # TODO: Deletar do Redis
            pass
        
        count = ChatHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return count
    
    def delete_old_history(self, days: int = 30) -> int:
        """
        Deleta histórico antigo (limpeza automática)
        
        Args:
            days: Número de dias para manter
            
        Returns:
            Número de registros deletados
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        count = ChatHistory.query.filter(
            ChatHistory.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        return count
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Obtém estatísticas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict com estatísticas
        """
        total_messages = ChatHistory.query.filter_by(user_id=user_id).count()
        
        from sqlalchemy import func
        model_stats = db.session.query(
            ChatHistory.model_used,
            func.count(ChatHistory.id)
        ).filter_by(user_id=user_id).group_by(ChatHistory.model_used).all()
        
        service_stats = db.session.query(
            ChatHistory.service_type,
            func.count(ChatHistory.id)
        ).filter_by(user_id=user_id).group_by(ChatHistory.service_type).all()
        
        return {
            'total_messages': total_messages,
            'models': dict(model_stats),
            'services': dict(service_stats)
        }
    
    # Métodos preparados para Redis (futuro)
    def _save_to_redis(self, chat: ChatHistory):
        """TODO: Implementar salvamento no Redis"""
        pass
    
    def _get_from_redis(self, user_id: int, limit: int) -> List[Dict]:
        """TODO: Implementar busca no Redis"""
        pass
    
    def _delete_from_redis(self, user_id: int):
        """TODO: Implementar deleção no Redis"""
        pass

chat_history_service = ChatHistoryService()
