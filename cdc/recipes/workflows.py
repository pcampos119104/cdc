# seu_app/workflows.py
from wagtail.workflows import Task
from wagtail.models import WorkflowState, TaskState
from django.utils.translation import gettext_lazy as _

class IATask(Task):
    name = _("Processar com IA")
    active = True  # ativa por default

    def start(self, page, user):
        # Inicia a task: enfileira o processamento assíncrono
        process_ia.delay(page.id, self.id, user.id if user else None)
        return super().start(page, user)

    def on_action(self, task_state, user, action_name, **kwargs):
        # Aqui gerencia ações (ex: se rejeitado na review humana, volta aqui)
        if action_name == 'reject':
            # Re-enfileira com nota do usuário
            nota = kwargs.get('comment', '')  # nota da rejeição
            process_ia.delay(task_state.page.id, self.id, user.id, nota=nota)
        super().on_action(task_state, user, action_name, **kwargs)

def process_ia(page_id, task_id, user_id=None, nota=None):



class HumanReviewTask(Task):
    name = _("Revisão Humana")
    active = True

    # Aqui você pode customizar botões: aprovar (avança para publish), rejeitar (volta para IA com nota)
    # O Wagtail cuida do form para nota na rejeição