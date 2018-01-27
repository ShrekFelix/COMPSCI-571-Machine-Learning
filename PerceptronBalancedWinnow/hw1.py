# library
import numpy as np
import matplotlib.pyplot as plt
import copy

# S: [(x, y)(x,y)...(x,y)]
#      |  |
#      |  S[i][1]:labels yi
#      S[i][0]:images xi(784,)

def perceptron(S, I, converge=1):
    # initialization
    w = [0 for d in range( len(S[0][0]) )]
    W = []
    for e in range(I):
        mistakes = 0 # number of mistakes made in each epoch
        for i in range(len(S)): # iterate over dataset
            if S[i][1] * np.dot(w, S[i][0]) <= 0: # label not agree with prediction
                mistakes += 1
                w += np.dot(S[i][1], S[i][0])
        W.append(copy.deepcopy(w)) # save w after each epoch
        if ( 1 - mistakes / len(S) ) >= converge: # converges
            break
    return W

def balanced_winnow(S, I, eta=0.1, converge=1):
    p = len(S[0][0])
    wp = [1/(2*p) for i in range(p)]
    wn = [1/(2*p) for i in range(p)]
    W = []
    for e in range(I):
        mistakes = 0
        for i in range(len(S)): # iterate over dataset
            if S[i][1] * ( np.dot(wp, S[i][0]) - np.dot(wn, S[i][0]) ) <= 0: # label not agree with prediction
                mistakes += 1
                s = 0 # to normalize w
                for j in range(p): # update each element of one weight vector
                    wp[j] *= np.exp(eta * S[i][1] * S[i][0][j])
                    wn[j] *= np.exp(-eta * S[i][1] * S[i][0][j])
                    s += wp[j] + wn[j]
                # normalization
                wp = np.dot(wp, 1/s)
                wn = np.dot(wn, 1/s)
        W.append(wp - wn) # save w after each epoch
        if ( 1 - mistakes / len(S) ) >= converge: # converges
            break
    return W

def accuracy(S, W):
    accuracy = []
    for e in range(len(W)): # for each epoch
        mistakes = 0
        for i in range(len(S)): # count mistakes
            if S[i][1] * np.dot(W[e], S[i][0]) <= 0: # label not agree with prediction
                mistakes += 1
        accuracy.append( 1 - mistakes / len(S) ) # update list of accuracy for each epoch
    return accuracy
    
def confusion_matrix(data, w, b=0):
    '''
b: bias in the classification hyperplane.
Useful for computing different sets of TPR/FPR pairs and plotting ROCs.
'''
    TP = 0
    FP = 0
    FN = 0
    TN = 0
    for i in range(len(data)): # iterate over dataset
        y_hat = np.dot(w, data[i][0]) - b
        if y_hat * data[i][1] > 0:
            if data[i][1] > 0:
                TP += 1
            else:
                TN += 1
        else:
            if data[i][1] > 0:
                FN += 1
            else:
                FP += 1            
    return [ [TP, FP], [FN, TN] ]

def ROC(data, w, start = -10, stop = 10, num = 100):
    x = []
    y = []
    for b in np.linspace(start, stop, num):
        [ [TP, FP], [FN, TN] ] = confusion_matrix(data, w, b)
        TPR = TP / (TP + FN)
        FPR = FP / (FP + TN)
        x.append(FPR)
        y.append(TPR)
    return x, y

def AUC(x, y):
    area = 0
    x.append(0)
    y.append(0)
    for i in range(len(x)-1):
        area += (x[i] - x[i+1]) * (y[i+1] + y[i])
    area /= 2
    return area

# import data from MNIST
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/")

# Datasets    DataSet         ndarray
#
# mnist ------ train -------- images(55000, 784)
#        |____ test        |_ labels(55000,)

