import random as ra
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from numpy import linalg as LA
from scipy.misc import logsumexp

#---------------------------------------------------------------------------------
# Utility Functions - There is no need to edit code in this section.
#---------------------------------------------------------------------------------

# Reads a data matrix from file.
# Output: X: data matrix.
def readData(file):
    X = []
    with open(file,"r") as f:
        for line in f:
            X.append(map(float,line.split(" ")))
    return np.array(X)


# plot 2D toy data
# input: X: n*d data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
#        Label: n*K matrix, each row corresponds to the soft counts for all mixtures for an example
#        title: a string represents the title for the plot
def plot2D(X,K,Mu,P,Var,Label,title):
    r=0.25
    color=["r","b","k","y","m","c"]
    n,d = np.shape(X)
    per= Label/(1.0*np.tile(np.reshape(np.sum(Label,axis=1),(n,1)),(1,K)))
    fig=plt.figure()
    plt.title(title)
    ax=plt.gcf().gca()
    ax.set_xlim((-20,20))
    ax.set_ylim((-20,20))
    for i in xrange(len(X)):
        angle=0
        for j in xrange(K):
            cir=pat.Arc((X[i,0],X[i,1]),r,r,0,angle,angle+per[i,j]*360,edgecolor=color[j])
            ax.add_patch(cir)
            angle+=per[i,j]*360
    for j in xrange(K):
        sigma = np.sqrt(Var[j])
        circle=plt.Circle((Mu[j,0],Mu[j,1]),sigma,color=color[j],fill=False)
        ax.add_artist(circle)
        text=plt.text(Mu[j,0],Mu[j,1],"mu=("+str("%.2f" %Mu[j,0])+","+str("%.2f" %Mu[j,1])+"),stdv="+str("%.2f" % np.sqrt(Var[j])))
        ax.add_artist(text)
    plt.axis('equal')
    plt.show()

#---------------------------------------------------------------------------------



#---------------------------------------------------------------------------------
# K-means methods - There is no need to edit code in this section.
#---------------------------------------------------------------------------------

# initialization for k means model for toy data
# input: X: n*d data matrix;
#        K: number of mixtures;
#        fixedmeans: is an optional variable which is
#        used to control whether Mu is generated from a deterministic way
#        or randomized way
# output: Mu: K*d matrix, each row corresponds to a mixture mean;
#         P: K*1 matrix, each entry corresponds to the weight for a mixture;
#         Var: K*1 matrix, each entry corresponds to the variance for a mixture;
def init(X,K,fixedmeans=False):
    n, d = np.shape(X)
    P=np.ones((K,1))/float(K)

    if (fixedmeans):
        assert(d==2 and K==3)
        Mu = np.array([[4.33,-2.106],[3.75,2.651],[-1.765,2.648]])
    else:
        # select K random points as initial means
        rnd = np.random.rand(n,1)
        ind = sorted(range(n),key = lambda i: rnd[i])
        Mu = np.zeros((K,d))
        for i in range(K):
            Mu[i,:] = np.copy(X[ind[i],:])

    Var=np.mean( (X-np.tile(np.mean(X,axis=0),(n,1)))**2 )*np.ones((K,1))
    return (Mu,P,Var)


# K Means method
# input: X: n*d data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
# output: Mu: K*d matrix, each row corresponds to a mixture mean;
#         P: K*1 matrix, each entry corresponds to the weight for a mixture;
#         Var: K*1 matrix, each entry corresponds to the variance for a mixture;
#         post: n*K matrix, each row corresponds to the soft counts for all mixtures for an example
def kMeans(X, K, Mu, P, Var):
    prevCost=-1.0; curCost=0.0
    n=len(X)
    d=len(X[0])
    while abs(prevCost-curCost)>1e-4:
        post=np.zeros((n,K))
        prevCost=curCost
        #E step
        for i in xrange(n):
            post[i,np.argmin(np.sum(np.square(np.tile(X[i,],(K,1))-Mu),axis=1))]=1
        #M step
        n_hat=np.sum(post,axis=0)
        P=n_hat/float(n)
        curCost = 0
        for i in xrange(K):
            Mu[i,:]= np.dot(post[:,i],X)/float(n_hat[i])
            # summed squared distance of points in the cluster from the mean
            sse = np.dot(post[:,i],np.sum((X-np.tile(Mu[i,:],(n,1)))**2,axis=1))
            curCost += sse
            Var[i]=sse/float(d*n_hat[i])
        print curCost
    # return a mixture model retrofitted from the K-means solution
    return (Mu,P,Var,post)
