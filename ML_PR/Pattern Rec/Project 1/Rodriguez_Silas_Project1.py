from pandas import read_excel, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

def npDescribe(features:np.ndarray, labels:np.ndarray, df:DataFrame):
    # Describe the data
    min_values = np.min(features, axis=0)
    max_values = np.max(features, axis=0)
    mean_values = np.mean(features, axis=0)
    variance_values = np.var(features, axis=0)

    # Print the results
    print("Minimum values:", min_values)
    print("Maximum values:", max_values)
    print("Mean values:", mean_values)
    print("Variance values:", variance_values)

    # Get each bin's frequency in the data
    P_js = np.bincount(labels) / labels.shape[0]
    clusters = np.unique(labels)

    # Compute the within-class variance
    Sw = []
    for k, cluster in enumerate(clusters):
        # isolate the data of this cluster:
        feature_cluster = features[labels==cluster]
        # compute each column's variance
        variance_values = np.var(feature_cluster, axis=0)
        # multiply with the P_j of this corresponding class
        variance_values *= P_js[k]
        Sw.append(variance_values)
    Sw = np.sum(Sw, axis=0)
    print(f'Within-Class Variance: {Sw}')

    # Compute the between-class variance
    Sb = []
    for k, cluster in enumerate(clusters):
        # isolate the data of this cluster:
        feature_cluster = features[labels==cluster]
        # compute each column's variance
        variance_values = np.power(np.mean(feature_cluster, axis=0) - mean_values, 2)
        # multiply with the P_j of this corresponding class
        variance_values *= P_js[k]
        Sb.append(variance_values)
    Sb = np.sum(Sb, axis=0)
    print(f'Between-Class Variance: {Sb}')

    # Compute the correlation matrix
    df[:, -1] = labels
    col_names = ['SepalL', 'SepalW', 'PetalL', 'PetalW', 'Species']
    df = DataFrame(df,columns=col_names)
    corr_matrix = df.corr()
    plt.figure(figsize=(10,8))    # create a 10 in x 8 in figure
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
    plt.title('Correlation Heatmap')

    # Plot each feature against the class label in a loop
    features_columns = df.columns[:-1]  # Exclude the last column (label)
    num_features = len(features_columns)

    plt.figure(figsize=(10, 8))

    for i, feature in enumerate(features_columns, start=1):
        plt.subplot(2, 2, i)
        plt.scatter(df[feature], df['Species'], marker='x', color='red')
        plt.title(f'{feature} vs Species')
        plt.xlabel(feature)
        plt.ylabel('Species')
        plt.xticks(np.arange(0,9,step=2))

    plt.tight_layout()
    plt.show()

def LS_classifier(X:np.ndarray, t:np.ndarray):
    weights = np.linalg.pinv(X).dot(t)
    return weights

def LS_evaluator(Weights:np.ndarray, X:np.ndarray, t:np.ndarray):
    prediction_matrix = X.dot(Weights)
    prediction_matrix = np.round(prediction_matrix, 0)
    misclassed = np.sum(prediction_matrix!=t)
    accuracy = 1 - misclassed / t.shape[0]
    return misclassed, accuracy*100

def BatchPerceptron(X:np.ndarray, epochs=1000):
    """
    @purpose:
        - try to compute the weights that would classify X correctly
    @pre:
        - X be a 2 class problem, with features in class 2 being scaled by -1
        - X is to be augmented with a column of 1s
    @return:
        weights- the weights that correctly all features of class X, if convergence
        k - epoch that BP converged on
    """
    weights = np.random.normal(loc=0, scale=1.0, size=X.shape[1]) # initial guess
    rho_k = .1 # initial learning rate
    for k in range(1,epochs+1):
        # compute the predictions
        predictions = X.dot(weights)
        # get the indeces of negative (misclassed) features
        bad_classes = predictions<=0
        # print(X[bad_classes].shape) # this should shrink over time
        # if no misclassifications, convergence
        if not np.any(predictions<=0):
            print(f'Converged at {k} epochs')
            return k, weights
        weights += rho_k * np.sum(X[bad_classes], axis=0)
        if k%10 == 0:
            rho_k *= 0.9
    print(f'Batch Perceptron Failed to Converge in {epochs} epochs')
    return k, weights

