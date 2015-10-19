"""
The code removes colors from a sentence using trie data structure
which stores prefixes of colours.
Input: List of colors and sentence
Output: Sentence after removing colours
"""
from utilities import COLOR_SET
import re

"""
Create a trie to store list of strings with a word as a key.
"""


class Node(object):
    def __init__(self, end_node=False):
        self.end_node = end_node
        self.children = {}


class Trie(object):
    def __init__(self):
        self.root = Node()

    def insert(self, key):
        """
		Split a string and store the prefix as the child of
		the root.
		"""
        current = self.root
        for k in key.split():
            # print k
            if k not in current.children:
                current.children[k] = Node()
            current = current.children[k]
        current.end_node = True

    def search(self, key):
        """
		Search a word as a child of the root and return
		pointer to the node.
		"""
        current = self.root

        if key not in current.children:
            return False
        else:
            return current.children[key]


db = Trie()
for colors in COLOR_SET:
    db.insert(colors.lower())

def removeColor(sentence):
    """
	Creates a trie from list of colors.
	Uses this trie to remove color names from sentence
	"""

    # stringIndexed = sentence.split()
    stringIndexed  = re.findall(r"[\w']+", sentence)
    index = 0
    while index <= len(stringIndexed) - 1:
        # print stringIndexed[index],index,stringIndexed[index+1]
        j = index
        # print index
        current = db.search(stringIndexed[index])
        if current:
            while (current and current.children and stringIndexed[j + 1] in current.children):
                current = current.children[stringIndexed[j + 1]]
                j = j + 1

            if current.end_node:
                del stringIndexed[index:j + 1]
                # print stringIndexed
                # print index
                index = index - 1
            else:
                index = j + 1
            # print "index is",index
        else:
            index = index + 1

    return ' '.join(stringIndexed)


# if __name__ == '__main__':
#     print removeColor("jabra solemate nfc wireless bluetooth speakers (black)".lower())

