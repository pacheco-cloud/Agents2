# 📁 tools/task_manager.py
from pydantic_ai import RunContext
from models.context import ConversationContext
from typing import Annotated, List, Dict, Any
from datetime import datetime, timedelta

def tool_metadata():
    return {
        "name": "task_manager",
        "description": "Gerenciador de tarefas pessoais",
        "version": "2.0.0", 
        "author": "Productivity Team",
        "category": "productivity"
    }

async def manage_task(
    ctx: RunContext[ConversationContext],
    action: Annotated[str, "Ação: 'add', 'list', 'complete', 'remove', 'search', 'stats'"],
    task: Annotated[str, "Descrição da tarefa"] = "",
    task_id: Annotated[int, "ID da tarefa"] = 0,
    priority: Annotated[str, "Prioridade: 'low', 'medium', 'high'"] = "medium",
    due_date: Annotated[str, "Data limite (YYYY-MM-DD)"] = ""
) -> str:
    """Gerencia tarefas com prioridades e datas limite"""
    
    # Inicializar estrutura de tarefas
    tasks_data = ctx.deps.get_user_data('tasks', {
        'tasks': [],
        'next_id': 1,
        'completed_count': 0
    })
    
    if action == 'add':
        if not task:
            return "❌ Forneça a descrição da tarefa"
        
        # Validar prioridade
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'
        
        # Validar data limite
        due_datetime = None
        if due_date:
            try:
                due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                return "❌ Formato de data inválido. Use YYYY-MM-DD"
        
        # Criar nova tarefa
        new_task = {
            'id': tasks_data['next_id'],
            'description': task,
            'priority': priority,
            'due_date': due_date,
            'created': datetime.now().isoformat(),
            'completed': False,
            'completed_date': None
        }
        
        tasks_data['tasks'].append(new_task)
        tasks_data['next_id'] += 1
        ctx.deps.set_user_data('tasks', tasks_data)
        
        priority_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}[priority]
        due_info = f" (vence em {due_date})" if due_date else ""
        
        return f"✅ Tarefa adicionada: #{new_task['id']} {priority_emoji} {task}{due_info}"
    
    elif action == 'list':
        tasks = tasks_data['tasks']
        if not tasks:
            return "📝 Nenhuma tarefa cadastrada!"
        
        # Separar pendentes e completas
        pending = [t for t in tasks if not t['completed']]
        completed = [t for t in tasks if t['completed']]
        
        result = "📋 SUAS TAREFAS:\n\n"
        
        if pending:
            result += "⏳ PENDENTES:\n"
            for t in sorted(pending, key=lambda x: {'high': 1, 'medium': 2, 'low': 3}[x['priority']]):
                priority_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}[t['priority']]
                due_info = f" 📅{t['due_date']}" if t['due_date'] else ""
                result += f"   {priority_emoji} #{t['id']} - {t['description']}{due_info}\n"
        
        if completed:
            result += f"\n✅ COMPLETAS ({len(completed)}):\n"
            for t in completed[-3:]:  # Mostrar apenas as 3 mais recentes
                result += f"   ✓ #{t['id']} - {t['description']}\n"
        
        result += f"\n📊 Total: {len(pending)} pendentes, {len(completed)} completas"
        return result
    
    elif action == 'complete':
        if task_id <= 0:
            return "❌ Forneça o ID da tarefa"
        
        for t in tasks_data['tasks']:
            if t['id'] == task_id and not t['completed']:
                t['completed'] = True
                t['completed_date'] = datetime.now().isoformat()
                tasks_data['completed_count'] += 1
                ctx.deps.set_user_data('tasks', tasks_data)
                
                return f"🎉 Tarefa #{task_id} concluída: {t['description']}"
        
        return f"❌ Tarefa #{task_id} não encontrada ou já está completa"
    
    elif action == 'remove':
        if task_id <= 0:
            return "❌ Forneça o ID da tarefa"
        
        original_count = len(tasks_data['tasks'])
        tasks_data['tasks'] = [t for t in tasks_data['tasks'] if t['id'] != task_id]
        
        if len(tasks_data['tasks']) < original_count:
            ctx.deps.set_user_data('tasks', tasks_data)
            return f"🗑️ Tarefa #{task_id} removida!"
        else:
            return f"❌ Tarefa #{task_id} não encontrada"
    
    elif action == 'search':
        if not task:
            return "❌ Forneça o termo de busca"
        
        matching = [
            t for t in tasks_data['tasks'] 
            if task.lower() in t['description'].lower()
        ]
        
        if not matching:
            return f"🔍 Nenhuma tarefa encontrada com: '{task}'"
        
        result = f"🔍 Encontradas {len(matching)} tarefa(s):\n"
        for t in matching:
            status = "✅" if t['completed'] else "⏳"
            priority = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}[t['priority']]
            result += f"   {status} #{t['id']} {priority} {t['description']}\n"
        
        return result
    
    elif action == 'stats':
        tasks = tasks_data['tasks']
        pending = len([t for t in tasks if not t['completed']])
        completed = len([t for t in tasks if t['completed']])
        
        # Tarefas por prioridade
        priorities = {'high': 0, 'medium': 0, 'low': 0}
        for t in tasks:
            if not t['completed']:
                priorities[t['priority']] += 1
        
        # Tarefas vencendo
        overdue = 0
        if pending > 0:
            today = datetime.now().date()
            for t in tasks:
                if not t['completed'] and t['due_date']:
                    due = datetime.strptime(t['due_date'], '%Y-%m-%d').date()
                    if due < today:
                        overdue += 1
        
        return (
            f"📊 ESTATÍSTICAS DAS TAREFAS:\n"
            f"   📝 Total: {len(tasks)}\n"
            f"   ⏳ Pendentes: {pending}\n"
            f"   ✅ Completas: {completed}\n"
            f"   🔴 Alta prioridade: {priorities['high']}\n"
            f"   🟡 Média prioridade: {priorities['medium']}\n"
            f"   🟢 Baixa prioridade: {priorities['low']}\n"
            f"   ⚠️ Atrasadas: {overdue}"
        )
    
    else:
        return "❌ Ação inválida. Use: add, list, complete, remove, search, stats"

manage_task.__tool_metadata__ = tool_metadata()

# ========================
