from Qt.QtWidgets import QGraphicsItem


class ShadowSelectableItem(QGraphicsItem):
    def __init__(self, parent=None):
        """A special property inherited by some scheme items.
        Shadow selection occurs independently from normal selection. It is not enabled by rubber-band selection.
        Shadow selection is meant for items that derive their selection status from other factors.
        This class is intended for inheritance. When shadow selected, it will send an itemChange event with
        change = ShadowSelectable.ItemShadowSelectedChange, as well as ShadowSelectable.ItemShadowSelectedHasChanged.
        """
        super().__init__(parent)
        self._is_shadow_selected = False

    def setShadowSelected(self, value: bool):
        self.itemShadowSelectedChangeEvent(value)
        self._is_shadow_selected = value
        self.itemShadowSelectedHasChangedEvent(value)

    def isShadowSelected(self) -> bool:
        return self._is_shadow_selected

    def itemShadowSelectedChangeEvent(self, value: bool):
        """Replacement for itemChange() function.
        This function is called when item's shadow selection status changes.
        """
        pass

    def itemShadowSelectedHasChangedEvent(self, value: bool):
        """Replacement for itemChange() function.
        This function is called when item's shadow selection status has changed.
        """