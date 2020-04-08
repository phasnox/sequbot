import tensorflow as tf
import numpy as np


def get_test_operation(scope_name, num_features, w, b):
    with tf.name_scope(scope_name):
        X       = tf.placeholder(tf.float32, [1, num_features], name='X')
        weights = tf.constant(w)
        bias    = tf.constant(b)
        
        apply_weights_OP = tf.matmul(X, weights, name='apply_weights')
        add_bias_OP      = tf.add(apply_weights_OP, bias, name='add_bias') 
        activation_OP    = tf.nn.sigmoid(add_bias_OP, name='activation')
    return tf.Session(), X, activation_OP

s, x, op = get_test_operation('q', 3, [[1.0],[2.0],[3.0]], [[4.0]])
a = s.run(op, feed_dict={x: [[1.0,2.0,3.0]]})
print()
print(a)
print()
s.close()
