"""Internally used dictionary for blocks."""
from nfb_studio.util.qt.tree_model import TreeModelItem
from nfb_studio.item_dict import ItemDict
from nfb_studio.widgets.sequence_nodes import BlockNode

from .block import Block
from .block_view import BlockView


class BlockDict(ItemDict):
    """Internally used dictionary for blocks.
    This dictionary also contains some logic related to naming new blocks.
    """
    stored_cls = Block

'''    def updateView(self, key):
        """Update the experiment view about an added/deleted item."""
        if self.experiment() is None or self.experiment().view() is None:
            return
        
        view = self._experiment.view()

        print(list(self.keys()))
        if key in self:
            # Item was added
            tree_item = TreeModelItem()
            tree_item.setText(key)
            view.property_tree.blocks_item.addItem(tree_item)
            
            block_view = BlockView()
            block_view.setModel(self[key])
            view.blocks.addWidget(key, block_view)

            node = BlockNode()
            node.setTitle(key)
            view.sequence_editor.toolbox().addItem(key, node)

            print("Added " + key)
        else:
            # Item was removed
            for i in range(view.property_tree.blocks_item.childrenCount()):
                item = view.property_tree.blocks_item.item(i)
                if item.text() == key:
                    view.property_tree.blocks_item.removeItem(i)
                    break

            view.blocks.removeWidget(key)
            view.sequence_editor.toolbox().removeItem(key)

            print("Removed " + key)
'''