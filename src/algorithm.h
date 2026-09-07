#ifndef ALGORITHM_H
#define ALGORITHM_H

#ifdef _WIN32
#define ALGORITHM_API __declspec(dllexport)
#else
#define ALGORITHM_API
#endif

typedef enum NodeColor {
    NODE_RED = 0,
    NODE_BLACK = 1
} NodeColor;

typedef struct TreeNode {
    int value;
    NodeColor color;
    struct TreeNode *left;
    struct TreeNode *right;
    struct TreeNode *parent;
} TreeNode;

typedef struct RedBlackTree RedBlackTree;

ALGORITHM_API RedBlackTree *rb_tree_create(void);
ALGORITHM_API void rb_tree_destroy(RedBlackTree *tree);
ALGORITHM_API void rb_tree_clear(RedBlackTree *tree);

/* Retorna 1 ao inserir, 0 para valor repetido e -1 em erro de memoria. */
ALGORITHM_API int rb_tree_insert(RedBlackTree *tree, int value);

/* O ponteiro pertence a arvore e permanece valido ate a proxima alteracao. */
ALGORITHM_API const TreeNode *rb_tree_root(const RedBlackTree *tree);

#endif
