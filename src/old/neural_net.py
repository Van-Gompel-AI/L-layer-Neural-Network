import numpy as np
import time

import math_operations

"""
Code based on the Neural Networks and Deep Learning courses on Coursera.
"""


def initialize_parameters_deep(layer_dims):
    """
    Arguments:
    layer_dims -- python array (list) containing the dimensions of each layer in our network

    :return:
    parameters -- python dictionary containing your parameters "W1", "b1", ..., "WL", "bL":
                    Wl -- weight matrix of shape (layer_dims[l], layer_dims[l-1])
                    bl -- bias vector of shape (layer_dims[l], 1)
    """
    np.random.seed(3)
    parameters = {}
    L = len(layer_dims)  # number of layers in the network

    for l in range(1, L):
        parameters['W' + str(l)] = np.random.randn(layer_dims[l], layer_dims[l - 1]) * 0.1
        parameters['b' + str(l)] = np.zeros((layer_dims[l], 1))

        assert (parameters['W' + str(l)].shape == (layer_dims[l], layer_dims[l - 1]))
        assert (parameters['b' + str(l)].shape == (layer_dims[l], 1))

    return parameters


def linear_forward(A, W, b):
    """
    Implement the linear part of a layer's forward propagation.

    Arguments:
    A -- activations from previous layer (or input data): (size of previous layer, number of examples)
    W -- weights matrix: numpy array of shape (size of current layer, size of previous layer)
    b -- bias vector, numpy array of shape (size of the current layer, 1)

    :return:
    Z -- the input of the activation function, also called pre-activation parameter
    cache -- a python tuple containing "A", "W" and "b" ; stored for computing the backward pass efficiently
    """

    Z = np.dot(W, A) + b
    cache = (A, W, b)

    return Z, cache


def linear_activation_forward(A_prev, W, b, activation):
    """
    Implement the forward propagation for the LINEAR->ACTIVATION layer

    Arguments:
    A_prev -- activations from previous layer (or input data): (size of previous layer, number of examples)
    W -- weights matrix: numpy array of shape (size of current layer, size of previous layer)
    b -- bias vector, numpy array of shape (size of the current layer, 1)
    activation -- the activation to be used in this layer, stored as a text string: "sigmoid" or "relu"

    :return:
    A -- the output of the activation function, also called the post-activation value
    cache -- a python tuple containing "linear_cache" and "activation_cache";
             stored for computing the backward pass efficiently
    """
    Z, linear_cache = linear_forward(A_prev, W, b)

    if activation == "sigmoid":
        A, activation_cache = math_operations.sigmoid(Z)

    elif activation == "relu":
        A, activation_cache = math_operations.relu(Z)

    cache = (linear_cache, activation_cache)

    return A, cache


def L_model_forward(X, parameters):
    """
    Implement forward propagation for the [LINEAR->RELU]*(L-1)->LINEAR->SIGMOID computation

    Arguments:
    X -- data, numpy array of shape (input size, number of examples)
    parameters -- output of initialize_parameters_deep()

    :return:
    AL -- activation value from the output (last) layer
    caches -- list of caches containing:
                every cache of linear_activation_forward() (there are L of them, indexed from 0 to L-1)
    """
    caches = []
    A = X
    L = len(parameters) // 2  # number of layers in the neural network

    # Implement [LINEAR -> RELU]*(L-1). Add "cache" to the "caches" list.
    # The for loop starts at 1 because layer 0 is the input
    for l in range(1, L):
        A_prev = A
        A, cache = linear_activation_forward(A_prev,
                                             parameters[f'W{l}'],
                                             parameters[f'b{l}'],
                                             activation="relu")
        caches.append(cache)

    # Implement LINEAR -> SIGMOID. Add "cache" to the "caches" list.
    AL, cache = linear_activation_forward(A,
                                          parameters[f'W{L}'],
                                          parameters[f'b{L}'],
                                          activation="sigmoid")
    caches.append(cache)

    return AL, caches


def compute_cost(AL, Y):
    """
    Implement the cost function defined by equation (7).

    Arguments:
    AL -- probability vector corresponding to your label predictions, shape (1, number of examples)
    Y -- true "label" vector (for example: containing 0 if non-cat, 1 if cat), shape (1, number of examples)

    :return:
    cost -- cross-entropy cost
    """

    m = Y.shape[1]

    # Compute loss from aL and y.
    cost = -(1 / m) * (np.sum(np.multiply(Y, np.log(AL)) + np.multiply((1 - Y), np.log(1 - AL))))

    cost = np.squeeze(cost)  # To make sure your cost's shape is what we expect (e.g. this turns [[17]] into 17).

    return cost


def linear_backward(dZ, cache):
    """
      Implement the linear portion of backward propagation for a single layer (layer l)

      Arguments:
      dZ -- Gradient of the cost with respect to the linear output (of current layer l)
      cache -- tuple of values (A_prev, W, b) coming from the forward propagation in the current layer

      :return:
      dA_prev -- Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
      dW -- Gradient of the cost with respect to W (current layer l), same shape as W
      db -- Gradient of the cost with respect to b (current layer l), same shape as b
      """
    A_prev, W, b = cache
    m = A_prev.shape[1]

    dW = (1 / m) * np.dot(dZ, A_prev.T)
    db = (1 / m) * np.sum(dZ, axis=1, keepdims=True)
    dA_prev = np.dot(W.T, dZ)

    return dA_prev, dW, db


