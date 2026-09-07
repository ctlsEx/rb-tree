#include "algorithm.h"

#include <stdlib.h>

struct RedBlackTree {
    TreeNode *root;
};

static TreeNode *create_node(int value, TreeNode *parent)
{
    TreeNode *node = (TreeNode *)malloc(sizeof(*node));
    if (node == NULL) {
        return NULL;
    }

    node->value = value;
    node->color = NODE_RED;
    node->left = NULL;
    node->right = NULL;
    node->parent = parent;
    return node;
}

static int is_red(const TreeNode *node)
{
    return node != NULL && node->color == NODE_RED;
}

static void rotate_left(RedBlackTree *tree, TreeNode *node)
{
    TreeNode *pivot = node->right;
    if (pivot == NULL) {
        return;
    }

    node->right = pivot->left;
    if (pivot->left != NULL) {
        pivot->left->parent = node;
    }

    pivot->parent = node->parent;
    if (node->parent == NULL) {
        tree->root = pivot;
    } else if (node == node->parent->left) {
        node->parent->left = pivot;
    } else {
        node->parent->right = pivot;
    }

    pivot->left = node;
    node->parent = pivot;
}

static void rotate_right(RedBlackTree *tree, TreeNode *node)
{
    TreeNode *pivot = node->left;
    if (pivot == NULL) {
        return;
    }

    node->left = pivot->right;
    if (pivot->right != NULL) {
        pivot->right->parent = node;
    }

    pivot->parent = node->parent;
    if (node->parent == NULL) {
        tree->root = pivot;
    } else if (node == node->parent->right) {
        node->parent->right = pivot;
    } else {
        node->parent->left = pivot;
    }

    pivot->right = node;
    node->parent = pivot;
}

static void fix_insert(RedBlackTree *tree, TreeNode *node)
{
    while (node->parent != NULL && is_red(node->parent)) {
        TreeNode *grandparent = node->parent->parent;
        TreeNode *uncle;

        if (grandparent == NULL) {
            break;
        }

        if (node->parent == grandparent->left) {
            uncle = grandparent->right;
            if (is_red(uncle)) {
                node->parent->color = NODE_BLACK;
                uncle->color = NODE_BLACK;
                grandparent->color = NODE_RED;
                node = grandparent;
            } else {
                if (node == node->parent->right) {
                    node = node->parent;
                    rotate_left(tree, node);
                }
                node->parent->color = NODE_BLACK;
                grandparent->color = NODE_RED;
                rotate_right(tree, grandparent);
            }
        } else {
            uncle = grandparent->left;
            if (is_red(uncle)) {
                node->parent->color = NODE_BLACK;
                uncle->color = NODE_BLACK;
                grandparent->color = NODE_RED;
                node = grandparent;
            } else {
                if (node == node->parent->left) {
                    node = node->parent;
                    rotate_right(tree, node);
                }
                node->parent->color = NODE_BLACK;
                grandparent->color = NODE_RED;
                rotate_left(tree, grandparent);
            }
        }
    }

    tree->root->color = NODE_BLACK;
}

static void destroy_nodes(TreeNode *node)
{
    if (node == NULL) {
        return;
    }

    destroy_nodes(node->left);
    destroy_nodes(node->right);
    free(node);
}

RedBlackTree *rb_tree_create(void)
{
    RedBlackTree *tree = (RedBlackTree *)malloc(sizeof(*tree));
    if (tree != NULL) {
        tree->root = NULL;
    }
    return tree;
}

void rb_tree_destroy(RedBlackTree *tree)
{
    if (tree == NULL) {
        return;
    }

    destroy_nodes(tree->root);
    free(tree);
}

void rb_tree_clear(RedBlackTree *tree)
{
    if (tree == NULL) {
        return;
    }

    destroy_nodes(tree->root);
    tree->root = NULL;
}

int rb_tree_insert(RedBlackTree *tree, int value)
{
    TreeNode *current;
    TreeNode *parent = NULL;
    TreeNode *node;

    if (tree == NULL) {
        return -1;
    }

    current = tree->root;
    while (current != NULL) {
        parent = current;
        if (value == current->value) {
            return 0;
        }
        current = value < current->value ? current->left : current->right;
    }

    node = create_node(value, parent);
    if (node == NULL) {
        return -1;
    }

    if (parent == NULL) {
        tree->root = node;
    } else if (value < parent->value) {
        parent->left = node;
    } else {
        parent->right = node;
    }

    fix_insert(tree, node);
    return 1;
}

const TreeNode *rb_tree_root(const RedBlackTree *tree)
{
    return tree == NULL ? NULL : tree->root;
}
