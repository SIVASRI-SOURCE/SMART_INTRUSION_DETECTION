print("**********************************************")
print("AI POWERED HONEYPOTS FOR ADVANCED THREAT DETECTION AND ANAYSIS")
print("**********************************************")
print()

#**************************Importing the libraries *****************************************
import numpy as np
import pandas as pd 
import pickle # saving and loading trained model
from os import path
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split 
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score
from sklearn.metrics import roc_curve, auc
import tensorflow as tf
from keras.layers import Dense, LSTM, MaxPool1D, Flatten, Dropout # importing dense layer
from keras.models import Sequential #importing Sequential layer
from keras.layers import Input
from keras.models import Model
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings('ignore')

#**************************1.Data Selection *****************************************

print("**********************************************")
print("Module2 --- Dataset Selection   ")
data =pd.read_csv('honeypot.csv')
print(data.head(5))
print(data.columns)
print(data.shape)
print("Dataset Selection Completed ")

#**************************2.Data Preprocessing *****************************************

print("**********************************************")
print("Module2 --- Dataset Preprocessing   ")
print("**********************************************")
print("Preprocessing Missing-value ")
print(data.isnull().sum())
data.drop(['difficulty'],axis=1,inplace=True)
data.info()
data.describe().T
data['label'].value_counts()
def change_label(df):
  df.label.replace(['apache2','back','land','neptune','mailbomb','pod','processtable','smurf','teardrop','udpstorm','worm'],'Dos',inplace=True)
  df.label.replace(['ftp_write','guess_passwd','httptunnel','imap','multihop','named','phf','sendmail','snmpgetattack','snmpguess','spy','warezclient','warezmaster','xlock','xsnoop'],'R2L',inplace=True)      
  df.label.replace(['ipsweep','mscan','nmap','portsweep','saint','satan'],'Probe',inplace=True)
  df.label.replace(['buffer_overflow','loadmodule','perl','ps','rootkit','sqlattack','xterm'],'U2R',inplace=True)
change_label(data)
data.label.value_counts()
label = pd.DataFrame(data.label)
std_scaler = StandardScaler()
def standardization(df,col):
    for i in col:
        arr = df[i]
        arr = np.array(arr)
        df[i] = std_scaler.fit_transform(arr.reshape(len(arr),1))
    return df
numeric_col = data.select_dtypes(include='number').columns
data = standardization(data,numeric_col)
data.drop(labels= ['label'], axis=1, inplace=True)
# label encoding (0,1,2,3,4) multi-class labels (Dos,normal,Probe,R2L,U2R)
le2 = preprocessing.LabelEncoder()
enc_label = label.apply(le2.fit_transform)
data['intrusion'] = enc_label
print(data.shape)
data
from sklearn.preprocessing import LabelEncoder
label_encoder=LabelEncoder()
print(data.shape)
print("Preprocessing-Label Encoding  ")
data['protocol_type']= label_encoder.fit_transform(data['protocol_type'])
data['service']= label_encoder.fit_transform(data['service'])
data['flag']= label_encoder.fit_transform(data['flag'])
print("Dataset Preprocessing Completed ")

#**************************3.EDA **************************************************

print("**********************************************")
print("EDA plot  ")
correlation_matrix = data.corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix (Heatmap)')
plt.show()
plt.figure(figsize=(10, 6))
plt.hist(data['protocol_type'], bins=30, edgecolor='black')
plt.title('Histogram of protocol_type')
plt.xlabel('Time')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()
plt.figure(figsize=(10, 6))
plt.hist(data['flag'], bins=30, edgecolor='black')
plt.title('Histogram of Flag')
plt.xlabel('Time')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()
data['intrusion'].value_counts()
sns.countplot(x ='intrusion', data = data)
plt.title(' Attack in intrusion  ')
plt.show()
print("Dataset EDA Completed ")

#**************************4.Data Splitting *****************************************

print("**********************************************")
X= data.drop(labels=['intrusion'], axis=1)
y= data['intrusion']
from sklearn.preprocessing import LabelBinarizer
y_data = LabelBinarizer().fit_transform(y)
X_data=np.array(X)
y_data=np.array(y_data)
print("Module4 --- Dataset Splitting -80% Training and 20% testing   ")
X_train, X_test, y_train, y_test = train_test_split(X_data,y_data, test_size=0.20, random_state=42)
print("X_train Shapes ",X_train.shape)
print("y_train Shapes ",y_train.shape)
print("x_test Shapes ",X_test.shape)
print("y_test Shapes ",y_test.shape)
print("Data Splitting Completed  ")

#**************************5.Classification  *****************************************

print("**********************************************")
print("Classification- Deep Learning -Autoencoder Feature Extraction using CNN Algorithm ")
print("**********************************************")
print("AutoEncoder Extract features ")
X = X_data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)
# Define autoencoder
input_dim = X_train.shape[1]
encoding_dim = 32  # Size of the encoded representation
input_layer = Input(shape=(input_dim,))
encoded = Dense(encoding_dim, activation='relu')(input_layer)
decoded = Dense(input_dim, activation='sigmoid')(encoded)
autoencoder = Model(input_layer, decoded)
encoder = Model(input_layer, encoded)
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')
# Train autoencoder
autoencoder.fit(X_train, X_train,
                epochs=50,
                batch_size=256,
                shuffle=True,
                validation_data=(X_test, X_test))