def linear_activation_backward(dA, cache, activation):
    """
    Implement the backward propagation for the LINEAR->ACTIVATION layer.

    Arguments:
    dA -- post-activation gradient for current layer l
    cache -- tuple of values (linear_cache, activation_cache) we store for computing backward propagation efficiently
    activation -- the activation to be used in this layer, stored as a text string: "sigmoid" or "relu"

    :return:
    dA_prev -- Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
    dW -- Gradient of the cost with respect to W (current layer l), same shape as W
    db -- Gradient of the cost with respect to b (current layer l), same shape as b
    """
    linear_cache, activation_cache = cache

    if activation == "relu":
        dZ = math_operations.relu_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)

        # YOUR CODE ENDS HERE

    elif activation == "sigmoid":
        dZ = math_operations.sigmoid_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)

        # YOUR CODE ENDS HERE
    return dA_prev, dW, db


def L_model_backward(AL, Y, caches):
    """
    Implement the backward propagation for the [LINEAR->RELU] * (L-1) -> LINEAR -> SIGMOID group

    Arguments:
    AL -- probability vector, output of the forward propagation (L_model_forward())
    Y -- true "label" vector (containing 0 if non-cat, 1 if cat)
    caches -- list of caches containing:
                every cache of linear_activation_forward() with "relu" (it's caches[l], for l in range(L-1) i.e l = 0...L-2)
                the cache of linear_activation_forward() with "sigmoid" (it's caches[L-1])

    Returns:
    grads -- A dictionary with the gradients
             grads["dA" + str(l)] = ...
             grads["dW" + str(l)] = ...
             grads["db" + str(l)] = ...
    """
    grads = {}
    L = len(caches)  # the number of layers
    m = AL.shape[1]
    Y = Y.reshape(AL.shape)  # after this line, Y is the same shape as AL

    # Initializing the backpropagation
    dAL = - (np.divide(Y, AL) - np.divide(1 - Y, 1 - AL))

    # Lth layer (SIGMOID -> LINEAR) gradients.
    current_cache = caches[L - 1]
    dA_prev_temp, dW_temp, db_temp = linear_activation_backward(dAL, current_cache, activation="sigmoid")
    grads["dA" + str(L - 1)] = dA_prev_temp
    grads["dW" + str(L)] = dW_temp
    grads["db" + str(L)] = db_temp

    # Loop from l=L-2 to l=0
    for l in reversed(range(L - 1)):
        # lth layer: (RELU -> LINEAR) gradients.
        current_cache = caches[l]
        dA_prev_temp, dW_temp, db_temp = linear_activation_backward(grads["dA" + str(l + 1)], current_cache,
                                                                    activation="relu")
        grads["dA" + str(l)] = dA_prev_temp
        grads["dW" + str(l + 1)] = dW_temp
        grads["db" + str(l + 1)] = db_temp

    return grads


def update_parameters(params, grads, learning_rate):
    """
    Update parameters using gradient descent

    Arguments:
    params -- python dictionary containing your parameters
    grads -- python dictionary containing your gradients, output of L_model_backward

    Returns:
    parameters -- python dictionary containing your updated parameters
                  parameters["W" + str(l)] = ...
                  parameters["b" + str(l)] = ...
    """
    parameters = params.copy()
    L = len(parameters) // 2  # Number of layers in the neural network.

    # Update rule for each parameter.
    for l in range(L):
        parameters["W" + str(l + 1)] = parameters["W" + str(l + 1)] - learning_rate * grads[f"dW{l + 1}"]
        parameters["b" + str(l + 1)] = parameters["b" + str(l + 1)] - learning_rate * grads[f"db{l + 1}"]

    return parameters


class NeuralNet:
    def __init__(self, layers_dims, learning_rate=0.1, iterations=3000, print_cost=False):
        """
        Implements a L-layer neural network: [LINEAR->RELU]*(L-1)->LINEAR->SIGMOID.

        Arguments:
        X -- data, numpy array of shape (num_px * num_px * 3, number of examples)
        Y -- true "label" vector (containing 0 if cat, 1 if non-cat), of shape (1, number of examples)
        layers_dims -- list containing the input size and each layer size, of length (number of layers + 1).
        learning_rate -- learning rate of the gradient descent update rule
        num_iterations -- number of iterations of the optimization loop
        print_cost -- if True, it prints the cost every 100 steps

        :return:
        parameters -- parameters learnt by the model. They can then be used to predict.
        """
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.print_cost = print_cost
        self.costs = []  # Keep track of cost.
        self.parameters = initialize_parameters_deep(layers_dims)  # Initialise parameters based on layers dimensions.
        np.random.seed(1)

    def train(self, X, Y):
        """
        Loop over iterations. This step cannot be vectorised (unfortunately).

        :return:
        Parameters and costs.
        """
        startTime = time.time()

        for i in range(0, self.iterations):
            # Forward propagation: [LINEAR -> RELU]*(L-1) -> LINEAR -> SIGMOID.
            AL, caches = L_model_forward(X, self.parameters)

            # Compute cost:
            cost = compute_cost(AL, Y)

            # Backward propagation - compute gradients:
            grads = L_model_backward(AL, Y, caches)

            # Update parameters:
            self.parameters = update_parameters(self.parameters, grads, self.learning_rate)

            # Print the cost every 100 iterations
            if self.print_cost and i % 100 == 0 or i == self.iterations - 1:
                print("Cost after iteration {}: {}".format(i, np.squeeze(cost)))
            if i % 100 == 0 or i == self.iterations:
                self.costs.append(cost)

        executionTime = (time.time() - startTime)
        print('\nTraining time in seconds: ' + str(round(executionTime, 2)))
