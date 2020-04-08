import numpy as np
import tensorflow as tf

NUM_EPOCHS      = 500
CURRENT_SESSION = None
TFCONFIG = tf.ConfigProto(device_count={'GPU': 0})

# TODO this file needs a serious cleanup
def train(x, y):
    print('======================================')
    print(x)
    print('======================================')
    print(y)
    n     = len(x)
    cut   = round(n*0.7) 
    trainX = np.array(x[:cut])
    trainY = np.array(y[:cut])
    testX  = np.array(x[cut:])
    testY  = np.array(y[cut:])
    numFeatures = trainX.shape[1]
    numLabels   = trainY.shape[1]

    print()
    print('Num features: %s' % numFeatures)
    print('Num labels: %s' % numLabels)
    print()

    with tf.Graph().as_default():
        with tf.Session(config=TFCONFIG) as sess:
            # TODO remove this. Tensorflow tries to use the gpu to
            # distribute load between cpu and gpu.
            with tf.device('/cpu:0'):
                # a smarter learning rate for gradientOptimizer
                learningRate = tf.train.exponential_decay(learning_rate=0.0008,
                                                          global_step= 1,
                                                          decay_steps=trainX.shape[0],
                                                          decay_rate= 0.95,
                                                          staircase=True)

                X = tf.placeholder(tf.float32, [None, numFeatures])
                yGold = tf.placeholder(tf.float32, [None, numLabels])
                weights = tf.Variable(tf.random_normal([numFeatures, numLabels],
                                                       mean=0,
                                                       stddev=(np.sqrt(6/numFeatures+
                                                                         numLabels+1)),
                                                       name="weights"))

                bias = tf.Variable(tf.random_normal([1,numLabels],
                                                    mean=0,
                                                    stddev=(np.sqrt(6/numFeatures+numLabels+1)),
                                                    name="bias"))
                
                # INITIALIZE our weights and biases
                init_OP = tf.initialize_all_variables()

                # PREDICTION ALGORITHM i.e. FEEDFORWARD ALGORITHM
                apply_weights_OP = tf.matmul(X, weights, name="apply_weights")
                add_bias_OP = tf.add(apply_weights_OP, bias, name="add_bias") 
                activation_OP = tf.nn.sigmoid(add_bias_OP, name="activation")

                # COST FUNCTION i.e. MEAN SQUARED ERROR
                cost_OP = tf.nn.l2_loss(activation_OP-yGold, name="squared_error_cost")

                # OPTIMIZATION ALGORITHM i.e. GRADIENT DESCENT
                training_OP = tf.train.GradientDescentOptimizer(learningRate).minimize(cost_OP)

                #####################
                ### RUN THE GRAPH ###
                #####################

                # Initialize all tensorflow variables
                sess.run(init_OP)

                ## Ops for vizualization
                # argmax(activation_OP, 1) gives the label our model thought was most likely
                # argmax(yGold, 1) is the correct label
                correct_predictions_OP = tf.equal(activation_OP,yGold)
                # False is 0 and True is 1, what was our average?
                accuracy_OP = tf.reduce_mean(tf.cast(correct_predictions_OP, "float"))

                # Initialize reporting variables
                cost = 0
                diff = 1

                train_accuracy = .0
                # Training epochs
                for i in range(NUM_EPOCHS):
                    if (i > 1 and diff < .0001) or train_accuracy > .85: 
                        print("change in cost %g; convergence."%diff)
                        break
                    else:
                        # Run training step
                        step = sess.run(training_OP, feed_dict={X: trainX, yGold: trainY})
                        # Report occasional stats
                        if i % 10 == 0:
                            # Generate accuracy stats on test data
                            train_accuracy, newCost = sess.run(
                                [accuracy_OP, cost_OP], 
                                feed_dict={X: trainX, yGold: trainY}
                            )
                            # Re-assign values for variables
                            diff = abs(newCost - cost)
                            cost = newCost

                            #generate print statements
                            print("step %d, save weightstraining accuracy %g"%(i, train_accuracy))
                            print("step %d, cost %g"%(i, newCost))
                            print("step %d, change in cost %g"%(i, diff))


                # How well do we perform on held-out test data?
                accuracy = sess.run(accuracy_OP, feed_dict={X: testX, yGold: testY})
                print(accuracy)
                print("final accuracy on test set: %s" % str(accuracy))

                weights_ = weights.eval(session=sess)
                bias_    = bias.eval(session=sess)
                sess.close()
                return weights_, bias_

def get_test_operation(scope_name, num_features, w, b):
    g = tf.Graph()
    with g.as_default():
        X       = tf.placeholder(tf.float32, [1, num_features], name='X')
        weights = tf.constant(w)
        bias    = tf.constant(b)
        
        apply_weights_OP = tf.matmul(X, weights, name='apply_weights')
        add_bias_OP      = tf.add(apply_weights_OP, bias, name='add_bias') 
        activation_OP    = tf.nn.sigmoid(add_bias_OP, name='activation')
    return g, X, activation_OP