def BP_evaluator(w:np.ndarray, X:np.ndarray, t:np.ndarray):
    """
    @purpose:
        compute the misclassifications of the BP regardless of convergence
    @pre:
        weights (l+1) x 1
        X be the biased features N x (l+1)
        t is the labels for classes : 0,1 - N x 1
    """
    prediction_matrix = X.dot(w)
    classes = np.where(prediction_matrix > 0, 0, 1)   # if above threshold, give me a class 2, else class 1
    misclasses = np.sum(classes!=t)
    accuracy = 1 - misclasses / t.shape[0]   # get the accuracy from correct classes
    return misclasses, accuracy*100

def LS_multi_classifier(X:np.ndarray, T:np.ndarray):
    W = np.linalg.pinv(X).dot(T)
    return W

def LS_multi_evaluator(W:np.ndarray, X:np.ndarray, T:np.ndarray):
    # Computes the values s.t. N x (l+1) dot (l+1) x M => N x M predictions. N data points classed by M cols
    prediction_matrix = X.dot(W)
    predicts_one_hot = np.eye(W.shape[1])[np.argmax(prediction_matrix, axis=1)]
    # Find the misclassed points
    misclassed_data = np.where(~np.all(T == predicts_one_hot, axis=0))[0]
    # report the accuracy and count
    count = len(misclassed_data)
    accuracy = 1- count / T.shape[0]
    return count, accuracy*100