# Extract features
X_train_encoded = encoder.predict(X_train)
X_test_encoded = encoder.predict(X_test)
print("**********************************************")
print("Train Data Autoencoder Feature X_train_encoded Shapes ",X_train_encoded.shape)
print("Test Data Autoencoder Feature X_test_encoded Shapes ",X_test_encoded.shape)
# Reshape encoded data for CNN
X_train_reshaped = X_train_encoded.reshape((X_train_encoded.shape[0], X_train_encoded.shape[1], 1))
X_test_reshaped = X_test_encoded.reshape((X_test_encoded.shape[0], X_test_encoded.shape[1], 1))
print("**********************************************")
print("Train Data CNN  X_train_encoded Shapes ",X_train_reshaped.shape)
print("Test Data CNN X_test_encoded Shapes ",X_test_reshaped.shape)
# ************************************************************************************
print("**********************************************")
print("Convolutional neural networks Model ")
print("**********************************************")
# Define CNN model
model = Sequential([
    Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(X_train_reshaped.shape[1], 1)),
    MaxPooling1D(pool_size=2),
    Conv1D(filters=128, kernel_size=3, activation='relu'),
    MaxPooling1D(pool_size=2),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(y_train.shape[1], activation='softmax')  # Assuming y_train is one-hot encoded
])
# Compile the model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
# Train the CNN model
history = model.fit(X_train_reshaped, y_train,
                    epochs=10,
                    batch_size=64,
                    validation_split=0.2)
model.save('Model.h5')
loss, accuracy = model.evaluate(X_test_reshaped, y_test)
print(f'Test Loss: {loss}')
print(f'Test Accuracy: {accuracy}')
# Plot training & validation accuracy values
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
# Plot training & validation loss values
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.tight_layout()
plt.show()

#**************************6.Prediction   *****************************************

print("**********************************************")
print("Prediction- Deep Learning -Autoencoder Feature Extraction using CNN Algorithm ")
y_predict = model.predict(X_test_reshaped)
y_pred = y_predict.argmax(axis=-1)
y_test = y_test.argmax(axis = -1 )

#**************************7.Performance Analysis *****************************************

Acc_result=accuracy_score(y_test, y_pred)*100
print("-Autoencoder Feature Extraction using CNN Algorithm Accuracy is:",Acc_result,'%')
print()
print("**********************************************")
print("-Autoencoder Feature Extraction using CNN Algorithm Classification Report ")
print()
report = classification_report(y_test, y_pred)
print(report)
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
cm = confusion_matrix(y_test, y_pred)
cm_display = ConfusionMatrixDisplay(cm)
print("Confusion Matrix:\n", cm)
cm_display.plot()
plt.show()
AECNN_cm=cm
print(AECNN_cm)
print()
i=1
j=1
TP = AECNN_cm[i, i]
TN = sum(AECNN_cm[i, j] for j in range(AECNN_cm.shape[1]) if i != j)
FP = sum(AECNN_cm[i, j] for j in range(AECNN_cm.shape[1]) if i != j)
FN = sum(AECNN_cm[i, j] for i in range(AECNN_cm.shape[0]) if i != j)

def calculate_metrics(tp, tn, fp, fn):
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1_score = 2 * (precision * recall) / (precision + recall)
    ccu = (tp + tn) / (tp + tn + fp + fn)
    memory_switch_kb = 10 * (tp + tn + fp + fn)  
    return precision, recall, f1_score, ccu, memory_switch_kb

print("**********************************************")
print("Calculation - Classification Report ")
print("**********************************************")
tp = TP
tn = TN
fp = FP
fn = FN
precision, recall, f1_score, ccu, memory_switch_kb = calculate_metrics(tp, tn, fp, fn)
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1_score:.4f}")
print(f"CCU: {ccu:.4f}")
print(f"Memory in switch (Kb): {memory_switch_kb} Kb")
metrics = ['Precision', 'Recall', 'F1 Score', 'CCU']
values = [precision, recall, f1_score, ccu]  
plt.figure(figsize=(10, 6))
bars = plt.bar(metrics, values, color=['blue', 'orange', 'green', 'red'])
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2 - 0.1, yval + 0.05, round(yval, 4), ha='center', va='bottom')

plt.title('Performance Metrics')
plt.xlabel('Metrics')
plt.ylabel('Values')
plt.show()

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

# Flatten data for classical models
X_train_flat = X_train_encoded
X_test_flat = X_test_encoded

# Random Forest
print("\n--- Random Forest ---")
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train_flat, y_train.argmax(axis=1))
rf_pred = rf.predict(X_test_flat)
print("RF Accuracy:", accuracy_score(y_test, rf_pred)*100)
print(classification_report(y_test, rf_pred))

# Decision Tree
print("\n--- Decision Tree ---")
dt = DecisionTreeClassifier()
dt.fit(X_train_flat, y_train.argmax(axis=1))
dt_pred = dt.predict(X_test_flat)
print("DT Accuracy:", accuracy_score(y_test, dt_pred)*100)
print(classification_report(y_test, dt_pred))



#**************************9.Prediction on sample data  *****************************************
import numpy as np
from tensorflow.keras.models import load_model
model = load_model('Model.h5')
Sampledata=X_test_reshaped[0]
test_sample = Sampledata.reshape((Sampledata.shape[0], Sampledata.shape[1], 1))
test_sample.shape
test_sample = test_sample.reshape(1, 32, 1)  
predictions = model.predict(test_sample)

predicted_class = np.argmax(predictions, axis=1)
class_labels = ['Normal', 'Dos', 'Probe', 'R2L', 'U2R']  # Update if needed
print(f"Predicted class: {class_labels[predicted_class[0]]}")
print("Validated Prediction ")
print("Actual data",y_test[0])
print("predictions data",predicted_class)

"Test Samples"
df = pd.DataFrame(X_test_encoded)
df.to_csv('testdata.csv', index=False)

