"""Model index tests."""
from unittest.mock import Mock

import pytest

from django_reports.index.model import FieldTree, TreeNode


class TestTreeNode(object):
    def test_is_leaf_node(self):
        assert TreeNode(children=[]).is_leaf_node is True
        assert TreeNode(children=["some-child"]).is_leaf_node is False

    def test_add(self):
        mock_node = Mock(children=[])
        TreeNode.add(mock_node, "new-node")

        assert "new-node" in mock_node.children

    def test_remove(self):
        child_node_to_remove = Mock()
        mock_node = Mock(children=[Mock(), child_node_to_remove, Mock()])

        TreeNode.remove(mock_node, child_node_to_remove)

        assert child_node_to_remove not in mock_node.children


class TestFieldTree(object):
    @pytest.fixture
    def book_model_field_tree(self):
        return Mock(
            root=Mock(
                key="root",
                children=[
                    Mock(key="title", children=[]),  # Leaf node, char field
                    Mock(key="publication_date", children=[]),  # Leaf node, date field
                    Mock(key="edition", children=[]),  # Leaf node, char field
                    Mock(
                        key="reviews",
                        children=[Mock(key="rating", children=[])],
                    ),
                    Mock(
                        key="author",
                        children=[
                            Mock(
                                key="books",
                                children=[
                                    Mock(key="title", children=[]),
                                    Mock(key="publication_date", children=[]),
                                    Mock(key="edition", children=[]),
                                    Mock(
                                        key="reviews",
                                        children=[Mock(key="rating", children=[])],
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            )
        )

    @pytest.mark.parametrize(
        "node_path,expected_return_key",
        [
            # ========= Positive test cases =========
            # Node exists somewhere in the tree
            # =======================================
            (
                [],
                "root",
            ),
            (
                # Deep, non-leaf node
                ("author", "books", "reviews"),
                "reviews",
            ),
            (
                # leaf node
                ("author", "books", "reviews", "rating"),
                "rating",
            ),
            (
                # Depth 1 node
                ("edition",),
                "edition",
            ),
            # ========= Negative test cases =========
            # Node does not exist
            # =======================================
            (
                ("subtitle"),
                None,
            ),
            (
                ("author", "magazines"),
                None,
            ),
            (
                ("author", "books", "reviews", "rating", "posted_by"),
                None,
            ),
        ],
    )
    def test_find(self, node_path, expected_return_key, book_model_field_tree):
        node = FieldTree.find(book_model_field_tree, node_path)

        if expected_return_key:
            assert node and node.key == expected_return_key
        else:
            assert node is None
