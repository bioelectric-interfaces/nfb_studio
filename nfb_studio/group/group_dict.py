"""Internally used dictionary for groups."""
from nfb_studio.item_dict import ItemDict
from nfb_studio.widgets.sequence_nodes import GroupNode

from .group import Group
from .group_view import GroupView


class GroupDict(ItemDict):
    """Internally used dictionary for groups.
    This dictionary also contains some logic related to naming new groups.
    """
    stored_cls = Group

'''    def updateView(self, key):
        """Update the experiment view about an added/deleted item."""
        if self.experiment() is None or self.experiment().view() is None:
            return
        
        view = self._experiment.view()

        if key in self:
            # Item was added
            tree_item = TreeModelItem()
            tree_item.setText(key)
            view.property_tree.groups_item.addItem(tree_item)

            group_view = GroupView()
            group_view.setModel(self[key])
            view.groups.addWidget(key, group_view)

            node = GroupNode()
            node.setTitle(key)
            view.sequence_editor.toolbox().addItem(key, node)
        else:
            # Item was removed
            for i in range(view.property_tree.groups_item.childrenCount()):
                item = view.property_tree.groups_item.item(i)
                if item.text() == key:
                    view.property_tree.groups_item.removeItem(i)
                    break

            view.groups.removeWidget(key)
            view.sequence_editor.toolbox().removeItem(key)
'''