def main():
    # Seed the program
    np.random.seed(0)
    # Open the dataset
    df = read_excel('Proj1DataSet.xlsx').to_numpy()
    # Extract features and labels
    features = df[:, :-1]
    labels_text = df[:, -1]
    # Define class mapping
    class_mapping = {'setosa': 0, 'versicolor': 1, 'virginica': 2}
    # Convert text labels to numerical values
    labels = np.array([class_mapping[label] for label in labels_text])

    npDescribe(features=features, labels=labels, df=df)

    # Standardize the data:
    scaler = StandardScaler()
    feat_std = scaler.fit_transform(features)

    # Augment the features with a col of 1s
    feat_std = np.c_[np.ones(feat_std.shape[0]), feat_std]

    ######################################################################
    # Compute the weights for LS method on setosa vs others All Features #
    print('\nCompute the weights for LS method on setosa vs others All Features\n')
    features_part1 = feat_std.copy()    # copy the data to not overwrite original
    labels_part1 = labels.copy()
    # Convert the labels to 2 - class problem
    labels_part1 = np.where(labels_part1==0, 0, 1)
    # LS classifier weights output
    weights_LS1 = LS_classifier(X=features_part1, t=labels_part1)
    print(f'Least-Squares Weights: {weights_LS1.shape}, {weights_LS1}')
    misclassifications, accuracy = LS_evaluator(Weights=weights_LS1, X=features_part1, t=labels_part1)
    print(f'{misclassifications} miclassed vectors from Least-Squares with {accuracy}% using all features.')

    # Batch Perceptron Algorithm - take labels not in 0, and take a -1 scale of the rows
    X_batch = np.vstack((features_part1[labels_part1==0], np.multiply(-1,features_part1[labels_part1!=0])))
    k, weights_BP1 = BatchPerceptron(X=X_batch)
    print(f'Batch-Perceptron Weights: {weights_BP1.shape}, {weights_BP1}')
    misclasses, accuracy = BP_evaluator(w=weights_BP1, X=features_part1, t=labels_part1)
    print(f'{misclasses} miclassed vectors from Batch-Perceptron with {accuracy}% using all features & {k} epochs.')

    ######################################################################
    # Compute the weights for LS method on setosa vs others Features 3&4 #
    print('\nCompute the weights for LS method on setosa vs others Features 3&4\n')
    features_part2 = feat_std.copy()    # copy the data to not overwrite original
    features_part2 = features_part2[:, [0,3,4]]
    labels_part2 = labels.copy()
    # Convert the labels to 2 - class problem
    labels_part2 = np.where(labels_part1==0, 0, 1)
    # LS classifier weights output
    weights_LS2 = LS_classifier(X=features_part2, t=labels_part2)
    print(f'Least-Squares Weights: {weights_LS2.shape}, {weights_LS2}')
    misclassifications, accuracy = LS_evaluator(Weights=weights_LS2, X=features_part2, t=labels_part2)
    print(f'{misclassifications} miclassed vectors from Least-Squares with {accuracy}% using all features.')

    # Batch Perceptron Algorithm - take labels not in 0, and take a -1 scale of the rows
    X_batch = np.vstack((features_part2[labels_part2==0], np.multiply(-1,features_part2[labels_part2!=0])))
    k, weights_BP2 = BatchPerceptron(X=X_batch)
    print(f'Batch-Perceptron Weights: {weights_BP2.shape}, {weights_BP2}')
    misclasses, accuracy = BP_evaluator(w=weights_BP2, X=features_part2, t=labels_part2)
    print(f'{misclasses} miclassed vectors from Batch-Perceptron with {accuracy}% using all features & {k} epochs.')

    # plot least squares vs scatter data
    xline = np.linspace(features_part2[:, 1].min(), features_part2[:, 1].max())
    yline_LS = -(weights_LS2[0] + weights_LS2[1] * xline) / weights_LS2[2]
    yline_BP = -(weights_BP2[0] + weights_BP2[1] * xline) / weights_BP2[2]

    # since l = 2 , plot the features
    plt.scatter(features_part2[:,1], features_part2[:,2], cmap='rainbow_r', c=labels_part2, marker='o')
    plt.colorbar(label='Class labels')
    plt.plot(xline, yline_LS, color='green', label='Least-Squares d(x)')
    plt.plot(xline, yline_BP, color='black', label=f'Batch-Perceptron d(x) - {k}')
    plt.xlabel('Feature 3')
    plt.ylabel('Feature 4')
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    plt.legend()
    plt.show()
    ######################################################################
    # Compute the weights for LS method on virgi vs others All Features  #
    print('\nCompute the weights for LS method on virgi vs others All Features\n')
    features_part3 = feat_std.copy()    # copy the data to not overwrite original
    labels_part3 = labels.copy()
    # Convert the labels to 2 - class problem
    labels_part3 = np.where(labels_part3==2, 0, 1)
    # LS classifier weights output
    weights_LS3 = LS_classifier(X=features_part3, t=labels_part3)
    print(f'Least-Squares Weights: {weights_LS3.shape}, {weights_LS3}')
    misclassifications, accuracy = LS_evaluator(Weights=weights_LS3, X=features_part3, t=labels_part3)
    print(f'{misclassifications} miclassed vectors from Least-Squares with {accuracy}% using all features.')

    # Batch Perceptron Algorithm - take labels not in 0, and take a -1 scale of the rows
    X_batch = np.vstack((features_part3[labels_part3==0], np.multiply(-1,features_part3[labels_part3!=0])))
    k, weights_BP3 = BatchPerceptron(X=X_batch)
    print(f'Batch-Perceptron Weights: {weights_BP3.shape}, {weights_BP3}')
    misclasses, accuracy = BP_evaluator(w=weights_BP3, X=features_part3, t=labels_part3)
    print(f'{misclasses} miclassed vectors from Batch-Perceptron with {accuracy}% using all features & {k} epochs.')
    ######################################################################
    # Compute the weights for LS method on virgi vs others Features 3&4  #
    print('\nCompute the weights for LS method on virgi vs others Features 3&4\n')
    features_part4 = feat_std.copy()    # copy the data to not overwrite original
    features_part4 = features_part4[:, [0,3,4]]
    labels_part4 = labels.copy()
    # Convert the labels to 2 - class problem
    labels_part4 = np.where(labels_part4==2, 0, 1)
    # LS classifier weights output
    weights_LS4 = LS_classifier(X=features_part4, t=labels_part4)
    print(f'Least-Squares Weights: {weights_LS4.shape}, {weights_LS4}')
    misclassifications, accuracy = LS_evaluator(Weights=weights_LS4, X=features_part4, t=labels_part4)
    print(f'{misclassifications} miclassed vectors from Least-Squares with {accuracy}% using all features.')

    # Batch Perceptron Algorithm - take labels not in 0, and take a -1 scale of the rows
    X_batch = np.vstack((features_part4[labels_part4==0], np.multiply(-1,features_part4[labels_part4!=0])))
    k, weights_BP4 = BatchPerceptron(X=X_batch)
    print(f'Batch-Perceptron Weights: {weights_BP4.shape}, {weights_BP4}')
    misclasses, accuracy = BP_evaluator(w=weights_BP4, X=features_part4, t=labels_part4)
    print(f'{misclasses} miclassed vectors from Batch-Perceptron with {accuracy}% using all features & {k} epochs.')

    # plot least squares vs scatter data
    xline = np.linspace(features_part4[:, 1].min(), features_part4[:, 1].max())
    yline_LS = -(weights_LS4[0] + weights_LS4[1] * xline) / weights_LS4[2]
    yline_BP = -(weights_BP4[0] + weights_BP4[1] * xline) / weights_BP4[2]

    # since l = 2 , plot the features
    plt.scatter(features_part4[:,1], features_part4[:,2], cmap='rainbow_r', c=labels_part4, marker='o')
    plt.colorbar(label='Class labels')
    plt.plot(xline, yline_LS, color='green', label='Least-Squares d(x)')
    plt.plot(xline, yline_BP, color='black', label=f'Batch-Perceptron d(x) - {k}')
    plt.xlabel('Feature 3')
    plt.ylabel('Feature 4')
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    plt.legend()
    plt.show()
    ######################################################################
    # Multiclass LS on features 3 & 4 only
    print('Computing Boundaries for Setosa vs Versi vs Virgi Features 3 & 4 only...')
    # Design feature matrix
    features_part5 = feat_std.copy()    # copy the data to not overwrite original
    features_part5 = features_part5[:, [0,3,4]]
    # Design the T matrix
    labels_part5 = labels.copy()
    num_classes = len(np.unique(labels_part5))
    T_matrix = np.eye(num_classes)[labels_part5]    # one- hot encoding matrix

    # Design the W_matrix
    W_matrix = LS_multi_classifier(X=features_part5, T=T_matrix)
    print(W_matrix.shape, W_matrix) # l+1 x M -> 3x3 in this case
    misclasses, accuracy = LS_multi_evaluator(W=W_matrix, X=features_part5, T=T_matrix)
    print(f'{misclasses} misclassed points from Multi-Least-Squares with {accuracy}% using features 3 & 4')

    # l = 2 , plot the data 
    xline = np.linspace(features_part5[:, 1].min(), features_part5[:, 1].max())
    y1_line = -(W_matrix[0, 0] + W_matrix[1, 0] * xline) / W_matrix[2, 0]
    y2_line = -(W_matrix[0, 1] + W_matrix[1, 1] * xline) / W_matrix[2, 1]
    y3_line = -(W_matrix[0, 2] + W_matrix[1, 2] * xline) / W_matrix[2, 2]

    d01 = y1_line - y2_line
    d02 = y1_line - y3_line
    d12 = y2_line - y3_line

    plt.scatter(features_part5[:,1], features_part5[:,2], cmap='rainbow_r', c=labels_part5, marker='^')
    plt.colorbar(label='Class labels')
    plt.plot(xline, d01, color='green', label='d01')
    plt.plot(xline, d02, color='purple', label='d02')
    plt.plot(xline, d12, color='orange', label='d12')
    plt.xlabel('Feature 3')
    plt.ylabel('Feature 4')
    plt.xlim(-2,2)
    plt.ylim(-2,2)
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()