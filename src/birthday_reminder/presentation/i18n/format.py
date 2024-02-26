from logging import getLogger

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text

from ..i18n.constants import I18N_FORMAT_KEY
from ..i18n.typehints import FormatText

logger = getLogger(__name__)


class I18NFormat(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        format_text: FormatText = manager.middleware_data[I18N_FORMAT_KEY]

        return format_text(self.text, data)