# arrange data into training and testing group, filter for digit '9' and '4'
train =[]
for i in range( len(mnist.train.labels) ):
    # digit "4" -> -1
    if mnist.train.labels[i] == 4:
        train.append( (mnist.train.images[i], -1) )
    # digit "9" -> 1
    elif mnist.train.labels[i] == 9:
        train.append( (mnist.train.images[i], 1) )

test =[]
for i in range( len(mnist.test.labels) ):
    # digit "4" -> -1
    if mnist.test.labels[i] == 4:
        test.append( (mnist.test.images[i], -1) )
    # digit "9" -> 1
    elif mnist.test.labels[i] == 9:
        test.append( (mnist.test.images[i], 1) )
        
# homework problems
# analysis
# (a)
plt.scatter([0,0], [0,1], marker='+')
plt.scatter([1,1], [0,1], marker='_')
plt.plot([0.5 for i in range(100)], np.linspace(0,1,100))
plt.show()

# (b)
plt.scatter([0,1], [0,1], marker='+')
plt.scatter([0,1], [1,0], marker='_')
plt.show()

# (c)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter([0,1,0,1], [0,0,1,1], [0,0,0,0], marker='+')
ax.scatter([0,1,0,1], [0,0,1,1], [1,1,1,1], marker='_')
x = np.linspace(0,1,100)
y = np.linspace(0,1,100)
x, y = np.meshgrid(x, y)
ax.plot(x, y, [0.5 for i in range(100)])
plt.show()

# programming
# 1 perceptron
# (a). Run the function perceptron on the training set and plot the evolution of the accuracy versus the epoch counter.
W_p = perceptron(train, 500)
acc_p_train = accuracy(train, W_p)
plt.plot(range(1, len(acc_p_train)+1), acc_p_train)
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.show()

# (b). Plot the evolution of testing dataset accuracy versus the epoch counter (use the same figure as in part (a)).
acc_p_test = accuracy(test, W_p)
l_train, = plt.plot(range(1, len(acc_p_train)+1), acc_p_train)
l_test, = plt.plot(range(1, len(acc_p_test)+1), acc_p_test)
plt.legend(handles=[l_train, l_test], labels=['train', 'test'], loc='best')
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.show()

# (c). Report the accuracy and confusion matrix of the perceptron algorithm on the testing set after the last epoch.
print('accuracy: ',acc_p_test[-1])
print('confusion matrix: ', confusion_matrix(test, W_p[-1]))

# (d).
w_prime = perceptron(train[:round(len(test)/3)], 1)[-1]
x_prime, y_prime = ROC(test[:round(len(test)/3)], w_prime, -1000, 1000, 1000)
w_star = perceptron(train, 100)[-1]
x_star, y_star = ROC(test, w_star, -1000, 1000, 1000)
plt.figure()
l_prime, = plt.plot(x_prime, y_prime)
l_star, = plt.plot(x_star, y_star)
plt.xlabel('FPR')
plt.ylabel('TPR')
plt.legend(handles=[l_prime, l_star], labels=['w_prime', 'w_star'], loc='best')
plt.show()


# (e).
print( AUC(x_prime, y_prime) )
print( AUC(x_star, y_star) )

# 2 balanced winnow
# (a).
W_bw = balanced_winnow(train, 30, 0.05)
acc_bw_train = accuracy(train, W_bw)
plt.plot(range(1,len(acc_bw_train)+1), acc_bw_train)
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.show()

acc_bw_test = accuracy(test, W_bw)
print('accuracy: ',acc_bw_test[-1])
print('confusion matrix: ', confusion_matrix(test, W_bw[-1]))

# (b).
# test eta iteratively
eta=0.03
L=[]
label=[]
while eta<0.11:
    eta+=0.01
    W_bw = balanced_winnow(train, 30, eta)
    acc_bw = accuracy(train, W_bw)
    print('plotting ', eta)
    label.append(eta)
    l, = plt.plot(range(1, len(acc_bw)+1), acc_bw)
    L.append(l)



plt.legend(handles=L, labels=label, loc='best')
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.show()