#---------------------------------------------------------------------------------



#---------------------------------------------------------------------------------
# PART 1 - EM algorithm for a Gaussian mixture model
#---------------------------------------------------------------------------------

# E step of EM algorithm
# input: X: n*d data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
# output:post: n*K matrix, each row corresponds to the soft counts for all mixtures for an example
#        LL: a Loglikelihood value
def Estep(X,K,Mu,P,Var):
    n,d = np.shape(X) # n data points of dimension d
    post = np.zeros((n,K)) # posterior probabilities to compute
    LL = 0.0    # the LogLikelihood

    #Write your code here
    for n in range(len(X)):
        for m in range(K):

            post[n,m] = P[m]*gaussian(X[n,:],Mu[m,:],Var[m])

        total = sum(post[n,:])
        post[n,:] = post[n,:]/total
        LL += np.log(total)
    return (post,LL)

# Helper function for E-step
def gaussian(x, mean, var):
    d = len(x)
    logP = -d/2.0*np.log(2*np.pi*var)-0.5*np.sum((x-mean)**2)/var
    return np.exp(logP)


# M step of EM algorithm
# input: X: n*d data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
#        post: n*K matrix, each row corresponds to the soft counts for all mixtures for an example
# output:Mu: updated Mu, K*d matrix, each row corresponds to a mixture mean;
#        P: updated P, K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: updated Var, K*1 matrix, each entry corresponds to the variance for a mixture;
def Mstep(X,K,Mu,P,Var,post):
    n,d = np.shape(X) # n data points of dimension d

    #Write your code here
    num_points = np.sum(post, axis = 0)

    # Compute Mixture
    P = (num_points/np.sum(num_points)).reshape((K,1))
    for m in range(K):
        # Compute Mean
        prob_p = np.tile(post[:,m],d).reshape([d,n]).T
        Mu[m] = np.sum(np.multiply(prob_p,X), axis=0)/num_points[m]

        # Compute variance
        norm = lambda x: np.linalg.norm(x - Mu[m])**2
        Var[m] = np.sum(np.multiply(post[:,m],np.apply_along_axis(norm,1,X)))/(d*num_points[m])

    return (Mu,P,Var)


# Mixture of Guassians
# input: X: n*d data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
# output: Mu: updated Mu, K*d matrix, each row corresponds to a mixture mean;
#         P: updated P, K*1 matrix, each entry corresponds to the weight for a mixture;
#         Var: updated Var, K*1 matrix, each entry corresponds to the variance for a mixture;
#         post: updated post, n*K matrix, each row corresponds to the soft counts for all mixtures for an example
#         LL: Numpy array for Loglikelihood values
def mixGauss(X,K,Mu,P,Var):
    n,d = np.shape(X) # n data points of dimension d
    post = np.zeros((n,K)) # posterior probabilities

    #Write your code here
    #Use function Estep and Mstep as two subroutines
    LL = np.array([])
    prevLL = -np.infty
    currLL = -np.infty
    while (True):
        prevLL = currLL
        (post, currLL) = Estep(X,K,Mu,P,Var)
        #print currLL
        if (currLL-prevLL) <= 1e-6*np.abs(currLL): break
        LL = np.append(LL,currLL)
        (Mu,P,Var) = Mstep(X,K,Mu,P,Var,post)

    return (Mu,P,Var,post,LL)


# Bayesian Information Criterion (BIC) for selecting the number of mixture components
# input:  n*d data matrix X, a list of K's to try
# output: the highest scoring choice of K
def BICmix(X,Kset):
    n,d = np.shape(X)

    #Write your code here
    print Kset
    maxbic = -1e+300
    for k in Kset:
        # try each Gaussian with 5 random initializations
        for it in range(5):
            (Mu,P,Var) = init(X,k)
            (Mu,P,Var,post,LL) = mixGauss(X,k,Mu,P,Var)
            bic = LL[-1] - (k-1+k*d+k)*np.log(n)/2.0
            if (bic>=maxbic):
                maxbic = bic
                K=k
                print "k=%3d BIC=%f" % (K, maxbic)
    return K
#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------
# PART 2 - Mixture models for matrix completion
#---------------------------------------------------------------------------------

# RMSE criteria
# input: X: n*d data matrix;
#        Y: n*d data matrix;
# output: RMSE
def rmse(X,Y):
    return np.sqrt(np.mean((X-Y)**2))


# E step of EM algorithm
# input: X: n*d data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
# output:post: n*K matrix, each row corresponds to the soft counts for all mixtures for an example
#        LL: a Loglikelihood value
def Estep_part2(X,K,Mu,P,Var):
    n,d = np.shape(X) # n data points of dimension d
    post = np.zeros((n,K)) # posterior probabilities to tbd
    LL = 0.0

    #Write your code here
    for t in range(n):
        mask = (X[t,:]!=0)
        for j in range(K):
            post[t,j] = np.log(P[j])+log_gaussian(X[t,mask],Mu[j,mask],Var[j])
        total = logsumexp(post[t,:])
        LL += total
        post[t,:] = post[t,:] - total
    if K == 1:
        post = np.ones([n,1])
        return (post,LL)

    return (np.exp(post),LL)

def log_gaussian(x, mean, var):
    d = len(x)
    logP = -(d/2.0)*np.log(2*np.pi*var)-0.5*np.sum((x-mean)**2)/var
    return logP


# M step of EM algorithm
# input: X: n*d data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
#        post: n*K matrix, each row corresponds to the soft counts for all mixtures for an example
# output:Mu: updated Mu, K*d matrix, each row corresponds to a mixture mean;
#        P: updated P, K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: updated Var, K*1 matrix, each entry corresponds to the variance for a mixture;
def Mstep_part2(X,K,Mu,P,Var,post, minVariance=0.25):
    n,d = np.shape(X) # n data points of dimension d

    #Write your code here
    num_points = np.sum(post, axis = 0)
    # Compute Mixture
    P = (num_points/np.sum(num_points))
    for j in range(K):
        sse, weight = 0.0, 0.0
        for i in range(d):
            mask = (X[:,i]!=0)
            n_sum = np.sum(post[mask,j])

            if (n_sum>=1.0):
                Mu[j,i] = np.dot(post[mask,j],X[mask,i])/n_sum
            sse += np.dot(post[mask,j],(X[mask,i]-Mu[j,i])**2)
            weight += n_sum
        # Compute variance
        Var[j] = sse/weight
    for j in range(K):
        Var[j] = max([minVariance,Var[j]])
    return (Mu,P,Var)


# mixture of Guassians
# input: X: n*d data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
# output: Mu: updated Mu, K*d matrix, each row corresponds to a mixture mean;
#         P: updated P, K*1 matrix, each entry corresponds to the weight for a mixture;
#         Var: updated Var, K*1 matrix, each entry corresponds to the variance for a mixture;
#         post: updated post, n*K matrix, each row corresponds to the soft counts for all mixtures for an example
#         LL: Numpy array for Loglikelihood values
def mixGauss_part2(X,K,Mu,P,Var):
    n,d = np.shape(X) # n data points of dimension d
    post = np.zeros((n,K)) # posterior probs tbd

    #Write your code here
    LL = np.array([])
    prevLL = -1e+300
    #Use function Estep and Mstep as two subroutines
    c = 0

    while (True):
        (post, currLL) = Estep_part2(X,K,Mu,P,Var)
        if (currLL-prevLL) <= 1e-6*np.abs(currLL): break
        LL = np.append(LL,currLL)
        (Mu,P,Var) = Mstep_part2(X,K,Mu,P,Var,post)
        prevLL = currLL
        c+=1
    return (Mu,P,Var,post,LL)


# fill incomplete Matrix
# input: X: n*d incomplete data matrix;
#        K: number of mixtures;
#        Mu: K*d matrix, each row corresponds to a mixture mean;
#        P: K*1 matrix, each entry corresponds to the weight for a mixture;
#        Var: K*1 matrix, each entry corresponds to the variance for a mixture;
# output: Xnew: n*d data matrix with unrevealed entries filled
def fillMatrix(X,K,Mu,P,Var):
    n,d = np.shape(X)
    Xnew = np.copy(X)

    #Write your code here
    for u in range(n):
        mask = X[u,:]!=0
        mask0 = X[u,:]==0
        post = np.zeros(K)
        for j in range(K):
            post[j] = np.log(P[j])+log_gaussian(X[u,mask],Mu[j,mask],Var[j])
        post = np.exp(post-logsumexp(post))
        Xnew[u,mask0] = np.dot(post, Mu[:,mask0])
    return Xnew
#---------------------------------------------------------------------------------
